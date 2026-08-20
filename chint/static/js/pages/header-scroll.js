(function () {
  const header = document.getElementById("siteHeader");
  if (!header) return;

  const THRESHOLD = 12; // сколько пикселей вниз — и меняем стиль

  function onScroll() {
    if (window.scrollY > THRESHOLD) {
      header.classList.add("is-scrolled");
    } else {
      header.classList.remove("is-scrolled");
    }
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll(); // сразу при загрузке (если страница открыта не сверху)
})();


const burger = document.getElementById('burgerBtn');
const menu = document.getElementById('mobileMenu');
const body = document.body;

burger.addEventListener('click', () => {
  menu.classList.toggle('is-open');
  body.classList.toggle('lock');
});
