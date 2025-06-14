let videoStream;
let isCameraOn = false; // Flag to track the camera status

function startVideo() {
    const video = document.querySelector('video');

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function (stream) {
            video.srcObject = stream;
            videoStream = stream;
            isCameraOn = true; // Camera is now on
            console.log('Camera is on');
        })
        .catch(function (err) {
            console.error('Error accessing the camera: ', err);
        });
}

function stopVideo() {
    const video = document.querySelector('video');
    if (videoStream) {
        const tracks = videoStream.getTracks();
        tracks.forEach(track => track.stop());
        videoStream = null;
    }
    video.srcObject = null; // Ensure no stream is being set
    video.src = `${window.location.origin}/static/video/video.mp4`;
    isCameraOn = false; // Camera is now off
    console.log('Camera is off');
}

function capture() {
    const video = document.querySelector('video');
    if (!isCameraOn) {
        console.warn('Camera is off, cannot capture.');
        return null; // or handle the case when the camera is off
    }
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    const base64Image = canvas.toDataURL('image/png');
    return base64Image;
}

function isCameraActive() {
    // Check if video stream is active
    if (videoStream && videoStream.getVideoTracks().length > 0) {
        const track = videoStream.getVideoTracks()[0];
        return track.readyState === 'live'; // 'live' indicates the camera is active
    }
    return false;
}

