// Toggle password visibility
function togglePassword(inputId, eyeId) {
  const input = document.getElementById(inputId);
  const eye = document.getElementById(eyeId);
  const showing = input.type === "password";
  input.type = showing ? "text" : "password";
  eye.classList.toggle("text-blue-500", showing);
}

// Simple email validation
function validateEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Signup form validation with alerts
document.getElementById("signupForm").addEventListener("submit", (e) => {
  const fields = {
    first_name: "First Name is required",
    last_name: "Last Name is required",
    email_address: "Email Address is required",
    student_id: "Student ID is required",
    password: "Password is required",
    confirm_password: "Confirm Password is required",
  };

  for (const [name, message] of Object.entries(fields)) {
    const input = document.querySelector(`[name='${name}']`);
    if (!input.value.trim()) {
      alert(message);
      input.focus();
      e.preventDefault();
      return;
    }
  }

  const email = document.querySelector("[name='email_address']");
  if (!validateEmail(email.value)) {
    alert("Please enter a valid email");
    email.focus();
    e.preventDefault();
    return;
  }

  const password = document.getElementById("password");
  const confirm = document.getElementById("confirm_password");
  if (password.value !== confirm.value) {
    alert("Passwords do not match");
    confirm.focus();
    e.preventDefault();
    return;
  }
});
