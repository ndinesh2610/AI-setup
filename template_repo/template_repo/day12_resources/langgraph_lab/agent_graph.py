"""LangGraph implementation of the tool-calling agent."""

import operator
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from llm import ChatModel
from tools import Tool, build_tools, validate_arguments


class AgentState(TypedDict):
    messages: Annotated[list[dict], operator.add]
    audit: Annotated[list[str], operator.add]


def build_graph(model: ChatModel, tools: dict[str, Tool] | None = None):
    registry = tools if tools is not None else build_tools()

    def llm_call(state: AgentState) -> dict:
        reply = model.chat(
            state["messages"],
            [tool.schema() for tool in registry.values()],
        )
        return {"messages": [reply]}

    def tool_node(state: AgentState) -> dict:
        reply = state["messages"][-1]
        new_messages = []
        new_audit = []

        for call in reply.get("tool_calls") or []:
            call_id = call.get("id", "")
            name = call.get("name", "")
            arguments = call.get("arguments", {})
            tool = registry.get(name)
            result = ""

            if tool is None:
                result = f"Unknown tool: {name}"
                new_audit.append(f"{name}: failed: unknown tool")

            elif not isinstance(arguments, dict):
                result = "Invalid arguments: expected a JSON object."
                new_audit.append(f"{name}: invalid arguments: expected a JSON object")

            else:
                problem = validate_arguments(tool, arguments)

                if problem:
                    result = f"Invalid arguments: {problem}"
                    new_audit.append(f"{name}: invalid arguments: {problem}")

                elif tool.needs_approval:
                    approved = interrupt(
                        {
                            "tool": name,
                            "arguments": arguments,
                            "preview": tool.preview(arguments),
                        }
                    )

                    if not approved:
                        result = "Action denied by human."
                        new_audit.append(f"{name}: denied by human")
                    else:
                        try:
                            result = tool.run(arguments)
                            new_audit.append(f"{name}: ran with {arguments}")
                        except Exception as exc:  # noqa: BLE001 - handle tool and approval failures
                            result = f"Tool error: {exc}"
                            new_audit.append(f"{name}: failed: {exc}")

                else:
                    try:
                        result = tool.run(arguments)
                        new_audit.append(f"{name}: ran with {arguments}")
                    except Exception as exc:  # noqa: BLE001 - handle tool and approval failures
                        result = f"Tool error: {exc}"
                        new_audit.append(f"{name}: failed: {exc}")

            new_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call_id,
                    "name": name,
                    "content": str(result),
                }
            )

        return {"messages": new_messages, "audit": new_audit}

    def should_continue(state: AgentState) -> str:
        last_message = state["messages"][-1]
        if last_message.get("tool_calls"):
            return "tool_node"
        return END

    builder = StateGraph(AgentState)
    builder.add_node("llm_call", llm_call)
    builder.add_node("tool_node", tool_node)
    builder.add_edge(START, "llm_call")
    builder.add_conditional_edges("llm_call", should_continue)
    builder.add_edge("tool_node", "llm_call")

    return builder.compile(checkpointer=InMemorySaver())


def _result(graph, result: dict) -> dict:
    interruptions = result.get("__interrupt__")
    if interruptions:
        return {
            "status": "needs_approval",
            "request": interruptions[0].value,
        }

    messages = result.get("messages", [])
    answer = messages[-1].get("content", "") if messages else ""

    return {
        "status": "done",
        "answer": answer,
        "audit": result.get("audit", []),
    }


def start(graph, question: str, thread_id: str, max_steps: int = 10) -> dict:
    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": max_steps,
    }

    result = graph.invoke(
        {
            "messages": [{"role": "user", "content": question}],
            "audit": [],
        },
        config=config,
    )
    return _result(graph, result)


def resume(
    graph,
    thread_id: str,
    approved: bool,
    max_steps: int = 10,
) -> dict:
    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": max_steps,
    }

    result = graph.invoke(
        Command(resume=approved),
        config=config,
    )
    return _result(graph, result)
