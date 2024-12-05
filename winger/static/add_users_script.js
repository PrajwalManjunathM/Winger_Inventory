// User data store
let users = [];
let editingIndex = -1;

// Add a user
function addUser() {
    const fullNameInput = document.getElementById('user-full-name');
    const userNameInput = document.getElementById('user-name');
    const passwordInput = document.getElementById('user-password');
    const roleInput = document.getElementById('user-role');

    const fullName = fullNameInput.value.trim();
    const userName = userNameInput.value.trim();
    const password = passwordInput.value.trim();
    const role = roleInput.value.trim();

    if (fullName === "" || userName === "" || password === "" || role === "") {
        alert("All fields are required.");
        return;
    }

    // Add user to the array
    users.push({
        fullName: fullName,
        userName: userName,
        password: password,
        role: role,
    });
    renderUserList();

    // Clear the input fields
    fullNameInput.value = "";
    userNameInput.value = "";
    passwordInput.value = "";
    roleInput.value = "";
}

// Render the user list in a separate section
function renderUserList() {
    const userList = document.getElementById('user-list');
    userList.innerHTML = ""; // Clear current list

    users.forEach((user, index) => {
        const listItem = document.createElement('li');
        listItem.textContent = `${user.fullName} (${user.userName}) - Role: ${user.role}`;
        listItem.className = "user-item";
        listItem.setAttribute("data-index", index);
        listItem.onclick = () => editUser(index);
        userList.appendChild(listItem);
    });
}

// Edit a user
function editUser(index) {
    editingIndex = index;
    const user = users[index];

    // Populate edit form with user details
    document.getElementById('edit-user-id').value = user.userName;
    document.getElementById('edit-user-password').value = user.password;

    // Show the edit form
    document.getElementById('edit-user-container').style.display = "block";
}

// Save user changes
function saveUser() {
    const userIdInput = document.getElementById('edit-user-id');
    const passwordInput = document.getElementById('edit-user-password');

    const userName = userIdInput.value.trim();
    const password = passwordInput.value.trim();

    if (userName === "" || password === "") {
        alert("Both fields are required.");
        return;
    }

    // Update the user in the array
    users[editingIndex].userName = userName;
    users[editingIndex].password = password;
    renderUserList();

    // Hide the edit form and reset index
    document.getElementById('edit-user-container').style.display = "none";
    editingIndex = -1;
}
