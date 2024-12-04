document.addEventListener("DOMContentLoaded", () => {
    // Handle unread message badge
    const messageIcon = document.querySelector("#menu-messages");
    const unreadBadge = document.getElementById("unread-badge");

    if (messageIcon && unreadBadge) {
        fetch('/messages/unread_count/')
            .then(response => response.json())
            .then(data => {
                if (data.unread_count > 0) {
                    unreadBadge.style.display = "inline-block";
                    unreadBadge.textContent = data.unread_count;
                }
            })
            .catch(error => console.error("Error fetching unread messages count:", error));
    }

    // Toggle tutor-specific fields in the registration form
    const userTypeRadios = document.querySelectorAll('input[name="user_type"]');
    const tutorFields = document.getElementById('tutor-fields');

    if (userTypeRadios && tutorFields) {
        userTypeRadios.forEach(radio => {
            radio.addEventListener('change', function () {
                tutorFields.style.display = this.value === 'tutor' ? 'block' : 'none';
            });
        });
    }
});
