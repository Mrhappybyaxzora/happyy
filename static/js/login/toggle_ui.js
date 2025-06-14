const loginTab = document.getElementById('loginTab');
const signupTab = document.getElementById('signupTab');
const loginForm = document.getElementById('loginForm');
const signupForm = document.getElementById('signupForm');
const forgotPasswordForm = document.getElementById('forgotPasswordForm');
const forgotPasswordLink = document.getElementById('forgotPasswordLink');
const backToLoginLink = document.getElementById('backToLoginLink');

loginTab.addEventListener('click', () => {
    loginTab.classList.add('bg-primary', 'text-white');
    loginTab.classList.remove('bg-gray-700', 'text-gray-300');
    signupTab.classList.add('bg-gray-700', 'text-gray-300');
    signupTab.classList.remove('bg-primary', 'text-white');
    loginForm.classList.remove('hidden');
    signupForm.classList.add('hidden');
    forgotPasswordForm.classList.add('hidden');
});

signupTab.addEventListener('click', () => {
    signupTab.classList.add('bg-primary', 'text-white');
    signupTab.classList.remove('bg-gray-700', 'text-gray-300');
    loginTab.classList.add('bg-gray-700', 'text-gray-300');
    loginTab.classList.remove('bg-primary', 'text-white');
    signupForm.classList.remove('hidden');
    loginForm.classList.add('hidden');
    forgotPasswordForm.classList.add('hidden');
});

forgotPasswordLink.addEventListener('click', (e) => {
    e.preventDefault();
    loginForm.classList.add('hidden');
    signupForm.classList.add('hidden');
    forgotPasswordForm.classList.remove('hidden');
});

backToLoginLink.addEventListener('click', (e) => {
    e.preventDefault();
    loginForm.classList.remove('hidden');
    signupForm.classList.add('hidden');
    forgotPasswordForm.classList.add('hidden');
});
