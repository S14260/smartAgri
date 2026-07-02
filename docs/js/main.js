/* ============================================
   智慧农业监测平台 · Portfolio JS
   ============================================ */

(function () {
  'use strict';

  /* ---------- Scroll Animations ---------- */
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    },
    { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
  );

  document.querySelectorAll('.fade-in').forEach((el) => observer.observe(el));

  /* ---------- Nav Scroll ---------- */
  const nav = document.querySelector('.nav');
  let lastScroll = 0;

  window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;
    nav.classList.toggle('scrolled', scrollY > 50);
    lastScroll = scrollY;
  }, { passive: true });

  /* ---------- Mobile Nav Toggle ---------- */
  const mobileBtn = document.querySelector('.nav-mobile-btn');
  const navLinks = document.querySelector('.nav-links');

  if (mobileBtn && navLinks) {
    mobileBtn.addEventListener('click', () => {
      navLinks.classList.toggle('open');
    });
  }

  /* ---------- Smooth Scroll for Nav Links ---------- */
  document.querySelectorAll('.nav-links a[href^="#"]').forEach((link) => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const target = document.querySelector(link.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        navLinks && navLinks.classList.remove('open');
      }
    });
  });

  /* ---------- Active Nav Link on Scroll ---------- */
  const sectionNavMap = {};
  document.querySelectorAll('.nav-links a[href^="#"]').forEach((link) => {
    const id = link.getAttribute('href').slice(1);
    if (id) sectionNavMap[id] = link;
  });

  const sectionIds = Object.keys(sectionNavMap);
  if (sectionIds.length) {
    const activeObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            document.querySelectorAll('.nav-links a.active').forEach((el) => el.classList.remove('active'));
            const link = sectionNavMap[entry.target.id];
            if (link) link.classList.add('active');
          }
        });
      },
      { rootMargin: '-20% 0px -60% 0px' }
    );
    sectionIds.forEach((id) => {
      const el = document.getElementById(id);
      if (el) activeObserver.observe(el);
    });
  }

  /* ---------- Number Counter ---------- */
  function animateCounter(el) {
    const target = parseInt(el.getAttribute('data-count'), 10);
    const suffix = el.getAttribute('data-suffix') || '';
    const duration = 1600;
    const start = performance.now();

    function update(now) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(eased * target);
      el.textContent = current.toLocaleString() + suffix;
      if (progress < 1) requestAnimationFrame(update);
    }

    requestAnimationFrame(update);
  }

  const counterObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting && !entry.target.dataset.counted) {
          entry.target.dataset.counted = 'true';
          animateCounter(entry.target);
        }
      });
    },
    { threshold: 0.5 }
  );

  document.querySelectorAll('[data-count]').forEach((el) => counterObserver.observe(el));

  /* ---------- Lightbox ---------- */
  const lightbox = document.getElementById('lightbox');
  const lightboxImg = lightbox ? lightbox.querySelector('img') : null;

  document.querySelectorAll('[data-lightbox]').forEach((el) => {
    el.style.cursor = 'pointer';
    el.addEventListener('click', () => {
      if (lightbox && lightboxImg) {
        lightboxImg.src = el.src || el.getAttribute('data-lightbox');
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
      }
    });
  });

  if (lightbox) {
    lightbox.addEventListener('click', () => {
      lightbox.classList.remove('active');
      document.body.style.overflow = '';
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && lightbox && lightbox.classList.contains('active')) {
      lightbox.classList.remove('active');
      document.body.style.overflow = '';
    }
  });

  /* ---------- Screenshots Carousel Auto-scroll ---------- */
  const carousel = document.querySelector('.screenshots-carousel');
  if (carousel) {
    let scrollDir = 1;
    let autoScrollTimer;

    function autoScroll() {
      const maxScroll = carousel.scrollWidth - carousel.clientWidth;
      if (maxScroll <= 0) return;

      carousel.scrollLeft += scrollDir * 1;
      if (carousel.scrollLeft >= maxScroll) scrollDir = -1;
      if (carousel.scrollLeft <= 0) scrollDir = 1;
    }

    function startAutoScroll() {
      autoScrollTimer = setInterval(autoScroll, 30);
    }

    function stopAutoScroll() {
      clearInterval(autoScrollTimer);
    }

    startAutoScroll();
    carousel.addEventListener('mouseenter', stopAutoScroll);
    carousel.addEventListener('mouseleave', startAutoScroll);
    carousel.addEventListener('touchstart', stopAutoScroll, { passive: true });
    carousel.addEventListener('touchend', startAutoScroll, { passive: true });
  }

  /* ---------- Bento Mini Chart Bar Heights ---------- */
  document.querySelectorAll('.mini-chart').forEach((chart) => {
    const bars = chart.querySelectorAll('.mini-chart-bar');
    bars.forEach((bar) => {
      const h = bar.getAttribute('data-height');
      if (h) bar.style.height = h + 'px';
    });
  });

  /* ---------- AI Chat Simulation ---------- */
  const chatMessages = document.getElementById('chat-messages');
  const chatTrigger = document.getElementById('chat-trigger');

  const chatSequence = [
    { type: 'user', text: '帮我看看3号地块有没有异常？' },
    { type: 'thinking', text: '分析意图中' },
    { type: 'tool-call', name: 'query_plots', args: '{ "plot_id": 3 }' },
    { type: 'tool-result', text: '地块：3号地 · 小麦 · 12.5亩' },
    { type: 'tool-call', name: 'trigger_anomaly_detection', args: '{ "plot_id": 3 }' },
    { type: 'tool-result', text: '检测完成 · 发现2处异常区域' },
    { type: 'assistant', text: '3号地块检测到 **2处异常**：\n\n1. **西南角** — NDVI 持续下降，疑似干旱胁迫\n2. **东侧边界** — NDWI 升高，可能积水\n\n建议优先巡田西南区域，是否生成巡田路线？' },
  ];

  let chatPlaying = false;

  function addMessage(msg) {
    const div = document.createElement('div');

    if (msg.type === 'user') {
      div.className = 'ai-message user';
      div.textContent = msg.text;
    } else if (msg.type === 'assistant') {
      div.className = 'ai-message assistant';
      div.innerHTML = msg.text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
    } else if (msg.type === 'thinking') {
      div.className = 'ai-message-thinking';
      div.innerHTML = '<span>🤔</span> ' + msg.text + '<span class="dots"><span></span><span></span><span></span></span>';
    } else if (msg.type === 'tool-call') {
      div.className = 'ai-tool-call';
      div.innerHTML = '<div class="ai-tool-call-header">⚡ 调用工具</div><div class="ai-tool-call-name">' + msg.name + '</div><div style="color:var(--text-tertiary);margin-top:4px;font-size:11px">' + msg.args + '</div>';
    } else if (msg.type === 'tool-result') {
      div.className = 'ai-tool-call';
      div.innerHTML = '<div class="ai-tool-call-header" style="color:var(--green)">✓ 工具结果</div><div class="ai-tool-call-result">' + msg.text + '</div>';
    }

    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return div;
  }

  async function playChat() {
    if (chatPlaying) return;
    chatPlaying = true;
    chatMessages.innerHTML = '';

    for (const msg of chatSequence) {
      await new Promise((r) => setTimeout(r, msg.type === 'thinking' ? 800 : 500));
      addMessage(msg);
    }

    chatPlaying = false;
  }

  if (chatTrigger) {
    chatTrigger.addEventListener('click', playChat);
  }

  // Auto-play when section is visible
  const chatSection = document.getElementById('ai-section');
  if (chatSection) {
    const chatObserver = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !chatSection.dataset.played) {
          chatSection.dataset.played = 'true';
          setTimeout(playChat, 600);
        }
      },
      { threshold: 0.3 }
    );
    chatObserver.observe(chatSection);
  }

})();
