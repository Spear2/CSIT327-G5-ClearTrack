window.addEventListener("DOMContentLoaded", () => {
    let tab = localStorage.getItem("active_tab") || "profile-section";
    showSection(tab);

    // Highlight the correct sidebar item
    document.querySelectorAll(".settings-sidebar ul li").forEach(li => {
        if (li.dataset.section === tab) {
            li.classList.add("active");
        }

        // Add click listener to update active section
        li.addEventListener("click", () => {
            const sectionId = li.dataset.section;
            if (sectionId) {
                showSection(sectionId, li);
                localStorage.setItem("active_tab", sectionId);
            }
        });
    });
});

function showSection(sectionId, element = null) {
    // Hide all sections
    document.querySelectorAll(".settings-card.main-settings-card")
        .forEach(el => el.classList.add("hidden"));

    // Show selected section
    const section = document.getElementById(sectionId);
    if (section) section.classList.remove("hidden");

    // Remove all active states
    document.querySelectorAll(".settings-sidebar ul li")
        .forEach(li => li.classList.remove("active"));

    // Activate clicked element
    if (element) element.classList.add("active");

    // Clear flash messages
    const flashBox = document.getElementById("flash-messages");
    if (flashBox) flashBox.innerHTML = "";
}
