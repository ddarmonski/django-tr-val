document.addEventListener('DOMContentLoaded', function () {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');
    const pdfViewer = document.getElementById('pdfViewer');

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

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            const reader = new FileReader();
            reader.onload = function (e) {
                pdfViewer.src = e.target.result;
                extractInvoiceData(file);
            };
            reader.readAsDataURL(file);
        }
    }

    function extractInvoiceData(file) {
        // This is a placeholder for extracting invoice data
        // In a real application, you'd likely send the file to the server
        // for processing and then display the extracted data

        // Placeholder data
        const vat = '20%';
        const totalAmount = '1000 EUR';
        const gasIndexation = '5%';
        const lineItems = [
            { tourId: 'T1', quantity: 10, price: '50 EUR', total: '500 EUR' },
            { tourId: 'T2', quantity: 5, price: '100 EUR', total: '500 EUR' },
        ];

        // Update summary table
        document.getElementById('vat').innerText = vat;
        document.getElementById('totalAmount').innerText = totalAmount;
        document.getElementById('gasIndexation').innerText = gasIndexation;

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
            row.insertCell(0).innerText = item.tourId;
            row.insertCell(1).innerText = item.quantity;
            row.insertCell(2).innerText = item.price;
            row.insertCell(3).innerText = item.total;
        });
    }

    window.validateInvoice = function () {
        alert('Invoice validated!');
    };

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
