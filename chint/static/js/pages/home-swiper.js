(function () {
  const el = document.querySelector(".homeSwiper");
  if (!el || typeof Swiper === "undefined") return;

  const bar = document.querySelector(".home-swiper-progress__bar");

  const swiper = new Swiper(".homeSwiper", {
    loop: true,
    speed: 700,

    // autoplay = “полоса заполняется → слайд меняется”
    autoplay: {
      delay: 9000,
      disableOnInteraction: false,
      pauseOnMouseEnter: true,
    },

    navigation: {
      nextEl: ".homeSwiperNext",
      prevEl: ".homeSwiperPrev",
    },

    pagination: {
      el: ".homeSwiperPagination",
      clickable: true,
    },

    on: {
      autoplayTimeLeft(s, time, progress) {
        // progress: 0..1 (1 = закончился)
        const pct = Math.round((1 - progress) * 100);
        if (bar) bar.style.width = pct + "%";
      },
      slideChangeTransitionStart() {
        // чтобы при ручном перелистывании “не зависало”
        if (bar) bar.style.width = "0%";
      },
    },
  });
})();

new Swiper(".recommendSwiper", {

  loop: true,
  speed: 800,

  autoplay: {
    delay: 3500,
    disableOnInteraction: false,
    pauseOnMouseEnter: true,
  },

  slidesPerView: 4,
  spaceBetween: 30,

  navigation: {
    nextEl: ".recommendNext",
    prevEl: ".recommendPrev",
  },

  breakpoints: {

    0: {
      slidesPerView: 1,
      spaceBetween: 20
    },

    480: {
      slidesPerView: 2,
      spaceBetween: 20
    },

    768: {
      slidesPerView: 3,
      spaceBetween: 25
    },

    1100: {
      slidesPerView: 4,
      spaceBetween: 30
    }

  }

});