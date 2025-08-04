/**
 * Animation controller for Synapse Landing Page
 * Handles scroll-based animations and interactive effects
 */

class ScrollAnimations {
  constructor() {
    this.observer = null;
    this.animatedElements = [];
    this.currentSection = 0;
    this.sections = [];
    this.animationState = {
      sectionsVisible: [],
      scrollProgress: 0,
      isScrolling: false
    };
    this.scrollTimeout = null;
    this.reducedMotion = this.checkReducedMotion();
    this.isLowEndDevice = this.detectLowEndDevice();
    this.init();
  }

  init() {
    // Skip complex animations for reduced motion or low-end devices
    if (this.reducedMotion) {
      this.setupReducedMotionMode();
      return;
    }
    
    this.setupIntersectionObserver();
    this.observeElements();
    this.setupScrollListeners();
    this.setupSectionTracking();
    this.setupSmoothScrolling();
    this.setupPerformanceOptimizations();
  }

  checkReducedMotion() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  detectLowEndDevice() {
    // Detect low-end devices based on various factors
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    const memory = navigator.deviceMemory;
    const cores = navigator.hardwareConcurrency;
    
    // Check for slow connection
    const slowConnection = connection && (
      connection.effectiveType === 'slow-2g' || 
      connection.effectiveType === '2g' ||
      connection.saveData === true
    );
    
    // Check for low memory (less than 4GB)
    const lowMemory = memory && memory < 4;
    
    // Check for few CPU cores (less than 4)
    const fewCores = cores && cores < 4;
    
    // Check for small screen (likely mobile)
    const smallScreen = window.screen.width < 768;
    
    return slowConnection || lowMemory || fewCores || (smallScreen && (lowMemory || fewCores));
  }

  setupReducedMotionMode() {
    // Immediately show all elements without animation
    const elementsToShow = document.querySelectorAll('[data-animate]');
    elementsToShow.forEach(element => {
      element.style.opacity = '1';
      element.style.transform = 'none';
      element.classList.add('animate-in');
    });
    
    // Disable smooth scrolling
    document.documentElement.style.scrollBehavior = 'auto';
  }

  setupPerformanceOptimizations() {
    // Use passive event listeners for better performance
    this.setupPassiveListeners();
    
    // Implement frame rate limiting for low-end devices
    if (this.isLowEndDevice) {
      this.setupFrameRateLimiting();
    }
    
    // Setup intersection observer with performance optimizations
    this.setupOptimizedObserver();
  }

  setupPassiveListeners() {
    // Mark scroll listeners as passive for better performance
    const scrollOptions = { passive: true };
    
    // Update existing scroll listener to be passive
    window.removeEventListener('scroll', this.handleScroll);
    window.addEventListener('scroll', this.handleScroll.bind(this), scrollOptions);
  }

  setupFrameRateLimiting() {
    // Limit animation frame rate on low-end devices
    this.frameRateLimit = 30; // 30fps instead of 60fps
    this.lastFrameTime = 0;
  }

  setupOptimizedObserver() {
    // Use more conservative intersection observer settings for performance
    const options = {
      root: null,
      rootMargin: this.isLowEndDevice ? '50px' : '0px 0px -10% 0px',
      threshold: this.isLowEndDevice ? [0.2] : [0.1, 0.3, 0.5]
    };

    this.observer = new IntersectionObserver((entries) => {
      // Batch DOM updates for better performance
      this.batchAnimationUpdates(entries);
    }, options);
  }

