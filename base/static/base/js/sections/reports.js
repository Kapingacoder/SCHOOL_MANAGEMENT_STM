// Reports Section Functionality

// Initialize reports section
function initReportsSection() {
    // Initialize charts
    initReportCharts();
    
    // Initialize term filter
    initTermFilter();
    
    // Initialize report cards
    initReportCards();
}

// Initialize performance charts
function initReportCharts() {
    const chartElements = document.querySelectorAll('.performance-chart canvas');
    
    chartElements.forEach(chartEl => {
        const ctx = chartEl.getContext('2d');
        const chartData = JSON.parse(chartEl.parentElement.getAttribute('data-chart-data'));
        
        if (chartData && ctx) {
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: chartData.labels,
                    datasets: [{
                        label: 'Scores',
                        data: chartData.data,
                        backgroundColor: 'rgba(78, 115, 223, 0.8)',
                        borderColor: 'rgba(78, 115, 223, 1)',
                        borderWidth: 1,
                        borderRadius: 4,
                        barPercentage: 0.7
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            },
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleFont: {
                                size: 14,
                                weight: 'bold'
                            },
                            bodyFont: {
                                size: 13
                            },
                            padding: 12,
                            cornerRadius: 6,
                            displayColors: false,
                            callbacks: {
                                label: function(context) {
                                    return `Score: ${context.raw}%`;
                                }
                            }
                        }
                    }
                }
            });
        }
    });
}

// Initialize term filter dropdown
function initTermFilter() {
    const termDropdown = document.getElementById('termDropdown');
    if (!termDropdown) return;
    
    termDropdown.addEventListener('change', function() {
        const selectedTerm = this.value;
        const loadingOverlay = document.getElementById('loadingOverlay');
        
        // Show loading state
        if (loadingOverlay) loadingOverlay.style.display = 'flex';
        
        // In a real app, this would be an AJAX call to fetch reports for the selected term
        console.log('Selected term:', selectedTerm);
        
        // Simulate API call
        setTimeout(() => {
            // Update the reports for the selected term
            updateReportsForTerm(selectedTerm);
            
            // Hide loading state
            if (loadingOverlay) loadingOverlay.style.display = 'none';
            
            // Show success message
            showToast('Reports updated', `Showing reports for ${this.options[this.selectedIndex].text}`);
        }, 800);
    });
}

// Update reports when term changes
function updateReportsForTerm(term) {
    // In a real app, this would update the reports based on the selected term
    // For this example, we'll just update the term display
    const termDisplay = document.getElementById('currentTermDisplay');
    if (termDisplay) {
        const termText = document.querySelector(`#termDropdown option[value="${term}"]`).text;
        termDisplay.textContent = termText;
    }
    
    // Here you would typically make an AJAX call to get reports for the selected term
    // and then update the DOM with the new data
}

// Initialize report cards with interactive elements
function initReportCards() {
    // Handle view report details
    const viewReportButtons = document.querySelectorAll('.btn-view-report');
    
    viewReportButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const reportId = this.getAttribute('data-report-id');
            
            // In a real app, this would be an AJAX call to fetch the full report
            console.log('Viewing report:', reportId);
            
            // Show the report details modal
            const modal = new bootstrap.Modal(document.getElementById('reportDetailsModal'));
            const modalContent = document.getElementById('reportDetailsContent');
            
            if (modalContent) {
                // Show loading state
                modalContent.innerHTML = `
                    <div class="text-center my-5">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                    </div>
                `;
                
                // Simulate loading report data
                setTimeout(() => {
                    // In a real app, this would be the actual report data from the server
                    const reportData = {
                        id: reportId,
                        studentName: 'John Doe',
                        className: 'Grade 5A',
                        term: '2nd Term',
                        year: '2023',
                        overallGrade: 'A-',
                        comments: 'John has shown significant improvement in Mathematics and Science this term. He participates actively in class discussions and completes assignments on time. Keep up the good work!',
                        subjects: [
                            { name: 'Mathematics', score: 85, grade: 'A-', comment: 'Excellent problem-solving skills' },
                            { name: 'English', score: 78, grade: 'B+', comment: 'Good reading comprehension' },
                            { name: 'Science', score: 92, grade: 'A', comment: 'Outstanding performance in experiments' },
                            { name: 'History', score: 80, grade: 'A-', comment: 'Good understanding of historical events' },
                            { name: 'Geography', score: 75, grade: 'B', comment: 'Shows interest in the subject' },
                            { name: 'Art', score: 88, grade: 'A-', comment: 'Very creative and expressive' },
                            { name: 'Physical Education', score: 90, grade: 'A', comment: 'Excellent participation and teamwork' }
                        ],
                        attendance: {
                            present: 45,
                            absent: 2,
                            late: 3,
                            percentage: 93.8
                        },
                        teacher: 'Ms. Johnson',
                        date: '2023-06-15'
                    };
                    
                    // Render the report details
                    renderReportDetails(modalContent, reportData);
                }, 800);
            }
            
            modal.show();
        });
    });
    
    // Handle download report
    const downloadReportButtons = document.querySelectorAll('.btn-download-report');
    
    downloadReportButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation(); // Prevent triggering the view report click
            const reportId = this.getAttribute('data-report-id');
            
            // In a real app, this would trigger a file download
            console.log('Downloading report:', reportId);
            
            // Show success message
            showToast('Download Started', 'Your report download has started.', 'success');
            
            // Simulate file download
            setTimeout(() => {
                // In a real app, this would be the actual file download
                const link = document.createElement('a');
                link.href = '#'; // Replace with actual download URL
                link.download = `report_${reportId}.pdf`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }, 1000);
        });
    });
}

