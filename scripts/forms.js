/**
 * Form handling for Synapse Landing Page
 * Manages email capture forms with validation and submission
 */

class EmailCapture {
  constructor(formElement) {
    this.form = formElement;
    this.input = formElement.querySelector('input[type="email"]');
    this.button = formElement.querySelector('button[type="submit"]');
    this.errorElement = formElement.querySelector('.form__error');
    this.isSubmitting = false;
    this.validationTimeout = null;
    
    this.init();
    this.setupAccessibility();
  }

  init() {
    this.setupEventListeners();
    this.setupValidation();
  }

  setupAccessibility() {
    // Ensure proper ARIA attributes
    if (!this.input.getAttribute('aria-describedby') && this.errorElement) {
      this.input.setAttribute('aria-describedby', this.errorElement.id);
    }

    // Ensure error element has proper attributes
    if (this.errorElement) {
      this.errorElement.setAttribute('role', 'alert');
      this.errorElement.setAttribute('aria-live', 'polite');
      this.errorElement.setAttribute('aria-atomic', 'true');
    }

    // Add proper button attributes
    if (this.button) {
      this.button.setAttribute('aria-describedby', this.errorElement?.id || '');
    }

    // Set up keyboard navigation
    this.setupKeyboardNavigation();
    
    // Set up screen reader announcements
    this.setupScreenReaderSupport();
  }

