(function () {
    "use strict";

    function setCurrentYear() {
        const year = String(new Date().getFullYear());
        document.querySelectorAll("[data-current-year]").forEach((node) => {
            node.textContent = year;
        });
    }

    function initMobileMenu() {
        const menuButton = document.querySelector("[data-menu-toggle]");
        const mobileMenu = document.querySelector("[data-mobile-menu]");

        if (!menuButton || !mobileMenu) {
            return;
        }

        const menuIcon = menuButton.querySelector(".menu-icon");
        const closeIcon = menuButton.querySelector(".close-icon");

        function closeMenu() {
            mobileMenu.classList.add("hidden");
            menuButton.setAttribute("aria-expanded", "false");
            if (menuIcon) {
                menuIcon.classList.remove("hidden");
            }
            if (closeIcon) {
                closeIcon.classList.add("hidden");
            }
        }

        menuButton.addEventListener("click", () => {
            const isHidden = mobileMenu.classList.toggle("hidden");
            menuButton.setAttribute("aria-expanded", String(!isHidden));

            if (menuIcon) {
                menuIcon.classList.toggle("hidden", !isHidden);
            }
            if (closeIcon) {
                closeIcon.classList.toggle("hidden", isHidden);
            }
        });

        mobileMenu.querySelectorAll("a").forEach((link) => {
            link.addEventListener("click", closeMenu);
        });

        window.addEventListener("resize", () => {
            if (window.innerWidth >= 768) {
                closeMenu();
            }
        });
    }

    function initScrollSnap() {
        const container = document.querySelector(".scroll-snap-container");
        if (!container) {
            return;
        }

        function scrollToNextSection() {
            const sections = Array.from(container.querySelectorAll(".snap-section"));
            if (sections.length === 0) {
                return;
            }

            const currentScrollTop = container.scrollTop;
            const viewportHeight = container.clientHeight || window.innerHeight;
            const currentSection = Math.round(currentScrollTop / viewportHeight);
            const nextIndex = Math.min(currentSection + 1, sections.length - 1);
            sections[nextIndex].scrollIntoView({ behavior: "smooth", block: "start" });
        }

        container.querySelectorAll(".scroll-indicator").forEach((indicator) => {
            indicator.style.cursor = "pointer";
            indicator.addEventListener("click", scrollToNextSection);
        });

        const mobileMediaQuery = window.matchMedia("(max-width: 1024px)");
        const applySnapMode = () => {
            container.style.scrollSnapType = mobileMediaQuery.matches
                ? "y proximity"
                : "y mandatory";
        };

        applySnapMode();
        mobileMediaQuery.addEventListener("change", applySnapMode);
    }

    function init() {
        setCurrentYear();
        initMobileMenu();
        initScrollSnap();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

    window.App = {
        init,
    };
})();
