window.addEventListener("DOMContentLoaded", () => {
    let tab = localStorage.getItem("active_tab") || "profile-section";
    showSection(tab);

    const matchingLi = document.querySelector(`[onclick*="${tab}"]`);
    if (matchingLi) matchingLi.classList.add("active");
});

function showSection(sectionId, element = null) {
    // Hide all main cards
    document.querySelectorAll(".settings-card.main-settings-card")
        .forEach(el => el.classList.add("hidden"));

    // Show selected section
    document.getElementById(sectionId).classList.remove("hidden");

    // Remove all active states
    document.querySelectorAll(".settings-sidebar ul li")
        .forEach(li => li.classList.remove("active"));

    // If a sidebar element was clicked, activate it
    if (element) {
        element.classList.add("active");
    }

    // 🔥 CLEAR DJANGO FLASH MESSAGES AFTER SWITCHING TABS
    const flashBox = document.getElementById("flash-messages");
    if (flashBox) {
        flashBox.innerHTML = "";
    }
}

