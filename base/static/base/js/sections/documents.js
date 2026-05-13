// Documents Section Functionality

// Initialize documents section
function initDocumentsSection() {
    // Initialize document filters
    initDocumentFilters();
    
    // Initialize document actions (preview, download, share)
    initDocumentActions();
    
    // Initialize document upload
    initDocumentUpload();
    
    // Initialize document search
    initDocumentSearch();
    
    // Initialize document grid/list view toggle
    initViewToggle();
}

// Initialize document filters
function initDocumentFilters() {
    const filterButtons = document.querySelectorAll('.doc-filter-btn');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');
            const documentsContainer = document.getElementById('documentsGrid');
            
            if (!documentsContainer) return;
            
            // Update active filter button
            document.querySelectorAll('.doc-filter-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            this.classList.add('active');
            
            // Show loading state
            const originalContent = documentsContainer.innerHTML;
            documentsContainer.innerHTML = `
                <div class="col-12 text-center my-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Filtering documents...</p>
                </div>
            `;
            
            // Simulate API call to filter documents
            setTimeout(() => {
                // In a real app, this would be an AJAX call to get filtered documents
                console.log('Filtering documents by:', filter);
                
                // For this example, we'll just show/hide based on the filter
                const documentItems = documentsContainer.querySelectorAll('.document-item');
                let hasResults = false;
                
                documentItems.forEach(item => {
                    const itemCategory = item.getAttribute('data-category');
                    
                    if (filter === 'all' || itemCategory === filter) {
                        item.style.display = '';
                        hasResults = true;
                    } else {
                        item.style.display = 'none';
                    }
                });
                
                // Show no results message if no documents match the filter
                const noResults = documentsContainer.querySelector('.no-documents');
                if (!hasResults) {
                    if (!noResults) {
                        const noResultsHtml = `
                            <div class="col-12 no-documents">
                                <div class="card">
                                    <div class="card-body text-center py-5">
                                        <i class="fas fa-folder-open fa-3x text-muted mb-3"></i>
                                        <h5>No documents found</h5>
                                        <p class="text-muted">There are no documents in this category.</p>
                                    </div>
                                </div>
                            </div>
                        `;
                        documentsContainer.insertAdjacentHTML('beforeend', noResultsHtml);
                    } else {
                        noResults.style.display = '';
                    }
                } else if (noResults) {
                    noResults.style.display = 'none';
                }
                
                // Restore original content if needed (in case of async loading)
                // documentsContainer.innerHTML = originalContent;
                
            }, 500);
        });
    });
}

