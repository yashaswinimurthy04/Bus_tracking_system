// BusTrack Cinematic Animation Engine
(function () {
  const cursor = document.getElementById('cursor');
  const aura = document.getElementById('aura');
  const canvas = document.getElementById('particle-field');
  const hudTime = document.getElementById('hud-time');

  let mouseX = window.innerWidth / 2;
  let mouseY = window.innerHeight / 2;
  let cursorX = mouseX, cursorY = mouseY;
  let auraX = mouseX, auraY = mouseY;

  document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  });

  // --- EXTREME PARTICLE FLOW FIELD ---
  if (canvas) {
    const ctx = canvas.getContext('2d');
    let particles = [];
    const particleCount = 400;

    class Particle {
      constructor() {
        this.init();
      }
      init() {
        this.x = Math.random() * window.innerWidth;
        this.y = Math.random() * window.innerHeight;
        this.vx = (Math.random() - 0.5) * 1;
        this.vy = (Math.random() - 0.5) * 1;
        this.size = Math.random() * 2 + 0.5;
        this.color = Math.random() > 0.5 ? 'rgba(0, 242, 255, 0.4)' : 'rgba(189, 0, 255, 0.4)';
        this.history = [];
      }
      update() {
        const dx = mouseX - this.x;
        const dy = mouseY - this.y;
        const dist = Math.hypot(dx, dy);

        // Swirl around mouse
        if (dist < 300) {
          const force = (300 - dist) / 300;
          this.vx += (dy / dist) * force * 0.5;
          this.vy -= (dx / dist) * force * 0.5;

          // Slight attraction
          this.vx += (dx / dist) * force * 0.1;
          this.vy += (dy / dist) * force * 0.1;
        }

        this.x += this.vx;
        this.y += this.vy;

        // Friction
        this.vx *= 0.98;
        this.vy *= 0.98;

        // Boundary bounce
        if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
        if (this.y < 0 || this.y > canvas.height) this.vy *= -1;

        // Trail history
        this.history.push({ x: this.x, y: this.y });
        if (this.history.length > 10) this.history.shift();
      }
      draw() {
        ctx.strokeStyle = this.color;
        ctx.lineWidth = this.size;
        ctx.beginPath();
        if (this.history.length > 0) {
          ctx.moveTo(this.history[0].x, this.history[0].y);
          for (let i = 1; i < this.history.length; i++) {
            ctx.lineTo(this.history[i].x, this.history[i].y);
          }
        }
        ctx.stroke();
      }
    }

    function resize() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      particles = [];
      for (let i = 0; i < particleCount; i++) particles.push(new Particle());
    }

    function render() {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.15)'; // Motion blur effect
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      particles.forEach(p => {
        p.update();
        p.draw();
      });
      requestAnimationFrame(render);
    }

    resize();
    window.addEventListener('resize', resize);
    render();
  }

  // --- INTERACTION LOOP ---
  function updateLoop() {
    cursorX = mouseX - 30;
    cursorY = mouseY - 30;

    auraX += (mouseX - auraX) * 0.1;
    auraY += (mouseY - auraY) * 0.1;

    if (cursor) cursor.style.transform = `translate(${cursorX}px, ${cursorY}px)`;
    if (aura) aura.style.transform = `translate(${auraX}px, ${auraY}px) translate(-50%, -50%)`;

    if (hudTime) {
      hudTime.innerText = new Date().toTimeString().split(' ')[0];
    }

    requestAnimationFrame(updateLoop);
  }
  updateLoop();

  // --- MAGNETIC BUTTONS ---
  document.querySelectorAll('.magnetic-btn').forEach(btn => {
    btn.addEventListener('mousemove', (e) => {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      btn.style.transform = `translate(${x * 0.4}px, ${y * 0.4}px) scale(1.1)`;
    });
    btn.addEventListener('mouseleave', () => {
      btn.style.transform = 'translate(0, 0) scale(1)';
    });
  });
})();