  batchAnimationUpdates(entries) {
    // Use requestAnimationFrame to batch DOM updates
    requestAnimationFrame(() => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.animateElement(entry.target);
          this.updateSectionVisibility(entry.target, true);
        } else {
          this.updateSectionVisibility(entry.target, false);
        }
      });
    });
  }

  setupIntersectionObserver() {
    const options = {
      root: null,
      rootMargin: '0px 0px -10% 0px',
      threshold: [0.1, 0.3, 0.5]
    };

    this.observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.animateElement(entry.target);
          this.updateSectionVisibility(entry.target, true);
        } else {
          this.updateSectionVisibility(entry.target, false);
        }
      });
    }, options);
  }

  observeElements() {
    const elementsToAnimate = document.querySelectorAll('[data-animate]');
    elementsToAnimate.forEach(element => {
      this.observer.observe(element);
      this.animatedElements.push(element);
    });
  }

  animateElement(element) {
    // Skip animation if reduced motion is preferred
    if (this.reducedMotion) {
      element.style.opacity = '1';
      element.style.transform = 'none';
      element.classList.add('animate-in');
      return;
    }

    const animationType = element.getAttribute('data-animate');
    const delay = parseInt(element.getAttribute('data-animate-delay') || 0);
    const stagger = element.getAttribute('data-animate-stagger');

    // Reduce delay on low-end devices
    const actualDelay = this.isLowEndDevice ? Math.min(delay, 100) : delay;

    // Handle staggered animations for child elements
    if (stagger) {
      this.animateStaggeredChildren(element, animationType, actualDelay);
      return;
    }

    // Use requestAnimationFrame for better performance
    const animateWithRAF = () => {
      requestAnimationFrame(() => {
        element.classList.add('animate-in');
        
        // Trigger custom animations based on type
        switch (animationType) {
          case 'fade-in':
            element.classList.add('animate-fade-in');
            break;
          case 'slide-left':
            element.classList.add('animate-slide-in-left');
            break;
          case 'slide-right':
            element.classList.add('animate-slide-in-right');
            break;
          case 'slide-up':
            element.classList.add('animate-slide-in-up');
            break;
          case 'scale-in':
            element.classList.add('animate-scale-in');
            break;
          case 'network-expand':
            element.classList.add('animate-network-expand');
            break;
          default:
            element.classList.add('animate-fade-in');
        }

        // Clean up will-change property after animation
        setTimeout(() => {
          element.style.willChange = 'auto';
        }, 600);

        // Trigger callback if specified
        const callback = element.getAttribute('data-animate-callback');
        if (callback && typeof window[callback] === 'function') {
          try {
            window[callback](element);
          } catch (error) {
            console.warn('Animation callback error:', error);
          }
        }

        // Stop observing once animated (unless specified to keep observing)
        if (!element.hasAttribute('data-animate-repeat')) {
          this.observer.unobserve(element);
        }
      });
    };

    if (actualDelay > 0) {
      setTimeout(animateWithRAF, actualDelay);
    } else {
      animateWithRAF();
    }
  }

  animateStaggeredChildren(container, animationType, baseDelay) {
    const children = container.querySelectorAll('[data-animate-child]');
    const staggerDelay = parseInt(container.getAttribute('data-animate-stagger')) || 100;

    children.forEach((child, index) => {
      const totalDelay = baseDelay + (index * staggerDelay);
      setTimeout(() => {
        child.classList.add('animate-in');
        switch (animationType) {
          case 'fade-in':
            child.classList.add('animate-fade-in');
            break;
          case 'slide-left':
            child.classList.add('animate-slide-in-left');
            break;
          case 'slide-right':
            child.classList.add('animate-slide-in-right');
            break;
          case 'slide-up':
            child.classList.add('animate-slide-in-up');
            break;
          default:
            child.classList.add('animate-fade-in');
        }
      }, totalDelay);
    });
  }

  setupScrollListeners() {
    let ticking = false;

    const updateScrollEffects = () => {
      this.updateParallaxEffects();
      this.updateScrollProgress();
      this.updateSectionTracking();
      this.animationState.isScrolling = true;
      
      // Clear existing timeout
      if (this.scrollTimeout) {
        clearTimeout(this.scrollTimeout);
      }
      
      // Set scroll end detection
      this.scrollTimeout = setTimeout(() => {
        this.animationState.isScrolling = false;
        this.onScrollEnd();
      }, 150);
      
      ticking = false;
    };

    window.addEventListener('scroll', () => {
      if (!ticking) {
        requestAnimationFrame(updateScrollEffects);
        ticking = true;
      }
    }, { passive: true });
  }

  setupSectionTracking() {
    this.sections = Array.from(document.querySelectorAll('section[id]'));
    
    // Create section observer for navigation tracking
    const sectionOptions = {
      root: null,
      rootMargin: '-50% 0px -50% 0px',
      threshold: 0
    };

    this.sectionObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const sectionIndex = this.sections.indexOf(entry.target);
          if (sectionIndex !== -1) {
            this.currentSection = sectionIndex;
            this.onSectionChange(entry.target, sectionIndex);
          }
        }
      });
    }, sectionOptions);

    this.sections.forEach(section => {
      this.sectionObserver.observe(section);
    });
  }

  setupSmoothScrolling() {
    // Enable smooth scrolling behavior
    document.documentElement.style.scrollBehavior = 'smooth';
    
    // Handle anchor links
    document.addEventListener('click', (e) => {
      const link = e.target.closest('a[href^="#"]');
      if (link) {
        e.preventDefault();
        const targetId = link.getAttribute('href').substring(1);
        const targetElement = document.getElementById(targetId);
        
        if (targetElement) {
          this.smoothScrollTo(targetElement);
        }
      }
    });
  }

  updateParallaxEffects() {
    const scrolled = window.scrollY;
    const parallaxElements = document.querySelectorAll('[data-parallax]');

    parallaxElements.forEach(element => {
      const speed = parseFloat(element.getAttribute('data-parallax')) || 0.5;
      const yPos = -(scrolled * speed);
      element.style.transform = `translateY(${yPos}px)`;
    });
  }

  updateScrollProgress() {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight;
    const winHeight = window.innerHeight;
    const scrollPercent = Math.min(scrollTop / (docHeight - winHeight), 1);
    
    this.animationState.scrollProgress = scrollPercent;
    
    // Update any scroll progress indicators
    const progressBars = document.querySelectorAll('[data-scroll-progress]');
    progressBars.forEach(bar => {
      bar.style.transform = `scaleX(${scrollPercent})`;
    });

    // Dispatch custom scroll progress event
    document.dispatchEvent(new CustomEvent('scrollProgress', {
      detail: { progress: scrollPercent }
    }));
  }

  updateSectionTracking() {
    const scrollTop = window.scrollY;
    const windowHeight = window.innerHeight;
    
    this.sections.forEach((section, index) => {
      const rect = section.getBoundingClientRect();
      const isVisible = rect.top < windowHeight && rect.bottom > 0;
      
      if (isVisible && !this.animationState.sectionsVisible.includes(index)) {
        this.animationState.sectionsVisible.push(index);
      } else if (!isVisible && this.animationState.sectionsVisible.includes(index)) {
        const visibleIndex = this.animationState.sectionsVisible.indexOf(index);
        this.animationState.sectionsVisible.splice(visibleIndex, 1);
      }
    });
  }

  updateSectionVisibility(element, isVisible) {
    const section = element.closest('section');
    if (section) {
      const sectionIndex = this.sections.indexOf(section);
      if (sectionIndex !== -1) {
        if (isVisible && !this.animationState.sectionsVisible.includes(sectionIndex)) {
          this.animationState.sectionsVisible.push(sectionIndex);
        }
      }
    }
  }

  onSectionChange(section, index) {
    // Dispatch custom section change event
    document.dispatchEvent(new CustomEvent('sectionChange', {
      detail: { section, index, id: section.id }
    }));
  }

  onScrollEnd() {
    // Dispatch custom scroll end event
    document.dispatchEvent(new CustomEvent('scrollEnd', {
      detail: { 
        currentSection: this.currentSection,
        scrollProgress: this.animationState.scrollProgress
      }
    }));
  }

  smoothScrollTo(target, duration = 800) {
    const targetElement = typeof target === 'string' ? document.querySelector(target) : target;
    if (!targetElement) return;

    const targetPosition = targetElement.offsetTop;
    const startPosition = window.scrollY;
    const distance = targetPosition - startPosition;
    let startTime = null;

    const animation = (currentTime) => {
      if (startTime === null) startTime = currentTime;
      const timeElapsed = currentTime - startTime;
      const run = this.easeInOutQuad(timeElapsed, startPosition, distance, duration);
      window.scrollTo(0, run);
      if (timeElapsed < duration) requestAnimationFrame(animation);
    };

    requestAnimationFrame(animation);
  }

  easeInOutQuad(t, b, c, d) {
    t /= d / 2;
    if (t < 1) return c / 2 * t * t + b;
    t--;
    return -c / 2 * (t * (t - 2) - 1) + b;
  }

  // Method to manually trigger animations
  triggerAnimation(selector, animationType = 'fade-in', staggerDelay = 100) {
    const elements = document.querySelectorAll(selector);
    elements.forEach((element, index) => {
      setTimeout(() => {
        element.classList.add('animate-in', `animate-${animationType}`);
      }, index * staggerDelay);
    });
  }

  // Method to reset animations
  resetAnimations() {
    this.animatedElements.forEach(element => {
      element.classList.remove(
        'animate-in', 
        'animate-fade-in', 
        'animate-slide-in-left', 
        'animate-slide-in-right',
        'animate-slide-in-up',
        'animate-scale-in',
        'animate-network-expand'
      );
      this.observer.observe(element);
    });
    
    // Reset animation state
    this.animationState.sectionsVisible = [];
    this.animationState.scrollProgress = 0;
    this.currentSection = 0;
  }

  // Get current animation state
  getAnimationState() {
    return { ...this.animationState };
  }

  // Check if element is in viewport
  isInViewport(element, threshold = 0.1) {
    const rect = element.getBoundingClientRect();
    const windowHeight = window.innerHeight;
    const elementHeight = rect.height;
    
    return (
      rect.top <= windowHeight - (elementHeight * threshold) &&
      rect.bottom >= (elementHeight * threshold)
    );
  }

  // Cleanup method
  destroy() {
    if (this.observer) {
      this.observer.disconnect();
    }
    if (this.sectionObserver) {
      this.sectionObserver.disconnect();
    }
    if (this.scrollTimeout) {
      clearTimeout(this.scrollTimeout);
    }
    
    // Remove event listeners
    document.removeEventListener('click', this.handleAnchorClick);
  }
}

