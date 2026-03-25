// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// FAQ accordion
document.querySelectorAll('.faq-q').forEach(q => {
  q.addEventListener('click', function() {
    const item = this.closest('.faq-item');
    const answer = item.querySelector('.faq-a');
    const isOpen = item.classList.contains('open');

    // Close all
    document.querySelectorAll('.faq-item').forEach(i => {
      i.classList.remove('open');
      i.querySelector('.faq-a').style.display = 'none';
    });

    // Open clicked if was closed
    if (!isOpen) {
      item.classList.add('open');
      answer.style.display = 'block';
    }
  });
});

// Init FAQ - hide all answers
document.querySelectorAll('.faq-a').forEach(a => {
  a.style.display = 'none';
});

// Navbar scroll effect
window.addEventListener('scroll', function() {
  const navbar = document.querySelector('.navbar');
  if (navbar && !navbar.classList.contains('navbar-light')) {
    if (window.scrollY > 50) {
      navbar.style.background = 'rgba(61, 31, 13, 0.98)';
    } else {
      navbar.style.background = 'rgba(61, 31, 13, 0.95)';
    }
  }
});

// Animate stats on scroll
const observerOptions = {
  threshold: 0.5,
  rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('animate-in');
    }
  });
}, observerOptions);

document.querySelectorAll('.step-card, .feature-card, .pricing-card').forEach(el => {
  observer.observe(el);
});
