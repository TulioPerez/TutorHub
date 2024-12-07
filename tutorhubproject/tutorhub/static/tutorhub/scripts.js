document.addEventListener("DOMContentLoaded", () => {
    // Handle unread message badge
    const unreadBadge = document.getElementById("unread-badge");

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

    // Handle clickable rows for navigation
    document.querySelectorAll('.clickable-row').forEach(row => {
        row.addEventListener('click', function () {
            const href = this.dataset.href; // Get the URL from data-href
            if (href) {
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
                    <label><input type="checkbox" name="grade_levels_${subjectCount}[]" value="Pre-K / KG"> Pre-K / KG</label>
                    <label><input type="checkbox" name="grade_levels_${subjectCount}[]" value="Elementary"> Elementary</label>
                    <label><input type="checkbox" name="grade_levels_${subjectCount}[]" value="Middle School"> Middle School</label>
                    <label><input type="checkbox" name="grade_levels_${subjectCount}[]" value="High School"> High School</label>
                    <label><input type="checkbox" name="grade_levels_${subjectCount}[]" value="University"> University</label>
                </div>
            `;
            subjectRowsContainer.appendChild(newRow);
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
});
