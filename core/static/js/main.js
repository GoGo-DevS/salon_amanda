/* ============================================================
   Salón Amanda — main.js
   Desarrollado por GoGoDevS
============================================================ */

'use strict';

/* ============================================================
   NAVBAR — cambio de estilo al hacer scroll
============================================================ */
const navbar = document.getElementById('mainNavbar');

function handleNavbarScroll() {
    navbar.classList.toggle('scrolled', window.scrollY > 60);
}

window.addEventListener('scroll', handleNavbarScroll, { passive: true });
handleNavbarScroll();


/* ============================================================
   CERRAR MENÚ MOBILE AL HACER CLICK EN UN LINK
============================================================ */
const navbarCollapse = document.getElementById('navbarNav');

document.querySelectorAll('#navbarNav .nav-link').forEach(link => {
    link.addEventListener('click', () => {
        if (navbarCollapse && navbarCollapse.classList.contains('show')) {
            const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
            if (bsCollapse) bsCollapse.hide();
        }
    });
});


/* ============================================================
   SCROLL REVEAL — Intersection Observer
   Delay escalonado en cards: 0, 100, 200 ms...
============================================================ */
const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (!entry.isIntersecting) return;

        const el = entry.target;
        const parent = el.parentElement;

        const siblings = Array.from(parent.querySelectorAll(':scope > .reveal:not(.revealed)'));

        if (siblings.length > 1) {
            siblings.forEach((sibling, i) => {
                setTimeout(() => {
                    sibling.classList.add('revealed');
                    revealObserver.unobserve(sibling);
                }, i * 100);
            });
        } else {
            el.classList.add('revealed');
            revealObserver.unobserve(el);
        }
    });
}, {
    threshold: 0.15,
    rootMargin: '0px 0px -40px 0px'
});

document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));


/* ============================================================
   NAV LINK ACTIVO SEGÚN SECCIÓN VISIBLE
   (funciona con hrefs tipo "/#seccion" usando link.hash)
============================================================ */
const allNavLinks = document.querySelectorAll('.navbar-nav .nav-link');

const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        allNavLinks.forEach(link => link.classList.remove('active'));
        const activeLink = Array.from(allNavLinks).find(
            link => link.hash === `#${entry.target.id}`
        );
        if (activeLink) activeLink.classList.add('active');
    });
}, {
    threshold: 0.35,
    rootMargin: `-68px 0px -45% 0px`
});

document.querySelectorAll('section[id]').forEach(section => sectionObserver.observe(section));


/* ============================================================
   SMOOTH SCROLL para anclas internas
   Soporta "#seccion" y "/#seccion": si el destino existe en la
   página actual hace scroll suave; si no, deja navegar normal.
============================================================ */
document.querySelectorAll('a[href*="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const url = new URL(this.href, window.location.href);
        if (url.pathname !== window.location.pathname) return; // otra página → navegación normal
        const hash = url.hash;
        if (!hash || hash === '#') return;
        const target = document.querySelector(hash);
        if (!target) return;
        e.preventDefault();
        const offsetTop = target.getBoundingClientRect().top + window.scrollY - 68;
        window.scrollTo({ top: offsetTop, behavior: 'smooth' });
        history.replaceState(null, '', hash);
    });
});


/* ============================================================
   LIGHTBOX — galería navegable (flechas, teclado, swipe)
============================================================ */
(function () {
    const items = Array.from(document.querySelectorAll('.gallery-item'));
    if (!items.length) return;

    const imgs = items.map(it => {
        const im = it.querySelector('img');
        return { src: im.getAttribute('src'), alt: im.getAttribute('alt') || '' };
    });

    const lb = document.createElement('div');
    lb.className = 'lightbox';
    lb.setAttribute('role', 'dialog');
    lb.setAttribute('aria-label', 'Galería de imágenes');
    lb.innerHTML =
        '<button class="lightbox-close" aria-label="Cerrar">&times;</button>' +
        '<button class="lightbox-prev" aria-label="Imagen anterior">&#8249;</button>' +
        '<img class="lightbox-img" src="" alt="">' +
        '<button class="lightbox-next" aria-label="Imagen siguiente">&#8250;</button>' +
        '<div class="lightbox-counter"></div>';
    document.body.appendChild(lb);

    const lbImg = lb.querySelector('.lightbox-img');
    const counter = lb.querySelector('.lightbox-counter');
    let idx = 0;

    function show(i) {
        idx = (i + imgs.length) % imgs.length;
        lbImg.src = imgs[idx].src;
        lbImg.alt = imgs[idx].alt;
        counter.textContent = (idx + 1) + ' / ' + imgs.length;
    }
    function open(i) {
        show(i);
        lb.classList.add('open');
        document.body.style.overflow = 'hidden';
    }
    function close() {
        lb.classList.remove('open');
        document.body.style.overflow = '';
    }

    items.forEach((it, i) => it.addEventListener('click', e => { e.preventDefault(); open(i); }));
    lb.querySelector('.lightbox-close').addEventListener('click', close);
    lb.querySelector('.lightbox-prev').addEventListener('click', e => { e.stopPropagation(); show(idx - 1); });
    lb.querySelector('.lightbox-next').addEventListener('click', e => { e.stopPropagation(); show(idx + 1); });
    lb.addEventListener('click', e => { if (e.target === lb) close(); });

    document.addEventListener('keydown', e => {
        if (!lb.classList.contains('open')) return;
        if (e.key === 'Escape') close();
        else if (e.key === 'ArrowLeft') show(idx - 1);
        else if (e.key === 'ArrowRight') show(idx + 1);
    });

    let startX = 0;
    lb.addEventListener('touchstart', e => { startX = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener('touchend', e => {
        const dx = e.changedTouches[0].clientX - startX;
        if (Math.abs(dx) > 50) show(dx < 0 ? idx + 1 : idx - 1);
    }, { passive: true });
})();
