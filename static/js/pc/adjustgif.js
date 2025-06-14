 // Function to set fixed height for the main layout
 function fixLayoutHeight() {
    const mainLayout = document.getElementById('main-layout');
    const windowHeight = window.innerHeight;
    const headerHeight = 150; // Adjust according to your header size (30px top + header)
    const inputHeight = 100;  // Approximate height for input section at the bottom
    const fixedHeight = windowHeight - (headerHeight + inputHeight);

    mainLayout.style.height = `${fixedHeight}px`;
}

// Function to add the video after height is set
function addVideo() {
    const videoContainer = document.querySelector('.video-container');
    const videoElement = document.createElement('video');
    videoElement.src = `${window.location.origin}/static/video/video.mp4`; // Add your video source
    videoElement.classList.add('w-full', 'h-auto', 'max-h-full');
    videoElement.autoplay = true;
    videoElement.loop = true;
    videoContainer.innerHTML = ''; // Clear any existing video
    videoContainer.appendChild(videoElement);
}

// Event listener to handle window resize and UI adjustment
window.addEventListener('resize', () => {
    const videoContainer = document.querySelector('.video-container');
    videoContainer.innerHTML = ''; // Remove video during resize
    fixLayoutHeight(); // Fix height again
    setTimeout(addVideo, 1); // Add video back after a short delay
});

// Initialize layout and add video after page load
window.addEventListener('load', () => {
    fixLayoutHeight();
    addVideo();
});