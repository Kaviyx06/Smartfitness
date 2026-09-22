// Smart Fitness Monitor - simple client-side helpers
document.addEventListener("DOMContentLoaded", function () {
  // Auto-dismiss success alerts after a few seconds
  document.querySelectorAll(".alert-success").forEach(function (el) {
    setTimeout(function () {
      el.classList.add("fade");
      el.style.opacity = "0";
    }, 4000);
  });

  console.log("Smart Fitness Monitor UI loaded.");
});
