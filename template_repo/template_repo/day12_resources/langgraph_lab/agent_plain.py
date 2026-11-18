"""Plain Python tool-calling agent with limits, approval and audit logging."""

import time
from collections.abc import Callable
from dataclasses import dataclass, field

from llm import ChatModel
from tools import Tool, build_tools, validate_arguments


@dataclass
class AgentResult:
    answer: str
    steps: int
    stopped_by: str = "answer"
    audit: list[str] = field(default_factory=list)


def run_agent(
    question: str,
    model: ChatModel,
    approve: Callable[[str], bool],
    tools: dict[str, Tool] | None = None,
    max_steps: int = 6,
    max_seconds: float = 30.0,
) -> AgentResult:
    """Run the agent loop with execution limits and human approval."""

    registry = tools if tools is not None else build_tools()
    messages = [{"role": "user", "content": question}]
    audit: list[str] = []
    started = time.monotonic()
    steps = 0

    while steps < max_steps:
        if time.monotonic() - started >= max_seconds:
            return AgentResult("Stopped: time limit reached.", steps, "time_limit", audit)

        reply = model.chat(messages, [tool.schema() for tool in registry.values()])
        steps += 1
        messages.append(reply)

        calls = reply.get("tool_calls") or []
        if not calls:
            return AgentResult(reply.get("content", ""), steps, "answer", audit)

        for call in calls:
            call_id = call.get("id", "")
            name = call.get("name", "")
            arguments = call.get("arguments", {})
            result = ""

            tool = registry.get(name)

            if tool is None:
                result = f"Unknown tool: {name}"
                audit.append(f"{name}: failed: unknown tool")
            elif not isinstance(arguments, dict):
                result = "Invalid arguments: expected a JSON object."
                audit.append(f"{name}: invalid arguments: expected a JSON object")
            else:
                problem = validate_arguments(tool, arguments)

                if problem:
                    result = f"Invalid arguments: {problem}"
                    audit.append(f"{name}: invalid arguments: {problem}")
                elif tool.needs_approval:
                    try:
                        approved = approve(tool.preview(arguments))
                    except Exception as exc:  # noqa: BLE001 - handle tool and approval failures
                        approved = False
                        result = f"Approval failed: {exc}"

                    if not approved:
                        if not result:
                            result = "Action denied by human."
                        audit.append(f"{name}: denied by human")
                    else:
                        try:
                            result = tool.run(arguments)
                            audit.append(f"{name}: ran with {arguments}")
                        except Exception as exc:  # noqa: BLE001 - handle tool and approval failures
                            result = f"Tool error: {exc}"
                            audit.append(f"{name}: failed: {exc}")
                else:
                    try:
                        result = tool.run(arguments)
                        audit.append(f"{name}: ran with {arguments}")
                    except Exception as exc:  # noqa: BLE001 - handle tool and approval failures
                        result = f"Tool error: {exc}"
                        audit.append(f"{name}: failed: {exc}")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call_id,
                    "name": name,
                    "content": str(result),
                }
            )

    return AgentResult("Stopped: step limit reached.", steps, "step_limit", audit)
