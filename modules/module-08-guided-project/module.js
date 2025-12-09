// modules/module-03-telemetry/module.js
(function () {
  const sidebarLinks = document.querySelectorAll(".sidebar-link");
  const sections = document.querySelectorAll(".module-section");
  const completeBtn = document.getElementById("mark-complete-btn");
  const completeStatus = document.getElementById("complete-status");
  const STORAGE_KEY = "wao_module_8_complete";

  // Smooth scrolling
  sidebarLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const target = document.querySelector(link.getAttribute("href"));
      if (target) {
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });

  // Active sidebar highlight based on scroll
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const id = entry.target.getAttribute("id");
        sidebarLinks.forEach((link) => {
          link.classList.toggle(
            "active",
            link.getAttribute("href") === `#${id}`
          );
        });
      });
    },
    { rootMargin: "-45% 0px -45% 0px", threshold: 0.1 }
  );

  sections.forEach((section) => observer.observe(section));

  // Completion state
  function updateCompleteUI(isComplete) {
    if (!completeStatus || !completeBtn) return;
    if (isComplete) {
      completeStatus.textContent = "Marked as complete on this browser.";
      completeBtn.textContent = "Completed ✔";
      completeBtn.disabled = true;
    } else {
      completeStatus.textContent = "Not marked as complete yet.";
      completeBtn.textContent = "Mark this module as complete";
      completeBtn.disabled = false;
    }
  }

  const stored = localStorage.getItem(STORAGE_KEY) === "true";
  updateCompleteUI(stored);

  if (completeBtn) {
    completeBtn.addEventListener("click", () => {
      localStorage.setItem(STORAGE_KEY, "true");
      updateCompleteUI(true);
    });
  }
})();