/**
 * Network Animation Controller
 * Handles the hero section network visualization
 */
class NetworkAnimation {
  constructor(container) {
    this.container = container;
    this.nodes = [];
    this.connections = [];
    this.animationId = null;
    this.init();
  }

  init() {
    this.createNodes();
    this.createConnections();
    this.startAnimation();
  }

  createNodes() {
    // This will be implemented in later tasks
    // Placeholder for network node creation
  }

  createConnections() {
    // This will be implemented in later tasks
    // Placeholder for connection line creation
  }

  startAnimation() {
    // This will be implemented in later tasks
    // Placeholder for animation loop
  }

  stopAnimation() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
    }
  }
}

/**
 * Typewriter Effect
 * Creates typewriter animation for text elements
 */
class TypewriterEffect {
  constructor(element, options = {}) {
    this.element = element;
    this.text = options.text || element.textContent;
    this.speed = options.speed || 50;
    this.delay = options.delay || 0;
    this.cursor = options.cursor || '|';
    this.showCursor = options.showCursor !== false;
    this.currentIndex = 0;
    this.isTyping = false;
    this.cursorInterval = null;
  }

  start() {
    if (this.isTyping) return;
    
    this.isTyping = true;
    this.element.textContent = '';
    
    setTimeout(() => {
      this.type();
    }, this.delay);
  }

