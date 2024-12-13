document.addEventListener("DOMContentLoaded", () => {
    // Authentication status
    const authStatus = JSON.parse(document.getElementById("auth-status").textContent);

    // Handle unread message badge
    const unreadBadge = document.getElementById("unread-badge");

    // Toggle tutor-specific fields in the registration form
    const userTypeRadios = document.querySelectorAll('input[name="user_type"]');
    const tutorFields = document.getElementById('tutor-fields');

    // Handle row clicks on index page

    const pageTitle = document.getElementById('page-title');
    const searchForm = document.getElementById('search-form');
    const searchButton = document.querySelector('#search-form button[type="submit"]');

    // Profile section editing
    const editForm = document.getElementById("editProfileForm");

    // Toggle visibility of tutor-specific registration fields
    if (userTypeRadios && tutorFields) {
        userTypeRadios.forEach(radio => {
            radio.addEventListener('change', function () {
                tutorFields.style.display = this.value === 'tutor' ? 'block' : 'none';
            });
        });
    }

    // If search performed when not logged in, alert
    if (searchButton.dataset.alert) {
        searchButton.addEventListener("click", (event) => {
            event.preventDefault();
            alert("Please login to use this feature");
            window.location.href = searchButton.closest("form").action;
        });
    }

    // Handle clickable rows for navigation
    document.querySelectorAll(".clickable-row").forEach((row) => {
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

    // Subject Handling
    const maxSubjects = 10;
    const subjectRowsContainer = document.getElementById("subject-rows-container");
    const addSubjectButton = document.getElementById("btn-add-subject");

    let subjectCount = document.querySelectorAll(".subject-row").length;

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

    let credentialCount = document.querySelectorAll(".credential-row").length;

    if (addCredentialButton) {
        addCredentialButton.addEventListener("click", function () {
            console.log("Add Credential Button Clicked");

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
                    <button type="button" class="btn btn-danger btn-sm remove-row">Remove</button>
                </div>
            `;

            // Append the new row
            credentialRowsContainer.appendChild(newRow);

            // Add event listener to the "Remove" button
            newRow.querySelector(".remove-row").addEventListener("click", function () {
                newRow.remove();
                credentialCount--;
                console.log("Credential Removed");
            });
            credentialCount++;
        });
    }

    // Modal functionality for profile editing
    document.querySelectorAll(".modal form").forEach((form) => {
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


    // addCredentialButton.addEventListener("click", () => {
    //     const newRow = document.createElement("div");
    //     newRow.classList.add("row", "mb-3");

    //     newRow.innerHTML = `
    //         <div class="col">
    //             <input type="file" name="credentials[]" class="form-control" accept=".pdf,.doc,.docx,.jpg,.png" required>
    //         </div>
    //     `;
    //     credentialRowsContainer.appendChild(newRow);
    // });

    // Handle removing existing credentials
    document.querySelectorAll(".remove-existing").forEach(button => {
        button.addEventListener("click", function () {
            const credentialId = this.dataset.id;
            const row = this.closest(".credential-row");
            if (confirm("Are you sure you want to remove this credential?")) {
                fetch(`/credentials/${credentialId}/delete/`, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                }).then(response => {
                    if (response.ok) {
                        row.remove();
                    } else {
                        alert("Failed to delete credential. Please try again.");
                    }
                });
            }
        });
    });

});
