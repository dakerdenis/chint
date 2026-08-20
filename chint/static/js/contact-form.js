document.addEventListener("DOMContentLoaded", () => {
  const forms = document.querySelectorAll('form[data-form="contact"]');

  forms.forEach(form => {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const result = form.querySelector(".contact__form-result");
      result.hidden = true;

      const data = new FormData(form);

      try {
        const response = await fetch(form.action, {
          method: "POST",
          headers: {
            "X-Requested-With": "XMLHttpRequest",
          },
          body: data
        });

        const json = await response.json();

        result.hidden = false;
        result.textContent = json.message;

        if (json.success) {
          form.reset();
        }

      } catch (err) {
        result.hidden = false;
        result.textContent = "Error. Try again later.";
      }
    });
  });
});
