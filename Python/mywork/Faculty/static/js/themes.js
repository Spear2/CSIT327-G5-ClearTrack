document.addEventListener("DOMContentLoaded", () => {
    const body = document.body;
    const selector = document.getElementById("theme-selector");
    const saveBtn = document.getElementById("save-preferences");

    let savedTheme = localStorage.getItem("theme") || "light";

    const applyTheme = (theme) => {
        if (theme === "dark") {
            body.classList.add("dark-mode");
            body.classList.remove("light-mode");
        } else {
            body.classList.remove("dark-mode");
            body.classList.add("light-mode");
        }
    };

    const resolveTheme = (theme) => {
        if (theme === "system") {
            return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
        }
        return theme;
    };

    // Only try to set selector value if element exists
    if (selector) {
        selector.value = savedTheme;
    }

    applyTheme(resolveTheme(savedTheme));

    // Save theme only if the button exists (page where prefs section is shown)
    if (selector && saveBtn) {
        saveBtn.addEventListener("click", () => {
            const selectedTheme = selector.value;
            localStorage.setItem("theme", selectedTheme);
            applyTheme(resolveTheme(selectedTheme));
        });
    }
});
