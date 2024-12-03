document.addEventListener("DOMContentLoaded", () => {
    const messageIcon = document.querySelector("#menu-messages");
    const unreadBadge = document.getElementById("unread-badge");

    fetch('/messages/unread_count/')
        .then(response => response.json())
        .then(data => {
            if (data.unread_count > 0) {
                unreadBadge.style.display = "inline-block";
                unreadBadge.textContent = data.unread_count;
            }
        })
        .catch(error => console.error("Error fetching unread messages count:", error));
});
