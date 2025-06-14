const micBtn = document.getElementById('micBtn');
const circles = document.querySelectorAll('.circle');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('sendBtn');
let isActive = false;

function setCircleAnimation(circle, delay, animation) {
    circle.style.animation = `${animation} 4s infinite cubic-bezier(.36, .11, .89, .32)`;
    circle.style.animationDelay = `${delay}s`;
}

function startAnimation() {
    circles.forEach((circle, index) => {
        setCircleAnimation(circle, index - 1, 'scaleOut');
    });
}

function reverseAnimation() {
    circles.forEach((circle, index) => {
        setCircleAnimation(circle, (3 - index) * 0.20, 'scaleIn');
    });
}

function stopAnimation() {
    circles.forEach(circle => {
        circle.style.animation = 'none';
    });
}

micBtn.addEventListener('click', () => {
    isActive = !isActive;
    micBtn.classList.toggle('active', isActive);

    if (isActive) {
        sendBtn.disabled = true;
        sendBtn.style.cursor = 'not-allowed';
        sendBtn.style.opacity = '0.5';
        userInput.disabled = true;
        userInput.style.opacity = '0.5';
    }
    else {
        const micIcon = document.getElementById('micIcon');
        if (micIcon.style.display != 'none') {
            sendBtn.disabled = false;
            sendBtn.style.cursor = 'pointer';
            sendBtn.style.opacity = '1';
            userInput.disabled = false;
            userInput.style.opacity = '1';
        }
    }
    if (isActive) {
        startAnimation();
    } else {
        reverseAnimation();
        setTimeout(() => {
            if (!isActive) {
                stopAnimation();
            }
        }, 1000);
    }
});