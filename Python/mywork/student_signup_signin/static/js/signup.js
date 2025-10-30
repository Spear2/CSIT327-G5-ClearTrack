// ✅ Toggle password visibility
function togglePassword(inputId, eyeId) {
  const input = document.getElementById(inputId);
  const eye = document.getElementById(eyeId);
  const isHidden = input.type === "password";
  input.type = isHidden ? "text" : "password";
  eye.src = isHidden
    ? eye.src.replace("visible.png", "hidden.png")
    : eye.src.replace("hidden.png", "visible.png");
}

// ✅ Validate email format
function validateEmail(email) {
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return pattern.test(email);
}

// ✅ Handle Sign Up form validation
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("signupForm");

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    let hasError = false;

    // Hide all previous error messages
    document.querySelectorAll(".error-msg").forEach((msg) => {
      msg.classList.add("hidden");
    });

    // Field validation messages
    const fields = {
      first_name: "First Name is required",
      last_name: "Last Name is required",
      email_address: "Email Address is required",
      student_id: "Student ID is required",
      password: "Password is required",
      confirm_password: "Confirm Password is required",
    };

    // Loop through each field
    Object.entries(fields).forEach(([name, message]) => {
      const input = form.querySelector(`[name="${name}"]`);
      const errorMsg = input.closest("div").parentElement.querySelector(".error-msg");

      if (!input.value.trim()) {
        errorMsg.textContent = message;
        errorMsg.classList.remove("hidden");
        input.classList.add("border-red-500");
        hasError = true;
      } else {
        input.classList.remove("border-red-500");
      }
    });

    // Validate email format
    const email = form.querySelector("[name='email_address']");
    if (email.value && !validateEmail(email.value)) {
      const error = email.closest("div").parentElement.querySelector(".error-msg");
      error.textContent = "Please enter a valid email address";
      error.classList.remove("hidden");
      email.classList.add("border-red-500");
      hasError = true;
    }

    // Password match check
    const password = document.getElementById("password");
    const confirm = document.getElementById("confirm_password");

    if (password.value && confirm.value && password.value !== confirm.value) {
      const error = confirm.closest("div").parentElement.querySelector(".error-msg");
      error.textContent = "Passwords do not match";
      error.classList.remove("hidden");
      confirm.classList.add("border-red-500");
      hasError = true;
    }

    if (!hasError) {
      form.submit(); // Only submit if no errors
    }
  });

  // ✅ Navigation active tab handling
  const path = window.location.pathname;
  const signinTab = document.querySelector('a[href*="signin"]');
  const signupTab = document.querySelector('a[href*="signup"]');

  if (signinTab && signupTab) {
    if (path.includes("signup")) {
      signupTab.classList.add("bg-blue-600", "text-white");
      signupTab.classList.remove("bg-gray-100", "text-gray-600");
      signinTab.classList.add("bg-gray-100", "text-gray-600");
      signinTab.classList.remove("bg-blue-600", "text-white");
    } else {
      signinTab.classList.add("bg-blue-600", "text-white");
      signinTab.classList.remove("bg-gray-100", "text-gray-600");
      signupTab.classList.add("bg-gray-100", "text-gray-600");
      signupTab.classList.remove("bg-blue-600", "text-white");
    }
  }
});
