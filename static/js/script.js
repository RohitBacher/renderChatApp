/* =========================================
   CHAT ROOM PAGE LOGIC (AJAX integration)
   ========================================= */
const sendBtn = document.getElementById('sendBtn');
const messageInput = document.getElementById('messageInput');
const chatBox = document.getElementById('chatBox');

// Only run this code if we are actually on the chat page
if (sendBtn && messageInput && chatBox) {

    // 1. Function to send a message to the Django Backend
    function sendMessage() {
        const text = messageInput.value.trim();
        if (text === '') return;

        const csrfToken = document.getElementById('csrfToken').value;

        // Create form data to send to the server
        const formData = new FormData();
        formData.append('content', text);

        // Send POST request to your send_message view
        fetch('/send_message/', {  // Ensure this URL matches your urls.py path
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            messageInput.value = ''; // Clear input after sending
            fetchMessages(); // Immediately fetch messages to show the new one
        })
        .catch(error => console.error('Error sending message:', error));
    }

    // 2. Function to fetch new messages automatically
    function fetchMessages() {
        const roomId = document.getElementById('roomId').value;
        const currentUsername = document.getElementById('currentUsername').value;

        fetch(`/getMessages/${roomId}/`) // Ensure this URL matches your urls.py path
        .then(response => response.json())
        .then(data => {
            chatBox.innerHTML = ''; // Clear the current chat box
            
            // Loop through the data from Django and rebuild the chat HTML
            data.messages.forEach(msg => {
                // If the message is from the logged-in user, align right. Otherwise, left.
                const alignment = msg.sender === currentUsername ? 'right' : 'left'; 
                
                const messageHTML = `
                    <div class="message ${alignment}">
                        <div class="bubble">
                            <div class="text">${msg.val}</div>
                            <div class="time">${msg.date}</div>
                        </div>
                        <div class="avatar default-avatar">👤</div>
                    </div>
                `;
                chatBox.insertAdjacentHTML('beforeend', messageHTML);
            });

            // Keep scrolled to the bottom
            chatBox.scrollTop = chatBox.scrollHeight;
        })
        .catch(error => console.error('Error fetching messages:', error));
    }

    // Event listeners for clicking Send or pressing Enter
    sendBtn.addEventListener('click', sendMessage);

    messageInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    // Run fetchMessages every 1.5 seconds (1500 milliseconds) to get live updates
    setInterval(fetchMessages, 1500);

    // Scroll to bottom on initial page load
    window.onload = function() {
        chatBox.scrollTop = chatBox.scrollHeight;
    };
}