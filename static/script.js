document.getElementById('send-btn').addEventListener('click', function(event) {
    event.preventDefault();
    sendUserInput();
});

document.getElementById('user-input').addEventListener('keypress', function(event) {
    if (event.keyCode === 13) {
        event.preventDefault();
        sendUserInput();
    }
});

function sendUserInput() {
    var userInput = document.getElementById('user-input').value;
    fetch('/process_chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'user_input=' + encodeURIComponent(userInput)
    })
    .then(response => response.json())
    .then(data => {
        if (typeof data === 'string') {
            appendChat("user", userInput);
            appendChat("robot", data);
        } else if (data.options) {
            appendChat("user", userInput);
            displayOptions(data.options);
        } else if (data.response) {
            appendChat("user", userInput);
            appendChat("robot", data.response);
        } else if (data.error) {
            appendChat("robot", "Error: " + data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}

function appendChat(role, message) {
    var chatContainer = document.getElementById('chat-container');
    var chatBubble = document.createElement('div');
    chatBubble.classList.add('chat-bubble');
    chatBubble.classList.add(role);
    chatBubble.innerText = message;
    chatContainer.appendChild(chatBubble);
    document.getElementById('user-input').value = ''; // Clear input field after sending
    chatContainer.scrollTop = chatContainer.scrollHeight; // Scroll to bottom of chat
}

function displayOptions(options) {
    var chatContainer = document.getElementById('chat-container');
    var optionsContainer = document.createElement('div');
    optionsContainer.classList.add('chat-bubble', 'robot');
    var optionsHtml = '<ul class="options-list">';
    options.forEach(option => {
        optionsHtml += `<li><button class="option-button" onclick="sendOption('${option}')">${option}</button></li>`;
    });
    optionsHtml += '</ul>';
    optionsContainer.innerHTML = optionsHtml;
    chatContainer.appendChild(optionsContainer);
    chatContainer.scrollTop = chatContainer.scrollHeight; // Scroll to bottom of chat
}

function sendOption(option) {
    appendChat("user", option);
    fetch('/process_chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'user_input=' + encodeURIComponent(option)
    })
    .then(response => response.json())
    .then(data => {
        if (data.response) {
            appendChat("robot", data.response);
        } else if (data.error) {
            appendChat("robot", "Error: " + data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}
