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
const chatContent = document.getElementById('chat-container');

addMessage = (message, ai = false) => {
    const userMessage = document.createElement('p');
    userMessage.classList.add('break-all');
    if (ai) {
        userMessage.classList.add('bot-text');
        userMessage.innerHTML = `Happy<span style="color: white;">:</span> `;
    } else {
        userMessage.classList.add('user-text');
        userMessage.innerHTML = `${USERNAME}<span style="color: white;">:</span> `;
    }
    userMessage.innerHTML += escapeHtml(queryModifier(message));

    chatContent.appendChild(userMessage);
    chatContent.scrollTop = chatContent.scrollHeight;
}