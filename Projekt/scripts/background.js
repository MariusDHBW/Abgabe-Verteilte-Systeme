function toggleDarkMode() {
	const body = document.body;
	const toggleBtn = document.getElementById("theme-toggle");

	body.classList.toggle("darkmode");

	const isDark = body.classList.contains("darkmode");
	if (toggleBtn) toggleBtn.textContent = isDark ? "🌞" : "🌙";

	// Nur speichern, wenn Cookies akzeptiert wurden
	if (getCookie("accepted") === true) {
		localStorage.setItem("darkmode", isDark ? "true" : "false");
	}
}

function setDarkMode(isDark) {
	const bodyElement = document.body;
	const toggleButton = document.getElementById("theme-toggle");

	bodyElement.classList.toggle("darkmode", isDark);

	if (toggleButton) {
		toggleButton.textContent = isDark ? "🌞" : "🌙";
	}

	if (getCookie("accepted") === true) {
		localStorage.setItem("darkmode", isDark ? "true" : "false");
	}
}

// Beim Laden prüfen
window.addEventListener("DOMContentLoaded", () => {
	const savedMode = localStorage.getItem("darkmode");

	if (getCookie("accepted") === true) {
		const savedMode = localStorage.getItem("darkmode");

		if (savedMode === null) {
			const prefersDark = window.matchMedia(
				"(prefers-color-scheme: dark)",
			).matches;
			setDarkMode(prefersDark);
		} else {
			setDarkMode(savedMode === "true");
		}
	} else {
		// Cookies wurden nicht akzeptiert → keine Speicherung, stattdessen Systemfarbe nutzen
		const prefersDark = window.matchMedia(
			"(prefers-color-scheme: dark)",
		).matches;
		setDarkMode(prefersDark);
	}
});

// Systemwechsel live überwachen, aber nur wenn Nutzer nichts manuell gesetzt hat
window
	.matchMedia("(prefers-color-scheme: dark)")
	.addEventListener("change", (event) => {
		const cookiesAccepted = getCookie("accepted") === true;
		const savedMode = localStorage.getItem("darkmode");
		if (savedMode === null) {
			// Nur automatisch anpassen, wenn noch kein Modus gespeichert ist
			setDarkMode(event.matches);
		}
	});
