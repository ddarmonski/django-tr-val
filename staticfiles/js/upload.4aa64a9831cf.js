document.addEventListener('DOMContentLoaded', function () {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');
    const pdfViewer = document.getElementById('pdfViewer');
    const validateButton = document.querySelector('.validate-btn');

    dropzone.addEventListener('click', () => fileInput.click());

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        handleFiles(files);
    });

    fileInput.addEventListener('change', (e) => {
        const files = e.target.files;
        handleFiles(files);
    });

    validateButton.addEventListener('click', validateInvoice);

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            const reader = new FileReader();
            reader.onload = function (e) {
                pdfViewer.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    }

    function extractInvoiceData(file) {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        progressBar.style.width = '0%';  // Reset progress bar
        progressText.textContent = 'Starting data extraction...';
    
        const formData = new FormData();
        formData.append('invoices', file);
    
        fetch('/upload/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            progressBar.style.width = '33%';  // Update progress bar
            progressText.textContent = 'Received server response...';
            return response.json();
        })
        .then(data => {
            progressBar.style.width = '66%';  // Update progress bar
            progressText.textContent = 'Processing server data...';
            console.log('Response data:', data);
            if (data.errors) {
                alert(data.errors.join('\n'));
            } else {
                console.log('Extracted data:', data.extracted_data);
                updateUI(data.extracted_data);
            }
            progressBar.style.width = '100%';  // Update progress bar
            progressText.textContent = 'Done!';
        })
        .catch(error => {
            console.error('Fetch error:', error);
            alert('An error occurred while processing the invoice.');
        });
    }

    function updateUI(extractedData) {
        // Flatten the nested list
        extractedData = extractedData.flat();
    
        // Assuming extractedData is an array of objects
        if (extractedData.length > 0) {
            const summary = extractedData[0]; // Assuming the first object contains summary data
            const lineItems = extractedData.slice(1); // The rest are line items
    
            // Update summary table
            document.getElementById('vat').innerText = summary.vat || 'N/A';
            document.getElementById('totalAmount').innerText = summary.totalAmount || 'N/A';
            document.getElementById('gasIndexation').innerText = summary.gasIndexation || 'N/A';
    
            // Update line items table
            const lineItemsTable = document.getElementById('lineItemsTable');
            // Clear existing line items
            lineItemsTable.innerHTML = `
                <tr>
                    <th>Tour ID</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Total</th>
                </tr>
            `;
            // Add new line items
            lineItems.forEach(item => {
                const row = lineItemsTable.insertRow();
                row.insertCell(0).innerText = item.tour_id || 'N/A';
                row.insertCell(1).innerText = item.tour_qty || 'N/A';
                row.insertCell(2).innerText = item.price_per_unit || 'N/A';
                row.insertCell(3).innerText = item.total_cost_tour || 'N/A';
            });
        }
    }

    function validateInvoice() {
        const files = fileInput.files;
        if (files.length > 0) {
            extractInvoiceData(files[0]);
        } else {
            alert('Please upload a file first.');
        }
    }

    window.cancelUpload = function () {
        fileInput.value = '';
        pdfViewer.src = '';
        document.getElementById('vat').innerText = '';
        document.getElementById('totalAmount').innerText = '';
        document.getElementById('gasIndexation').innerText = '';
        const lineItemsTable = document.getElementById('lineItemsTable');
        // Clear existing line items
        lineItemsTable.innerHTML = `
            <tr>
                <th>Tour ID</th>
                <th>Quantity</th>
                <th>Price</th>
                <th>Total</th>
            </tr>
        `;
    };
});