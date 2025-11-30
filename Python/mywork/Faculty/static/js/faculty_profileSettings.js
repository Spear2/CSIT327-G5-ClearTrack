function showSection(sectionId) {
    document.querySelectorAll(".settings-card.main-settings-card").forEach(el => el.classList.add("hidden"));
    document.getElementById(sectionId).classList.remove("hidden");

    document.querySelectorAll(".settings-sidebar ul li").forEach(li => li.classList.remove("active"));
    event.target.classList.add("active");
}