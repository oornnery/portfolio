import { Controller } from "@hotwired/stimulus";

/**
 * Stimulus controller: reading-progress
 *
 * Updates a progress bar (scaleX transform) based on scroll position
 * relative to the post content element.
 *
 * The controller element IS the reading-progress root (is-active toggle target).
 * Only the inner bar is declared as a Stimulus target.
 *
 * HTML structure:
 *   <div class="reading-progress"
 *        data-controller="reading-progress"
 *        data-reading-progress-content-selector-value="[data-post-content]"
 *        aria-hidden="true">
 *     <div class="reading-progress__bar" data-reading-progress-target="bar"></div>
 *   </div>
 *
 * Note: bar.style.transform is set via JavaScript (not an inline HTML attribute),
 * which is permitted under style-src 'self' CSP — only HTML style= attributes
 * and <style> blocks are restricted, not JS DOM style mutations.
 */
export default class ReadingProgressController extends Controller {
    static targets = ["bar"];
    static values = {
        contentSelector: { type: String, default: "[data-post-content]" },
    };

    connect() {
        this._content = document.querySelector(this.contentSelectorValue);
        if (!this._content || !this.hasBarTarget) return;

        this._update = () => this._tick();
        addEventListener("scroll", this._update, { passive: true });
        addEventListener("resize", this._update);
        this._tick();
    }

    disconnect() {
        if (this._update) {
            removeEventListener("scroll", this._update);
            removeEventListener("resize", this._update);
        }
    }

    _tick() {
        const content = this._content;
        const bar = this.barTarget;

        const rect = content.getBoundingClientRect();
        const contentTop = rect.top + scrollY;
        const contentHeight = content.offsetHeight;

        if (contentHeight <= 0) {
            bar.style.transform = "scaleX(0)";
            return;
        }

        const start = contentTop - innerHeight * 0.2;
        const end = contentTop + contentHeight - innerHeight * 0.7;
        const progress = Math.max(
            0,
            Math.min(1, (scrollY - start) / Math.max(end - start, 1)),
        );

        bar.style.transform = `scaleX(${progress})`;
        // this.element is the controller root (.reading-progress div)
        this.element.classList.toggle("is-active", progress > 0 && progress < 1);
    }
}