  type() {
    if (this.currentIndex < this.text.length) {
      this.element.textContent = this.text.slice(0, this.currentIndex + 1);
      
      if (this.showCursor && this.currentIndex === this.text.length - 1) {
        // Don't show cursor while typing, only at the end
      } else if (this.showCursor) {
        this.element.textContent += this.cursor;
      }
      
      this.currentIndex++;
      setTimeout(() => this.type(), this.speed);
    } else {
      this.isTyping = false;
      if (this.showCursor) {
        // Start blinking cursor after typing is complete
        this.startBlinkingCursor();
      }
    }
  }

  startBlinkingCursor() {
    let visible = true;
    this.cursorInterval = setInterval(() => {
      if (visible) {
        this.element.textContent = this.text + this.cursor;
      } else {
        this.element.textContent = this.text;
      }
      visible = !visible;
    }, 500);

    // Stop blinking after 3 seconds
    setTimeout(() => {
      if (this.cursorInterval) {
        clearInterval(this.cursorInterval);
        this.element.textContent = this.text;
      }
    }, 3000);
  }

  reset() {
    this.currentIndex = 0;
    this.isTyping = false;
    if (this.cursorInterval) {
      clearInterval(this.cursorInterval);
      this.cursorInterval = null;
    }
    this.element.textContent = '';
  }
}

