// static/js/calendar-live.js

(function () {
    // == Public API na okno (nech vieš zavolať manuálne ak treba) ==
    window.refreshNextMatch = refreshNextMatch;
    window.initNextCountdown = initCountdown;
  
    // == Auto-hook na AJAX úspechy konkrétnych endpointov ==
    // Nemusíš meniť svoj existujúci kód ukladania; keď prebehne úspech
    // na /calendar/insert, /calendar/update alebo /calendar/ajax_delete,
    // automaticky sa refreshne box "Najbližší zápas".
    if (window.jQuery) {
      jQuery(document).ajaxSuccess(function (_e, _xhr, settings) {
        try {
          var url = settings && settings.url ? settings.url : "";
          if (
            url.indexOf("/calendar/insert") === 0 ||
            url.indexOf("/calendar/update") === 0 ||
            url.indexOf("/calendar/ajax_delete") === 0
          ) {
            refreshNextMatch();
          }
        } catch (err) {
          console.error("ajaxSuccess hook error:", err);
        }
      });
    }
  
    // == Pri prvom načítaní stránky spusti countdown z aktuálneho DOMu ==
    document.addEventListener("DOMContentLoaded", function () {
      var startEl = document.getElementById("next-start");
      if (startEl && startEl.dataset && startEl.dataset.start) {
        initCountdown(startEl.dataset.start);
      }
    });
  
    // === Funkcie ===
  
    // Dotiahne nový HTML fragment a nahradí #next-match-container;
    // potom reštartuje countdown.
    function refreshNextMatch() {
      if (!window.jQuery) {
        console.error("refreshNextMatch: jQuery nie je k dispozícii.");
        return;
      }
      jQuery.get("/calendar/next-fragment", function (html) {
        var $ = jQuery;
        var container = $("#next-match-container");
        if (!container.length) {
          console.warn(
            "Nenájdený #next-match-container – pridaj obal okolo sekcie 'Najbližší zápas'."
          );
        } else {
          container.html(html);
        }
  
        // nájdi dátum a spusti countdown
        var startEl = document.getElementById("next-start");
        if (startEl && startEl.dataset && startEl.dataset.start) {
          initCountdown(startEl.dataset.start);
        } else {
          // nič na odpočítavanie
          clearExistingTimer();
        }
      }).fail(function () {
        console.error("Nepodarilo sa načítať /calendar/next-fragment.");
      });
    }
  
    // Jednoduchý countdown s jedným intervalom na stránke.
    var _countdownTimer = null;
  
    function clearExistingTimer() {
      if (_countdownTimer) {
        clearInterval(_countdownTimer);
        _countdownTimer = null;
      }
    }
  
    function initCountdown(dateStr) {
      var target = Date.parse(dateStr);
      var el = document.getElementById("countdown");
      var elDesc = document.getElementById("countdown_desc");
      var frame = document.getElementById("liveFrame");
  
      if (!el || !elDesc || !frame || isNaN(target)) {
        clearExistingTimer();
        return;
      }
  
      frame.style.display = "block";
      clearExistingTimer();
  
      _countdownTimer = setInterval(function () {
        var now = Date.now();
        var dist = target - now;
  
        if (dist <= 0) {
          clearExistingTimer();
          el.textContent = "HRÁ SA";
          return;
        }
  
        var d = Math.floor(dist / (1000 * 60 * 60 * 24));
        var h = Math.floor((dist % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var m = Math.floor((dist % (1000 * 60 * 60)) / (1000 * 60));
        var s = Math.floor((dist % (1000 * 60)) / 1000);
  
        elDesc.textContent = "deň | hod | min | sek";
        el.innerHTML =
          '<button class="btn-live">' + d + "</button>" +
          '<button class="btn-live">' + h + "</button>" +
          '<button class="btn-live">' + m + "</button>" +
          '<button class="btn-live">' + s + "</button>";
      }, 1000);
    }
  })();
  