// Elements
const signinTab = document.getElementById("signinTab");
const signupTab = document.getElementById("signupTab");
const signinForm = document.getElementById("signinForm");
const signupForm = document.getElementById("signupForm");

// --- FORM TOGGLE ---
function showForm(formToShow, formToHide, activeTab, inactiveTab) {
  formToHide.classList.add("hidden");
  formToHide.classList.remove("show");

  formToShow.classList.remove("hidden");
  setTimeout(() => formToShow.classList.add("show"), 10);

  activeTab.classList.add("border-b-2", "border-blue-600", "text-blue-600");
  inactiveTab.classList.remove("border-b-2", "border-blue-600", "text-blue-600");
  inactiveTab.classList.add("text-gray-500");
}

signinTab.addEventListener("click", () => {
  showForm(signinForm, signupForm, signinTab, signupTab);
});

signupTab.addEventListener("click", () => {
  showForm(signupForm, signinForm, signupTab, signinTab);
});

// --- PASSWORD TOGGLE ---
function togglePassword(fieldId) {
  const field = document.getElementById(fieldId);
  field.type = field.type === "password" ? "text" : "password";
}

// --- FORM VALIDATION ---
function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

function showError(input, message) {
  let errorEl = input.nextElementSibling;
  if (!errorEl || !errorEl.classList.contains("error-msg")) {
    errorEl = document.createElement("p");
    errorEl.classList.add("text-red-500", "text-sm", "mt-1", "error-msg");
    input.parentNode.appendChild(errorEl);
  }
  errorEl.innerText = message;
  input.classList.add("border-red-500");
}

function clearError(input) {
  const errorEl = input.nextElementSibling;
  if (errorEl && errorEl.classList.contains("error-msg")) {
    errorEl.remove();
  }
  input.classList.remove("border-red-500");
}

// --- SIGNUP VALIDATION ---
signupForm.addEventListener("submit", (e) => {
  let valid = true;
  const firstName = signupForm.querySelector("input[name='first_name']");
  const lastName = signupForm.querySelector("input[name='last_name']");
  const email = signupForm.querySelector("input[name='email']");
  const studentId = signupForm.querySelector("input[name='student_id']");
  const password1 = signupForm.querySelector("input[name='password1']");
  const password2 = signupForm.querySelector("input[name='password2']");

  [firstName, lastName, email, studentId, password1, password2].forEach(input => {
    clearError(input);
    if (input.value.trim() === "") {
      showError(input, "This field is required");
      valid = false;
    }
  });

  if (email.value && !validateEmail(email.value)) {
    showError(email, "Enter a valid email");
    valid = false;
  }

  if (password1.value && password2.value && password1.value !== password2.value) {
    showError(password2, "Passwords do not match");
    valid = false;
  }

  if (!valid) e.preventDefault();
});

// --- SIGNIN VALIDATION ---
signinForm.addEventListener("submit", (e) => {
  let valid = true;
  const email = signinForm.querySelector("input[name='email']");
  const password = signinForm.querySelector("input[name='password']");

  [email, password].forEach(input => {
    clearError(input);
    if (input.value.trim() === "") {
      showError(input, "This field is required");
      valid = false;
    }
  });

  if (email.value && !validateEmail(email.value)) {
    showError(email, "Enter a valid email");
    valid = false;
  }

  if (!valid) e.preventDefault();
});

// --- PASSWORD STRENGTH INDICATOR ---
const signupPassword = signupForm.querySelector("input[name='password1']");
signupPassword.addEventListener("input", () => {
  let strengthEl = document.getElementById("passwordStrength");
  if (!strengthEl) {
    strengthEl = document.createElement("p");
    strengthEl.id = "passwordStrength";
    strengthEl.classList.add("text-sm", "mt-1");
    signupPassword.parentNode.appendChild(strengthEl);
  }

  const val = signupPassword.value;
  if (val.length < 6) {
    strengthEl.innerText = "Weak password";
    strengthEl.className = "text-red-500 text-sm mt-1";
  } else if (val.length < 10) {
    strengthEl.innerText = "Moderate password";
    strengthEl.className = "text-yellow-500 text-sm mt-1";
  } else {
    strengthEl.innerText = "Strong password";
    strengthEl.className = "text-green-500 text-sm mt-1";
  }
});
