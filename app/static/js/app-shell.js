(function () {
    const modalEl = document.getElementById("calendarModal");
    if (!modalEl) return;
  
    const modal = new bootstrap.Modal(modalEl, { backdrop: true, keyboard: true });
  
    // Open calendar
    document.addEventListener("click", (e) => {
      const btn = e.target.closest("[data-open-calendar]");
      if (!btn) return;
  
      modal.show();
  
      // trigger HTMX načítanie obsahu do modalu
      document.body.dispatchEvent(new Event("calendar:load"));
    });
  
    // Keď sa modal zobrazí, FullCalendar často potrebuje render
    modalEl.addEventListener("shown.bs.modal", () => {
      try {
        // ak je FC už inicializovaný, prepočíta layout
        const cal = window.jQuery && window.jQuery("#schedule-calendar");
        if (cal && cal.length) cal.fullCalendar("render");
      } catch (e) {}
    });
  
    // Voliteľné: keď zatvoríš modal, nechať obsah v pamäti (lepší UX)
    // Ak chceš vždy fresh reload, odkomentuj:
    /*
    modalEl.addEventListener("hidden.bs.modal", () => {
      const inner = document.getElementById("calendar-modal-body-inner");
      if (inner) inner.innerHTML = '<div class="text-center p-4" style="opacity:.8;">Načítavam…</div>';
    });
    */
  })();
  