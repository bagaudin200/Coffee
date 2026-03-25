document.getElementById('briefForm').addEventListener('submit', async function(e) {
  e.preventDefault();

  const submitBtn = document.getElementById('submitBtn');
  const btnText = submitBtn.querySelector('.btn-text');
  const btnLoading = submitBtn.querySelector('.btn-loading');
  const errorDiv = document.getElementById('errorMessage');

  // Collect form data
  const formData = {
    coffee_name: document.getElementById('coffee_name').value.trim(),
    location: document.getElementById('location').value.trim(),
    coffee_type: document.getElementById('coffee_type').value,
    price_range: document.getElementById('price_range').value,
    target_audience: document.getElementById('target_audience').value.trim(),
    unique_features: document.getElementById('unique_features').value.trim(),
    competitors: document.getElementById('competitors').value.trim(),
    social_media: document.getElementById('social_media').value.trim(),
    additional_info: document.getElementById('additional_info').value.trim(),
  };

  // Validate
  const required = ['coffee_name', 'location', 'coffee_type', 'price_range', 'target_audience'];
  for (const field of required) {
    if (!formData[field]) {
      showError('Пожалуйста, заполните все обязательные поля.');
      return;
    }
  }

  // Show loading
  btnText.classList.add('hidden');
  btnLoading.classList.remove('hidden');
  submitBtn.disabled = true;
  errorDiv.classList.add('hidden');

  try {
    const response = await fetch('/api/generate-preview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    });

    const data = await response.json();

    if (data.success) {
      window.location.href = '/preview';
    } else {
      showError(data.error || 'Произошла ошибка. Попробуйте ещё раз.');
      resetBtn();
    }
  } catch (err) {
    showError('Ошибка соединения. Проверьте интернет и попробуйте снова.');
    resetBtn();
  }

  function showError(msg) {
    errorDiv.textContent = msg;
    errorDiv.classList.remove('hidden');
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function resetBtn() {
    btnText.classList.remove('hidden');
    btnLoading.classList.add('hidden');
    submitBtn.disabled = false;
  }
});

// Character counter for textareas
document.querySelectorAll('textarea[maxlength]').forEach(ta => {
  const max = parseInt(ta.getAttribute('maxlength'));
  const hint = ta.closest('.form-group').querySelector('.field-hint');
  if (hint) {
    ta.addEventListener('input', function() {
      const remaining = max - this.value.length;
      if (remaining < 100) {
        hint.textContent = `Осталось символов: ${remaining}`;
        hint.style.color = remaining < 20 ? '#C0392B' : '#888';
      }
    });
  }
});
