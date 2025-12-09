// modules/module-05-loki/module.js

(function () {
  const sidebarLinks = document.querySelectorAll(".sidebar-link");
  const sections = document.querySelectorAll(".module-section");
  const completeBtn = document.getElementById("mark-complete-btn");
  const completeStatus = document.getElementById("complete-status");
  const STORAGE_KEY = "wao_module_5_complete";

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

  // Highlight active link based on scroll position (same pattern as Module 1 & 2)
  if ("IntersectionObserver" in window) {
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
  }

  // Completion state
  function updateCompleteUI(isComplete) {
    if (!completeStatus || !completeBtn) return;
    if (isComplete) {
      completeStatus.textContent = "Marked as complete on this browser.";
      completeBtn.textContent = "Module completed ✓";
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

  // -------- Copy-to-clipboard for code snippets --------

  function copyTextToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }

    // Fallback for older browsers
    return new Promise((resolve, reject) => {
      const textarea = document.createElement("textarea");
      textarea.value = text;
      textarea.style.position = "fixed";
      textarea.style.opacity = "0";
      document.body.appendChild(textarea);
      textarea.focus();
      textarea.select();
      try {
        const ok = document.execCommand("copy");
        document.body.removeChild(textarea);
        ok ? resolve() : reject();
      } catch (err) {
        document.body.removeChild(textarea);
        reject(err);
      }
    });
  }

  function initCodeCopyButtons() {
    const buttons = document.querySelectorAll(".code-snippet-copy");
    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const targetSelector = btn.getAttribute("data-copy-target");
        if (!targetSelector) return;
        const codeBlock = document.querySelector(targetSelector);
        if (!codeBlock) return;

        const text = codeBlock.textContent;

        copyTextToClipboard(text)
          .then(() => {
            const original = btn.textContent;
            btn.textContent = "Copied";
            btn.classList.add("copied");
            setTimeout(() => {
              btn.textContent = original;
              btn.classList.remove("copied");
            }, 1500);
          })
          .catch(() => {
            // ignore errors
          });
      });
    });
  }

  initCodeCopyButtons();
})();