// Initialize document actions (preview, download, share)
function initDocumentActions() {
    // Handle document preview
    const previewButtons = document.querySelectorAll('.preview-document');
    
    previewButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const documentId = this.getAttribute('data-document-id');
            const documentName = this.getAttribute('data-document-name');
            const documentType = this.getAttribute('data-document-type');
            const documentUrl = this.getAttribute('data-document-url');
            
            // In a real app, this would open the document in a previewer
            console.log('Preview document:', documentId, documentName);
            
            // Show preview modal
            const previewModal = new bootstrap.Modal(document.getElementById('documentPreviewModal'));
            const previewTitle = document.getElementById('documentPreviewTitle');
            const previewContent = document.getElementById('documentPreviewContent');
            const downloadBtn = document.getElementById('downloadPreviewDoc');
            
            if (!previewTitle || !previewContent || !downloadBtn) return;
            
            // Set document title
            previewTitle.textContent = documentName;
            
            // Set download link
            downloadBtn.setAttribute('href', documentUrl);
            downloadBtn.setAttribute('download', documentName);
            
            // Show loading state
            previewContent.innerHTML = `
                <div class="text-center my-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Loading document preview...</p>
                </div>
            `;
            
            // Simulate loading the document preview
            setTimeout(() => {
                let previewHtml = '';
                const fileExtension = documentName.split('.').pop().toLowerCase();
                
                if (['jpg', 'jpeg', 'png', 'gif'].includes(fileExtension)) {
                    previewHtml = `
                        <div class="text-center">
                            <img src="${documentUrl}" alt="${documentName}" class="img-fluid">
                        </div>
                    `;
                } else if (fileExtension === 'pdf') {
                    previewHtml = `
                        <div class="ratio ratio-16x9">
                            <iframe src="${documentUrl}" title="${documentName}" allowfullscreen></iframe>
                        </div>
                    `;
                } else if (['doc', 'docx'].includes(fileExtension)) {
                    previewHtml = `
                        <div class="document-preview-placeholder">
                            <i class="fas fa-file-word text-primary" style="font-size: 4rem; margin-bottom: 1rem;"></i>
                            <p>Preview not available for Word documents. Please download to view.</p>
                        </div>
                    `;
                } else if (['xls', 'xlsx'].includes(fileExtension)) {
                    previewHtml = `
                        <div class="document-preview-placeholder">
                            <i class="fas fa-file-excel text-success" style="font-size: 4rem; margin-bottom: 1rem;"></i>
                            <p>Preview not available for Excel files. Please download to view.</p>
                        </div>
                    `;
                } else {
                    previewHtml = `
                        <div class="document-preview-placeholder">
                            <i class="fas fa-file-alt" style="font-size: 4rem; margin-bottom: 1rem;"></i>
                            <p>Preview not available for this file type. Please download to view.</p>
                        </div>
                    `;
                }
                
                previewContent.innerHTML = previewHtml;
            }, 1000);
            
            // Show the modal
            previewModal.show();
        });
    });
    
    // Handle document download
    const downloadButtons = document.querySelectorAll('.download-document');
    
    downloadButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            
            const documentId = this.getAttribute('data-document-id');
            const documentName = this.getAttribute('data-document-name');
            const documentUrl = this.getAttribute('data-document-url');
            
            // In a real app, this would trigger a file download
            console.log('Download document:', documentId, documentName);
            
            // Show download started message
            showToast('Download Started', `${documentName} is being downloaded.`, 'info');
            
            // Simulate download (in a real app, this would be an actual file download)
            setTimeout(() => {
                const link = document.createElement('a');
                link.href = documentUrl;
                link.download = documentName;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                // Show download complete message
                showToast('Download Complete', `${documentName} has been downloaded.`, 'success');
            }, 1000);
        });
    });
    
    // Handle document share
    const shareButtons = document.querySelectorAll('.share-document');
    
    shareButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            
            const documentId = this.getAttribute('data-document-id');
            const documentName = this.getAttribute('data-document-name');
            
            // In a real app, this would open a share dialog
            console.log('Share document:', documentId, documentName);
            
            // Show share modal
            const shareModal = new bootstrap.Modal(document.getElementById('shareDocumentModal'));
            const shareForm = document.getElementById('shareDocumentForm');
            const documentNameEl = document.getElementById('shareDocumentName');
            
            if (documentNameEl) {
                documentNameEl.textContent = documentName;
            }
            
            // Reset form
            if (shareForm) {
                shareForm.reset();
                
                // Set up form submission
                shareForm.onsubmit = function(e) {
                    e.preventDefault();
                    
                    const email = shareForm.querySelector('input[type="email"]')?.value;
                    const message = shareForm.querySelector('textarea')?.value;
                    
                    if (!email) {
                        showToast('Error', 'Please enter a valid email address.', 'error');
                        return;
                    }
                    
                    // In a real app, this would send the share request to the server
                    console.log('Sharing document with:', { email, message });
                    
                    // Show success message
                    shareModal.hide();
                    showToast('Document Shared', `${documentName} has been shared with ${email}.`, 'success');
                };
            }
            
            // Show the modal
            shareModal.show();
        });
    });
    
    // Handle document delete
    const deleteButtons = document.querySelectorAll('.delete-document');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            
            const documentId = this.getAttribute('data-document-id');
            const documentName = this.getAttribute('data-document-name');
            
            // Show confirmation dialog
            if (confirm(`Are you sure you want to delete "${documentName}"? This action cannot be undone.`)) {
                // In a real app, this would send a delete request to the server
                console.log('Delete document:', documentId, documentName);
                
                // Remove the document from the UI
                const documentItem = this.closest('.document-item');
                if (documentItem) {
                    documentItem.style.animation = 'fadeOut 0.3s';
                    setTimeout(() => {
                        documentItem.remove();
                        
                        // Show success message
                        showToast('Document Deleted', `${documentName} has been moved to trash.`, 'success');
                        
                        // Check if there are no more documents
                        const documentsContainer = document.getElementById('documentsGrid');
                        const documentItems = documentsContainer?.querySelectorAll('.document-item');
                        
                        if (documentItems && documentItems.length === 0) {
                            const noResultsHtml = `
                                <div class="col-12 no-documents">
                                    <div class="card">
                                        <div class="card-body text-center py-5">
                                            <i class="fas fa-folder-open fa-3x text-muted mb-3"></i>
                                            <h5>No documents found</h5>
                                            <p class="text-muted">There are no documents in this category.</p>
                                        </div>
                                    </div>
                                </div>
                            `;
                            documentsContainer.insertAdjacentHTML('beforeend', noResultsHtml);
                        }
                    }, 300);
                }
            }
        });
    });
}

