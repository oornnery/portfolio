import { Controller } from "@hotwired/stimulus";

/**
 * Stimulus controller: toc
 *
 * Auto-generates a Table of Contents from h2/h3 headings in the post content,
 * tracks the active heading on scroll, and supports hash-based navigation.
 *
 * HTML structure:
 *   <div data-controller="toc" data-toc-content-selector-value="[data-post-content]">
 *     <div class="hidden" data-toc-target="wrapper">
 *       <nav data-toc-target="container"></nav>
 *     </div>
 *   </div>
 */
export default class TocController extends Controller {
    static targets = ["wrapper", "container"];
    static values = { contentSelector: { type: String, default: "[data-post-content]" } };

    connect() {
        const content = document.querySelector(this.contentSelectorValue);
        if (!content) return;

        this._content = content;
        this._links = [];
        this._raf = false;

        this._build();

        if (this._links.length === 0) return;

        this.wrapperTarget.classList.remove("hidden");

        this._onScroll = () => {
            if (this._raf) return;
            this._raf = true;
            requestAnimationFrame(() => {
                this._raf = false;
                this._updateActive();
            });
        };
        this._onResize = () => {
            this._updateLayout();
            this._updateActive();
        };
        this._onHashChange = () => {
            const hash = decodeURIComponent(location.hash.replace(/^#/, ""));
            if (!hash) return;
            const match = this._links.find((l) => l.heading.id === hash);
            if (match) this._setActive(match.heading.id);
        };

        addEventListener("scroll", this._onScroll, { passive: true });
        addEventListener("resize", this._onResize);
        addEventListener("hashchange", this._onHashChange);

        this._updateLayout();
        location.hash ? this._onHashChange() : this._updateActive();
    }

    disconnect() {
        if (this._onScroll) removeEventListener("scroll", this._onScroll);
        if (this._onResize) removeEventListener("resize", this._onResize);
        if (this._onHashChange) removeEventListener("hashchange", this._onHashChange);
    }

    _slugify(text) {
        return text
            .normalize("NFKD")
            .replace(/[^\w\s-]/g, "")
            .trim()
            .toLowerCase()
            .replace(/[\s-]+/g, "-")
            .replace(/^-|-$/g, "");
    }

    _build() {
        const content = this._content;
        const usedIds = new Set(
            [...content.querySelectorAll("[id]")].map((el) => el.id).filter(Boolean),
        );

        const headings = [...content.querySelectorAll("h2, h3")].filter(
            (h) => h.textContent?.trim(),
        );

        this.containerTarget.textContent = "";

        for (const [i, heading] of headings.entries()) {
            if (!heading.id) {
                let base = this._slugify(heading.textContent ?? "") || `section-${i + 1}`;
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
            link.addEventListener("click", () => this._setActive(heading.id));
            this.containerTarget.appendChild(link);
            this._links.push({ heading, link });
        }
    }

    _setActive(id) {
        for (const { heading, link } of this._links) {
            link.classList.toggle("is-active", heading.id === id);
        }
    }

    _updateLayout() {
        const links = this._links;
        if (links.length === 0) return;

        if (links.length === 1) {
            const label = links[0].heading.textContent.trim();
            links[0].link.style.setProperty("--toc-offset", "50%");
            links[0].link.dataset.label = label;
            links[0].link.setAttribute("aria-label", label);
            return;
        }

        const offsets = links.map((l) => l.heading.offsetTop);
        const min = Math.min(...offsets);
        const max = Math.max(...offsets);
        const range = Math.max(max - min, 1);

        links.forEach(({ heading, link }, i) => {
            const text = heading.textContent.trim();
            const mapped = 8 + ((offsets[i] - min) / range) * 84;
            link.style.setProperty("--toc-offset", `${mapped}%`);
            link.dataset.label = text;
            link.setAttribute("aria-label", text);
        });
    }

    _updateActive() {
        const links = this._links;
        if (links.length === 0) return;

        const pageH = document.documentElement.scrollHeight;
        if (scrollY + innerHeight >= pageH - 2) {
            this._setActive(links.at(-1).heading.id);
            return;
        }

        const content = this._content;
        const baseOffset = Math.max(96, innerHeight * 0.12);
        const remaining =
            scrollY + content.getBoundingClientRect().bottom - scrollY - innerHeight;
        const boost = Math.max(0, innerHeight * 0.45 - remaining);
        const line = scrollY + baseOffset + boost;

        let idx = 0;
        for (const [i, { heading }] of links.entries()) {
            if (scrollY + heading.getBoundingClientRect().top <= line) idx = i;
        }
        this._setActive(links[idx].heading.id);
    }
}
