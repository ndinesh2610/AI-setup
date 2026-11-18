document.addEventListener("htmx:responseError", function (event) {
    const result = document.getElementById("result");
    const status = event.detail.xhr.status;

    const messages = {
        401: "Authentication is not configured. Contact your administrator.",
        403: "Session expired. Refresh the page and try again.",
        400: "Enter a valid question and try again.",
        422: "Check your question and try again."
    };

    result.textContent = messages[status] ||
        "Something went wrong. Please try again later.";
    result.setAttribute("role", "alert");
});

document.addEventListener("htmx:sendError", function () {
    const result = document.getElementById("result");
    result.textContent = "Connection failed. Check your connection and try again.";
    result.setAttribute("role", "alert");
});
