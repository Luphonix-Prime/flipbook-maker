document.getElementById('pdfFile').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        document.querySelector('.file-text').textContent = file.name;
    }
});

document.getElementById('uploadForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('pdfFile');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a PDF file');
        return;
    }
    
    const uploadBtn = document.getElementById('uploadBtn');
    const progress = document.getElementById('progress');
    const result = document.getElementById('result');
    
    uploadBtn.disabled = true;
    progress.style.display = 'block';
    result.style.display = 'none';
    
    const formData = new FormData();
    formData.append('pdf', file);
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        progress.style.display = 'none';
        
        if (data.success) {
            result.className = 'result success';
            result.innerHTML = `
                <h3>✓ Flipbook Created Successfully!</h3>
                <p>${data.total_pages} pages converted</p>
                <a href="/flipbook/${data.flipbook_id}" class="view-btn">View Flipbook</a>
            `;
            result.style.display = 'block';
        } else {
            throw new Error(data.error || 'Upload failed');
        }
    } catch (error) {
        progress.style.display = 'none';
        result.className = 'result error';
        result.innerHTML = `
            <h3>✗ Error</h3>
            <p>${error.message}</p>
        `;
        result.style.display = 'block';
    } finally {
        uploadBtn.disabled = false;
    }
});
