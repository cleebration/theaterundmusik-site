// Menü (Handy) + einfache Lightbox für Bilder mit data-lightbox
document.addEventListener("DOMContentLoaded", () => {
  const head = document.querySelector(".head"), t = document.querySelector(".nav-toggle");
  t?.addEventListener("click", () => {
    const open = head.classList.toggle("open");
    t.setAttribute("aria-expanded", open);
  });

  const links = [...document.querySelectorAll("a[data-lightbox]")];
  if (!links.length) return;
  let box, img, i = 0, set = [];
  const show = (k) => { i = (k + set.length) % set.length; img.src = set[i].href; img.alt = set[i].querySelector("img")?.alt || ""; };
  const close = () => { box?.remove(); box = null; document.removeEventListener("keydown", key); };
  const key = (e) => { if (e.key === "Escape") close(); if (e.key === "ArrowRight") show(i + 1); if (e.key === "ArrowLeft") show(i - 1); };
  links.forEach((a) => a.addEventListener("click", (e) => {
    e.preventDefault();
    const g = a.dataset.lightbox;
    set = g ? links.filter((x) => x.dataset.lightbox === g && x.closest(".gallery") === a.closest(".gallery")) : [a];
    box = document.createElement("div");
    box.className = "lb"; box.setAttribute("role", "dialog"); box.setAttribute("aria-modal", "true");
    box.innerHTML = '<img alt=""><button class="x" aria-label="Schließen">×</button>' +
      (set.length > 1 ? '<button class="p" aria-label="Zurück">‹</button><button class="n" aria-label="Weiter">›</button>' : "");
    img = box.querySelector("img");
    box.addEventListener("click", (ev) => {
      if (ev.target.classList.contains("n")) show(i + 1);
      else if (ev.target.classList.contains("p")) show(i - 1);
      else if (ev.target !== img) close();
    });
    document.body.append(box);
    document.addEventListener("keydown", key);
    show(set.indexOf(a));
    box.querySelector(".x").focus();
  }));
});
