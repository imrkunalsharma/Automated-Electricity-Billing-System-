// Show Insert Form when Insert Button is clicked
document.getElementById('insert-data-btn').addEventListener('click', function () {
    document.getElementById('insert-form').style.display = 'block'; // Show insert form
    document.getElementById('output').innerHTML = ''; // Clear any output
    document.getElementById('fetch-data-btn').style.display = 'block'; // Show Fetch Data button
});

// Insert Data Form Submission
document.getElementById('insert-data-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const table_name = document.getElementById('table-select').value;
    const formData = new FormData(e.target);

    const data = {
        table_name: table_name,
        previous_date: formData.get('previous_date'),
        previous_reading: formData.get('previous_reading'),
        date_upto: formData.get('date_upto'),
        net_unit: formData.get('net_unit'),
        current_reading: formData.get('current_reading'),
        cost_of_unit: formData.get('cost_of_unit')
    };

    fetch('/insert_data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('output').textContent = data.message || data.error;

        if (data.message) {
            // Clear the form fields
            document.getElementById('insert-data-form').reset();
        }
    })
    .catch(error => console.error('Error:', error));
});

// Fetch Data Button Click
document.getElementById('fetch-data-btn').addEventListener('click', function () {
    document.getElementById('insert-form').style.display = 'none'; // Hide the insert form

    const table_name = document.getElementById('table-select').value;

    fetch('/fetch_data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ table_name })
    })
    .then(response => response.json())
    .then(data => {
        if (data.data) {
            const tableHTML = generateTableHTML(data.data.records, data.data.total_bill);
            document.getElementById('output').innerHTML = tableHTML;
        } else {
            document.getElementById('output').textContent = data.error;
        }
    })
    .catch(error => console.error('Error:', error));
});

// Function to create headings HTML
function createHeadingsHTML() {
    return `
        <h3>Fetched Data</h3>
        <table>
            <thead>
                <tr>
                    <th>Previous Date (Day)</th>
                    <th>Previous Reading</th>
                    <th>Date Upto (Day)</th>
                    <th>Current Reading</th>
                    
                    <th>Cost of Unit</th>
                    <th>Total Bill</th>
                </tr>
            </thead>
            <tbody>
    `;
}

// Function to format date to include day of the week
function formatDateWithDay(dateString) {
    const options = { weekday: 'long', year: 'numeric', month: 'numeric', day: 'numeric' };
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, options); // Return formatted date
}

// Function to generate HTML for fetched data
function generateTableHTML(data, totalBill) {
    let tableHTML = createHeadingsHTML(); // Start with table headings

    // Create table rows
    const rows = data.split("\n").map(row => row.split('|').filter(cell => cell.trim()));
    rows.forEach(row => {
        tableHTML += "<tr>";
        row.forEach((cell, index) => {
            // For the previous date and date up to columns, format the date to include the day
            if (index === 0) { // Previous Date
                tableHTML += `<td>${formatDateWithDay(cell.trim())}</td>`;
            } else if (index === 2) { // Date Upto
                tableHTML += `<td>${formatDateWithDay(cell.trim())}</td>`;
            } else {
                tableHTML += `<td>${cell.trim()}</td>`;
            }
        });
        tableHTML += "</tr>";
    });

    

    return tableHTML;
}
