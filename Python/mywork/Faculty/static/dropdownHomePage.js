console.log("Dropdown script loaded!");

document.addEventListener("DOMContentLoaded", () => {
  const userBtn = document.getElementById("userBtn");
  const menu = document.getElementById("dropdownMenu");

  if (userBtn) {
    userBtn.addEventListener("click", () => {
      menu.style.display = menu.style.display === "none" ? "block" : "none";
    });
  }
});
