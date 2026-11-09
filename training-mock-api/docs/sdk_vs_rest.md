# SDK vs REST API

## REST API
- Communicate directly with HTTP endpoints using methods such as GET and POST.
- The caller handles URL construction, headers, authentication, timeouts, retries, pagination, and response parsing.
- Provides flexibility and direct control over requests.
- Requires more repetitive implementation code.

## SDK
- A Software Development Kit wraps API calls in reusable methods and classes.
- Hides HTTP details and provides convenient functions such as `get_parcels()`.
- Can centralize timeout handling, retries, pagination, and validation.
- Improves readability and reduces duplicated code.

## Conclusion
REST is the underlying communication interface, while an SDK provides a convenient abstraction over it. This assignment implements a small Python SDK using `httpx` and Pydantic.
