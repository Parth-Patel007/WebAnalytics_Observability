// module-01-web-analytics/module.js

(function () {
  const sidebarLinks = document.querySelectorAll(".sidebar-link");
  const sections = document.querySelectorAll(".module-section");
  const completeBtn = document.getElementById("mark-complete-btn");
  const completeStatus = document.getElementById("complete-status");
  const STORAGE_KEY = "wao_module_1_complete";

  // Smooth scroll for sidebar links
  sidebarLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const targetId = link.getAttribute("href");
      const target = document.querySelector(targetId);
      if (!target) return;
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  // Highlight active link based on scroll position
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
    {
      rootMargin: "-45% 0px -45% 0px",
      threshold: 0.1,
    }
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

  const storedValue = localStorage.getItem(STORAGE_KEY);
  const initiallyComplete = storedValue === "true";
  updateCompleteUI(initiallyComplete);

  if (completeBtn) {
    completeBtn.addEventListener("click", () => {
      localStorage.setItem(STORAGE_KEY, "true");
      updateCompleteUI(true);
    });
  }
})();
