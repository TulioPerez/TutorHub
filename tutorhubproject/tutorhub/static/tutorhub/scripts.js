document.addEventListener("DOMContentLoaded", () => {
    // Authentication status
    const authStatus = JSON.parse(document.getElementById("auth-status").textContent);

    
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


    // Handle row clicks
    const clickableRow = document.querySelectorAll(".clickable-row");
    if (clickableRow.length > 0) {
        clickableRow.forEach((row) => {
            row.addEventListener("click", function () {
                const href = this.dataset.href;
    
                if (!authStatus) {
                    alert("Please login to view tutor profiles.");
                    window.location.href = "/login";
                } else if (href) {
                    window.location.href = href;
                }
            });
        });
    } else {
        console.warn("No clickable rows found.");
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

            // You might want to reload the page or update the UI here
            // For example:
            // window.location.href = `/?lang=${language}`;
        });
    });
    
});
