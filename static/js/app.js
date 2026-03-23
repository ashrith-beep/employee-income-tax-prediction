/* app.js – Client-side logic for TaxAI */

$(document).ready(function() {

  // Auto-dismiss Flash Messages
  setTimeout(function() {
    $('.alert').fadeOut('slow', function() {
      $(this).remove();
    });
  }, 5000);

  // Password toggle
  $('.toggle-pw').on('click', function(e) {
    e.preventDefault();
    const targetId = $(this).data('target');
    if (!targetId) return;
    const $input = $('#' + targetId);
    if ($input.length) {
      if ($input.attr('type') === 'password') {
        $input.attr('type', 'text');
        $(this).find('i').removeClass('bi-eye').addClass('bi-eye-slash');
        $(this).text('🙈');
      } else {
        $input.attr('type', 'password');
        $(this).find('i').removeClass('bi-eye-slash').addClass('bi-eye');
        $(this).text('👁');
      }
    }
  });

  // Password Strength Meter
  $('#register-password').on('input', function() {
    const pw = $(this).val();
    const $bar = $('#pw-bar');
    if ($bar.length === 0) return;

    let strength = 0;
    if (pw.length >= 6) strength++;
    if (pw.length >= 10) strength++;
    if (/[A-Z]/.test(pw)) strength++;
    if (/[0-9]/.test(pw)) strength++;
    if (/[^a-zA-Z0-9]/.test(pw)) strength++;

    const levels = [
      { width: '0%', class: '', text: '' },
      { width: '25%', class: 'bg-danger', text: 'Weak' },
      { width: '50%', class: 'bg-warning text-dark', text: 'Fair' },
      { width: '75%', class: 'bg-info text-dark', text: 'Good' },
      { width: '100%', class: 'bg-success', text: 'Strong' }
    ];

    const lvl = levels[Math.min(strength, 4)];
    $bar.css('width', lvl.width)
        .removeClass('bg-danger bg-warning bg-info bg-success text-dark')
        .addClass(lvl.class)
        .text(lvl.text);
  });

  // Range Slider Sync
  $('input[type="range"]').on('input', function() {
    const targetId = $(this).attr('id').replace('-slider', '');
    $('#' + targetId).val($(this).val());
  });

  // Tooltips Init
  if(typeof bootstrap !== 'undefined') {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl)
    });
  }

  // --- Validations ---
  function isValidEmail(email) {
    return /^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$/.test(email.trim());
  }

  function markInvalid($el, msg) {
    $el.addClass('is-invalid').removeClass('is-valid');
    
    let $errDiv = $el.siblings('.invalid-feedback');
    if ($errDiv.length === 0) {
      $errDiv = $el.closest('.input-group, .form-floating').siblings('.invalid-feedback');
      if ($errDiv.length === 0) {
          $el.after('<div class="invalid-feedback"></div>');
          $errDiv = $el.next('.invalid-feedback');
      }
    }
    $errDiv.text(msg);
  }

  function markValid($el) {
    $el.removeClass('is-invalid').addClass('is-valid');
    let $errDiv = $el.siblings('.invalid-feedback');
    if ($errDiv.length === 0) {
      $errDiv = $el.closest('.input-group, .form-floating').siblings('.invalid-feedback');
    }
    if ($errDiv.length) {
      $errDiv.text('');
    }
  }

  // Login Form
  $('#login-form').on('submit', function(e) {
    let valid = true;
    const $email = $('#login-email');
    const $pw = $('#login-password');

    if ($email.length && !isValidEmail($email.val())) {
      markInvalid($email, 'Please enter a valid email address.');
      valid = false;
    } else if ($email.length) {
      markValid($email);
    }

    if ($pw.length && $pw.val().trim() === '') {
      markInvalid($pw, 'Password is required.');
      valid = false;
    } else if ($pw.length) {
      markValid($pw);
    }

    if (!valid) e.preventDefault();
  });

  // Register Form
  $('#register-form').on('submit', function(e) {
    let valid = true;
    const $email = $('#register-email');
    const $pw = $('#register-password');
    const $confirm = $('#confirm-password');

    if ($email.length && !isValidEmail($email.val())) {
      markInvalid($email, 'Please enter a valid email address.');
      valid = false;
    } else if ($email.length) {
      markValid($email);
    }

    if ($pw.length && $pw.val().length < 6) {
      markInvalid($pw, 'Password must be at least 6 characters.');
      valid = false;
    } else if ($pw.length) {
      markValid($pw);
    }

    if ($confirm.length && $pw.length && $confirm.val() !== $pw.val()) {
      markInvalid($confirm, 'Passwords do not match.');
      valid = false;
    } else if ($confirm.length) {
      markValid($confirm);
    }

    if (!valid) e.preventDefault();
  });

  // Predict Form validation
  $('#predict-form').on('submit', function(e) {
    // Show spinner if valid
    let valid = true;
    const $salary = $('#annual_salary');
    if($salary.length && parseFloat($salary.val()) < 0) {
        markInvalid($salary, 'Salary cannot be negative');
        valid = false;
    }
    
    if (valid) {
      const $btn = $(this).find('button[type="submit"]');
      $btn.html('<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Processing...');
      $btn.prop('disabled', true);
    } else {
      e.preventDefault();
    }
  });

});
