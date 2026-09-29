// Keyboard shortcuts for the review page and answer timing.
(() => {
  const reveal = document.getElementById("reveal");
  const form = document.querySelector("form.ratings");
  const shownAt = performance.now();

  form?.addEventListener("submit", (event) => {
    // Disabling buttons would drop the clicked rating from the form data,
    // so guard against double submits with a flag instead.
    if (form.dataset.sent) {
      event.preventDefault();
      return;
    }
    form.dataset.sent = "1";
    form.elements.duration_ms.value = Math.round(performance.now() - shownAt);
  });

  document.addEventListener("keydown", (event) => {
    if (event.metaKey || event.ctrlKey || event.altKey || event.target.closest("input, textarea, select")) return;

    if (event.key === "Escape") {
      window.location.href = "/";
      return;
    }
    if (!reveal) return;

    if (!reveal.open && (event.key === " " || event.key === "Enter")) {
      event.preventDefault();
      reveal.open = true;
      return;
    }
    if (reveal.open && ["1", "2", "3", "4"].includes(event.key)) {
      event.preventDefault();
      form?.querySelector(`button[value="${event.key}"]`)?.click();
    }
  });
})();
