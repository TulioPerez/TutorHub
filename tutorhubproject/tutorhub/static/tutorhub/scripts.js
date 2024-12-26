document.addEventListener("DOMContentLoaded", () => {
    // Authentication status
    const authStatus = JSON.parse(document.getElementById("auth-status").textContent);
    
    
    // Message auto scrolling
    const scrollTarget = document.getElementById("scroll-target");
    const scrollToId = scrollTarget ? scrollTarget.getAttribute("data-scroll-to") : null;
    if (scrollToId) {
        const targetElement = document.getElementById(`message-${scrollToId}`);
        if (targetElement) {
            targetElement.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    }


    // Message editing
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', () => {
            const messageId = button.getAttribute('data-message-id');
            const messageElement = button.parentElement.querySelector('p');
            const originalContent = messageElement.textContent;

            const textarea = document.createElement('textarea');
            textarea.value = originalContent;
            textarea.style.width = "100%";
            textarea.style.marginBottom = "5px";
            messageElement.replaceWith(textarea);

            const saveButton = document.createElement('button');
            saveButton.textContent = 'Save';
            saveButton.classList.add("btn", "btn-success", "btn-sm");

            const cancelButton = document.createElement("button");
            cancelButton.textContent = "Cancel";
            cancelButton.classList.add("btn", "btn-secondary", "btn-sm");
            cancelButton.style.marginLeft = "5px";

            button.after(saveButton, cancelButton);
            button.style.display = "none";

            saveButton.addEventListener("click", () => {
                fetch(`/edit_message/${messageId}/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                    },
                    body: JSON.stringify({ action: "edit", content: textarea.value })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === "success") {
                        const newMessageElement = document.createElement("p");
                        newMessageElement.textContent = data.content;
                        textarea.replaceWith(newMessageElement);
                        saveButton.remove();
                        cancelButton.remove();
                        button.style.display = "inline-block";
                    }
                });
            });

            // Cancel edit
            cancelButton.addEventListener("click", () => {
                const originalMessage = document.createElement("p");
                originalMessage.textContent = originalContent;
                textarea.replaceWith(originalMessage);
                saveButton.remove();
                cancelButton.remove();
                button.style.display = "inline-block";
            });
        });
    });


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
                    <input type="text" name="subjects[]" class="form-control" placeholder="Subject" maxlength="100" required>
                </div>
                <div class="col-md-8">
                    <div class="checkbox-group">
                        ${levels.map(level => `
                            <label><input type="checkbox" name="levels_${subjectCount}[]" value="${level.name}"> ${level.name}</label>
                        `).join('')}
                    </div>
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


        // Remove Prepopulated Rows
        document.querySelectorAll(".remove-row").forEach(button => {
            button.addEventListener("click", function () {
                this.closest(".subject-row").remove();
                subjectCount--;
            });
        });

    }


    // Credential Editing
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


    // Delete existing credentials
    credentialRowsContainer.addEventListener("click", (event) => {
        if (event.target.classList.contains("remove-credential")) {
            const row = event.target.closest(".credential-row");
            const credentialId = event.target.getAttribute("data-id");

            // Confirm deletion
            if (confirm("Are you sure you want to delete this credential?")) {
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
    const availabilityContainer = document.getElementById("availability-rows-container");
    const addAvailabilityButton = document.getElementById("btn-add-availability");
    const daysOfWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

    const createAvailabilityRow = (day = "", start = "", end = "") => {
        const newRow = document.createElement("div");
        newRow.classList.add("availability-row", "row", "mb-3");

        newRow.innerHTML = `
            <div class="col-md-4">
                <select name="availability_days[]" class="form-select" required>
                    <option value="" disabled ${!day ? "selected" : ""}>Select a day</option>
                    ${daysOfWeek
                        .map(d => `<option value="${d}" ${d === day ? "selected" : ""}>${d}</option>`)
                        .join("")}
                </select>
            </div>
            <div class="col-md-3">
                <input type="time" name="availability_start[]" value="${start}" class="form-control" required>
            </div>
            <div class="col-md-3">
                <input type="time" name="availability_end[]" value="${end}" class="form-control" required>
            </div>
            <div class="col-md-2 text-end">
                <button type="button" class="btn btn-danger btn-sm remove-availability">X</button>
            </div>
        `;

        // Event listener for "Remove" button
        newRow.querySelector(".remove-availability").addEventListener("click", () => {
            newRow.remove();
        });

        return newRow;
    };

    // Event listener for "Add availability" button
    addAvailabilityButton.addEventListener("click", () => {
        availabilityContainer.appendChild(createAvailabilityRow());
    });


    // Remove availability rows
    availabilityContainer.querySelectorAll(".remove-availability").forEach(button => {
        button.addEventListener("click", () => {
            button.closest(".availability-row").remove();
        });
    });


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


    // Handle following
    const followButtons = document.querySelectorAll(".follow-btn");

    followButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const tutorId = button.getAttribute("data-tutor-id");

            fetch(`/follow/${tutorId}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken(),
                },
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.action === "followed") {
                        button.textContent = "Unfollow";
                    } else if (data.action === "unfollowed") {
                        button.textContent = "Follow";
                    }
                })
                .catch((error) => console.error("Error following/unfollowing:", error));
        });
    });

    // Helper function for CSRF tokens
    function getCSRFToken() {
        const cookieValue = document.cookie
            .split("; ")
            .find((row) => row.startsWith("csrftoken="))
            ?.split("=")[1];
        return cookieValue || "";
    }

});
