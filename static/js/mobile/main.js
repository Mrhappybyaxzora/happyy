const wsProtocol = window.location.protocol === "https:" ? "wss://" : "ws://";
const wsUrl = `${wsProtocol}${window.location.host}/c/ws`;
const socket = new WebSocket(wsUrl);


// When the connection is opened
socket.onopen = function(event) {
    console.log('WebSocket is connected:', event);
};

// When a message is received from the server
socket.onmessage = async function(event) {
    console.log('Message from server:', event.data);
    const data = JSON.parse(event.data);

    const allUrls = [
        ...data.wopens,
        ...data.plays,
        ...data.images,
        ...data.contents,
        ...data.googlesearches,
        ...data.youtubesearches,
    ];
    
    openUrlsInNewTabs(allUrls);

    console.log(data);
    console.log(allUrls);

    if (data.text) {
        addMessage(data.text, true);
    }
    if (data.cam === false) {
        stopVideo();
    }
    if (data.cam === true) {
        startVideo();
    }
    if (data.audiobase64) {
        try {
            await playAudio(data.audiobase64);
            releaseAllInputs();
            mayActiveSpeechRecognition();
        } catch (error) {
            console.error('Error playing audio:', error);
        }
    }
    else {
        releaseAllInputs();
        mayActiveSpeechRecognition();
    }
    
};

// When the WebSocket is closed
socket.onclose = function(event) {
    console.log('WebSocket is closed:', event);
    // Try to reconnect in 5 seconds
    setTimeout(() => {
        location.reload();
    }, 100);
};

// If there's an error with the connection
socket.onerror = function(error) {
    console.log('WebSocket error:', error);
};

function playAudio(base64Audio) {
    return new Promise((resolve, reject) => {
        const audio = new Audio();
        audio.src = `data:audio/mpeg;base64,${base64Audio}`;
        
        // When audio is ready to play
        audio.oncanplaythrough = () => {
            audio.play().then(() => {
                // Resolve the promise when the audio starts playing
                audio.onended = () => {
                    resolve(); // Resolve when playback ends
                };
            }).catch((error) => {
                reject(error); // Reject if playback fails
            });
        };

        // Handle errors
        audio.onerror = (error) => {
            reject(error);
        };
    });
}

function openUrlsInNewTabs(urls) {
    urls.forEach(url => {
        window.open(url, '_blank');
    });
}

addLoadingToMicButton = () => {
    const micIcon = document.getElementById('micIcon');
    const micLoader = document.getElementById('micLoader');
    micIcon.style.display = 'none';
    micLoader.style.display = 'block';
}
// after result
mayActiveSpeechRecognition = () => {
    const hasActiveClass = micBtn.classList.contains('active');
    if (hasActiveClass) {
        try {
            listeningIndicator.textContent = "Listening ...";
            recognition.start();
        } catch (e) {
            console.log(e);
        }
    }
}


blockAllInputs = () => {
    try {
        recognition.stop();
    } catch (e) {
        console.log(e);
    }
}


releaseAllInputs = () => {
    micIcon.style.display = 'block';
    micLoader.style.display = 'none';
}


/**
 * @param {string} q - The query string to process.
 * @returns {void} - This function does not return anything.
 */
QuerySendMain = (q) => {
    blockAllInputs();
    addLoadingToMicButton();
    addMessage(q, false);
    
    payload = {
        prompt : q
    }
    if (isCameraOn){
        payload['imgbase64'] = capture();
    }
    socket.send(JSON.stringify(payload));
    setTimeout(() => {
        listeningIndicator.textContent = "Working on it ...";
    },500);
    
}