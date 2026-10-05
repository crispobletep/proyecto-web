document.addEventListener("DOMContentLoaded", () => {
    const brandFilter = document.querySelector("#catalog-brand-filter");
    brandFilter?.addEventListener("change", () => {
        brandFilter.form.requestSubmit();
    });
    const menuToggle = document.querySelector(".menu-toggle");
    const mainNavigation = document.querySelector(".main-nav");
    const menuIcon = menuToggle?.querySelector(".menu-toggle-icon");
    const branches = document.querySelectorAll(".nav-branch details");
    function closeBranches() {
        branches.forEach((branch) => { branch.open = false; });
    }
    branches.forEach((branch) => {
        branch.addEventListener("toggle", () => {
            if (branch.open) branches.forEach((other) => {
                if (other !== branch) other.open = false;
            });
        });
    });
    document.addEventListener("click", (event) => {
        if (!event.target.closest(".nav-branch")) closeBranches();
    });
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            const openBranch = [...branches].find((branch) => branch.open);
            openBranch?.querySelector("summary").focus();
            closeBranches();
        }
    });

    function closeMenu({ returnFocus = false } = {}) {
        if (!menuToggle || !mainNavigation) return;

        mainNavigation.classList.remove("open");
        document.body.classList.remove("menu-open");
        menuToggle.setAttribute("aria-expanded", "false");
        menuToggle.setAttribute("aria-label", "Abrir menú");
        if (menuIcon) menuIcon.textContent = "☰";
        if (returnFocus) menuToggle.focus();
    }

    if (menuToggle && mainNavigation) {
        menuToggle.addEventListener("click", () => {
            const willOpen = !mainNavigation.classList.contains("open");
            if (!willOpen) {
                closeMenu();
                return;
            }

            mainNavigation.classList.add("open");
            document.body.classList.add("menu-open");
            menuToggle.setAttribute("aria-expanded", "true");
            menuToggle.setAttribute("aria-label", "Cerrar menú");
            if (menuIcon) menuIcon.textContent = "×";
        });

        mainNavigation.querySelectorAll("a").forEach((link) => {
            link.addEventListener("click", () => closeMenu());
        });

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && mainNavigation.classList.contains("open")) {
                closeMenu({ returnFocus: true });
            }
        });

        document.addEventListener("click", (event) => {
            const header = menuToggle.closest(".header");
            if (
                mainNavigation.classList.contains("open")
                && header
                && !header.contains(event.target)
            ) {
                closeMenu();
            }
        });

        window.addEventListener("resize", () => {
            if (window.innerWidth > 760) closeMenu();
        });
    }

    const slides = document.querySelectorAll(".hero-slide");
    const dots = document.querySelectorAll(".carousel-dot");
    const btnNext = document.querySelector(".carousel-next");
    const btnPrev = document.querySelector(".carousel-prev");
    const carousel = document.querySelector(".hero-carousel");

    if (slides.length > 0) {
        let currentSlide = 0;
        let timer = null;
        const totalSlides = slides.length;
        const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

        function updateCarousel(index) {
            slides.forEach((slide, slideIndex) => {
                const active = slideIndex === index;
                slide.classList.toggle("active", active);
                slide.setAttribute("aria-hidden", active ? "false" : "true");
                slide.inert = !active;
            });

            dots.forEach((dot, dotIndex) => {
                const active = dotIndex === index;
                dot.classList.toggle("active", active);
                dot.setAttribute("aria-current", active ? "true" : "false");
            });

            currentSlide = index;
        }

        function stopAutoplay() {
            if (timer) window.clearInterval(timer);
            timer = null;
        }

        function startAutoplay() {
            stopAutoplay();
            if (reduceMotion.matches || totalSlides < 2 || document.hidden
                || carousel?.matches(":hover") || carousel?.contains(document.activeElement)) return;
            timer = window.setInterval(() => {
                updateCarousel((currentSlide + 1) % totalSlides);
            }, 6000);
        }

        btnNext?.addEventListener("click", () => {
            updateCarousel((currentSlide + 1) % totalSlides);
            startAutoplay();
        });

        btnPrev?.addEventListener("click", () => {
            updateCarousel((currentSlide - 1 + totalSlides) % totalSlides);
            startAutoplay();
        });

        dots.forEach((dot, index) => {
            dot.addEventListener("click", () => {
                updateCarousel(index);
                startAutoplay();
            });
        });

        carousel?.addEventListener("mouseenter", stopAutoplay);
        carousel?.addEventListener("mouseleave", startAutoplay);
        carousel?.addEventListener("focusin", stopAutoplay);
        carousel?.addEventListener("focusout", () => window.setTimeout(startAutoplay, 0));
        document.addEventListener("visibilitychange", startAutoplay);
        reduceMotion.addEventListener?.("change", startAutoplay);

        updateCarousel(0);
        startAutoplay();
    }

    document.querySelectorAll(".catalog-card").forEach((card) => {
        const mainImage = card.querySelector(".catalog-main-image");
        if (!mainImage) return;

        const thumbnails = [...card.querySelectorAll(".catalog-thumb")];
        const variants = [...card.querySelectorAll(".catalog-variant-card")];
        const strip = card.querySelector(".catalog-variant-strip");
        const rail = card.querySelector(".catalog-thumbs");
        const status = card.querySelector(".catalog-selection-status");
        const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
        let selectedSrc = mainImage.getAttribute("src");
        let selectedAlt = mainImage.alt;

        // El ID identifica la variante incluso cuando varias comparten fotografía.
        card.querySelectorAll(".catalog-extra-image").forEach((extra) => {
            if (thumbnails.some(item => item.dataset.variantId && item.dataset.previewSrc === extra.dataset.previewSrc)) extra.remove();
        });
        function showImage(src, alt) {
            if (!src) return;
            mainImage.src = src;
            mainImage.alt = alt || selectedAlt;
        }
        function reveal(container, target, horizontal) {
            if (!container || !target) return;
            const bounds = container.getBoundingClientRect();
            const item = target.getBoundingClientRect();
            const delta = horizontal
                ? item.left - bounds.left - (container.clientWidth - item.width) / 2
                : item.top - bounds.top - (container.clientHeight - item.height) / 2;
            container.scrollTo({
                [horizontal ? "left" : "top"]: (horizontal ? container.scrollLeft : container.scrollTop) + delta,
                behavior: reduceMotion.matches ? "instant" : "smooth",
            });
        }
        function select(trigger, variant) {
            selectedSrc = trigger.dataset.previewSrc || selectedSrc;
            selectedAlt = trigger.dataset.previewAlt || selectedAlt;
            showImage(selectedSrc, selectedAlt);
            variants.forEach(item => {
                const active = item === variant;
                item.classList.toggle("selected", active);
                item.querySelector(".catalog-variant-select")?.setAttribute("aria-pressed", String(active));
            });
            let matched;
            thumbnails.forEach(item => {
                const active = variant ? item.dataset.variantId === variant.dataset.variantId : item === trigger;
                item.classList.toggle("active", active);
                item.setAttribute("aria-pressed", String(active));
                if (active) matched = item;
            });
            if (status) status.textContent = variant ? `Variante seleccionada: ${variant.dataset.variantName}` : "Imagen del producto";
            reveal(strip, variant, true);
            reveal(rail, matched, rail && getComputedStyle(rail).flexDirection === "row");
        }
        thumbnails.forEach(thumbnail => {
            thumbnail.addEventListener("click", () => select(thumbnail,
                variants.find(item => item.dataset.variantId === thumbnail.dataset.variantId)));
        });
        variants.forEach(variant => {
            variant.querySelector(".catalog-variant-select")?.addEventListener("click", () => select(variant, variant));
        });
        // La previsualización al pasar el cursor no cambia la selección confirmada.
        card.querySelectorAll(".catalog-thumb, .catalog-variant-select").forEach(trigger => {
            const source = trigger.matches(".catalog-thumb") ? trigger : trigger.closest(".catalog-variant-card");
            trigger.addEventListener("pointerenter", event => {
                if (event.pointerType === "mouse") showImage(source.dataset.previewSrc, source.dataset.previewAlt);
            });
            trigger.addEventListener("pointerleave", () => showImage(selectedSrc, selectedAlt));
        });
    });

    const projectFilters = document.querySelectorAll("[data-project-filter]");
    const projectCards = document.querySelectorAll("[data-project-category]");
    projectFilters.forEach((button) => {
        button.addEventListener("click", () => {
            const filter = button.dataset.projectFilter;
            projectFilters.forEach((item) => {
                const active = item === button;
                item.classList.toggle("active", active);
                item.setAttribute("aria-pressed", active ? "true" : "false");
            });
            projectCards.forEach((card) => {
                card.hidden = filter !== "todos"
                    && card.dataset.projectCategory !== filter;
            });
        });
    });

    function loadMapPreview(trigger) {
        const frame = trigger?.querySelector("[data-map-src]");
        if (!frame || frame.dataset.mapLoaded === "true") return;

        const source = frame.dataset.mapSrc;
        if (!source) return;

        const iframe = document.createElement("iframe");
        iframe.src = source;
        iframe.title = frame.dataset.mapTitle || "Vista previa de Google Maps";
        iframe.referrerPolicy = "no-referrer-when-downgrade";
        iframe.tabIndex = -1;
        iframe.setAttribute("aria-hidden", "true");
        iframe.addEventListener("load", () => {
            frame.querySelector(".project-map-loading")?.remove();
        }, { once: true });

        window.setTimeout(() => {
            const loading = frame.querySelector(".project-map-loading");
            if (loading) {
                loading.textContent = "No se pudo cargar la vista previa";
            }
        }, 6000);

        frame.dataset.mapLoaded = "true";
        frame.appendChild(iframe);
    }

    document.querySelectorAll("[data-map-preview]").forEach((trigger) => {
        trigger.addEventListener("mouseenter", () => loadMapPreview(trigger));
        trigger.addEventListener("focusin", () => loadMapPreview(trigger));
    });

    document.querySelectorAll("[data-map-address-preview]").forEach((address) => {
        const card = address.closest(".project-card-catalog");
        const trigger = card?.querySelector("[data-map-preview]");
        if (!card || !trigger) return;

        const showPreview = () => {
            card.classList.add("map-preview-from-address");
            loadMapPreview(trigger);
        };
        const hidePreview = () => {
            card.classList.remove("map-preview-from-address");
        };

        address.addEventListener("mouseenter", showPreview);
        address.addEventListener("mouseleave", hidePreview);
        address.addEventListener("focusin", showPreview);
        address.addEventListener("focusout", hidePreview);
    });

    const quoteForm = document.querySelector(".quote-form");
    quoteForm?.addEventListener("submit", () => {
        const submitButton = quoteForm.querySelector("[type='submit']");
        if (!submitButton) return;
        submitButton.disabled = true;
        submitButton.textContent = "Enviando solicitud…";
    });

    document.querySelector(".form-success")?.focus();
});
