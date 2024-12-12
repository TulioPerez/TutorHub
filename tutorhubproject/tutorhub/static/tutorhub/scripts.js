document.addEventListener("DOMContentLoaded", () => {
    // Authentication status
    const authStatus = JSON.parse(document.getElementById("auth-status").textContent);

    // Handle unread message badge
    const unreadBadge = document.getElementById("unread-badge");

    // Toggle tutor-specific fields in the registration form
    const userTypeRadios = document.querySelectorAll('input[name="user_type"]');
    const tutorFields = document.getElementById('tutor-fields');

    // Handle row clicks on index page
    // const rows = document.querySelectorAll('.clickable-row');

    const pageTitle = document.getElementById('page-title');
    const searchForm = document.getElementById('search-form');
    const searchButton = document.querySelector('#search-form button[type="submit"]');
    
    // Profile section editing
    const editForm = document.getElementById("editProfileForm");

    // const toggleSearchBtn = document.getElementById('toggle-search');
    // toggleSearchBtn.addEventListener('click', () => {
    //     const isSearchVisible = searchForm.classList.toggle('d-none');
    //     pageTitle.style.display = isSearchVisible ? 'block' : 'none';
    //     toggleSearchBtn.textContent = isSearchVisible ? 'Search' : 'Cancel';
    // });

    // rows.forEach(row => {
    //     row.addEventListener('click', function () {
    //         window.location.href = this.dataset.href;
    //     });
    // });
    
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

    // Dynamic rows for subjects and grade levels
    const maxSubjects = 10;
    const subjectRowsContainer = document.getElementById("subject-rows");
    const addSubjectButton = document.getElementById("add-subject-row");

    let subjectCount = 1;

    if (addSubjectButton) {
        addSubjectButton.addEventListener("click", function () {
            if (subjectCount >= maxSubjects) return;

            const newRow = document.createElement("div");
            newRow.classList.add("subject-row", "row", "mb-3");

            newRow.innerHTML = `
                <div class="col-md-4">
                    <input type="text" name="subjects[]" class="form-control" placeholder="Subject" maxlength="50" required>
                </div>
                <div class="col-md-8">
                    <div class="checkbox-group">
                        <label><input type="checkbox" name="grade_levels_${subjectCount}[]" value="PK / KG"> Pre-K / KG</label>
                    </div>
                    <div class="checkbox-group">
                        <label><input type="checkbox" name="grade_levels_${subjectCount}[]" value="1 - 5"> 1 - 5</label>
                    </div>
                    <div class="checkbox-group">
                        <label><input type="checkbox" name="grade_levels_${subjectCount}[]" value="6 - 8"> 6 - 8</label>
                    </div>
                    <div class="checkbox-group">
                        <label><input type="checkbox" name="grade_levels_${subjectCount}[]" value="9 - 12"> 9 - 12</label>
                    </div>
                    <div class="checkbox-group">
                        <label><input type="checkbox" name="grade_levels_${subjectCount}[]" value="Adults"> Adults</label>
                    </div>
                </div>
                <button type="button" class="btn btn-danger remove-row">Remove</button>
            `;
           // Append the new row to the subject rows container
           subjectRowsContainer.appendChild(newRow);

           // Add event listener for the remove button
           newRow.querySelector(".remove-row").addEventListener("click", function () {
               subjectRowsContainer.removeChild(newRow);
           });

           // Increment the subject count
           subjectCount++;
        });
    }

    // Dynamic rows for credentials
    const maxCredentials = 7;
    const credentialRowsContainer = document.getElementById("credential-rows");
    const addCredentialButton = document.getElementById("add-credential-row");

    let credentialCount = 1;

    if (addCredentialButton) {
        addCredentialButton.addEventListener("click", function () {
            if (credentialCount >= maxCredentials) return;

            const newRow = document.createElement("div");
            newRow.classList.add("credential-row", "row", "mb-3");

            newRow.innerHTML = `
                <div class="col-md-12">
                    <input type="file" name="credentials[]" class="form-control" accept=".pdf,.doc,.docx,.jpg,.png" required>
                </div>
            `;
            credentialRowsContainer.appendChild(newRow);
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


    addCredentialButton.addEventListener("click", () => {
        const newRow = document.createElement("div");
        newRow.classList.add("row", "mb-3");

        newRow.innerHTML = `
            <div class="col">
                <input type="file" name="credentials[]" class="form-control" accept=".pdf,.doc,.docx,.jpg,.png" required>
            </div>
        `;
        credentialRowsContainer.appendChild(newRow);
    });

    // Handle removing existing credentials
    document.querySelectorAll(".remove-existing").forEach(button => {
        button.addEventListener("click", function() {
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
