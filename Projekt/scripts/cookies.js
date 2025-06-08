function setCookie(cookieName, cookieValue, numDaysTillExpired) {
	const expireDate = new Date();
	expireDate.setTime(
		expireDate.getTime() + numDaysTillExpired * 24 * 60 * 60 * 1000,
	);
	document.cookie = `${cookieName}=${cookieValue};expires=${expireDate.toUTCString()}`;
}

function getCookie(cookieName) {
	const cookies = document.cookie.replace(" ", "").split(";");
	for (const cookie of cookies) {
		if (cookie.startsWith(cookieName)) {
			value = cookie.substring(cookieName.length + 1);
			// Automatisches Verarbeiten von Booleans macht Abfragen damit später leichter
			if (value === "true") {
				return true;
			}
			if (value === "false") {
				return false;
			}
			return value;
		}
	}
	return null;
}

function closeInitCookieBannerIfCookiesAccepted() {
	// Der Cookie Banner wird standardmäßig angezeigt.
	// Er wird geschlossen, wenn der Nutzer funktionale Cookies erlaubt hat.
	userAcceptedCookies = getCookie("accepted");
	if (userAcceptedCookies != null && userAcceptedCookies) {
		closeCookieBanner();
	}
}
function openCookieBanner() {
	const banner = document.getElementById("cookie-banner");
	banner.style.display = "";
}

function closeCookieBanner() {
	const banner = document.getElementById("cookie-banner");
	banner.style.display = "none";
}

function cookieButtonAccepted() {
	setCookie("accepted", true, 365);
	closeCookieBanner();
}
function cookieButtonDenied() {
	setCookie("accepted", false, 365);
	localStorage.clear();
	closeCookieBanner();
}

// Trollt den Nutzer. Funktioniert nicht auf Touchscreens. Womp womp
function cookieButtonMouseEntered() {
	btn = document.getElementById("cookie-button").innerHTML =
		"Doch bitte ich will Cookies";
}
function cookieButtonMouseLeft() {
	btn = document.getElementById("cookie-button").innerHTML =
		"Nein ich will keine Cookies";
}
