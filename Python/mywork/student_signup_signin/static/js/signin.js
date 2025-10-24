document.addEventListener("DOMContentLoaded", () => {
  console.log("GradeFlow Sign-In page loaded.");

  const form = document.querySelector('form[action*="signin"]');
  if (!form) return;

  // Add a simple shake animation for feedback
  const style = document.createElement("style");
  style.innerHTML = `
    @keyframes shake {
      0%, 100% { transform: translateX(0); }
      20%, 60% { transform: translateX(-5px); }
      40%, 80% { transform: translateX(5px); }
    }
    .shake { animation: shake 0.4s ease; }
  `;
  document.head.appendChild(style);

  // Form submission validation
  form.addEventListener("submit", (e) => {
    const email = form.querySelector('input[name="email_address"]').value.trim();
    const password = form.querySelector('input[name="password"]').value.trim();

    // Remove any existing error box before showing a new one
    const existingError = document.querySelector(".signin-error");
    if (existingError) existingError.remove();

    if (!email || !password) {
      e.preventDefault();

      // ✅ Create and show error box dynamically ONLY when needed
      const errorBox = document.createElement("div");
      errorBox.className =
        "signin-error mb-4 p-3 rounded-lg bg-red-100 text-red-700 text-sm border border-red-300";
      errorBox.textContent = "⚠️ Please fill in both Email Address and Password.";
      form.parentNode.insertBefore(errorBox, form);

      form.classList.add("shake");

      // Highlight missing fields
      if (!email) form.querySelector('input[name="email_address"]').classList.add("border-red-400");
      if (!password) form.querySelector('input[name="password"]').classList.add("border-red-400");

      // Auto-hide and clean up after 3 seconds
      setTimeout(() => {
        if (errorBox) errorBox.remove();
        form.classList.remove("shake");
        form.querySelectorAll("input").forEach((input) =>
          input.classList.remove("border-red-400")
        );
      }, 3000);
    }
  });
});
