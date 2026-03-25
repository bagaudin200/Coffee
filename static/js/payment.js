// Stripe button
const stripeBtn = document.getElementById('stripeBtn');
if (stripeBtn) {
  stripeBtn.addEventListener('click', async function() {
    this.disabled = true;
    this.textContent = 'Перенаправляем...';

    try {
      const response = await fetch('/api/stripe-checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      const data = await response.json();

      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        // Stripe not configured - hide button, show demo only
        document.getElementById('stripeBlock').style.display = 'none';
        this.disabled = false;
      }
    } catch (err) {
      document.getElementById('stripeBlock').style.display = 'none';
    }
  });
}

// Demo payment form
document.getElementById('paymentForm').addEventListener('submit', async function(e) {
  e.preventDefault();

  const payBtn = document.getElementById('payBtn');
  const btnText = payBtn.querySelector('.btn-text');
  const btnLoading = payBtn.querySelector('.btn-loading');
  const errorDiv = document.getElementById('paymentError');

  const email = document.getElementById('email').value.trim();
  const paymentCode = document.getElementById('payment_code').value.trim();

  if (!email || !paymentCode) {
    showError('Пожалуйста, заполните все поля.');
    return;
  }

  // Show loading
  btnText.classList.add('hidden');
  btnLoading.classList.remove('hidden');
  payBtn.disabled = true;
  errorDiv.classList.add('hidden');

  try {
    const response = await fetch('/api/process-payment', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, payment_code: paymentCode })
    });

    const data = await response.json();

    if (data.success) {
      window.location.href = '/success';
    } else {
      showError(data.error || 'Ошибка оплаты. Проверьте код и попробуйте снова.');
      resetBtn();
    }
  } catch (err) {
    showError('Ошибка соединения. Попробуйте ещё раз.');
    resetBtn();
  }

  function showError(msg) {
    errorDiv.textContent = msg;
    errorDiv.classList.remove('hidden');
  }

  function resetBtn() {
    btnText.classList.remove('hidden');
    btnLoading.classList.add('hidden');
    payBtn.disabled = false;
  }
});

// Auto-uppercase payment code
const codeInput = document.getElementById('payment_code');
if (codeInput) {
  codeInput.addEventListener('input', function() {
    this.value = this.value.toUpperCase();
  });
}
