/* lobby.js — lobby page interactions */
(function () {
  const form = document.querySelector("form");
  const btn  = form && form.querySelector("button[type=submit]");

  if (form && btn) {
    form.addEventListener("submit", () => {
      btn.disabled = true;
      btn.textContent = "Đang tạo phòng…";
      btn.style.opacity = "0.7";
    });
  }
})();
