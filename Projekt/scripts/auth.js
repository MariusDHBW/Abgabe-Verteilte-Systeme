// Basis-URL deines Backends (am besten in einer .env o.Ä. auslagern)
const API_BASE = "http://localhost:8000";

// Initiales Setup beim Laden der Seite
document.addEventListener("DOMContentLoaded", setupAuthState);

// Aktualisiert Button‑Text und Dropdown‑Menü
function setupAuthState() {
	const token = localStorage.getItem("access_token");
	const userButton = document.getElementById("userButton");
	const userDropdown = document.getElementById("userDropdown");
	if (!userButton || !userDropdown) return;

	if (token) {
		// eingeloggter Zustand
		userButton.textContent = "Logout";
		userButton.onclick = logoutUser;
		userDropdown.innerHTML = `<a onclick="logoutUser()">Abmelden</a>`;
	} else {
		// ausgeloggter Zustand
		userButton.textContent = "Login/Register";
		userButton.onclick = openLoginModal;
		userDropdown.innerHTML = `
            <a onclick="openLoginModal()">Login</a>
            <a onclick="openRegisterModal()">Register</a>
        `;
	}
}

// Logout: Token löschen und State neu aufbauen
function logoutUser() {
	localStorage.removeItem("access_token");
	window.location.reload();
	setupAuthState();
}

// Login-Routine: nach Erhalt des Tokens State neu aufbauen
async function loginUser(username, password) {
	try {
		const response = await fetch(`${API_BASE}/token`, {
			method: "POST",
			headers: { "Content-Type": "application/x-www-form-urlencoded" },
			body: new URLSearchParams({ username, password }),
		});
		if (!response.ok) throw new Error("Benutzer/Passwort falsch");

		const data = await response.json();
		localStorage.setItem("access_token", data.access_token);
		closeLoginModal();
		setupAuthState();
	} catch (err) {
		alert(`Login fehlgeschlagen: ${err.message}`);
	}
}

async function loginFormHandler(event) {
	event.preventDefault();
	const username = document.getElementById("loginUsername").value;
	const password = document.getElementById("loginPassword").value;
	await loginUser(username, password);
	window.location.reload();
}

async function validateRegisterForm(event) {
	event.preventDefault();

	const username = document.getElementById("registerUsername").value;
	const password = document.getElementById("registerPassword").value;
	const passwordRepeat = document.getElementById(
		"registerPasswordRepeat",
	).value;
	const email = document.getElementById("registerEmail").value;
	const fullName = document.getElementById("registerFullName").value;

	if (password !== passwordRepeat) {
		alert("Die Passwörter stimmen nicht überein.");
		return;
	}

	const registerData = new FormData();
	registerData.append("username", username);
	registerData.append("password", password);
	registerData.append("password_repeat", passwordRepeat);
	registerData.append("email", email);
	registerData.append("full_name", fullName);

	try {
		const regResp = await fetch(`${API_BASE}/register`, {
			method: "POST",
			body: registerData,
		});

		if (!regResp.ok) {
			const err = await regResp.json();
			alert(`Fehler bei der Registrierung: ${err.detail || regResp.status}`);
			return;
		}

		// Login nach erfolgreicher Registrierung
		await loginUser(username, password);
		window.location.reload();
		closeRegisterModal();
	} catch (error) {
		alert(`Unerwarteter Fehler: ${error.message}`);
	}
}

async function changePassword(event) {
	event.preventDefault();
	const oldPassword = document.getElementById("oldPassword").value;
	const newPassword = document.getElementById("newPassword").value;

	const token = localStorage.getItem("access_token");

	const response = await fetch(`${API_BASE}/change-password`, {
		method: "POST",
		headers: {
			"Content-Type": "application/x-www-form-urlencoded",
			Authorization: `Bearer ${token}`,
		},
		body: new URLSearchParams({
			old_password: oldPassword,
			new_password: newPassword,
		}),
	});

	if (response.ok) {
		alert("Passwort wurde erfolgreich geändert!");
		closeChangePasswordModal();
	} else {
		const data = await response.json();
		alert(`Fehler beim Passwort ändern: + ${data.detail}`);
	}
}
