const micBtn = document.getElementById('micBtn');
const circles = document.querySelectorAll('.circle');
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