// Render report details in the modal
function renderReportDetails(container, reportData) {
    if (!container) return;
    
    // Create subjects HTML
    const subjectsHtml = reportData.subjects.map(subject => `
        <tr>
            <td>${subject.name}</td>
            <td class="text-center">${subject.score}%</td>
            <td class="text-center"><span class="badge bg-primary">${subject.grade}</span></td>
            <td>${subject.comment}</td>
        </tr>
    `).join('');
    
    // Create attendance HTML
    const attendanceHtml = `
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">Attendance Summary</h5>
                        <div class="attendance-stats">
                            <div class="stat-item">
                                <span class="stat-label">Present:</span>
                                <span class="stat-value">${reportData.attendance.present} days</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Absent:</span>
                                <span class="stat-value">${reportData.attendance.absent} days</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Late Arrivals:</span>
                                <span class="stat-value">${reportData.attendance.late} days</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Attendance Rate:</span>
                                <span class="stat-value text-success">${reportData.attendance.percentage}%</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">Overall Performance</h5>
                        <div class="text-center my-4">
                            <div class="performance-grade">${reportData.overallGrade}</div>
                            <div class="text-muted">${getGradeDescription(reportData.overallGrade)}</div>
                        </div>
                        <div class="d-grid">
                            <button class="btn btn-primary">
                                <i class="fas fa-download me-2"></i>Download Full Report
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Set the HTML content
    container.innerHTML = `
        <div class="report-details">
            <div class="report-header mb-4">
                <h4>${reportData.studentName}'s Academic Report</h4>
                <p class="text-muted">${reportData.term} ${reportData.year} • ${reportData.className}</p>
            </div>
            
            ${attendanceHtml}
            
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Subject Performance</h5>
                </div>
                <div class="table-responsive">
                    <table class="table table-hover mb-0">
                        <thead>
                            <tr>
                                <th>Subject</th>
                                <th class="text-center">Score</th>
                                <th class="text-center">Grade</th>
                                <th>Teacher's Comment</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${subjectsHtml}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">Teacher's Comments</h5>
                </div>
                <div class="card-body">
                    <p>${reportData.comments}</p>
                    <div class="signature mt-4">
                        <div class="signature-line"></div>
                        <div class="signature-name">${reportData.teacher}</div>
                        <div class="text-muted">Class Teacher</div>
                        <div class="text-muted small">Date: ${formatDate(reportData.date)}</div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Helper function to get grade description
function getGradeDescription(grade) {
    const gradeDescriptions = {
        'A+': 'Outstanding Achievement',
        'A': 'Excellent Work',
        'A-': 'Very Good',
        'B+': 'Good Performance',
        'B': 'Satisfactory',
        'B-': 'Adequate',
        'C+': 'Basic Understanding',
        'C': 'Needs Improvement',
        'C-': 'Below Expectations',
        'D': 'Significant Improvement Needed',
        'F': 'Fail - Does Not Meet Requirements'
    };
    
    return gradeDescriptions[grade] || 'Performance evaluation';
}

// Helper function to show toast notifications
function showToast(title, message, type = 'info') {
    // In a real app, you would use a toast library or create a custom toast component
    console.log(`[${type.toUpperCase()}] ${title}: ${message}`);
    
    // For this example, we'll use the browser's built-in alert
    alert(`${title}\n\n${message}`);
}
