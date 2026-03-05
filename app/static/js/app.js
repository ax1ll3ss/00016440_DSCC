// Anonymous Confessions - App JavaScript

document.addEventListener('DOMContentLoaded', () => {
    // Apply animation delays from data-delay attribute
    document.querySelectorAll('[data-delay]').forEach(el => {
        const delay = parseInt(el.dataset.delay, 10) * 100;
        el.style.animationDelay = delay + 'ms';
    });

    // Apply progress bar widths from data-width attribute
    document.querySelectorAll('[data-width]').forEach(el => {
        el.style.width = el.dataset.width + '%';
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // AJAX reaction toggle
    const reactionBtns = document.querySelectorAll('.reaction-btn');
    reactionBtns.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const url = btn.getAttribute('href');

            try {
                const response = await fetch(url, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                });

                if (response.ok) {
                    const data = await response.json();
                    const countEl = btn.querySelector('.reaction-count');
                    if (countEl) {
                        countEl.textContent = data.count;
                    }
                    btn.classList.toggle('active', data.action === 'added');

                    // Add bounce animation
                    btn.style.transform = 'scale(1.2)';
                    setTimeout(() => {
                        btn.style.transform = '';
                    }, 200);
                }
            } catch (err) {
                // Fallback to regular navigation
                window.location.href = url;
            }
        });
    });

    // Intersection Observer for scroll animations
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animationPlayState = 'running';
                }
            });
        },
        { threshold: 0.1 }
    );

    document.querySelectorAll('.slide-up').forEach(el => {
        el.style.animationPlayState = 'paused';
        observer.observe(el);
    });
});

// Get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
