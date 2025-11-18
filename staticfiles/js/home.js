
    // Particle Animation System
    const canvas = document.getElementById('particles-canvas');
    const ctx = canvas.getContext('2d');

    function resizeCanvas() {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    }
    resizeCanvas();

    const particles = [];
    const particleCount = 100;

    class Particle {
      constructor() {
        this.reset();
      }

      reset() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.size = Math.random() * 3 + 1;
        this.speedX = Math.random() * 2 - 1;
        this.speedY = Math.random() * 2 - 1;
        this.opacity = Math.random() * 0.5 + 0.2;
      }

      update() {
        this.x += this.speedX;
        this.y += this.speedY;

        if (this.x > canvas.width) this.x = 0;
        if (this.x < 0) this.x = canvas.width;
        if (this.y > canvas.height) this.y = 0;
        if (this.y < 0) this.y = canvas.height;
      }

      draw() {
        ctx.fillStyle = `rgba(255, 255, 255, ${this.opacity})`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    function initParticles() {
      particles.length = 0;
      for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
      }
    }

    function animateParticles() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particles.forEach(particle => {
        particle.update();
        particle.draw();
      });

      particles.forEach((a, i) => {
        particles.slice(i + 1).forEach(b => {
          const dx = a.x - b.x;
          const dy = a.y - b.y;
          const distance = Math.sqrt(dx * dx + dy * dy);

          if (distance < 120) {
            ctx.strokeStyle = `rgba(255, 255, 255, ${0.15 * (1 - distance / 120)})`;
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
          }
        });
      });

      requestAnimationFrame(animateParticles);
    }

    initParticles();
    animateParticles();

    window.addEventListener('resize', () => {
      resizeCanvas();
      initParticles();
    });

    // AI Chatbot Functionality
    const aiChatBtn = document.getElementById('aiChatBtn');
    const aiChatWindow = document.getElementById('aiChatWindow');
    const closeChat = document.getElementById('closeChat');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatMessages = document.getElementById('chatMessages');

    const responses = {
      'hello': 'Hello! How can I assist you with your learning journey today?',
      'hi': 'Hi there! What would you like to know about our courses?',
      'hey': 'Hey! How can I help you explore our educational programs?',
      'courses': 'We offer Python Full Stack, Data Science, AI & Machine Learning, Cybersecurity, Cloud Computing, and Mobile App Development. Which interests you?',
      'python': 'Our Python Full Stack course covers HTML, CSS, JavaScript, Python, Django, MySQL, and REST APIs. Perfect for becoming a full-stack developer! Would you like enrollment details?',
      'data science': 'Data Science course includes Python programming, statistics, machine learning, and data visualization. Great for analytical minds! Interested in learning more?',
      'data': 'Data Science course includes Python programming, statistics, machine learning, and data visualization. Great for analytical minds! Interested in learning more?',
      'ai': 'Our AI & Machine Learning course teaches neural networks, deep learning, and building intelligent systems. The future is here! Want to know more?',
      'machine learning': 'Our AI & Machine Learning course teaches neural networks, deep learning, and building intelligent systems. The future is here! Want to know more?',
      'cyber': 'Cybersecurity covers ethical hacking, cryptography, network security, and risk management. Protect the digital world! Shall I provide enrollment details?',
      'security': 'Cybersecurity covers ethical hacking, cryptography, network security, and risk management. Protect the digital world! Shall I provide enrollment details?',
      'cloud': 'Cloud Computing course includes AWS, Azure, Docker, Kubernetes, and DevOps practices. Build scalable solutions! Want to know more?',
      'aws': 'We offer comprehensive AWS training covering EC2, S3, Lambda, RDS, and more. Part of our Cloud Computing course. Interested?',
      'mobile': 'Mobile App Development teaches Flutter and React Native for creating cross-platform apps. Go mobile! Want enrollment information?',
      'price': 'For detailed pricing and enrollment information, please contact us at +91 90470 20807 or email info@xploreitcorp.com. We offer flexible payment options!',
      'cost': 'For detailed pricing and enrollment information, please contact us at +91 90470 20807 or email info@xploreitcorp.com. We offer flexible payment options!',
      'fee': 'For detailed pricing and enrollment information, please contact us at +91 90470 20807 or email info@xploreitcorp.com. We offer flexible payment options!',
      'duration': 'Course durations vary from 3-6 months depending on the program. We offer flexible schedules including weekend and evening batches!',
      'time': 'Course durations vary from 3-6 months depending on the program. We offer flexible schedules including weekend and evening batches!',
      'contact': 'You can reach us at +91 90470 20807 or +91 90470 10807, or email info@xploreitcorp.com. We\'re here to help!',
      'location': 'We are located at No 18, 2nd Floor, Rani Complex, Kalingarayan Street, Ramnagar, Behind Central Bus Stand, Coimbatore, Tamil Nadu - 641 009. Easy to reach!',
      'address': 'We are located at No 18, 2nd Floor, Rani Complex, Kalingarayan Street, Ramnagar, Behind Central Bus Stand, Coimbatore, Tamil Nadu - 641 009. Easy to reach!',
      'help': 'I can help you with course information, enrollment details, pricing, schedules, and career guidance. What would you like to know?',
      'career': 'We provide placement assistance and career guidance. Our courses are designed to make you job-ready with real-world projects! Which career path interests you?',
      'job': 'We provide placement assistance and career guidance. Our courses are designed to make you job-ready with real-world projects! Which career path interests you?',
      'placement': 'Yes! We offer placement assistance to help you land your dream tech job. Our courses include interview preparation and resume building. Interested?',
      'java': 'While Java Full Stack is listed in our courses menu, I recommend contacting us for current batch schedules. Call +91 90470 20807 for details!',
      'thank': 'You\'re welcome! Feel free to ask if you have more questions. Happy to help! 😊',
      'bye': 'Goodbye! Feel free to chat anytime you need help. Best wishes on your learning journey! 👋'
    };

    aiChatBtn.addEventListener('click', () => {
      aiChatWindow.classList.add('active');
      chatInput.focus();
    });

    closeChat.addEventListener('click', () => {
      aiChatWindow.classList.remove('active');
    });

    function addMessage(content, isUser = false) {
      const messageDiv = document.createElement('div');
      messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;

      if (!isUser) {
        messageDiv.innerHTML = `
          <div class="bot-avatar" aria-hidden="true">
            <i class="fas fa-robot"></i>
          </div>
          <div class="message-content">${content}</div>
        `;
      } else {
        messageDiv.innerHTML = `
          <div class="message-content">${content}</div>
        `;
      }

      chatMessages.appendChild(messageDiv);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function getBotResponse(userMessage) {
      const message = userMessage.toLowerCase().trim();

      for (let key in responses) {
        if (message.includes(key)) {
          return responses[key];
        }
      }

      return "I'm here to help! You can ask me about our courses (Python, Data Science, AI, Cloud, Cybersecurity, Mobile), pricing, duration, contact details, or career opportunities. What would you like to know?";
    }

    function sendMessage() {
      const message = chatInput.value.trim();
      if (message === '') return;

      addMessage(message, true);
      chatInput.value = '';

      setTimeout(() => {
        const response = getBotResponse(message);
        addMessage(response);
      }, 600);
    }

    sendBtn.addEventListener('click', sendMessage);

    chatInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        sendMessage();
      }
    });

    // Mobile menu toggle
    const mobileToggle = document.getElementById('mobileToggle');
    const navMenu = document.getElementById('navMenu');

    mobileToggle.addEventListener('click', function(e) {
      e.stopPropagation();
      this.classList.toggle('active');
      navMenu.classList.toggle('active');
    });

    document.addEventListener('click', function(event) {
      if (!event.target.closest('.navbar-container')) {
        mobileToggle.classList.remove('active');
        navMenu.classList.remove('active');
      }
    });

    // Navbar scroll effect
    let lastScroll = 0;
    window.addEventListener('scroll', function() {
      const navbar = document.getElementById('navbar');
      const currentScroll = window.pageYOffset;
      
      if (currentScroll > 50) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
      
      lastScroll = currentScroll;
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href !== '#' && document.querySelector(href)) {
          e.preventDefault();
          const target = document.querySelector(href);
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });

    // Card animation observer
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.animation = 'fadeInUp 0.8s ease forwards';
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);

    document.querySelectorAll('.card').forEach(card => {
      card.style.opacity = '0';
      observer.observe(card);
    });

    // Keyboard accessibility for chatbot
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && aiChatWindow.classList.contains('active')) {
        aiChatWindow.classList.remove('active');
      }
    });
