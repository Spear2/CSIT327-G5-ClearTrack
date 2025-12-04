console.log("Analytics JS Loaded");

// Load chart data
let chartData = null;
let submissionChart = null; // store chart instance

try {
    chartData = JSON.parse(document.getElementById("chart-data-json").textContent);
} catch (e) {
    console.error("Chart data missing.");
}

document.querySelector("button[onclick=\"showTab('analytics')\"]")
    .addEventListener("click", () => {
        setTimeout(renderSubmissionTrend, 200);
    });

function renderSubmissionTrend() {
    if (!chartData) return;

    const ctx = document.getElementById("submissionTrendsChart").getContext("2d");
    if (!ctx) return;

    // Destroy previous chart if exists
    if (submissionChart) {
        submissionChart.destroy();
    }

    submissionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.submission_labels,
            datasets: [{
                label: "Submissions",
                data: chartData.submission_values,
                borderWidth: 2,
                borderColor: "blue",
                fill: false,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    console.log("Submission Trend Rendered");
}
