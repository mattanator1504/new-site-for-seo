/* Renovo Studio — motion & interactions (no dependencies) */
(() => {
  const doc = document.documentElement;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

  /* ---------- Page load / transition curtain ---------- */
  requestAnimationFrame(() => setTimeout(() => doc.classList.add('is-loaded'), 80));
  window.addEventListener('pageshow', e => { if (e.persisted) doc.classList.remove('is-leaving'); });
  if (!reduce) {
    document.addEventListener('click', e => {
      const a = e.target.closest('a');
      if (!a || e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || a.target === '_blank') return;
      const url = new URL(a.href, location.href);
      if (url.origin !== location.origin || url.hash && url.pathname === location.pathname) return;
      if (a.hasAttribute('download') || url.protocol !== location.protocol) return;
      e.preventDefault();
      doc.classList.add('is-leaving');
      setTimeout(() => { location.href = url.href; }, 650);
    });
  }

  /* ---------- Header: shrink + hide on scroll down ---------- */
  const header = $('.site-header');
  let lastY = window.scrollY;
  const onHeader = () => {
    const y = window.scrollY;
    header.classList.toggle('is-scrolled', y > 40);
    header.classList.toggle('is-hidden', y > 300 && y > lastY && !doc.classList.contains('menu-open'));
    lastY = y;
  };

  /* ---------- Mobile menu + services dropdown ---------- */
  const menuBtn = $('.menu-btn');
  menuBtn?.addEventListener('click', () => {
    const open = doc.classList.toggle('menu-open');
    menuBtn.setAttribute('aria-expanded', open);
    document.body.style.overflow = open ? 'hidden' : '';
  });
  $$('.has-dd').forEach(dd => {
    const btn = $('.dd-toggle', dd);
    $$('.dropdown li', dd).forEach((li, i) => li.style.setProperty('--i', i));
    btn.addEventListener('click', e => {
      e.preventDefault();
      const open = dd.classList.toggle('open');
      btn.setAttribute('aria-expanded', open);
    });
    dd.addEventListener('keydown', e => {
      if (e.key === 'Escape') { dd.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); btn.focus(); }
    });
    document.addEventListener('click', e => {
      if (!dd.contains(e.target)) { dd.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); }
    });
  });

  /* ---------- Custom ring cursor ---------- */
  if (finePointer && !reduce) {
    const ring = document.createElement('div');
    ring.className = 'cursor';
    ring.innerHTML = '<span class="cursor-label"></span>';
    const dot = document.createElement('div');
    dot.className = 'cursor-dot';
    document.body.append(ring, dot);
    const label = $('.cursor-label', ring);
    let mx = innerWidth / 2, my = innerHeight / 2, rx = mx, ry = my;
    addEventListener('mousemove', e => { mx = e.clientX; my = e.clientY; dot.style.transform = `translate(${mx}px,${my}px)`; });
    (function loop() {
      rx += (mx - rx) * .16; ry += (my - ry) * .16;
      ring.style.transform = `translate(${rx}px,${ry}px)`;
      requestAnimationFrame(loop);
    })();
    document.addEventListener('mouseover', e => {
      const t = e.target.closest('a, button, summary, [data-cursor], label.chip-input');
      ring.classList.toggle('is-hover', !!t);
      const text = t?.dataset.cursor || '';
      label.textContent = text;
      ring.classList.toggle('has-label', !!text);
    });
  }

  /* ---------- Magnetic buttons ---------- */
  if (finePointer && !reduce) {
    $$('.btn, .go, [data-magnetic]').forEach(el => {
      el.addEventListener('mousemove', e => {
        const r = el.getBoundingClientRect();
        const x = e.clientX - r.left - r.width / 2, y = e.clientY - r.top - r.height / 2;
        el.style.transform = `translate(${x * .25}px, ${y * .35}px)`;
      });
      el.addEventListener('mouseleave', () => { el.style.transform = ''; });
    });
  }

  /* ---------- Split text into characters ---------- */
  $$('[data-split]').forEach(el => {
    let i = 0;
    const walk = node => {
      [...node.childNodes].forEach(n => {
        if (n.nodeType === 3) {
          const frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(part => {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.append(document.createTextNode(' ')); return; }
            const word = document.createElement('span');
            word.className = 'word';
            [...part].forEach(ch => {
              const mask = document.createElement('span');
              mask.className = 'split-mask';
              const c = document.createElement('span');
              c.className = 'char';
              c.style.setProperty('--i', i++);
              c.textContent = ch;
              mask.append(c);
              word.append(mask);
            });
            frag.append(word);
          });
          n.replaceWith(frag);
        } else if (n.nodeType === 1) walk(n);
      });
    };
    // Screen readers get the plain text; the animated letters are hidden from them
    const label = document.createElement('span');
    label.className = 'sr-only';
    label.textContent = el.textContent.replace(/\s+/g, ' ').trim();
    walk(el);
    $$('.word', el).forEach(w => w.setAttribute('aria-hidden', 'true'));
    el.prepend(label);
    el.classList.add('split');
  });

  /* ---------- Reveal on scroll ---------- */
  const io = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (!en.isIntersecting) return;
      en.target.classList.add('in');
      io.unobserve(en.target);
      if (en.target.matches('[data-count]')) countUp(en.target);
    });
  }, { threshold: .15, rootMargin: '0px 0px -8% 0px' });
  $$('.reveal, .split, .clip-reveal, [data-count]').forEach(el => io.observe(el));
  // stagger children
  $$('[data-stagger]').forEach(g => [...g.children].forEach((c, i) => c.style.setProperty('--d', `${i * .09}s`)));

  /* ---------- Counters ---------- */
  function countUp(el) {
    const end = parseFloat(el.dataset.count);
    const dec = (el.dataset.count.split('.')[1] || '').length;
    const pre = el.dataset.prefix || '', suf = el.dataset.suffix || '';
    if (reduce) { el.textContent = pre + end.toFixed(dec) + suf; return; }
    const t0 = performance.now(), dur = 1800;
    const tick = now => {
      const p = clamp((now - t0) / dur, 0, 1), e = 1 - Math.pow(1 - p, 4);
      el.textContent = pre + (end * e).toFixed(dec).replace(/\B(?=(\d{3})+(?!\d))/g, ',') + suf;
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  /* ---------- Manifesto: words light up as you scroll ---------- */
  const manifestos = $$('[data-scrub-words]');
  manifestos.forEach(m => {
    const walk = node => [...node.childNodes].forEach(n => {
      if (n.nodeType === 3) {
        const frag = document.createDocumentFragment();
        n.textContent.split(/(\s+)/).forEach(p => {
          if (!p) return;
          if (/^\s+$/.test(p)) return frag.append(document.createTextNode(' '));
          const s = document.createElement('span'); s.className = 'w'; s.textContent = p; frag.append(s);
        });
        n.replaceWith(frag);
      } else if (n.nodeType === 1 && !n.classList.contains('pill')) walk(n);
      else if (n.nodeType === 1) n.classList.add('w');
    });
    walk(m);
  });

  /* ---------- Scroll-driven effects (parallax, marquee, h-scroll) ---------- */
  const parallax = $$('[data-speed]');
  const rotators = $$('[data-rotate]');
  const marquees = $$('.marquee__track').map(track => {
    const item = track.firstElementChild;
    for (let i = 0; i < 3; i++) { const c = item.cloneNode(true); c.setAttribute('aria-hidden', 'true'); track.append(c); }
    return { track, item, x: 0, dir: track.closest('.marquee--alt') ? 1 : -1 };
  });
  const hscrolls = $$('.hscroll').map(sec => ({ sec, track: $('.hscroll__track', sec), bar: $('.hscroll__progress i', sec) }));
  const sizeH = () => hscrolls.forEach(h => {
    if (innerWidth <= 760) { h.sec.style.height = ''; h.track.style.transform = ''; return; }
    const dist = h.track.scrollWidth - innerWidth;
    h.dist = Math.max(0, dist);
    h.sec.style.height = `${innerHeight + h.dist}px`;
  });
  sizeH();
  addEventListener('resize', sizeH);
  addEventListener('load', sizeH);

  // Cache sizes so the animation loop never forces a layout (read first, then write)
  const sizeMarquees = () => marquees.forEach(m => { m.w = m.item.offsetWidth; });
  sizeMarquees();
  addEventListener('resize', sizeMarquees);
  addEventListener('load', sizeMarquees);
  if (document.fonts) document.fonts.ready.then(sizeMarquees);
  manifestos.forEach(m => { m._words = $$('.w', m); });

  let velocity = 0, prevY = scrollY;
  function frame() {
    const y = scrollY;
    velocity += ((y - prevY) - velocity) * .1;
    prevY = y;
    const vh = innerHeight, small = innerWidth <= 760;

    // ---- read
    const pRects = reduce ? [] : parallax.map(el => el.parentElement.getBoundingClientRect());
    const hRects = hscrolls.map(h => (small || !h.dist) ? null : h.sec.getBoundingClientRect());
    const mRects = manifestos.map(m => m.getBoundingClientRect());

    // ---- write
    if (!reduce) {
      parallax.forEach((el, i) => {
        const r = pRects[i];
        if (r.bottom < -200 || r.top > vh + 200) return;
        const center = r.top + r.height / 2 - vh / 2;
        el.style.translate = `0 ${(-center * parseFloat(el.dataset.speed)).toFixed(1)}px`;
      });
      rotators.forEach(el => { el.style.rotate = `${(y * parseFloat(el.dataset.rotate)).toFixed(2)}deg`; });
      marquees.forEach(m => {
        const w = m.w || 1;
        m.x += m.dir * (0.6 + Math.abs(velocity) * .25);
        if (m.x <= -w) m.x += w;
        if (m.x >= 0) m.x -= w;
        m.track.style.transform = `translate3d(${m.x}px,0,0) skewX(${clamp(-velocity * .3, -10, 10)}deg)`;
      });
    }
    hscrolls.forEach((h, i) => {
      const r = hRects[i];
      if (!r) return;
      const p = clamp(-r.top / h.dist, 0, 1);
      h.track.style.transform = `translate3d(${-p * h.dist}px,0,0)`;
      if (h.bar) h.bar.style.transform = `scaleX(${p})`;
    });
    manifestos.forEach((m, i) => {
      const words = m._words, r = mRects[i];
      const p = clamp((vh * .85 - r.top) / (r.height + vh * .35), 0, 1);
      const lit = reduce ? words.length : Math.round(p * words.length);
      if (lit === m._lit) return;
      m._lit = lit;
      words.forEach((w, k) => w.classList.toggle('lit', k < lit));
    });

    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
  addEventListener('scroll', onHeader, { passive: true });
  onHeader();

  /* ---------- Hero mouse parallax ---------- */
  const stage = $('[data-mouse-stage]');
  if (stage && finePointer && !reduce) {
    const items = $$('[data-depth]', stage);
    addEventListener('mousemove', e => {
      const x = e.clientX / innerWidth - .5, y = e.clientY / innerHeight - .5;
      items.forEach(it => {
        const d = parseFloat(it.dataset.depth);
        it.style.transform = `translate(${x * d * 40}px, ${y * d * 40}px)`;
      });
    });
  }

  /* ---------- Work filters ---------- */
  $$('[data-filter]').forEach(btn => btn.addEventListener('click', () => {
    const f = btn.dataset.filter;
    $$('[data-filter]').forEach(b => { b.classList.toggle('is-active', b === btn); b.setAttribute('aria-pressed', b === btn); });
    $$('[data-cat]').forEach(card => {
      const show = f === 'all' || card.dataset.cat.split(' ').includes(f);
      card.classList.toggle('is-hidden', !show);
      if (show) { card.classList.remove('in'); requestAnimationFrame(() => card.classList.add('in')); }
    });
  }));

  // Deep link: work.html#filter=gtm-outbound opens the grid pre-filtered
  const hashFilter = (location.hash.match(/^#filter=([\w-]+)/) || [])[1];
  if (hashFilter) { const b = $(`[data-filter="${hashFilter}"]`); if (b) { b.click(); setTimeout(() => $('#grid-title')?.scrollIntoView(), 400); } }

  /* ---------- Contact form ---------- */
  const form = $('#contact-form');
  if (form) {
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const status = $('.form-status', form);
      let ok = true;
      $$('[required]', form).forEach(input => {
        const field = input.closest('.field');
        const valid = input.checkValidity();
        field?.classList.toggle('has-error', !valid);
        const err = field && $('.err', field);
        if (err) err.textContent = valid ? '' : (input.type === 'email' ? 'Please enter a valid email.' : 'This field is required.');
        if (!valid && ok) { input.focus(); ok = false; }
      });
      if (!ok) { status.textContent = 'Please check the highlighted fields.'; return; }
      const action = form.getAttribute('action');
      if (!action || action === '#') {
        status.textContent = 'Thanks! Form endpoint not connected yet — see README.';
        return;
      }
      status.textContent = 'Sending…';
      try {
        const res = await fetch(action, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' } });
        if (!res.ok) throw new Error(res.statusText);
        form.reset();
        status.textContent = 'Message received — I\'ll be in touch within one business day.';
      } catch {
        status.textContent = 'Something went wrong. Please email directly instead.';
      }
    });
  }

  /* ---------- Project cards: hover-scroll screenshots ---------- */
  const projShots = $$('.proj__view img');
  const sizeShots = () => projShots.forEach(img => {
    const view = img.parentElement;
    const dist = Math.max(0, img.offsetHeight - view.clientHeight);
    const frame = img.closest('.proj__frame');
    frame.style.setProperty('--dist', `${-dist}px`);
    frame.style.setProperty('--dur', `${Math.max(3, dist / 320).toFixed(1)}s`);
  });
  projShots.forEach(img => { if (img.complete) sizeShots(); else img.addEventListener('load', sizeShots); });
  addEventListener('resize', sizeShots);
  // Touch screens have no hover: tap the frame to play/stop the preview
  if (!finePointer) $$('.proj__hint').forEach(h => { h.textContent = 'Tap to scroll'; });
  $$('.proj.has-screen .proj__frame').forEach(frame => {
    const toggle = () => {
      const on = !frame.classList.contains('is-active');
      $$('.proj__frame.is-active').forEach(f => f.classList.remove('is-active'));
      frame.classList.toggle('is-active', on);
    };
    if (!finePointer) frame.addEventListener('click', toggle);
    frame.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); } });
  });

  /* ---------- Back to top + year ---------- */
  $$('.to-top').forEach(b => b.addEventListener('click', e => { e.preventDefault(); scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' }); }));
  $$('[data-year]').forEach(el => { el.textContent = new Date().getFullYear(); });
})();