  setupKeyboardNavigation() {
    // Handle Enter key in input field
    this.input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        this.handleSubmit();
      }
    });

    // Handle Escape key to clear errors
    this.form.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.clearError();
        this.announceToScreenReader('Form errors cleared');
      }
    });
  }

  setupScreenReaderSupport() {
    // Announce form purpose when focused
    this.form.addEventListener('focusin', () => {
      const formPurpose = this.getFormPurpose();
      if (formPurpose) {
        this.announceToScreenReader(formPurpose);
      }
    });
  }

  getFormPurpose() {
    if (this.form.closest('.hero')) {
      return 'Email signup form to join the Synapse waitlist';
    } else if (this.form.closest('.cta')) {
      return 'Email form to request an invitation to Synapse';
    }
    return 'Email signup form';
  }

  setupEventListeners() {
    // Form submission
    this.form.addEventListener('submit', (e) => {
      e.preventDefault();
      this.handleSubmit();
    });

    // Real-time validation
    this.input.addEventListener('input', () => {
      this.validateInput();
    });

    // Clear errors on focus
    this.input.addEventListener('focus', () => {
      this.clearError();
    });

    // Handle paste events
    this.input.addEventListener('paste', () => {
      setTimeout(() => this.validateInput(), 10);
    });
  }

  setupValidation() {
    // Set up HTML5 validation attributes
    this.input.setAttribute('required', '');
    this.input.setAttribute('type', 'email');
  }

  validateInput() {
    const email = this.input.value.trim();
    
    // Clear previous validation timeout
    if (this.validationTimeout) {
      clearTimeout(this.validationTimeout);
    }

    if (!email) {
      this.clearError();
      this.input.removeAttribute('aria-invalid');
      return true;
    }

    // Debounce validation for better UX
    this.validationTimeout = setTimeout(() => {
      if (!this.isValidEmail(email)) {
        this.showError('Please enter a valid email address');
        this.input.setAttribute('aria-invalid', 'true');
        this.announceToScreenReader('Invalid email address entered', true);
        return false;
      }

      this.clearError();
      this.input.setAttribute('aria-invalid', 'false');
      this.announceToScreenReader('Valid email address entered');
      return true;
    }, 500);

    return true;
  }

  isValidEmail(email) {
    // Comprehensive email validation regex that prevents consecutive dots and requires proper TLD
    const emailRegex = /^[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$/;
    
    // Additional checks for edge cases
    if (!email || email.includes('..') || email.startsWith('.') || email.endsWith('.')) {
      return false;
    }
    
    return emailRegex.test(email);
  }

  async handleSubmit() {
    if (this.isSubmitting) return;

    const email = this.input.value.trim();
    
    // Validate before submission
    if (!this.validateInput()) {
      this.input.focus();
      return;
    }

    if (!email) {
      this.showError('Email address is required');
      this.input.focus();
      return;
    }

    this.isSubmitting = true;
    this.setLoadingState(true);

    try {
      await this.submitEmail(email);
      this.handleSuccess();
    } catch (error) {
      this.handleError(error);
    } finally {
      this.isSubmitting = false;
      this.setLoadingState(false);
    }
  }

  async submitEmail(email) {
    // Get form source (hero, cta, or footer)
    let formSource = 'footer'; // default
    if (this.form.closest('.hero')) {
      formSource = 'hero';
    } else if (this.form.closest('.cta')) {
      formSource = 'cta';
    }
    
    const submissionData = {
      email: email,
      source: formSource,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      referrer: document.referrer || 'direct'
    };

    // Implement retry mechanism
    const maxRetries = 3;
    let retryCount = 0;
    
    const attemptSubmission = async () => {
      try {
        // Check network connectivity
        if (!navigator.onLine) {
          throw new Error('NETWORK_OFFLINE');
        }
        
        // Simulate API call with more realistic error scenarios
        return new Promise((resolve, reject) => {
          const timeout = setTimeout(() => {
            reject(new Error('REQUEST_TIMEOUT'));
          }, 10000); // 10 second timeout
          
          setTimeout(() => {
            clearTimeout(timeout);
            
            // Simulate different types of errors
            const random = Math.random();
            if (random > 0.85) { // 15% failure rate
              if (random > 0.92) {
                reject(new Error('SERVER_ERROR'));
              } else if (random > 0.89) {
                reject(new Error('VALIDATION_ERROR'));
              } else {
                reject(new Error('NETWORK_ERROR'));
              }
            } else {
              console.log('Email submitted:', submissionData);
              resolve(submissionData);
            }
          }, Math.random() * 2000 + 500); // Random delay 500-2500ms
        });
      } catch (error) {
        // Handle different error types
        if (error.message === 'NETWORK_OFFLINE') {
          throw new Error('You appear to be offline. Please check your connection and try again.');
        } else if (error.message === 'REQUEST_TIMEOUT') {
          throw new Error('Request timed out. Please try again.');
        } else if (error.message === 'SERVER_ERROR') {
          throw new Error('Server error. Please try again in a few minutes.');
        } else if (error.message === 'VALIDATION_ERROR') {
          throw new Error('Invalid email address. Please check and try again.');
        } else if (error.message === 'NETWORK_ERROR') {
          throw new Error('Network error. Please check your connection and try again.');
        } else {
          throw error;
        }
      }
    };
    
    // Retry logic with exponential backoff
    while (retryCount < maxRetries) {
      try {
        return await attemptSubmission();
      } catch (error) {
        retryCount++;
        
        // Don't retry for validation errors
        if (error.message.includes('Invalid email') || error.message.includes('VALIDATION_ERROR')) {
          throw error;
        }
        
        // Don't retry if we've reached max retries
        if (retryCount >= maxRetries) {
          throw new Error(`Failed after ${maxRetries} attempts: ${error.message}`);
        }
        
        // Exponential backoff: wait 1s, 2s, 4s
        const backoffDelay = Math.pow(2, retryCount - 1) * 1000;
        await new Promise(resolve => setTimeout(resolve, backoffDelay));
        
        console.log(`Retry attempt ${retryCount} after ${backoffDelay}ms delay`);
      }
    }
  }

  handleSuccess() {
    // Show success message
    const successMessage = 'Thank you! You\'ve been added to our waitlist.';
    this.showSuccess(successMessage);
    
    // Announce success to screen readers
    this.announceToScreenReader(successMessage + ' Form submission completed successfully.', true);
    
    // Clear form
    this.input.value = '';
    this.input.removeAttribute('aria-invalid');
    
    // Move focus to success message for screen readers
    const successElement = this.form.querySelector('.form__success');
    if (successElement) {
      successElement.focus();
    }
    
    // Optional: Track conversion
    this.trackConversion();
    
    // Optional: Show additional success UI
    this.showSuccessAnimation();
  }

  handleError(error) {
    console.error('Form submission error:', error);
    
    let errorMessage = 'Something went wrong. Please try again.';
    let showRetryButton = false;
    
    // Handle specific error types
    if (error.message.includes('offline') || error.message.includes('NETWORK_OFFLINE')) {
      errorMessage = 'You appear to be offline. Please check your connection and try again.';
      showRetryButton = true;
    } else if (error.message.includes('timeout') || error.message.includes('REQUEST_TIMEOUT')) {
      errorMessage = 'Request timed out. Please try again.';
      showRetryButton = true;
    } else if (error.message.includes('Server error') || error.message.includes('SERVER_ERROR')) {
      errorMessage = 'Server temporarily unavailable. Please try again in a few minutes.';
      showRetryButton = true;
    } else if (error.message.includes('Network') || error.message.includes('NETWORK_ERROR')) {
      errorMessage = 'Network error. Please check your connection and try again.';
      showRetryButton = true;
    } else if (error.message.includes('Invalid') || error.message.includes('VALIDATION_ERROR')) {
      errorMessage = 'Please enter a valid email address.';
      showRetryButton = false;
    } else if (error.message.includes('Failed after')) {
      errorMessage = 'Unable to submit after multiple attempts. Please try again later.';
      showRetryButton = true;
    }
    
    this.showError(errorMessage, showRetryButton);
    
    // Track error for analytics
    this.trackError(error);
  }

  trackError(error) {
    // Track form submission errors for monitoring
    const errorData = {
      event: 'form_error',
      error_type: error.message,
      form_source: this.getFormSource(),
      timestamp: new Date().toISOString(),
      user_agent: navigator.userAgent,
      online: navigator.onLine
    };
    
    console.log('Form error tracked:', errorData);
    
    // In production, this would send to analytics service
    // analytics.track('form_error', errorData);
  }

  getFormSource() {
    if (this.form.closest('.hero')) {
      return 'hero';
    } else if (this.form.closest('.cta')) {
      return 'cta';
    }
    return 'footer';
  }

  setLoadingState(isLoading) {
    if (isLoading) {
      this.button.disabled = true;
      this.button.classList.add('loading');
      this.button.textContent = 'Joining...';
      this.input.disabled = true;
    } else {
      this.button.disabled = false;
      this.button.classList.remove('loading');
      this.button.textContent = this.getButtonText();
      this.input.disabled = false;
    }
  }

  getButtonText() {
    // Get original button text based on form location
    if (this.form.closest('.hero')) {
      return 'Join Waitlist';
    } else if (this.form.closest('.cta')) {
      return 'Request My Invitation';
    }
    return 'Submit';
  }

  showError(message, showRetryButton = false) {
    if (this.errorElement) {
      this.errorElement.textContent = message;
      this.errorElement.classList.add('form__error--visible');
      this.errorElement.setAttribute('aria-live', 'assertive');
      this.errorElement.setAttribute('role', 'alert');
      
      // Add retry button if needed
      if (showRetryButton) {
        this.addRetryButton();
      }
    }
    
    this.input.classList.add('error');
    this.input.setAttribute('aria-invalid', 'true');
    
    // Announce error to screen readers
    this.announceToScreenReader(`Form error: ${message}`, true);
    
    // Focus the input field for correction
    setTimeout(() => {
      this.input.focus();
    }, 100);
    
    // Auto-hide error after 10 seconds
    setTimeout(() => {
      this.clearError();
    }, 10000);
  }

  addRetryButton() {
    // Remove existing retry button
    const existingRetry = this.form.querySelector('.form__retry');
    if (existingRetry) {
      existingRetry.remove();
    }
    
    // Create retry button
    const retryButton = document.createElement('button');
    retryButton.type = 'button';
    retryButton.className = 'form__retry btn btn--secondary';
    retryButton.textContent = 'Retry';
    retryButton.setAttribute('aria-label', 'Retry form submission');
    
    retryButton.addEventListener('click', () => {
      this.clearError();
      this.handleSubmit();
    });
    
    // Insert retry button after error message
    if (this.errorElement && this.errorElement.parentNode) {
      this.errorElement.parentNode.insertBefore(retryButton, this.errorElement.nextSibling);
    }
  }

  clearError() {
    if (this.errorElement) {
      this.errorElement.textContent = '';
      this.errorElement.classList.remove('form__error--visible');
    }
    
    // Remove retry button
    const retryButton = this.form.querySelector('.form__retry');
    if (retryButton) {
      retryButton.remove();
    }
    
    this.input.classList.remove('error');
    this.input.removeAttribute('aria-invalid');
  }

  showSuccess(message) {
    // Create or update success message
    let successElement = this.form.querySelector('.form__success');
    
    if (!successElement) {
      successElement = document.createElement('div');
      successElement.className = 'form__success';
      successElement.setAttribute('role', 'status');
      successElement.setAttribute('aria-live', 'polite');
      successElement.setAttribute('aria-atomic', 'true');
      successElement.setAttribute('tabindex', '0'); // Make focusable
      this.form.appendChild(successElement);
    }
    
    successElement.textContent = message;
    successElement.classList.add('form__success--visible');
    
    // Hide success message after 8 seconds
    setTimeout(() => {
      successElement.classList.remove('form__success--visible');
    }, 8000);
  }

  // Announce messages to screen readers
  announceToScreenReader(message, urgent = false) {
    // Use the global announcement function if available
    if (window.SynapseApp && window.SynapseApp.announceToScreenReader) {
      window.SynapseApp.announceToScreenReader(message, urgent);
      return;
    }

    // Fallback: create temporary live region
    const liveRegion = document.createElement('div');
    liveRegion.setAttribute('aria-live', urgent ? 'assertive' : 'polite');
    liveRegion.setAttribute('aria-atomic', 'true');
    liveRegion.className = 'visually-hidden';
    liveRegion.textContent = message;
    
    document.body.appendChild(liveRegion);
    
    // Remove after announcement
    setTimeout(() => {
      document.body.removeChild(liveRegion);
    }, 3000);
  }

  showSuccessAnimation() {
    // Add success animation class to form
    this.form.classList.add('form--success');
    
    // Remove animation class after animation completes
    setTimeout(() => {
      this.form.classList.remove('form--success');
    }, 1000);
  }

  trackConversion() {
    // Track successful email capture
    // This would integrate with analytics in production
    let formSource = 'footer'; // default
    if (this.form.closest('.hero')) {
      formSource = 'hero';
    } else if (this.form.closest('.cta')) {
      formSource = 'cta';
    }
    
    console.log('Conversion tracked:', {
      event: 'email_capture',
      source: formSource,
      timestamp: new Date().toISOString()
    });
  }

  // Public method to reset form
  reset() {
    this.input.value = '';
    this.clearError();
    this.setLoadingState(false);
  }

  // Public method to validate form
  validate() {
    return this.validateInput();
  }

  // Cleanup method
  destroy() {
    // Remove event listeners if needed
    this.form.removeEventListener('submit', this.handleSubmit);
    this.input.removeEventListener('input', this.validateInput);
  }
}

