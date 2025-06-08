document.addEventListener("DOMContentLoaded", async () => {
	const token = localStorage.getItem("access_token");
	if (!token) {
		return;
	}

	const tbody = document.getElementById("downloads-table-body");
	if (!tbody) return;

	try {
		const response = await fetch(`${API_BASE}/my-videos`, {
			headers: {
				Authorization: `Bearer ${token}`,
			},
		});

		if (!response.ok) {
			throw new Error("Fehler beim Laden der Videos");
		}

		const videos = await response.json();

		tbody.innerHTML = "";

		for (const video of videos) {
			const tr = document.createElement("tr");

			const thumbTd = document.createElement("td");
			const img = document.createElement("img");
			img.src = video.thumbnail_url || "default_thumbnail.jpg";
			img.alt = video.title || "Video Thumbnail";
			img.classList.add("thumbnail");
			img.style.cursor = "pointer";

			img.addEventListener("click", () => {
				modalVideo.src = video.download_url;
				modalVideo.play();
				videoModal.style.display = "flex"; 
			});

			thumbTd.appendChild(img);

			tr.appendChild(thumbTd);

			const titleTd = document.createElement("td");
			titleTd.textContent = video.title || "Unbekannt";
			tr.appendChild(titleTd);

			const dateTd = document.createElement("td");
			dateTd.textContent = new Date(video.created_at).toLocaleString("de-DE");
			tr.appendChild(dateTd);

			const actionTd = document.createElement("td");

			const downloadBtn = document.createElement("button");
			downloadBtn.textContent = "Download";
			downloadBtn.classList.add("action-button");
			downloadBtn.addEventListener("click", async (e) => {
				e.preventDefault();

				try {
					const token = localStorage.getItem("access_token");
					if (!token) {
						alert("Bitte zuerst einloggen!");
						return;
					}

					const url = video.download_url;
					const filename = `${video.title}.mp4`;

					const response = await fetch(url, {
						method: "GET",
						headers: {
							Authorization: `Bearer ${token}`,
						},
					});

					if (!response.ok) throw new Error("Download fehlgeschlagen");

					const blob = await response.blob();
					const blobUrl = window.URL.createObjectURL(blob);

					const a = document.createElement("a");
					a.href = blobUrl;
					a.download = filename;
					document.body.appendChild(a);
					a.click();
					a.remove();

					window.URL.revokeObjectURL(blobUrl);
				} catch (err) {
					aalert(`Fehler·beim·Download:·${err.message}`);
				}
			});

			actionTd.appendChild(downloadBtn);
			tr.appendChild(actionTd);

			const deleteBtn = document.createElement("button");
			deleteBtn.textContent = "Löschen";
			deleteBtn.classList.add("action-button");
			deleteBtn.style.marginLeft = "6px";
			deleteBtn.addEventListener("click", () => {
				deleteVideo(video.id, tr);
			});
			actionTd.appendChild(deleteBtn);

			tr.appendChild(actionTd);

			tbody.appendChild(tr);
		}
	} catch (error) {
		console.error(error);
		tbody.innerHTML = `<tr><td colspan="5" style="color: red;">Fehler beim Laden der Downloads</td></tr>`;
	}
});

async function handleDownload(event) {
	event.preventDefault();

	const token = localStorage.getItem("access_token");
	if (!token) {
		alert("Bitte zuerst einloggen! ");
		return;
	}

	const url = document.getElementById("url").value.trim();
	const formData = new FormData();
	const isPlaylist = url.startsWith("https://www.youtube.com/playlist?list=");

	if (isPlaylist) {
		formData.append("url", url);

		try {
			const response = await fetch(`${API_BASE}/download_playlist`, {
				method: "POST",
				headers: {
					Authorization: `Bearer ${token}`,
				},
				body: formData,
			});

			if (!response.ok) {
				const error = await response.json();
				throw new Error(`${response.status} – ${error.detail}`);
			}

			const data = await response.json();
			alert(
				`Playlist erfolgreich heruntergeladen: "${data.title}" mit ${data.videos.length} Videos`,
			);
			console.log(data);
		} catch (error) {
			console.error("Fehler beim Playlist-Download:", error);
			alert(`Fehler·beim·Playlist-Download:·${error.message}`);
		}
	} else {
		formData.append("link", url);

		try {
			const response = await fetch(`${API_BASE}/download`, {
				method: "POST",
				headers: {
					Authorization: `Bearer ${token}`,
				},
				body: formData,
			});

			if (!response.ok) {
				const errorText = await response.text();
				throw new Error(`Fehler: ${response.status} - ${errorText}`);
			}

			const data = await response.json();
			alert(`Video erfolgreich heruntergeladen: "${data.title}"`);
			console.log(data);
		} catch (error) {
			console.error(error);
			alert(`Fehler·beim·Video-Download:·${error.message}`);
		}
	}
}

async function deleteVideo(videoId) {
	const token = localStorage.getItem("access_token");
	if (!token) {
		alert("Bitte zuerst einloggen!");
		return;
	}

	const confirmed = confirm("Möchten Sie dieses Video wirklich löschen?");
	if (!confirmed) return;

	try {
		const response = await fetch(`${API_BASE}/my-videos/${videoId}`, {
			method: "DELETE",
			headers: {
				Authorization: `Bearer ${token}`,
			},
		});

		if (!response.ok) {
			throw new Error(
				(await response.json()).detail || "Unbekannter Fehler beim Löschen",
			);
		}

		alert("Video erfolgreich gelöscht!");
		location.reload(); // oder besser: Tabelle neu laden
	} catch (error) {
		alert(`Fehler beim Löschen: ${error.message}`);
	}
}

document.addEventListener("DOMContentLoaded", () => {
	const downloadsTable = document.getElementById("downloads-table-body");

	if (!downloadsTable) return;

	const token = localStorage.getItem("access_token");
	const mainContent = document.querySelector("main");

	if (!token) {
		mainContent.innerHTML = `
                    <div style="text-align:center; padding: 2em;">
                        <h2>❌ Zugriff verweigert ❌</h2>
                        <p>Bitte <a href="#" id="open-login-link">melden Sie sich an</a>, um Videos herunter zu laden und ihren Verlauf anzuzeigen.</p>
                    </div>
                `;
		setTimeout(() => {
			const loginLink = document.getElementById("open-login-link");
			if (loginLink) {
				loginLink.addEventListener("click", (e) => {
					e.preventDefault();
					openLoginModal();
				});
			}
		}, 0);
	}
});

const videoModal = document.getElementById("video-modal");
const modalVideo = document.getElementById("modal-video");
const modalClose = document.getElementById("modal-close");

if (modalClose) {
	modalClose.addEventListener("click", () => {
		modalVideo.pause();
		modalVideo.src = "";
		videoModal.style.display = "none";
	});
}

if (videoModal) {
	videoModal.addEventListener("click", (e) => {
		if (e.target === videoModal) {
			modalVideo.pause();
			modalVideo.src = "";
			videoModal.style.display = "none";
		}
	});
}
