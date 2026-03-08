"use strict";

(() => {
    /* ── Utilities ── */

    const $ = (sel, root = document) => root.querySelector(sel);
    const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

    const onReady = (fn) => {
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", fn);
        } else {
            fn();
        }
    };

    const slugify = (text) =>
        text
            .normalize("NFKD")
            .replace(/[^\w\s-]/g, "")
            .trim()
            .toLowerCase()
            .replace(/[\s-]+/g, "-")
            .replace(/^-|-$/g, "");

    /* ── Current Year ── */

    const initCurrentYear = () => {
        const year = String(new Date().getFullYear());
        for (const node of $$("[data-current-year]")) {
            node.textContent = year;
        }
    };

    /* ── Navbar ── */

    const initNavbar = () => {
        for (const navbar of $$("[data-navbar]")) {
            const toggle = $("[data-nav-toggle]", navbar);
            const menu = $("[data-nav-menu]", navbar);
            if (!toggle || !menu) continue;

            const openIcon = $("[data-nav-icon-open]", navbar);
            const closeIcon = $("[data-nav-icon-close]", navbar);

            const setMenuState = (open) => {
                const desktop = innerWidth >= 768;
                const expanded = !desktop && open;
                navbar.classList.toggle("is-open", expanded);
                toggle.setAttribute("aria-expanded", String(expanded));
                menu.classList.toggle("hidden", desktop ? false : !expanded);
                openIcon?.classList.toggle("hidden", expanded);
                closeIcon?.classList.toggle("hidden", !expanded);
            };

            const close = () => setMenuState(false);
            close();

            toggle.addEventListener("click", () => {
                setMenuState(toggle.getAttribute("aria-expanded") !== "true");
            });

            for (const link of $$("[data-nav-link]", navbar)) {
                link.addEventListener("click", close);
            }

            document.addEventListener("click", (e) => {
                if (e.target instanceof Node && !navbar.contains(e.target)) close();
            });
            addEventListener("keydown", (e) => { if (e.key === "Escape") close(); });
            addEventListener("resize", close);
        }
    };

    /* ── Scroll Snap ── */

    const initScrollSnap = () => {
        const container = $(".scroll-snap-container");
        if (!container) return;

        for (const indicator of $$(".scroll-indicator", container)) {
            indicator.addEventListener("click", () => {
                const sections = $$(".snap-section", container);
                if (!sections.length) return;
                const vh = container.clientHeight || innerHeight;
                const current = Math.round(container.scrollTop / vh);
                const next = Math.min(current + 1, sections.length - 1);
                sections[next].scrollIntoView({ behavior: "smooth", block: "start" });
            });
        }

        const mq = matchMedia("(max-width: 1024px)");
        const apply = () => { container.style.scrollSnapType = mq.matches ? "y proximity" : "y mandatory"; };
        apply();
        mq.addEventListener("change", apply);
    };

    /* ── Featured Carousel ── */

    const initFeaturedCarousel = () => {
        for (const carousel of $$("[data-featured-carousel]")) {
            const track = $("[data-featured-track]", carousel);
            const slides = $$("[data-featured-slide]", carousel);
            if (!track || !slides.length) continue;

            let currentIndex = 0;
            let autoplayId = null;
            const autoplayMs = Number(carousel.dataset.featuredAutoplayMs) || 3000;
            const currentLabel = $("[data-featured-current]", carousel);
            const dots = $$("[data-featured-dot]", carousel);
            const multiSlide = slides.length > 1;

            const goTo = (index, animate = true) => {
                currentIndex = (index + slides.length) % slides.length;
                track.style.transitionDuration = animate ? "" : "0ms";
                track.style.transform = `translateX(-${currentIndex * 100}%)`;

                slides.forEach((slide, i) => {
                    slide.setAttribute("aria-hidden", String(i !== currentIndex));
                });

                if (currentLabel) currentLabel.textContent = String(currentIndex + 1);

                dots.forEach((dot, i) => {
                    const active = i === currentIndex;
                    dot.classList.toggle("is-active", active);
                    dot.setAttribute("aria-current", String(active));
                });

                if (!animate) {
                    requestAnimationFrame(() => { track.style.transitionDuration = ""; });
                }
            };

            const stopAutoplay = () => {
                if (autoplayId) { clearInterval(autoplayId); autoplayId = null; }
            };

            const startAutoplay = () => {
                stopAutoplay();
                if (multiSlide) autoplayId = setInterval(() => goTo(currentIndex + 1), autoplayMs);
            };

            goTo(0, false);
            if (!multiSlide) continue;

            $("[data-featured-prev]", carousel)?.addEventListener("click", () => {
                goTo(currentIndex - 1); startAutoplay();
            });
            $("[data-featured-next]", carousel)?.addEventListener("click", () => {
                goTo(currentIndex + 1); startAutoplay();
            });

            for (const dot of dots) {
                dot.addEventListener("click", () => {
                    const idx = Number(dot.dataset.featuredIndex);
                    if (!Number.isNaN(idx)) { goTo(idx); startAutoplay(); }
                });
            }

            carousel.addEventListener("mouseenter", stopAutoplay);
            carousel.addEventListener("mouseleave", startAutoplay);
            carousel.addEventListener("focusin", stopAutoplay);
            carousel.addEventListener("focusout", (e) => {
                if (!e.relatedTarget || !carousel.contains(e.relatedTarget)) startAutoplay();
            });

            document.addEventListener("visibilitychange", () => {
                document.hidden ? stopAutoplay() : startAutoplay();
            });

            startAutoplay();
        }
    };

    /* ── Reading Progress ── */

    const initReadingProgress = (content) => {
        const root = $("[data-reading-progress]");
        const bar = $("[data-reading-progress-bar]");
        if (!root || !bar) return;

        const update = () => {
            const rect = content.getBoundingClientRect();
            const contentTop = rect.top + scrollY;
            const contentHeight = content.offsetHeight;
            if (contentHeight <= 0) { bar.style.transform = "scaleX(0)"; return; }

            const start = contentTop - innerHeight * 0.2;
            const end = contentTop + contentHeight - innerHeight * 0.7;
            const progress = Math.max(0, Math.min(1, (scrollY - start) / Math.max(end - start, 1)));
            bar.style.transform = `scaleX(${progress})`;
            root.classList.toggle("is-active", progress > 0 && progress < 1);
        };

        addEventListener("scroll", update, { passive: true });
        addEventListener("resize", update);
        update();
    };

    /* ── Table of Contents ── */

    const initToc = (content) => {
        const tocWrapper = $("[data-post-toc-wrapper]");
        const tocContainer = $("[data-post-toc]");
        if (!tocWrapper || !tocContainer) return;

        const headings = $$("h2, h3", content).filter((h) => h.textContent?.trim());
        if (!headings.length) return;

        const usedIds = new Set(
            $$("[id]", content).map((el) => el.id).filter(Boolean),
        );

        const tocLinks = [];
        tocContainer.textContent = "";

        for (const [i, heading] of headings.entries()) {
            if (!heading.id) {
                let base = slugify(heading.textContent ?? "") || `section-${i + 1}`;
                let candidate = base;
                let suffix = 2;
                while (usedIds.has(candidate)) candidate = `${base}-${suffix++}`;
                heading.id = candidate;
                usedIds.add(candidate);
            }

            const link = document.createElement("a");
            link.href = `#${heading.id}`;
            link.textContent = heading.textContent.trim();
            link.className = "blog-post-toc-link";
            if (heading.tagName === "H3") link.classList.add("is-subheading");
            tocContainer.appendChild(link);
            tocLinks.push({ heading, link });
        }

        if (!tocLinks.length) return;

        const setActive = (id) => {
            for (const item of tocLinks) {
                item.link.classList.toggle("is-active", item.heading.id === id);
            }
        };

        const updateLayout = () => {
            if (tocLinks.length === 1) {
                const label = tocLinks[0].heading.textContent.trim();
                tocLinks[0].link.style.setProperty("--toc-offset", "50%");
                tocLinks[0].link.dataset.label = label;
                tocLinks[0].link.setAttribute("aria-label", label);
                return;
            }

            const offsets = tocLinks.map((item) => item.heading.offsetTop);
            const min = Math.min(...offsets);
            const max = Math.max(...offsets);
            const range = Math.max(max - min, 1);

            tocLinks.forEach((item, i) => {
                const text = item.heading.textContent.trim();
                const mapped = 8 + ((offsets[i] - min) / range) * 84;
                item.link.style.setProperty("--toc-offset", `${mapped}%`);
                item.link.dataset.label = text;
                item.link.setAttribute("aria-label", text);
            });
        };

        let rafPending = false;

        const updateActiveHeading = () => {
            const pageH = document.documentElement.scrollHeight;
            if (scrollY + innerHeight >= pageH - 2) {
                setActive(tocLinks.at(-1).heading.id);
                return;
            }

            const baseOffset = Math.max(96, innerHeight * 0.12);
            const remaining = scrollY + content.getBoundingClientRect().bottom - scrollY - innerHeight;
            const boost = Math.max(0, innerHeight * 0.45 - remaining);
            const line = scrollY + baseOffset + boost;

            let idx = 0;
            for (const [i, item] of tocLinks.entries()) {
                if (scrollY + item.heading.getBoundingClientRect().top <= line) idx = i;
            }
            setActive(tocLinks[idx].heading.id);
        };

        const onScroll = () => {
            if (rafPending) return;
            rafPending = true;
            requestAnimationFrame(() => { rafPending = false; updateActiveHeading(); });
        };

        const onHashChange = () => {
            const hash = decodeURIComponent(location.hash.replace(/^#/, ""));
            if (!hash) return;
            const match = tocLinks.find((item) => item.heading.id === hash);
            if (match) setActive(match.heading.id);
        };

        for (const item of tocLinks) {
            item.link.addEventListener("click", () => setActive(item.heading.id));
        }

        tocWrapper.classList.remove("hidden");
        addEventListener("scroll", onScroll, { passive: true });
        addEventListener("resize", () => { updateLayout(); updateActiveHeading(); });
        addEventListener("hashchange", onHashChange);
        updateLayout();
        location.hash ? onHashChange() : updateActiveHeading();
    };

    /* ── Post Enhancements ── */

    const initPostEnhancements = () => {
        const content = $("[data-post-content]");
        if (!content) return;
        initReadingProgress(content);
        initToc(content);
    };

    /* ── Theme (mode + palette) ── */

    const initTheme = () => {
        const root = document.documentElement;

        const setMode = (mode) => {
            root.dataset.theme = mode;
            root.classList.toggle("dark", mode === "dark");
            localStorage.setItem("theme", mode);

            for (const btn of $$("[data-theme-toggle]")) {
                $("[data-theme-icon-light]", btn)?.classList.toggle("hidden", mode === "dark");
                $("[data-theme-icon-dark]", btn)?.classList.toggle("hidden", mode === "light");
            }
        };

        const setPalette = (palette) => {
            if (palette && palette !== "default") {
                root.dataset.palette = palette;
            } else {
                delete root.dataset.palette;
            }
            localStorage.setItem("palette", palette || "default");

            for (const opt of $$("[data-palette-option]")) {
                const active = opt.dataset.paletteOption === (palette || "default");
                opt.classList.toggle("text-accent", active);
                opt.classList.toggle("text-foreground", active);
                opt.setAttribute("aria-selected", String(active));
                const check = $("[data-palette-check]", opt);
                if (check) check.classList.toggle("hidden", !active);
            }
        };

        /* Init from stored values */
        setMode(root.dataset.theme || "dark");
        setPalette(localStorage.getItem("palette") || "default");

        /* Mode toggle */
        for (const btn of $$("[data-theme-toggle]")) {
            btn.addEventListener("click", () => {
                setMode(root.dataset.theme === "dark" ? "light" : "dark");
            });
        }

        /* Palette dropdown */
        for (const selector of $$("[data-palette-selector]")) {
            const trigger = $("[data-palette-trigger]", selector);
            const dropdown = $("[data-palette-dropdown]", selector);
            if (!trigger || !dropdown) continue;

            const toggle = (open) => {
                const show = open ?? dropdown.classList.contains("hidden");
                dropdown.classList.toggle("hidden", !show);
                trigger.setAttribute("aria-expanded", String(show));
            };

            trigger.addEventListener("click", (e) => {
                e.stopPropagation();
                toggle();
            });

            for (const opt of $$("[data-palette-option]", dropdown)) {
                opt.addEventListener("click", () => {
                    setPalette(opt.dataset.paletteOption);
                    toggle(false);
                });
            }

            document.addEventListener("click", (e) => {
                if (!selector.contains(e.target)) toggle(false);
            });
            addEventListener("keydown", (e) => {
                if (e.key === "Escape") toggle(false);
            });
        }
    };

    /* ── Bootstrap ── */

    onReady(() => {
        initCurrentYear();
        initNavbar();
        initTheme();
        initScrollSnap();
        initFeaturedCarousel();
        initPostEnhancements();
    });
})();
