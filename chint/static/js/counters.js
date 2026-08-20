(function () {
  const items = Array.from(document.querySelectorAll("[data-count][data-target]"));
  if (!items.length) return;

  const prefersReduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function formatNumber(n) {
    // можно заменить на Intl.NumberFormat('ru-RU') если хочешь пробелы/запятые
    return Math.round(n).toString();
  }

  function animate(el) {
    if (el.dataset.done === "1") return;
    el.dataset.done = "1";

    const target = Number(el.dataset.target || "0");
    const prefix = el.dataset.prefix || "";
    const suffix = el.dataset.suffix || "";

    if (prefersReduced) {
      el.textContent = `${prefix}${formatNumber(target)}${suffix}`;
      return;
    }

    const duration = 1600; // ms (можешь 800-1600)
    const start = performance.now();

    function tick(now) {
      const t = Math.min((now - start) / duration, 1);
      // easing (красивее чем линейно)
      const eased = 1 - Math.pow(1 - t, 3); // easeOutCubic
      const value = target * eased;

      el.textContent = `${prefix}${formatNumber(value)}${suffix}`;

      if (t < 1) requestAnimationFrame(tick);
    }

    requestAnimationFrame(tick);
  }

  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          animate(entry.target);
          observer.unobserve(entry.target); // один раз
        }
      }
    },
    { threshold: 0.45 } // когда почти половина видна
  );

  items.forEach((el) => observer.observe(el));
})();
