// Function to add a user message to the chat
function addUserMessageFromInput() {
    const userInput = document.getElementById('user-input');

    const message = userInput.value.trim();
    if (message !== "") {
        userInput.value = "";
        QuerySendMain(message);
    }
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;")
        .replace(/\n/g, "<br>")        // Converts newlines to <br> tags
        .replace(/ /g, "&nbsp;");     // Converts spaces to non-breaking spaces
}

// Function to modify query formatting
function queryModifier(query) {
    // Convert to lowercase and trim whitespace
    let newQuery = query.toLowerCase().trim();
    let queryWords = newQuery.split(' ');
    
    // List of question words to check for
    const questionWords = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"];
    
    // Check if query contains any question words
    const isQuestion = questionWords.some(word => newQuery.includes(word + " "));
    
    // Get last character of last word
    const lastChar = queryWords[queryWords.length - 1].slice(-1);
    
    // Remove existing punctuation if present
    if (['.', '?', '!'].includes(lastChar)) {
        newQuery = newQuery.slice(0, -1);
    }
    
    // Add appropriate punctuation
    newQuery += isQuestion ? '?' : '.';
    
    // Capitalize first letter and return
    return newQuery.charAt(0).toUpperCase() + newQuery.slice(1);
}

addMessage = (message, ai = false) => {
    const userMessage = document.createElement('p');
    userMessage.classList.add('text-[20px]', 'break-all');
    const identifier = document.createElement('b')
    if (ai) {
        identifier.classList.add('text-[#68B2D9]', 'text-[20px]');
        identifier.innerHTML = `Happy`;
    } else {
        identifier.classList.add('text-[#5FC7A2]', 'text-[20px]');
        identifier.innerHTML = `${USERNAME}`;
    }
    userMessage.innerHTML += identifier.outerHTML;
    userMessage.innerHTML += `<span style="color: white;">:</span> ${escapeHtml(queryModifier(message))}`;
    const chatContent = document.getElementById('chat-content');

    chatContent.appendChild(userMessage);
    chatContent.scrollTop = chatContent.scrollHeight;
    
}



// Add event listener for send button click
document.getElementById('sendBtn').addEventListener('click', addUserMessageFromInput);

// Optionally handle 'Enter' key to send message
document.getElementById('user-input').addEventListener('keydown', function (e) {
    if (e.key === 'Enter') {
        addUserMessageFromInput();
    }
});
// addMessage("Hello, how are you?", true)