document.addEventListener("DOMContentLoaded", () => {

    const slides = document.querySelectorAll(".hero-slide");
    const dots = document.querySelectorAll(".carousel-dot");
    const btnNext = document.querySelector(".carousel-next");
    const btnPrev = document.querySelector(".carousel-prev");

    let currentSlide = 0;
    const totalSlides = slides.length;

    function updateCarousel(index) {

        slides.forEach(slide => {
            slide.classList.remove("active");
        });

        dots.forEach(dot => {
            dot.classList.remove("active");
        });

        slides[index].classList.add("active");
        dots[index].classList.add("active");

        currentSlide = index;
    }

    if (btnNext) {
        btnNext.addEventListener("click", () => {
            const nextIndex = (currentSlide + 1) % totalSlides;
            updateCarousel(nextIndex);
        });
    }

    if (btnPrev) {
        btnPrev.addEventListener("click", () => {
            const prevIndex =
                (currentSlide - 1 + totalSlides) % totalSlides;

            updateCarousel(prevIndex);
        });
    }

    dots.forEach((dot, index) => {
        dot.addEventListener("click", () => {
            updateCarousel(index);
        });
    });

    setInterval(() => {
        const nextIndex = (currentSlide + 1) % totalSlides;
        updateCarousel(nextIndex);
    }, 5000);

});