// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss flash messages after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        });
    }, 5000);
});
