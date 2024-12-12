let currentUserId = null;
const viewChat = document.querySelector('#btn');
user_id = viewChat.value
viewChat.addEventListener('click', (user_id) =>{
    currentUserId = userId;
    document.getElementById('chat-container').style.display = 'block'; // Show the chat container
    loadMessages();
});

// Load messages for the selected user
function loadMessages() {
    if (!currentUserId) return;
    fetch(`/messages/${currentUserId}`)
        .then(response => response.json())
        .then(messages => {
            const chatMessages = document.getElementById('chat-messages');
            chatMessages.innerHTML = '';
            messages.forEach(msg => {
                const messageElem = document.createElement('div');
                messageElem.textContent = msg.sender_id === currentUserId ? msg.content : 'You: ' + msg.content;
                chatMessages.appendChild(messageElem);
            });
        });
}

// Send a message to the current user
function sendMessage() {
    const content = document.getElementById('message-input').value;
    fetch(`/send_message`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ receiver_id: currentUserId, content })
    }).then(() => {
        loadMessages(); // Refresh messages
        document.getElementById('message-input').value = ''; // Clear input
    });
}

// Poll every 5 seconds to check for new messages
setInterval(loadMessages, 5000);