(() => {
    document.documentElement.classList.add("js-enabled");

    const yearNodes = document.querySelectorAll("[data-current-year]");
    const year = String(new Date().getFullYear());
    for (const node of yearNodes) {
        node.textContent = year;
    }
})();
