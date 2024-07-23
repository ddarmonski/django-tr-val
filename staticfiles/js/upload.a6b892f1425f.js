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
        const formData = new FormData();
        formData.append('invoices', file);

        fetch('/upload/', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.errors) {
                alert(data.errors.join('\n'));
            } else {
                console.log('Extracted data:', data.extracted_data);
                // For now, just log the extracted data to the console
                // You can update the UI in the next step
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while processing the invoice.');
        });
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