// Mobile nav, submenus, testimonial carousel, gallery lightbox, form timestamp.
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

  document.querySelectorAll('.contact-form input[name="ts"]').forEach(function (t) { t.value = Math.floor(Date.now() / 1000); });
  var q = new URLSearchParams(location.search).get('error');
  var form = document.querySelector('.contact-form');
  if (q && form) {
    var m = document.createElement('p'); m.className = 'form-msg';
    m.textContent = q === 'rate' ? 'Too many messages from your connection. Please call us instead.' : 'Sorry, your message could not be sent. Please check the form or call the office.';
    form.prepend(m);
  }
})();
