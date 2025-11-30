function showTab(tabId) {
  // Hide all tab contents
  document.querySelectorAll('.tab-content').forEach(tab => {
    tab.style.display = 'none';
  });

  // Remove active state from all tab buttons
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.remove('active');
  });

  // Show the selected tab
  document.getElementById(tabId).style.display = 'block';

  // Highlight the clicked button
  event.target.classList.add('active');
}

// Default active tab
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.tab-content').forEach(tab => tab.style.display = 'none');
  document.getElementById('submissions').style.display = 'block';
});
