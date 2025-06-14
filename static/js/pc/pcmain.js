const wsProtocol = window.location.protocol === "https:" ? "wss://" : "ws://";
const wsUrl = `${wsProtocol}${window.location.host}/c/ws`;
blockAllInputs = () => {
    sendBtn.disabled = true;
    sendBtn.style.cursor = 'not-allowed';
    sendBtn.style.opacity = '0.5';
    userInput.disabled = true;
    userInput.style.opacity = '0.5';
    try {
        recognition.stop();
    } catch (e) {
        console.log(e);
    }
}
document.addEventListener('DOMContentLoaded', () => {
    blockAllInputs();
    micIcon.style.display = 'none';
    micLoader.style.display = 'block';
});

const socket = new WebSocket(wsUrl);
let closeFlag = false;

// When the connection is opened

socket.onopen = function(event) {
    console.log('WebSocket is connected:', event);
    releaseAllInputs();
    mayActiveSpeechRecognition();
};
function updateRecognitionLanguage() {
    const languageSelect = document.querySelector('select[name="InputLanguage"]');
    if (recognition && languageSelect) {
        recognition.lang = languageSelect.value;
        console.log("Speech recognition language updated to:", recognition.lang);
    }
}
// When a message is received from the server
socket.onmessage = async function(event) {
    console.log('Message from server:', event.data);
    const data = JSON.parse(event.data);
    if (data.user){
        for (const [key, value] of Object.entries(data.user)) {
            try {
                const element = document.querySelector(`[name="${key}"]`);
                if (element) {
                    element.value = value;
                }
            } catch (e) {
                console.log(e);
            }
        }
        updateRecognitionLanguage();
        return;
    }
    
    const allUrls = [
        ...data.wopens,
        ...data.plays,
        ...data.images,
        ...data.contents,
        ...data.googlesearches,
        ...data.youtubesearches
    ];
    
    openUrlsInNewTabs(allUrls);

    console.log(data);
    console.log(allUrls);
    console.log(data.cam);

    if (data.text) {
        addMessage(data.text, true);
    }
    if (data.cam === false) {
        stopVideo();
    }
    if (data.cam === true) {
        startVideo();
    }
    if (typeof data.cam == "string") {
        console.log("is string");
        if (!isCameraOn){
            startVideo();
            for (let i = 0; i < 30; i++) {
                if (isCameraOn) {
                    break;
                }
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }
        closeFlag = true;
        payload = {
            doNotSave: true,
            prompt : "TTCAMTOKENTT"+data.cam,
            imgbase64: capture()
        }
        socket.send(JSON.stringify(payload));
        return;
    }
    if (data.audiobase64) {
        try {
            await playAudio(data.audiobase64);
            if (closeFlag) {
                stopVideo();
                closeFlag = false;
            }
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
};

// If there's an error with the connection
socket.onerror = function(error) {
    console.log('WebSocket error:', error);
};


function openUrlsInNewTabs(urls) {
    urls.forEach(url => {
        window.open(url, '_blank');
    });
}

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





releaseAllInputs = () => {
    if (!isActive) {
        sendBtn.disabled = false;
        sendBtn.style.cursor = 'pointer';
        sendBtn.style.opacity = '1';
        userInput.disabled = false;
        userInput.style.opacity = '1';
    }
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
    payload = {
        prompt : q
    }
    if (q === "[User is inactive]") {
    }
    else {
        addMessage(q, false);
    }
    
    if (isCameraOn){
        payload['imgbase64'] = capture();
    }
    const files = Array.from(fileUrls.values()).map(fileData => ({
                url: fileData.url,
                mime_type: fileData.mime_type
            }));
    payload['files'] = files;
    console.log(JSON.stringify(payload));
    socket.send(JSON.stringify(payload));

    setTimeout(() => {
        listeningIndicator.textContent = "Working on it ...";
    },500);
}