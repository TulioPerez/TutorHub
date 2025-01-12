document.addEventListener("DOMContentLoaded", () => {
    // Authentication status
    const authMetaTag = document.querySelector('meta[name="auth-status"]');
    const isAuthenticated = authMetaTag?.content === "true";

    // Example: Log authentication status globally
    if (!isAuthenticated) {
        console.warn("User is not logged in.");
    }

    
    // ****************************
    // ***** Helper Functions *****
    // ****************************

    // Get CSRF token
    function getCSRFToken() {
        const cookieValue = document.cookie
            .split("; ")
            .find((row) => row.startsWith("csrftoken="))
            ?.split("=")[1];
        return cookieValue || "";
    }


    // Search button functionality
    const searchButton = document.querySelector('#search-form button[type="submit"]');
    if (searchButton && searchButton.dataset.alert) {
        searchButton.addEventListener("click", (event) => {
            event.preventDefault();
            alert("Please login to use this feature");
            window.location.href = searchButton.closest("form").action;
        });
    }


    // ******************************
    // ***** Language Selection *****
    // ******************************


    // Language selection handling
    const languageButtons = document.querySelectorAll('.language-select');
    languageButtons.forEach(button => {
        button.addEventListener('click', function() {
            const language = this.getAttribute('data-language');
            // Here, implement your language change logic
            console.log('Changing language to:', language);
            
            // Close the modal
            const modal = document.getElementById('languageModal');
            const bootstrapModal = bootstrap.Modal.getInstance(modal);
            bootstrapModal.hide();

            // Might want to reload the page or update the UI here as in:
            // window.location.href = `/?lang=${language}`;
        });
    });
    
});
