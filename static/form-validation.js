document.addEventListener('DOMContentLoaded', function() {
  const form = document.querySelector('form');

  // add red border to empty input fields
  form.addEventListener('submit', function(event) {
    const inputs = form.querySelectorAll('input');
    let isValid = true;

    for (let i = 0; i < inputs.length; i++) {
      if (inputs[i].value.trim() === '') {
        inputs[i].classList.add('is-invalid');
        isValid = false;
      } else {
        inputs[i].classList.remove('is-invalid');
      }
    }

  });

  // remove red border when user enters text
  form.addEventListener('input', function(event) {
    if (event.target.tagName === 'INPUT') {
      if (event.target.value.trim() === '') {
        event.target.classList.add('is-invalid');
      } else {
        event.target.classList.remove('is-invalid');
      }
    }
  });
});
