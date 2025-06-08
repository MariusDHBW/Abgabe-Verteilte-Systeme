async function loadComponents() {
	const [header, footer, modals, cookies] = await Promise.all([
		fetch("components/header.html").then((r) => r.text()),
		fetch("components/footer.html").then((r) => r.text()),
		fetch("components/modals.html").then((r) => r.text()),
		fetch("components/cookies.html").then((r) => r.text()),
	]);

	document.getElementById("header-placeholder").innerHTML = header;
	document.getElementById("footer-placeholder").innerHTML = footer;
	document.getElementById("cookies").innerHTML = cookies;
	const modalDiv = document.createElement("div");
	modalDiv.innerHTML = modals;
	document.body.appendChild(modalDiv);

	setupAuthState();
	closeInitCookieBannerIfCookiesAccepted();
}

function setupAuthState() {
	const token = localStorage.getItem("access_token");
	const userButton = document.getElementById("userButton");
	const userDropdown = document.getElementById("userDropdown");

	if (userButton && userDropdown) {
		userButton.textContent = token ? "Account" : "Login/Register";
		userDropdown.innerHTML = token
			? `<a onclick="openChangePasswordModal()">Passwort ändern</a><a onclick="logoutUser()">Logout</a>`
			: `<a onclick="openLoginModal()">Login</a><a onclick="openRegisterModal()">Register</a>`;
	}
}

// Open and close the navigation menu on mobile devices
function openNavMenu() {
	document.getElementById("navMobile").style.width = "250px";
}

function closeNav() {
	document.getElementById("navMobile").style.width = "0";
}

// open und close für die modals
function toggleModal(modalId, show) {
	const modal = document.getElementById(modalId);
	modal.classList.toggle("show", show);
	modal.classList.toggle("hide", !show);
}

function openLoginModal() {
	toggleModal("loginModal", true);
}

function closeLoginModal() {
	toggleModal("loginModal", false);
}

function openRegisterModal() {
	toggleModal("registerModal", true);
}

function closeRegisterModal() {
	toggleModal("registerModal", false);
}

function openChangePasswordModal() {
	toggleModal("changePasswordModal", true);
}

function closeChangePasswordModal() {
	toggleModal("changePasswordModal", false);
}

// Pixabay-Bild laden
const query = "developer";

async function loadRandomPixabayImage() {
	try {
		const response = await fetch(
			`${API_BASE}/api/pixabay?q=${encodeURIComponent(query)}`,
		);
		const { hits } = await response.json();
		if (hits && hits.length > 0) {
			const randomIndex = Math.floor(Math.random() * hits.length);
			const image = hits[randomIndex];
			const portraitImage = document.getElementById("portrait-image");
			if (portraitImage) {
				portraitImage.src = image.webformatURL;
				portraitImage.alt = image.tags.split(",").join(" ");
			}
		}
	} catch (error) {
		console.error("Failed to load images from Pixabay:", error);
	}
}

//Warten, bis DOM vollständig geladen ist
window.addEventListener("DOMContentLoaded", () => {
	loadComponents();
	loadRandomPixabayImage();

	const kontaktForm = document.getElementById("kontaktForm");
	if (kontaktForm) {
		kontaktForm.addEventListener("submit", function (event) {
			event.preventDefault();

			alert(
				"Vielen Dank für Ihre Nachricht! Wir melden uns zeitnah bei Ihnen. \nDa uns Nutzerfeedback egal ist wird diese Nachricht nicht versendet."
			);

			this.reset(); // optional
		});
	}
});