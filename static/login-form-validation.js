document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");

  // add red border to empty input fields
  form.addEventListener("submit", function (event) {
    const inputs = form.querySelectorAll("input");
    let isValid = true;

    for (let i = 0; i < inputs.length; i++) {
      if (inputs[i].value.trim() === "") {
        inputs[i].classList.add("is-invalid");
        isValid = false;
        localStorage.setItem(inputs[i].id, "invalid");
      } else {
        inputs[i].classList.remove("is-invalid");
        localStorage.setItem(inputs[i].id, "valid");
      }
    }

    if (isValid) {
      localStorage.clear(); // clear local storage on valid submission
    }
  });

  // remove red border when user enters text
  form.addEventListener("input", function (event) {
    if (event.target.tagName === "INPUT") {
      if (event.target.value.trim() === "") {
        event.target.classList.add("is-invalid");
        localStorage.setItem(event.target.id, "invalid");
      } else {
        event.target.classList.remove("is-invalid");
        localStorage.setItem(event.target.id, "valid");
      }
    }
  });

  // load validity state from local storage on page load
  const inputs = form.querySelectorAll("input");
  for (let i = 0; i < inputs.length; i++) {
    const validity = localStorage.getItem(inputs[i].id);
    if (validity === "invalid") {
      inputs[i].classList.add("is-invalid");
    } else if (validity === "valid") {
      inputs[i].classList.remove("is-invalid");
    }
  }
});
