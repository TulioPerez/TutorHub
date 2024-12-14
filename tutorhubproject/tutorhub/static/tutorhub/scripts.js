document.addEventListener("DOMContentLoaded", () => {
    // Authentication status
    const authStatus = JSON.parse(document.getElementById("auth-status").textContent);

    // Handle unread message badge
    const unreadBadge = document.getElementById("unread-badge");

    // Toggle tutor-specific fields in the registration form
    const userTypeRadios = document.querySelectorAll('input[name="user_type"]');
    const tutorFields = document.getElementById('tutor-fields');
   
    // Toggle visibility of tutor-specific registration fields
    if (userTypeRadios && tutorFields) {
        userTypeRadios.forEach(radio => {
            radio.addEventListener('change', function () {
                tutorFields.style.display = this.value === 'tutor' ? 'block' : 'none';
            });
        });
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

    // Handle row clicks on index page
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
    

    // Subject Handling
    const maxSubjects = 10;
    const subjectRowsContainer = document.getElementById("subject-rows-container");
    const addSubjectButton = document.getElementById("btn-add-subject");
    let subjectCount = subjectRowsContainer ? document.querySelectorAll(".subject-row").length : 0;

    if (addSubjectButton) {
        addSubjectButton.addEventListener("click", function () {
            console.log("Add Subject Button Clicked");
    
            if (subjectCount >= maxSubjects) {
                alert("You cannot add more than 10 subjects.");
                return;
            }
    
            const newRow = document.createElement("div");
            newRow.classList.add("subject-row", "row", "mb-3");
    
            newRow.innerHTML = `
                <div class="col-md-4">
                    <input type="text" name="subjects[]" class="form-control" placeholder="Subject" maxlength="50" required>
                </div>
                <div class="col-md-8">
                    <div class="checkbox-group">
                        <label><input type="checkbox" name="grade_levels_${subjectCount}[]" value="PK / KG"> Pre-K / KG</label>
                        <label><input type="checkbox" name="grade_levels_${subjectCount}[]" value="1 - 5"> 1 - 5</label>
                        <label><input type="checkbox" name="grade_levels_${subjectCount}[]" value="6 - 8"> 6 - 8</label>
                        <label><input type="checkbox" name="grade_levels_${subjectCount}[]" value="9 - 12"> 9 - 12</label>
                        <label><input type="checkbox" name="grade_levels_${subjectCount}[]" value="Adults"> Adults</label>
                    </div>
                </div>
                <div class="col-md-12 text-end mt-2">
                    <button type="button" class="btn btn-danger btn-sm remove-row">Remove</button>
                </div>
            `;
    
            // Append the new row
            subjectRowsContainer.appendChild(newRow);
    
            // Add event listener to the "Remove" button
            newRow.querySelector(".remove-row").addEventListener("click", function () {
                newRow.remove();
                subjectCount--;
                console.log("Subject Removed");
            });
    
            subjectCount++;
        });
    }

    // Credential Handling
    const maxCredentials = 7;
    const credentialRowsContainer = document.getElementById("credential-rows-container");
    const addCredentialButton = document.getElementById("btn-add-credential");

    if (addCredentialButton) {
        addCredentialButton.addEventListener("click", () => {
            const credentialCount = document.querySelectorAll(".credential-row").length;

            if (credentialCount >= maxCredentials) {
                alert("You cannot add more than 7 credentials.");
                return;
            }

            const newRow = document.createElement("div");
            newRow.classList.add("credential-row", "row", "mb-3");

            newRow.innerHTML = `
                <div class="col-md-10">
                    <input type="file" name="credentials[]" class="form-control" accept=".pdf,.doc,.docx,.jpg,.png" required>
                </div>
                <div class="col-md-2 text-end">
                    <button type="button" class="btn btn-danger btn-sm remove-row">X</button>
                </div>
            `;

            credentialRowsContainer.appendChild(newRow);

            // Add event listener to the "Remove" button
            newRow.querySelector(".remove-row").addEventListener("click", () => {
                newRow.remove();
            });
        });
    }

    // Event delegation for removing existing credentials
    credentialRowsContainer.addEventListener("click", (event) => {
        if (event.target.classList.contains("remove-credential")) {
            const row = event.target.closest(".credential-row");
            const credentialId = event.target.getAttribute("data-id");

            // Confirm deletion
            if (confirm("Are you sure you want to delete this credential?")) {
                // Make an AJAX request to delete the credential
                fetch(`/delete_credential/${credentialId}/`, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                    },
                })
                    .then((response) => {
                        if (response.ok) {
                            row.remove();
                            console.log("Credential deleted successfully.");
                        } else {
                            alert("Failed to delete credential.");
                        }
                    })
                    .catch((error) => console.error("Error:", error));
            }
        }
    });
    

    // Availability handling
    function addAvailabilityRow(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const newRow = document.createElement("div");
        newRow.classList.add("availability-row", "row", "mb-3");

        newRow.innerHTML = `
            <div class="col-md-4">
                <input type="text" name="availability_days[]" class="form-control" placeholder="Day (e.g., Mon)" maxlength="10" required>
            </div>
            <div class="col-md-4">
                <input type="time" name="availability_start[]" class="form-control" required>
            </div>
            <div class="col-md-4">
                <input type="time" name="availability_end[]" class="form-control" required>
            </div>
        `;

        container.appendChild(newRow);
    }


    // Availability button listener
    const addAvailabilityButton = document.getElementById("btn-add-availability");
    if (addAvailabilityButton) {
        addAvailabilityButton.addEventListener("click", () => {
            addAvailabilityRow("availability-rows-container");
        });
    }


    // Modal functionality for profile editing
    const modalForms = document.querySelectorAll(".modal form");
    modalForms.forEach(form => {
        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            const formData = new FormData(form);
            try {
                const response = await fetch(form.action, {
                    method: "POST",
                    body: formData,
                });
                if (response.ok) {
                    alert("Changes saved successfully!");
                    window.location.reload();
                } else {
                    alert("An error occurred. Please try again.");
                }
            } catch (error) {
                alert("Failed to save changes. Check your connection.");
            }
        });
    });
});