/**
 * Form Utilities
 * Helper functions for form handling
 */
const FormUtils = {
  // Sanitize input to prevent XSS
  sanitizeInput(input) {
    if (typeof input !== 'string') return '';
    
    // For Node.js testing environment
    if (typeof document === 'undefined' || !document.createElement) {
      return input.replace(/[<>&"']/g, function(match) {
        const escapeMap = {
          '<': '&lt;',
          '>': '&gt;',
          '&': '&amp;',
          '"': '&quot;',
          "'": '&#x27;'
        };
        return escapeMap[match];
      });
    }
    
    // For browser environment
    try {
      const div = document.createElement('div');
      div.textContent = input;
      return div.innerHTML;
    } catch (error) {
      // Fallback to manual escaping
      return input.replace(/[<>&"']/g, function(match) {
        const escapeMap = {
          '<': '&lt;',
          '>': '&gt;',
          '&': '&amp;',
          '"': '&quot;',
          "'": '&#x27;'
        };
        return escapeMap[match];
      });
    }
  },

  // Format email for display
  formatEmail(email) {
    return email.toLowerCase().trim();
  },

  // Check if email domain is valid
  isValidDomain(email) {
    const domain = email.split('@')[1];
    if (!domain) return false;
    
    // Basic domain validation
    const domainRegex = /^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9](?:\.[a-zA-Z]{2,})+$/;
    return domainRegex.test(domain);
  },

  // Debounce function for input validation
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { EmailCapture, FormUtils };
}