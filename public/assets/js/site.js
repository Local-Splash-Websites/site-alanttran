// Mobile nav, rotating hero background, submenus, testimonial carousel, gallery lightbox, form timestamp.
(function () {
  var toggle = document.querySelector('.nav-toggle'), nav = document.getElementById('main-nav');
  if (toggle && nav) toggle.addEventListener('click', function () {
    var open = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', open);
  });
  document.querySelectorAll('.sub-toggle').forEach(function (b) {
    b.addEventListener('click', function () {
      var sub = b.parentElement.querySelector('.sub');
      var open = sub.classList.toggle('open');
      b.setAttribute('aria-expanded', open);
    });
  });

  document.querySelectorAll('[data-carousel]').forEach(function (c) {
    var slides = c.querySelectorAll('.slide'), dots = c.querySelectorAll('.dot'), i = 0, timer;
    function show(n) {
      i = (n + slides.length) % slides.length;
      slides.forEach(function (s, k) { s.classList.toggle('active', k === i); });
      dots.forEach(function (d, k) { d.classList.toggle('active', k === i); });
    }
    function auto() { clearInterval(timer); timer = setInterval(function () { show(i + 1); }, 8000); }
    c.querySelector('.prev').addEventListener('click', function () { show(i - 1); auto(); });
    c.querySelector('.next').addEventListener('click', function () { show(i + 1); auto(); });
    dots.forEach(function (d, k) { d.addEventListener('click', function () { show(k); auto(); }); });
    show(0); auto();
  });

  var lb = document.querySelector('.lightbox');
  if (lb) {
    var items = Array.prototype.slice.call(document.querySelectorAll('[data-lightbox]')), cur = 0, img = lb.querySelector('img');
    function open(n) { cur = (n + items.length) % items.length; img.src = items[cur].href; img.alt = items[cur].querySelector('img').alt; lb.hidden = false; }
    items.forEach(function (a, k) { a.addEventListener('click', function (ev) { ev.preventDefault(); open(k); }); });
    lb.querySelector('.lb-close').onclick = function () { lb.hidden = true; };
    lb.querySelector('.lb-prev').onclick = function () { open(cur - 1); };
    lb.querySelector('.lb-next').onclick = function () { open(cur + 1); };
    lb.addEventListener('click', function (ev) { if (ev.target === lb) lb.hidden = true; });
    document.addEventListener('keydown', function (ev) {
      if (lb.hidden) return;
      if (ev.key === 'Escape') lb.hidden = true;
      if (ev.key === 'ArrowLeft') open(cur - 1);
      if (ev.key === 'ArrowRight') open(cur + 1);
    });
  }

  document.querySelectorAll('[data-review-popup]').forEach(function (a) {
    a.addEventListener('click', function (ev) {
      var popup = window.open(a.href, 'leaveReview', 'popup=yes,width=520,height=760');
      if (popup) ev.preventDefault();
    });
  });

  document.querySelectorAll('[data-lead-form]').forEach(function (form) {
    var status = form.querySelector('.form-status');
    var button = form.querySelector('[type="submit"]');
    function show(ok, text) {
      status.textContent = text;
      status.className = 'form-status form-msg' + (ok ? ' is-ok' : '');
    }
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var data = new FormData(form);
      var procedure = (data.get('service') || '').toString().trim();
      var note = (data.get('message') || '').toString().trim();
      var message = procedure ? ('Procedure of interest: ' + procedure + '\n\n' + note) : note;
      var fields = [
        ['name', data.get('name'), 'text'],
        ['email', data.get('email'), 'email'],
        ['phone', data.get('phone'), 'tel'],
        ['message', message, 'textarea']
      ];
      if ((data.get('website') || '').toString()) fields.push(['website', data.get('website'), 'text']);
      var payload = {
        event_type: 'CONTACT_FORM_SENT_V2',
        event_timestamp: Math.floor(Date.now() / 1000),
        resource_data: { site_name: '20e7336c' },
        data: { fieldsData: fields.map(function (f) {
          return { field_label: f[0], field_value: (f[1] || '').toString(), field_type: f[2], field_key: f[0], field_id: f[0] };
        }) }
      };
      button.disabled = true;
      show(true, 'Sending…');
      fetch('/lead-webhook', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(payload)
      }).then(function (res) {
        return res.json().catch(function () { return {}; }).then(function (body) {
          if (res.ok && body.ok !== false) {
            show(true, body.message || 'We got it. Thank you for contacting us. We’ll get back to you as soon as possible.');
            form.reset();
          } else {
            show(false, body.message || 'That didn’t work. The form wasn’t sent. Please try again.');
          }
        });
      }).catch(function () {
        show(false, 'That didn’t work. The form wasn’t sent. Please try again.');
      }).then(function () { button.disabled = false; });
    });
  });
})();

// Rotating hero background: crossfades every 5 seconds, loads each image just before it's shown,
// pauses while the tab is hidden, and stays on the first image for reduced-motion users.
(function () {
  var hero = document.querySelector('[data-hero-slides]');
  if (!hero) return;
  var slides = hero.querySelectorAll('.hero-slide');
  if (slides.length < 2 || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var i = 0, timer = null;
  function load(el) {
    if (el.dataset.bg) { el.style.backgroundImage = "url('" + el.dataset.bg + "')"; delete el.dataset.bg; }
  }
  function next() {
    var n = (i + 1) % slides.length;
    load(slides[n]);
    slides[i].classList.remove('is-active');
    slides[n].classList.add('is-active');
    i = n;
    load(slides[(i + 1) % slides.length]);
  }
  function start() { if (!timer) timer = setInterval(next, 5000); }
  function stop() { clearInterval(timer); timer = null; }
  load(slides[1]);
  start();
  document.addEventListener('visibilitychange', function () { document.hidden ? stop() : start(); });
})();


// Homepage service tiles and feature cards: reveal on hover, keyboard focus, or click.
(function () {
  function bindGroup(buttonSelector, panelSelector, buttonKey, panelKey) {
    var buttons = Array.prototype.slice.call(document.querySelectorAll(buttonSelector));
    var panels = Array.prototype.slice.call(document.querySelectorAll(panelSelector));
    if (!buttons.length || !panels.length) return;
    function show(key) {
      buttons.forEach(function (b) {
        var active = b.getAttribute(buttonKey) === key;
        b.classList.toggle('is-active', active);
        b.setAttribute('aria-expanded', active ? 'true' : 'false');
      });
      panels.forEach(function (p) { p.classList.toggle('is-active', p.getAttribute(panelKey) === key); });
    }
    buttons.forEach(function (b) {
      var activate = function () { show(b.getAttribute(buttonKey)); };
      b.addEventListener('mouseenter', activate);
      b.addEventListener('focus', activate);
      b.addEventListener('click', activate);
    });
  }
  bindGroup('[data-service-tile]', '[data-service-panel]', 'data-service-tile', 'data-service-panel');
  bindGroup('[data-feature-card]', '[data-feature-panel]', 'data-feature-card', 'data-feature-panel');
})();
