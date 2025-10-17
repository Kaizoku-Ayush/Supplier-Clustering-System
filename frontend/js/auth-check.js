// Authentication Check - Include in all protected pages

(function() {
    // Check if user is authenticated
    if (!isAuthenticated()) {
        // Redirect to login page
        window.location.href = '../login.html';
        return;
    }
    
    // Set user info in navbar if it exists
    const userName = localStorage.getItem('userName');
    const userEmail = localStorage.getItem('userEmail');
    
    if (userName) {
        const userNameElement = document.querySelector('.user-name');
        if (userNameElement) {
            userNameElement.textContent = userName;
        }
        
        // Set initials in avatar
        const userAvatar = document.querySelector('.user-avatar');
        if (userAvatar) {
            const initials = userName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
            userAvatar.textContent = initials;
        }
    }
    
    // Add logout functionality
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (confirm('Are you sure you want to logout?')) {
                AuthAPI.logout();
                window.location.href = '../login.html';
            }
        });
    }
})();
