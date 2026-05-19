/**
 * main.js — Complex SW СУСТАВЫ Landing Page
 * ============================================================
 * Модули:
 *   1. fadeIn       — анимация появления элементов при скролле
 *   2. ageBars      — анимация прогресс-баров (возраст)
 *   3. mobileNav    — бургер-меню для мобильных
 *   4. navHighlight — подсветка активного пункта меню
 *   5. contactForm  — обратная связь формы
 *   6. buyButtons   — переход от кнопок покупки к форме заявки
 * ============================================================
 */

'use strict';

/* ── 1. FADE-IN ПРИ СКРОЛЛЕ ──────────────────────────────── */
/**
 * Наблюдает за элементами .fade-in и добавляет класс .visible
 * при попадании в область видимости. Staggered-задержка делает
 * групповые появления плавными, а не одновременными.
 */
function initFadeIn() {
  const elements = document.querySelectorAll('.fade-in');
  if (!elements.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
          // Задержка для каждого следующего элемента в группе
          const delay = index * 80; // мс
          setTimeout(() => entry.target.classList.add('visible'), delay);
          observer.unobserve(entry.target); // очищаем наблюдение — не нужно снова
        }
      });
    },
    {
      threshold: 0.12,             // 12% элемента должно быть видно
      rootMargin: '0px 0px -40px 0px' // немного «ниже» реального края
    }
  );

  elements.forEach(el => observer.observe(el));
}


/* ── 2. АНИМАЦИЯ ВОЗРАСТНЫХ БАРОВ ────────────────────────── */
/**
 * Данные о ширине хранятся прямо в разметке через data-width.
 * Бар анимируется ровно один раз — при первом попадании в viewport.
 */
function initAgeBars() {
  const containers = document.querySelectorAll('.age-bars');
  if (!containers.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.querySelectorAll('.age-bar-fill').forEach(bar => {
            bar.style.width = bar.dataset.width; // CSS transition подхватит
          });
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.4 } // бар должен быть виден на 40% прежде чем запуститься
  );

  containers.forEach(el => observer.observe(el));
}


/* ── 3. МОБИЛЬНАЯ НАВИГАЦИЯ ──────────────────────────────── */
/**
 * Открывает/закрывает меню по клику на бургер.
 * Закрывается автоматически при клике на любую ссылку.
 */
function initMobileNav() {
  const toggle = document.getElementById('navToggle');
  const nav    = document.getElementById('mainNav');
  if (!toggle || !nav) return;

  toggle.addEventListener('click', () => {
    nav.classList.toggle('open');
    // Aria-атрибут для скринридеров
    const isOpen = nav.classList.contains('open');
    toggle.setAttribute('aria-expanded', isOpen);
  });

  // Закрыть меню при переходе по ссылке
  nav.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      nav.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    });
  });
}


/* ── 4. ПОДСВЕТКА АКТИВНОГО РАЗДЕЛА ─────────────────────── */
/**
 * Следит за скроллом и подсвечивает нужный пункт nav.
 * Passive: true — не блокирует главный поток рендера.
 */
function initNavHighlight() {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav a');
  if (!sections.length || !navLinks.length) return;

  const highlight = () => {
    let current = '';

    sections.forEach(section => {
      if (window.scrollY >= section.offsetTop - 80) {
        current = section.id;
      }
    });

    navLinks.forEach(link => {
      const isActive = link.getAttribute('href') === '#' + current;
      link.style.color = isActive ? 'var(--blue-main)' : '';
      link.style.fontWeight = isActive ? '700' : '';
    });
  };

  window.addEventListener('scroll', highlight, { passive: true });
  highlight(); // вызвать сразу при загрузке
}


/* ── 5. ФОРМА ОБРАТНОЙ СВЯЗИ ─────────────────────────────── */
/**
 * Показывает визуальный фидбэк после нажатия «Отправить».
 * Для реальной отправки замените логику внутри handleSubmit
 * на fetch() к вашему API или форм-сервису.
 */
function initContactForm() {
  const btn = document.getElementById('submitBtn');
  if (!btn) return;

  btn.addEventListener('click', handleSubmit);

  async function handleSubmit(e) {
    e.preventDefault();

    // Базовая валидация — проверяем, что имя и email заполнены
    const name  = document.querySelector('input[autocomplete="name"]');
    const email = document.querySelector('input[autocomplete="email"]');
    const phone = document.querySelector('input[autocomplete="tel"]');
    const city = document.querySelector('.contact__form input[placeholder="Город"]');
    const message = document.querySelector('.contact__form textarea');

    if (name && !name.value.trim()) {
      name.focus();
      name.style.borderColor = '#e74c3c';
      setTimeout(() => (name.style.borderColor = ''), 2000);
      return;
    }
    if (email && !email.value.includes('@')) {
      email.focus();
      email.style.borderColor = '#e74c3c';
      setTimeout(() => (email.style.borderColor = ''), 2000);
      return;
    }

    const endpoint = window.LEAD_ENDPOINT || 'https://earful-tubeless-chlorine.ngrok-free.dev/lead';
    const payload = {
      name: name ? name.value.trim() : '',
      email: email ? email.value.trim() : '',
      phone: phone ? phone.value.trim() : '',
      city: city ? city.value.trim() : '',
      message: message ? message.value.trim() : ''
    };

    btn.textContent = 'Отправляем...';
    btn.disabled = true;

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error('Lead request failed');
      }
    } catch (error) {
      btn.textContent = 'Не удалось отправить';
      btn.style.background = '#e74c3c';
      setTimeout(() => {
        btn.textContent = 'Отправить сообщение';
        btn.style.background = '';
        btn.disabled = false;
      }, 3000);
      return;
    }

    // Визуальный фидбэк
    btn.textContent = '✓ Сообщение отправлено!';
    btn.style.background = '#27ae60';

    [name, email, phone, city, message].forEach((field) => {
      if (field) field.value = '';
    });

    setTimeout(() => {
      btn.textContent = 'Отправить сообщение';
      btn.style.background = '';
      btn.disabled = false;
    }, 3000);
  }
}


/* ── 6. КНОПКИ ПОКУПКИ ───────────────────────────────────── */
function initBuyButtons() {
  const contact = document.getElementById('contact');
  if (!contact) return;

  const buyLabels = ['Купить сейчас', 'Купить в 1 клик', 'Оставить заявку'];

  document.querySelectorAll('button, a').forEach((el) => {
    if (el.id === 'submitBtn') return;

    const label = (el.textContent || '').replace(/\s+/g, ' ').trim();
    if (!buyLabels.some((text) => label.includes(text))) return;

    el.addEventListener('click', (event) => {
      event.preventDefault();
      contact.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
}


/* ── ИНИЦИАЛИЗАЦИЯ ───────────────────────────────────────── */
/**
 * Запускаем все модули после полной загрузки DOM.
 */
document.addEventListener('DOMContentLoaded', () => {
  initFadeIn();
  initAgeBars();
  initMobileNav();
  initNavHighlight();
  initContactForm();
  initBuyButtons();
});