/**
 * Demonstration Animation Controller
 * Handles the before/after comparison animations
 */
class DemonstrationAnimation {
  constructor() {
    this.typewriterElement = null;
    this.processingTags = [];
    this.typewriterInstance = null;
    this.init();
  }

  init() {
    this.setupElements();
    this.setupIntersectionObserver();
  }

  setupElements() {
    this.typewriterElement = document.querySelector('[data-typewriter="true"]');
    this.processingTags = document.querySelectorAll('.demonstration__tag');
  }

  setupIntersectionObserver() {
    const options = {
      root: null,
      rootMargin: '0px 0px -20% 0px',
      threshold: 0.3
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.startDemonstrationAnimation();
          observer.unobserve(entry.target);
        }
      });
    }, options);

    const demonstrationSection = document.querySelector('.demonstration__panels');
    if (demonstrationSection) {
      observer.observe(demonstrationSection);
    }
  }

  startDemonstrationAnimation() {
    // Animate panels first
    this.animatePanels();
    
    // Start processing tags animation
    setTimeout(() => {
      this.animateProcessingTags();
    }, 400);
    
    // Start typewriter effect after processing animation
    setTimeout(() => {
      this.startTypewriterEffect();
    }, 1600);
  }

  animatePanels() {
    const panels = document.querySelectorAll('.demonstration__panel');
    panels.forEach((panel, index) => {
      setTimeout(() => {
        panel.classList.add('animate-in');
      }, index * 200);
    });
  }

  animateProcessingTags() {
    this.processingTags.forEach((tag, index) => {
      setTimeout(() => {
        tag.classList.add('animate-in');
      }, index * 150);
    });
  }

  startTypewriterEffect() {
    if (!this.typewriterElement) return;

    const content = this.typewriterElement.querySelector('.demonstration__typewriter-content');
    if (!content) return;

    const text = content.textContent;
    content.textContent = '';
    content.classList.add('typing');
    
    this.typewriterInstance = new TypewriterEffect(content, {
      speed: 30,
      delay: 0,
      showCursor: true
    });

    // Set the text and start typing
    this.typewriterInstance.text = text;
    this.typewriterInstance.start();

    // Remove cursor after typing is complete
    setTimeout(() => {
      content.classList.add('typing-complete');
    }, text.length * 30 + 1000);
  }

  reset() {
    if (this.typewriterInstance) {
      this.typewriterInstance.reset();
    }
    
    const panels = document.querySelectorAll('.demonstration__panel');
    panels.forEach(panel => {
      panel.classList.remove('animate-in');
    });
    
    this.processingTags.forEach(tag => {
      tag.classList.remove('animate-in');
    });
  }
}

// Export classes for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { ScrollAnimations, NetworkAnimation, TypewriterEffect, DemonstrationAnimation };
}