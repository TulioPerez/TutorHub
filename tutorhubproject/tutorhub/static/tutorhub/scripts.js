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


    // ************************
    // ***** Landing Page *****
    // ************************


    const gpsButton = document.getElementById("gps-button");
    const locationInput = document.getElementById("location-input");
    const mapContainer = document.getElementById("map-container");

    gpsButton.addEventListener("click", () => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const latitude = position.coords.latitude;
                    const longitude = position.coords.longitude;

                    // Populate the location field with coordinates
                    locationInput.value = `${latitude}, ${longitude}`;

                    // Update the map with the user's location
                    const mapSrc = `https://www.google.com/maps/embed/v1/view?key=YOUR_GOOGLE_MAPS_API_KEY&center=${latitude},${longitude}&zoom=14`;
                    mapContainer.innerHTML = `
                        <iframe
                            src="${mapSrc}"
                            width="100%"
                            height="100%"
                            style="border:0;"
                            allowfullscreen=""
                            loading="lazy">
                        </iframe>`;
                },
                (error) => {
                    console.error("Geolocation error:", error);
                    alert("Unable to fetch your location. Please enable location services and try again.");
                }
            );
        } else {
            alert("Geolocation is not supported by your browser.");
        }
    });



    // ************************
    // ***** Edit Profile *****
    // ************************

    // Profile image handling
    const profileImageSelection = document.getElementById("profile_image");
    const profileImagePreview = document.querySelector("#profile_image + img");
    const removeImageButton = document.querySelector(".remove-profile-image");

    if (profileImageSelection && profileImagePreview) {
        profileImageSelection.addEventListener("change", (event) => {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    profileImagePreview.src = e.target.result;
                    profileImagePreview.style.display = "block"; // Ensure the preview is visible
                    if (removeImageButton) {
                        removeImageButton.style.display = "inline-block"; // Show remove button if hidden
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }


    // Remove profile image
    if (removeImageButton) {
        removeImageButton.addEventListener("click", async () => {
            const confirmRemoval = confirm("Are you sure you want to remove the profile image?");
            if (!confirmRemoval) return;

            try {
                const response = await fetch("/remove_profile_image/", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                    },
                });
    
                // todo fix bugs: image persists in modal and profile after deletion until page refresh
                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        alert("Profile image removed successfully.");
    
                        // Dynamically update the modal to remove the image
                        if (profileImagePreview) {
                            profileImagePreview.src = ""; // Clear the image source
                            profileImagePreview.style.display = "none"; // Hide the preview
                        }
                        if (removeImageButton) {
                            removeImageButton.style.display = "none"; // Hide the remove button
                        }
                        if (profileImageSelection) {
                            profileImageSelection.value = ""; // Reset file input
                        }
                    } else {
                        // If success = false, show the error from the response
                        alert(data.error || "Failed to remove profile image.");
                    }
                } else {
                    alert("An error occurred while removing the profile image. Please try again.");
                }
            } catch (error) {
                console.error("Error:", error);
                alert("Failed to remove the profile image. Check your internet connection.");
            }
        });
    }


    // Credential handling
    const maxCredentials = 5;
    const credentialRowsContainer = document.getElementById("credential-rows-container");
    const addCredentialButton = document.getElementById("btn-add-credential");

    if (addCredentialButton) {
        addCredentialButton.addEventListener("click", () => {
            const credentialCount = document.querySelectorAll(".credential-row").length;

            if (credentialCount >= maxCredentials) {
                alert(`You cannot add more than ${maxCredentials} credentials.`);
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


    // Remove existing credential row
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


    // Handle Subjects & Levels
    const subjectRowsContainer = document.getElementById("subject-rows-container");
    const addSubjectButton = document.getElementById("btn-add-subject");
    const levels = JSON.parse(document.getElementById("level-options").textContent);

    // Add a new subject row
    addSubjectButton.addEventListener("click", function () {
        const subjectIndex = subjectRowsContainer.children.length; // Get current row index
        const newRow = document.createElement("div");
        newRow.classList.add("subject-row", "row", "mb-3");
    
        newRow.innerHTML = `
            <div class="col-md-4">
                <input type="text" name="subjects[]" class="form-control" placeholder="Subject" maxlength="100" required>
            </div>
            <div class="col-md-8">
                <div class="checkbox-group">
                    ${levels.map(level => `
                        <label class="form-check-label me-3">
                            <input type="checkbox" name="levels_${subjectIndex}[]" value="${level.value}">
                            ${level.display}
                        </label>
                    `).join("")}
                </div>
            </div>
            <div class="col-md-12 text-end mt-2">
                <button type="button" class="btn btn-danger btn-sm remove-row">Remove</button>
            </div>
        `;
    
        subjectRowsContainer.appendChild(newRow);
    
        // "Remove" functionality for dynamic rows
        newRow.querySelector(".remove-row").addEventListener("click", function () {
            newRow.remove();
        });
    });


    // Remove existing subject & level row
    subjectRowsContainer.querySelectorAll(".remove-row").forEach((button) => {
        button.addEventListener("click", async function () {
            const row = button.closest(".subject-row");
            const subjectLevelId = button.getAttribute("data-id"); // Get the ID of the SubjectLevel

            if (subjectLevelId) {
                const confirmDelete = confirm("Are you sure you want to delete this subject?");
                if (!confirmDelete) return;

                try {
                    const response = await fetch(`/delete_subject_level/${subjectLevelId}/`, {
                        method: "POST",
                        headers: {
                            "X-CSRFToken": getCSRFToken(),
                        },
                    });

                    if (response.ok) {
                        const data = await response.json();
                        if (data.success) {
                            alert("Subject removed successfully.");
                            row.remove(); // Remove the row from the modal
                        } else {
                            alert(data.error || "An error occurred while removing the subject.");
                        }
                    } else {
                        alert("Failed to remove the subject. Please try again.");
                    }
                } catch (error) {
                    console.error("Error:", error);
                    alert("Failed to remove the subject. Check your internet connection.");
                }
            } else {
                // If there's no ID, just remove the row from the modal
                row.remove();
            }
        });
    });


    // Availability handling
    const maxAvailability = 8; 
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
        const rowCount = availabilityContainer.querySelectorAll(".availability-row").length;

        if (rowCount >= maxAvailability) {
            alert(`You cannot add more than ${maxAvailability} availability slots.`);
            return;
        }

        const newRow = createAvailabilityRow();
        availabilityContainer.appendChild(newRow);
    });


    // Remove availability row
    availabilityContainer.querySelectorAll(".remove-availability").forEach(button => {
        button.addEventListener("click", () => {
            button.closest(".availability-row").remove();
        });
    });


    // *****************************************
    // ***** Edit Profile Modal Validation *****
    // *****************************************

    const editProfileModal = document.querySelector("#editProfileModal");
    if (editProfileModal) {
        const form = editProfileModal.querySelector("form"); // Select the form inside the modal
        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            const formData = new FormData(form);

            // Handle availability
            const availabilityRows = form.querySelectorAll('.availability-row');
            formData.delete('availability_days[]');
            formData.delete('availability_start[]');
            formData.delete('availability_end[]');
            availabilityRows.forEach(row => {
                formData.append('availability_days[]', row.querySelector('[name="availability_days[]"]').value);
                formData.append('availability_start[]', row.querySelector('[name="availability_start[]"]').value);
                formData.append('availability_end[]', row.querySelector('[name="availability_end[]"]').value);
            });

            // Handle subjects and levels
            form.querySelectorAll('.subject-row').forEach((row, index) => {
                const subject = row.querySelector('[name="subjects[]"]').value;
                formData.append(`subjects[]`, subject);
    
                row.querySelectorAll(`[name="levels_${index}[]"]`).forEach(checkbox => {
                    if (checkbox.checked) {
                        formData.append(`levels_${index}[]`, checkbox.value);
                    }
                });
            });

            try {
                const response = await fetch(form.action, {
                    method: "POST",
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCSRFToken(),
                    },
                });
                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        alert(data.message);
                        window.location.reload();
                    } else {
                        alert(data.error || "An error occurred. Please try again.");
                    }
                } else {
                    alert("An error occurred. Please try again.");
                }
            } catch (error) {
                console.error('Error:', error);
                alert("Failed to save changes. Check your connection.");
            }
        });
    }
    

    // *********************
    // ***** Messaging *****
    // *********************

    // todo if profile data incomplete - disable messaging

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

            // Cancel message edit
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
        
        
    // Message auto scrolling
    const scrollTarget = document.getElementById("scroll-target");
    const scrollToId = scrollTarget ? scrollTarget.getAttribute("data-scroll-to") : null;
    if (scrollToId) {
        const targetElement = document.getElementById(`message-${scrollToId}`);
        if (targetElement) {
            targetElement.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    }


    // *********************
    // ***** Following *****
    // *********************


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
