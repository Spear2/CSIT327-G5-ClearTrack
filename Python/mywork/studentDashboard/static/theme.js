document.addEventListener("DOMContentLoaded", () => {
    const body = document.body;
    const selector = document.getElementById("theme-selector");

    // Get saved theme, default to light
    let theme = localStorage.getItem("theme") || "light";

    const applyTheme = (theme) => {
        if (theme === "dark") body.classList.add("dark-mode");
        else body.classList.remove("dark-mode");
    };

    // Handle system theme
    if (theme === "system") {
        const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
        applyTheme(prefersDark ? "dark" : "light");
    } else {
        applyTheme(theme);
    }

    // Set dropdown value to saved theme
    if (selector) selector.value = theme;

    // Apply theme immediately on change
    if (selector) {
        selector.addEventListener("change", (e) => {
            const selectedTheme = e.target.value;
            localStorage.setItem("theme", selectedTheme);

            if (selectedTheme === "system") {
                const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
                applyTheme(prefersDark ? "dark" : "light");
            } else {
                applyTheme(selectedTheme);
            }
        });
    }
});
