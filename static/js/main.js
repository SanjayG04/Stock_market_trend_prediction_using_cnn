// Form validation
document.addEventListener('DOMContentLoaded', function() {
    
    // Password match validation for registration
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;
            
            if (password !== confirmPassword) {
                e.preventDefault();
                alert('Passwords do not match!');
                return false;
            }
            
            if (password.length < 6) {
                e.preventDefault();
                alert('Password must be at least 6 characters long!');
                return false;
            }
        });
    }
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Confirm delete actions
    const deleteForms = document.querySelectorAll('form[action*="delete"]');
    deleteForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to delete this analysis?')) {
                e.preventDefault();
                return false;
            }
        });
    });
    
});

// File size validation
function validateFileSize(input) {
    const file = input.files[0];
    const maxSize = 16 * 1024 * 1024; // 16MB
    
    if (file && file.size > maxSize) {
        alert('File size must be less than 16MB!');
        input.value = '';
        return false;
    }
    return true;
}