// Initialize document upload
function initDocumentUpload() {
    const uploadForm = document.getElementById('uploadDocumentForm');
    const fileInput = document.getElementById('documentFile');
    const fileNameDisplay = document.getElementById('fileName');
    const uploadProgress = document.getElementById('uploadProgress');
    const progressBar = document.getElementById('uploadProgressBar');
    
    if (!uploadForm || !fileInput || !fileNameDisplay) return;
    
    // Show file name when a file is selected
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            fileNameDisplay.textContent = this.files[0].name;
            fileNameDisplay.classList.remove('text-muted');
            fileNameDisplay.classList.add('text-primary');
        } else {
            fileNameDisplay.textContent = 'No file chosen';
            fileNameDisplay.classList.remove('text-primary');
            fileNameDisplay.classList.add('text-muted');
        }
    });
    
    // Handle form submission
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const file = fileInput.files[0];
        
        if (!file) {
            showToast('Error', 'Please select a file to upload.', 'error');
            return;
        }
        
        // Show upload progress
        if (uploadProgress && progressBar) {
            uploadProgress.style.display = 'block';
            progressBar.style.width = '0%';
            progressBar.setAttribute('aria-valuenow', 0);
        }
        
        // In a real app, this would be an AJAX call to upload the file
        console.log('Uploading file:', file.name);
        
        // Simulate upload progress
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += Math.floor(Math.random() * 10) + 5;
            if (progress > 90) progress = 90; // Don't go to 100% until the end
            
            if (progressBar) {
                progressBar.style.width = `${progress}%`;
                progressBar.setAttribute('aria-valuenow', progress);
                progressBar.textContent = `${progress}%`;
            }
        }, 200);
        
        // Simulate file upload (in a real app, this would be an AJAX call)
        setTimeout(() => {
            clearInterval(progressInterval);
            
            // Complete the progress bar
            if (progressBar) {
                progressBar.style.width = '100%';
                progressBar.setAttribute('aria-valuenow', 100);
                progressBar.textContent = '100%';
            }
            
            // Hide progress bar after a short delay
            setTimeout(() => {
                if (uploadProgress) {
                    uploadProgress.style.display = 'none';
                }
                
                // Show success message
                showToast('Upload Complete', `${file.name} has been uploaded successfully.`, 'success');
                
                // Reset form
                uploadForm.reset();
                fileNameDisplay.textContent = 'No file chosen';
                fileNameDisplay.classList.remove('text-primary');
                fileNameDisplay.classList.add('text-muted');
                
                // In a real app, you would update the documents list here
                // For this example, we'll just log to the console
                console.log('File uploaded successfully:', file.name);
                
                // Close the modal
                const modal = bootstrap.Modal.getInstance(uploadForm.closest('.modal'));
                if (modal) modal.hide();
            }, 500);
        }, 2000);
    });
}

// Initialize document search
function initDocumentSearch() {
    const searchInput = document.getElementById('documentSearch');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function() {
        const query = this.value.trim().toLowerCase();
        const documentItems = document.querySelectorAll('.document-item');
        
        if (query === '') {
            // Show all documents if search is empty
            documentItems.forEach(item => {
                item.style.display = '';
            });
            return;
        }
        
        // Filter documents based on search query
        let hasResults = false;
        
        documentItems.forEach(item => {
            const name = item.querySelector('.document-name')?.textContent.toLowerCase() || '';
            const description = item.querySelector('.document-description')?.textContent.toLowerCase() || '';
            const category = item.getAttribute('data-category') || '';
            
            if (name.includes(query) || description.includes(query) || category.includes(query)) {
                item.style.display = '';
                hasResults = true;
            } else {
                item.style.display = 'none';
            }
        });
        
        // Show no results message if no documents match the search
        const noResults = document.querySelector('.no-documents');
        const documentsContainer = document.getElementById('documentsGrid');
        
        if (!hasResults) {
            if (!noResults && documentsContainer) {
                const noResultsHtml = `
                    <div class="col-12 no-documents">
                        <div class="card">
                            <div class="card-body text-center py-5">
                                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                                <h5>No results found</h5>
                                <p class="text-muted">No documents match your search for "${query}".</p>
                            </div>
                        </div>
                    </div>
                `;
                documentsContainer.insertAdjacentHTML('beforeend', noResultsHtml);
            }
        } else if (noResults) {
            noResults.remove();
        }
    });
}

// Initialize grid/list view toggle
function initViewToggle() {
    const gridViewBtn = document.getElementById('gridViewBtn');
    const listViewBtn = document.getElementById('listViewBtn');
    const documentsContainer = document.getElementById('documentsGrid');
    
    if (!gridViewBtn || !listViewBtn || !documentsContainer) return;
    
    // Load saved view preference or default to grid view
    const savedView = localStorage.getItem('documentsView') || 'grid';
    
    if (savedView === 'list') {
        documentsContainer.classList.add('list-view');
        gridViewBtn.classList.remove('active');
        listViewBtn.classList.add('active');
    } else {
        documentsContainer.classList.remove('list-view');
        gridViewBtn.classList.add('active');
        listViewBtn.classList.remove('active');
    }
    
    // Toggle to grid view
    gridViewBtn.addEventListener('click', function() {
        if (documentsContainer.classList.contains('list-view')) {
            documentsContainer.classList.remove('list-view');
            gridViewBtn.classList.add('active');
            listViewBtn.classList.remove('active');
            localStorage.setItem('documentsView', 'grid');
        }
    });
    
    // Toggle to list view
    listViewBtn.addEventListener('click', function() {
        if (!documentsContainer.classList.contains('list-view')) {
            documentsContainer.classList.add('list-view');
            listViewBtn.classList.add('active');
            gridViewBtn.classList.remove('active');
            localStorage.setItem('documentsView', 'list');
        }
    });
}
