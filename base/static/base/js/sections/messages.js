// Messages Section Functionality

// Initialize messages section
function initMessagesSection() {
    // Initialize message threads
    initMessageThreads();
    
    // Initialize new message button
    initNewMessageButton();
    
    // Initialize message search
    initMessageSearch();
    
    // Initialize message actions (reply, forward, delete)
    initMessageActions();
}

// Initialize message threads list
function initMessageThreads() {
    const messageThreads = document.querySelectorAll('.message-thread');
    
    messageThreads.forEach(thread => {
        thread.addEventListener('click', function() {
            const messageId = this.getAttribute('data-message-id');
            const senderId = this.getAttribute('data-sender-id');
            
            // Mark as read
            if (this.classList.contains('unread')) {
                this.classList.remove('unread');
                const unreadBadge = this.querySelector('.unread-badge');
                if (unreadBadge) unreadBadge.remove();
                
                // Update unread count
                updateUnreadCount(-1);
            }
            
            // Load message thread
            loadMessageThread(messageId, senderId);
        });
    });
    
    // If there are unread messages, mark the first one as read
    const firstUnread = document.querySelector('.message-thread.unread');
    if (firstUnread) {
        firstUnread.click();
    }
}

// Load message thread
function loadMessageThread(messageId, senderId) {
    const messageThreadView = document.getElementById('messageThreadView');
    const messageContent = document.getElementById('messageContent');
    const messageThreadBody = document.getElementById('messageThreadBody');
    
    if (!messageThreadView || !messageContent || !messageThreadBody) return;
    
    // Show loading state
    messageThreadBody.innerHTML = `
        <div class="text-center my-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
    
    // Show message thread view and hide empty state
    messageThreadView.style.display = 'block';
    messageContent.querySelector('.empty-message').style.display = 'none';
    
    // In a real app, this would be an AJAX call to fetch the message thread
    setTimeout(() => {
        // Simulate API response
        const message = {
            id: messageId,
            subject: 'Student Progress Update',
            content: `Dear Parent,\n\nI hope this message finds you well. I wanted to take a moment to update you on your child's progress in our class.\n\n${getRandomMessageContent()}\n\nPlease don't hesitate to reach out if you have any questions or would like to schedule a meeting.\n\nBest regards,\nMs. Johnson`,
            sender: {
                id: senderId,
                name: 'Ms. Johnson',
                email: 'johnson@school.edu',
                avatar: 'MJ',
                role: 'Class Teacher',
                phone: '(555) 123-4567'
            },
            timestamp: '2023-06-15T10:30:00Z',
            attachments: [
                { name: 'Progress_Report_Q2.pdf', size: 2450000, type: 'pdf' },
                { name: 'Science_Project_Rubric.pdf', size: 1800000, type: 'pdf' }
            ],
            replies: [
                {
                    id: 'reply-1',
                    content: 'Thank you for the update, Ms. Johnson. We will review the materials and get back to you with any questions.',
                    sender: {
                        id: 'parent-1',
                        name: 'You',
                        email: 'parent@example.com',
                        avatar: 'P',
                        role: 'Parent'
                    },
                    timestamp: '2023-06-15T14:45:00Z',
                    isCurrentUser: true
                },
                {
                    id: 'reply-2',
                    content: 'You\'re welcome! I\'m happy to discuss this further during our next parent-teacher meeting.',
                    sender: {
                        id: senderId,
                        name: 'Ms. Johnson',
                        email: 'johnson@school.edu',
                        avatar: 'MJ',
                        role: 'Class Teacher'
                    },
                    timestamp: '2023-06-16T09:15:00Z',
                    isCurrentUser: false
                }
            ]
        };
        
        // Update UI with message data
        renderMessageThread(message);
        
        // Initialize reply form
        initReplyForm(messageId, senderId);
        
    }, 800);
}

// Render message thread
function renderMessageThread(message) {
    const messageThreadBody = document.getElementById('messageThreadBody');
    if (!messageThreadBody) return;
    
    // Format message content with line breaks
    const formattedContent = message.content.replace(/\n/g, '<br>');
    
    // Create attachments HTML if there are any
    let attachmentsHtml = '';
    if (message.attachments && message.attachments.length > 0) {
        attachmentsHtml = `
            <div class="attachments mt-3">
                <h6 class="mb-2">
                    <i class="fas fa-paperclip me-1"></i> Attachments (${message.attachments.length})
                </h6>
                <div class="attachments-list">
                    ${message.attachments.map(attachment => `
                        <a href="#" class="attachment-item" data-attachment-id="${attachment.name}">
                            <div class="attachment-icon">
                                <i class="fas fa-file-${attachment.type === 'pdf' ? 'pdf' : 'word'}"></i>
                            </div>
                            <div class="attachment-info">
                                <div class="attachment-name">${attachment.name}</div>
                                <div class="attachment-size">${formatFileSize(attachment.size)}</div>
                            </div>
                        </a>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // Create message header
    const messageHeader = `
        <div class="message-header mb-4">
            <div class="d-flex justify-content-between align-items-start">
                <div class="d-flex align-items-center">
                    <div class="sender-avatar me-3">
                        ${message.sender.avatar}
                    </div>
                    <div>
                        <h5 class="mb-0">${message.sender.name}</h5>
                        <div class="text-muted small">
                            ${message.sender.role} • ${formatDate(message.timestamp)}
                        </div>
                    </div>
                </div>
                <div class="dropdown">
                    <button class="btn btn-sm btn-outline-secondary dropdown-toggle" type="button" 
                            data-bs-toggle="dropdown" aria-expanded="false">
                        <i class="fas fa-ellipsis-v"></i>
                    </button>
                    <ul class="dropdown-menu dropdown-menu-end">
                        <li><a class="dropdown-item" href="#" data-action="reply">
                            <i class="fas fa-reply me-2"></i>Reply
                        </a></li>
                        <li><a class="dropdown-item" href="#" data-action="forward">
                            <i class="fas fa-share me-2"></i>Forward
                        </a></li>
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item text-danger" href="#" data-action="delete">
                            <i class="fas fa-trash me-2"></i>Delete
                        </a></li>
                    </ul>
                </div>
            </div>
            <div class="message-metadata mt-2">
                <span class="badge bg-light text-dark">To: ${message.sender.role === 'Teacher' ? 'You' : message.sender.name}</span>
                <span class="text-muted ms-2">${formatTimeAgo(message.timestamp)}</span>
            </div>
        </div>
    `;
    
    // Create message body
    const messageBody = `
        <div class="message-body mb-4">
            <h4 class="mb-3">${message.subject}</h4>
            <div class="message-content">${formattedContent}</div>
            ${attachmentsHtml}
        </div>
    `;
    
    // Create replies section
    let repliesHtml = '';
    if (message.replies && message.replies.length > 0) {
        repliesHtml = `
            <div class="replies mb-4">
                <h6 class="mb-3">Replies (${message.replies.length})</h6>
                ${message.replies.map(reply => renderMessageReply(reply)).join('')}
            </div>
        `;
    }
    
    // Combine all parts
    messageThreadBody.innerHTML = `
        ${messageHeader}
        <div class="message-content-container">
            ${messageBody}
            ${repliesHtml}
        </div>
    `;
    
    // Initialize attachment click handlers
    initAttachmentHandlers();
}

// Render a single message reply
function renderMessageReply(reply) {
    const formattedContent = reply.content.replace(/\n/g, '<br>');
    
    return `
        <div class="message-reply ${reply.isCurrentUser ? 'current-user' : ''}" data-reply-id="${reply.id}">
            <div class="reply-header">
                <div class="sender-avatar">
                    ${reply.sender.avatar}
                </div>
                <div class="reply-info">
                    <div class="d-flex justify-content-between">
                        <strong>${reply.sender.name}</strong>
                        <small class="text-muted">${formatTimeAgo(reply.timestamp)}</small>
                    </div>
                    <div class="text-muted small">${reply.sender.role}</div>
                </div>
            </div>
            <div class="reply-content">
                ${formattedContent}
            </div>
        </div>
    `;
}

// Initialize new message button
function initNewMessageButton() {
    const newMessageBtn = document.getElementById('newMessageBtn');
    if (!newMessageBtn) return;
    
    newMessageBtn.addEventListener('click', function() {
        const newMessageModal = new bootstrap.Modal(document.getElementById('newMessageModal'));
        
        // Reset form
        const form = document.getElementById('newMessageForm');
        if (form) form.reset();
        
        // Show modal
        newMessageModal.show();
    });
    
    // Initialize new message form
    const newMessageForm = document.getElementById('newMessageForm');
    if (newMessageForm) {
        newMessageForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(this);
            const messageData = {
                recipient: formData.get('recipient'),
                subject: formData.get('subject'),
                message: formData.get('message'),
                attachments: []
            };
            
            // In a real app, send this data to the server via AJAX
            console.log('New message data:', messageData);
            
            // Show success message
            showToast('Message Sent', 'Your message has been sent successfully.', 'success');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(this.closest('.modal'));
            if (modal) modal.hide();
            
            // Reset form
            this.reset();
        });
    }
}

// Initialize message search
function initMessageSearch() {
    const searchInput = document.getElementById('messageSearch');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function() {
        const query = this.value.trim().toLowerCase();
        const messageThreads = document.querySelectorAll('.message-thread');
        
        if (query === '') {
            // Show all messages if search is empty
            messageThreads.forEach(thread => {
                thread.style.display = 'flex';
            });
            return;
        }
        
        // Filter messages based on search query
        messageThreads.forEach(thread => {
            const sender = thread.querySelector('.sender-name')?.textContent.toLowerCase() || '';
            const subject = thread.querySelector('.message-preview')?.textContent.toLowerCase() || '';
            
            if (sender.includes(query) || subject.includes(query)) {
                thread.style.display = 'flex';
            } else {
                thread.style.display = 'none';
            }
        });
    });
}

// Initialize reply form
function initReplyForm(messageId, recipientId) {
    const replyForm = document.getElementById('replyMessageForm');
    if (!replyForm) return;
    
    // Reset form
    replyForm.reset();
    
    // Set up form submission
    replyForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const replyContent = this.querySelector('textarea')?.value.trim();
        if (!replyContent) return;
        
        // In a real app, send the reply via AJAX
        console.log('Sending reply to message', messageId, ':', replyContent);
        
        // Create reply object
        const reply = {
            id: 'reply-' + Date.now(),
            content: replyContent,
            sender: {
                id: 'current-user',
                name: 'You',
                avatar: 'P',
                role: 'Parent'
            },
            timestamp: new Date().toISOString(),
            isCurrentUser: true
        };
        
        // Add reply to the thread
        addMessageToThread(reply);
        
        // Clear the reply textarea
        this.reset();
        
        // Show success message
        showToast('Reply Sent', 'Your reply has been sent successfully.', 'success');
    });
}

// Add a message to the thread
function addMessageToThread(message) {
    const messageThreadBody = document.getElementById('messageThreadBody');
    if (!messageThreadBody) return;
    
    const repliesContainer = messageThreadBody.querySelector('.replies') || 
                           document.createElement('div');
    
    if (!messageThreadBody.querySelector('.replies')) {
        repliesContainer.className = 'replies mb-4';
        repliesContainer.innerHTML = '<h6 class="mb-3">Replies</h6>';
        messageThreadBody.querySelector('.message-content-container').appendChild(repliesContainer);
    }
    
    // Create and append the new reply
    const replyElement = document.createElement('div');
    replyElement.className = 'message-reply current-user';
    replyElement.setAttribute('data-reply-id', message.id);
    replyElement.innerHTML = `
        <div class="reply-header">
            <div class="sender-avatar">
                ${message.sender.avatar}
            </div>
            <div class="reply-info">
                <div class="d-flex justify-content-between">
                    <strong>${message.sender.name}</strong>
                    <small class="text-muted">Just now</small>
                </div>
                <div class="text-muted small">${message.sender.role}</div>
            </div>
        </div>
        <div class="reply-content">
            ${message.content.replace(/\n/g, '<br>')}
        </div>
    `;
    
    repliesContainer.appendChild(replyElement);
    
    // Update the "Replies (X)" heading
    const repliesHeading = repliesContainer.querySelector('h6');
    if (repliesHeading) {
        const replyCount = repliesContainer.querySelectorAll('.message-reply').length;
        repliesHeading.textContent = `Replies (${replyCount})`;
    }
    
    // Scroll to the new reply
    replyElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Initialize attachment handlers
function initAttachmentHandlers() {
    const attachmentLinks = document.querySelectorAll('.attachment-item');
    
    attachmentLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const attachmentId = this.getAttribute('data-attachment-id');
            // In a real app, this would open the attachment or show a preview
            console.log('Viewing attachment:', attachmentId);
            
            // For this example, we'll show a preview modal
            const previewModal = new bootstrap.Modal(document.getElementById('attachmentPreviewModal'));
            const previewTitle = document.getElementById('attachmentPreviewTitle');
            const previewContent = document.getElementById('attachmentPreviewContent');
            
            if (previewTitle && previewContent) {
                previewTitle.textContent = attachmentId;
                previewContent.innerHTML = `
                    <div class="text-center my-5">
                        <i class="fas fa-file-pdf fa-4x text-danger mb-3"></i>
                        <p>Preview not available. Would you like to download the file?</p>
                        <a href="#" class="btn btn-primary" download="${attachmentId}">
                            <i class="fas fa-download me-2"></i>Download
                        </a>
                    </div>
                `;
                
                previewModal.show();
            }
        });
    });
}

// Initialize message actions (reply, forward, delete)
function initMessageActions() {
    // Handle action buttons in dropdown menus
    document.addEventListener('click', function(e) {
        const actionLink = e.target.closest('[data-action]');
        if (!actionLink) return;
        
        e.preventDefault();
        const action = actionLink.getAttribute('data-action');
        const messageId = actionLink.closest('.message-thread')?.getAttribute('data-message-id');
        
        switch (action) {
            case 'reply':
                // In a real app, this would set up a reply form
                console.log('Reply to message:', messageId);
                break;
                
            case 'forward':
                // In a real app, this would set up a forward form
                console.log('Forward message:', messageId);
                break;
                
            case 'delete':
                // In a real app, this would delete the message via AJAX
                console.log('Delete message:', messageId);
                
                // Remove the message from the UI
                const messageThread = actionLink.closest('.message-thread');
                if (messageThread) {
                    messageThread.style.animation = 'fadeOut 0.3s';
                    setTimeout(() => {
                        messageThread.remove();
                        
                        // If this was the current message being viewed, show empty state
                        const messageThreadView = document.getElementById('messageThreadView');
                        const messageContent = document.getElementById('messageContent');
                        
                        if (messageThreadView && messageContent) {
                            messageThreadView.style.display = 'none';
                            messageContent.querySelector('.empty-message').style.display = 'block';
                        }
                        
                        // Show success message
                        showToast('Message Deleted', 'The message has been moved to trash.', 'success');
                    }, 300);
                }
                break;
        }
    });
}

// Helper function to generate random message content
function getRandomMessageContent() {
    const contents = [
        "Your child has shown remarkable improvement in mathematics this term. Their problem-solving skills have developed significantly, and they actively participate in class discussions.",
        "I wanted to highlight your child's excellent performance in the recent science project. Their presentation was well-researched and demonstrated a deep understanding of the subject matter.",
        "We've noticed your child's strong leadership skills in group activities. They collaborate effectively with classmates and often take initiative to help others understand difficult concepts.",
        "Your child's creative writing has been exceptional. Their recent essay showcased not only strong writing skills but also a unique and imaginative perspective on the topic.",
        "I'm impressed with your child's consistent effort and positive attitude in class. They approach challenges with enthusiasm and are always willing to ask questions to deepen their understanding."
    ];
    
    return contents[Math.floor(Math.random() * contents.length)];
}

// Helper function to format time as "X time ago"
function formatTimeAgo(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    
    const intervals = {
        year: 31536000,
        month: 2592000,
        week: 604800,
        day: 86400,
        hour: 3600,
        minute: 60
    };
    
    if (seconds < 60) {
        return 'Just now';
    }
    
    for (const [unit, secondsInUnit] of Object.entries(intervals)) {
        const interval = Math.floor(seconds / secondsInUnit);
        if (interval >= 1) {
            return interval === 1 ? `1 ${unit} ago` : `${interval} ${unit}s ago`;
        }
    }
    
    return date.toLocaleDateString();
}
