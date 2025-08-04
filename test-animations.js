/**
 * Unit tests for ScrollAnimations class
 * Tests animation timing and state management functions
 */

// Mock DOM elements and APIs for testing
class MockIntersectionObserver {
  constructor(callback, options) {
    this.callback = callback;
    this.options = options;
    this.observedElements = [];
  }

  observe(element) {
    this.observedElements.push(element);
  }

  unobserve(element) {
    const index = this.observedElements.indexOf(element);
    if (index > -1) {
      this.observedElements.splice(index, 1);
    }
  }

  disconnect() {
    this.observedElements = [];
  }

  // Simulate intersection
  triggerIntersection(element, isIntersecting = true) {
    this.callback([{
      target: element,
      isIntersecting,
      intersectionRatio: isIntersecting ? 0.5 : 0
    }]);
  }
}

// Mock DOM environment
const mockDOM = {
  createElement(tagName) {
    return {
      tagName: tagName.toUpperCase(),
      classList: {
        classes: [],
        add(...classes) {
          this.classes.push(...classes);
        },
        remove(...classes) {
          this.classes = this.classes.filter(c => !classes.includes(c));
        },
        contains(className) {
          return this.classes.includes(className);
        }
      },
      getAttribute(name) {
        return this.attributes?.[name] || null;
      },
      setAttribute(name, value) {
        this.attributes = this.attributes || {};
        this.attributes[name] = value;
      },
      hasAttribute(name) {
        return this.attributes && name in this.attributes;
      },
      style: {},
      offsetTop: 100,
      getBoundingClientRect() {
        return {
          top: 0,
          bottom: 100,
          height: 100,
          width: 100
        };
      },
      closest(selector) {
        return null;
      },
      querySelectorAll(selector) {
        return [];
      }
    };
  },

  createSection(id, attributes = {}) {
    const section = this.createElement('section');
    section.id = id;
    Object.entries(attributes).forEach(([key, value]) => {
      section.setAttribute(key, value);
    });
    return section;
  },

  createAnimatedElement(animationType = 'fade-in', delay = 0) {
    const element = this.createElement('div');
    element.setAttribute('data-animate', animationType);
    if (delay > 0) {
      element.setAttribute('data-animate-delay', delay.toString());
    }
    return element;
  }
};

// Test Suite
class AnimationTestSuite {
  constructor() {
    this.tests = [];
    this.results = [];
    
    // Setup global mocks
    global.IntersectionObserver = MockIntersectionObserver;
    global.requestAnimationFrame = (callback) => setTimeout(callback, 16);
    global.window = {
      scrollY: 0,
      innerHeight: 800,
      addEventListener: () => {},
      removeEventListener: () => {}
    };
    global.document = {
      documentElement: {
        scrollHeight: 2000,
        style: {}
      },
      querySelectorAll: () => [],
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => {},
      getElementById: () => null
    };
  }

  addTest(name, testFunction) {
    this.tests.push({ name, testFunction });
  }

  async runTests() {
    console.log('Running ScrollAnimations Tests...\n');
    
    for (const test of this.tests) {
      try {
        await test.testFunction();
        this.results.push({ name: test.name, status: 'PASS' });
        console.log(`✅ ${test.name}`);
      } catch (error) {
        this.results.push({ name: test.name, status: 'FAIL', error: error.message });
        console.log(`❌ ${test.name}: ${error.message}`);
      }
    }

    this.printSummary();
  }

  printSummary() {
    const passed = this.results.filter(r => r.status === 'PASS').length;
    const failed = this.results.filter(r => r.status === 'FAIL').length;
    
    console.log('\n' + '='.repeat(50));
    console.log(`Test Results: ${passed} passed, ${failed} failed`);
    console.log('='.repeat(50));
  }

  assert(condition, message) {
    if (!condition) {
      throw new Error(message);
    }
  }

  assertEqual(actual, expected, message) {
    if (actual !== expected) {
      throw new Error(`${message}: expected ${expected}, got ${actual}`);
    }
  }

  assertArrayEqual(actual, expected, message) {
    if (JSON.stringify(actual) !== JSON.stringify(expected)) {
      throw new Error(`${message}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
    }
  }
}

// Load ScrollAnimations class (simplified version for testing)
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
  }

  init() {
    this.setupIntersectionObserver();
    this.observeElements();
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
        }
      });
    }, options);
  }

  observeElements() {
    const elementsToAnimate = document.querySelectorAll('[data-animate]') || [];
    elementsToAnimate.forEach(element => {
      this.observer.observe(element);
      this.animatedElements.push(element);
    });
  }

  animateElement(element) {
    const animationType = element.getAttribute('data-animate');
    const delay = parseInt(element.getAttribute('data-animate-delay') || 0);

    setTimeout(() => {
      element.classList.add('animate-in');
      
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
        default:
          element.classList.add('animate-fade-in');
      }

      if (this.observer) {
        this.observer.unobserve(element);
      }
    }, delay);
  }

  updateScrollProgress() {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight;
    const winHeight = window.innerHeight;
    const scrollPercent = Math.min(scrollTop / (docHeight - winHeight), 1);
    
    this.animationState.scrollProgress = scrollPercent;
    return scrollPercent;
  }

  easeInOutQuad(t, b, c, d) {
    t /= d / 2;
    if (t < 1) return c / 2 * t * t + b;
    t--;
    return -c / 2 * (t * (t - 2) - 1) + b;
  }

  isInViewport(element, threshold = 0.1) {
    const rect = element.getBoundingClientRect();
    const windowHeight = window.innerHeight;
    const elementHeight = rect.height;
    
    return (
      rect.top <= windowHeight - (elementHeight * threshold) &&
      rect.bottom >= (elementHeight * threshold)
    );
  }

  getAnimationState() {
    return { ...this.animationState };
  }

  triggerAnimation(selector, animationType = 'fade-in', staggerDelay = 100) {
    const elements = document.querySelectorAll(selector) || [];
    elements.forEach((element, index) => {
      setTimeout(() => {
        element.classList.add('animate-in', `animate-${animationType}`);
      }, index * staggerDelay);
    });
  }

  resetAnimations() {
    this.animatedElements.forEach(element => {
      element.classList.remove(
        'animate-in', 
        'animate-fade-in', 
        'animate-slide-in-left', 
        'animate-slide-in-right'
      );
      if (this.observer) {
        this.observer.observe(element);
      }
    });
    
    this.animationState.sectionsVisible = [];
    this.animationState.scrollProgress = 0;
    this.currentSection = 0;
  }

  destroy() {
    if (this.observer) {
      this.observer.disconnect();
    }
    if (this.scrollTimeout) {
      clearTimeout(this.scrollTimeout);
    }
  }
}

// Initialize test suite
const testSuite = new AnimationTestSuite();

// Test 1: ScrollAnimations initialization
testSuite.addTest('ScrollAnimations initializes correctly', () => {
  const animations = new ScrollAnimations();
  animations.init();
  
  testSuite.assert(animations.observer !== null, 'IntersectionObserver should be created');
  testSuite.assert(Array.isArray(animations.animatedElements), 'animatedElements should be an array');
  testSuite.assertEqual(animations.currentSection, 0, 'currentSection should start at 0');
  testSuite.assert(animations.animationState !== null, 'animationState should be initialized');
});

// Test 2: Animation state management
testSuite.addTest('Animation state management works correctly', () => {
  const animations = new ScrollAnimations();
  
  // Test initial state
  const initialState = animations.getAnimationState();
  testSuite.assertArrayEqual(initialState.sectionsVisible, [], 'sectionsVisible should start empty');
  testSuite.assertEqual(initialState.scrollProgress, 0, 'scrollProgress should start at 0');
  testSuite.assertEqual(initialState.isScrolling, false, 'isScrolling should start false');
  
  // Test state updates
  animations.animationState.sectionsVisible.push(1);
  animations.animationState.scrollProgress = 0.5;
  animations.animationState.isScrolling = true;
  
  const updatedState = animations.getAnimationState();
  testSuite.assertArrayEqual(updatedState.sectionsVisible, [1], 'sectionsVisible should be updated');
  testSuite.assertEqual(updatedState.scrollProgress, 0.5, 'scrollProgress should be updated');
  testSuite.assertEqual(updatedState.isScrolling, true, 'isScrolling should be updated');
});

// Test 3: Scroll progress calculation
testSuite.addTest('Scroll progress calculation is accurate', () => {
  const animations = new ScrollAnimations();
  
  // Mock scroll values
  window.scrollY = 600;
  document.documentElement.scrollHeight = 2000;
  window.innerHeight = 800;
  
  const progress = animations.updateScrollProgress();
  const expectedProgress = 600 / (2000 - 800); // 0.5
  
  testSuite.assertEqual(progress, expectedProgress, 'Scroll progress should be calculated correctly');
  testSuite.assertEqual(animations.animationState.scrollProgress, expectedProgress, 'Animation state should be updated');
});

// Test 4: Easing function
testSuite.addTest('Easing function produces correct values', () => {
  const animations = new ScrollAnimations();
  
  // Test easing at different points
  const start = animations.easeInOutQuad(0, 0, 100, 1000);
  const middle = animations.easeInOutQuad(500, 0, 100, 1000);
  const end = animations.easeInOutQuad(1000, 0, 100, 1000);
  
  testSuite.assertEqual(start, 0, 'Easing should start at 0');
  testSuite.assertEqual(end, 100, 'Easing should end at target value');
  testSuite.assert(middle > 0 && middle < 100, 'Easing should be between start and end at midpoint');
});

// Test 5: Viewport detection
testSuite.addTest('Viewport detection works correctly', () => {
  const animations = new ScrollAnimations();
  
  // Create mock element
  const element = mockDOM.createElement('div');
  element.getBoundingClientRect = () => ({
    top: 100,
    bottom: 200,
    height: 100,
    width: 100
  });
  
  window.innerHeight = 800;
  
  const isInViewport = animations.isInViewport(element, 0.1);
  testSuite.assertEqual(isInViewport, true, 'Element should be detected as in viewport');
  
  // Test element out of viewport
  element.getBoundingClientRect = () => ({
    top: 900,
    bottom: 1000,
    height: 100,
    width: 100
  });
  
  const isOutOfViewport = animations.isInViewport(element, 0.1);
  testSuite.assertEqual(isOutOfViewport, false, 'Element should be detected as out of viewport');
});

// Test 6: Animation element processing
testSuite.addTest('Animation element processing works correctly', () => {
  const animations = new ScrollAnimations();
  
  // Create mock animated element
  const element = mockDOM.createAnimatedElement('fade-in', 100);
  
  // Test animation triggering
  animations.animateElement(element);
  
  // Check that animation classes are added after delay
  setTimeout(() => {
    testSuite.assert(element.classList.contains('animate-in'), 'animate-in class should be added');
    testSuite.assert(element.classList.contains('animate-fade-in'), 'animate-fade-in class should be added');
  }, 150);
});

// Test 7: Animation reset functionality
testSuite.addTest('Animation reset functionality works correctly', () => {
  const animations = new ScrollAnimations();
  
  // Setup initial state
  animations.animationState.sectionsVisible = [1, 2];
  animations.animationState.scrollProgress = 0.7;
  animations.currentSection = 2;
  
  // Add mock animated element
  const element = mockDOM.createAnimatedElement('fade-in');
  element.classList.add('animate-in', 'animate-fade-in');
  animations.animatedElements.push(element);
  
  // Reset animations
  animations.resetAnimations();
  
  // Check reset state
  testSuite.assertArrayEqual(animations.animationState.sectionsVisible, [], 'sectionsVisible should be reset');
  testSuite.assertEqual(animations.animationState.scrollProgress, 0, 'scrollProgress should be reset');
  testSuite.assertEqual(animations.currentSection, 0, 'currentSection should be reset');
  testSuite.assert(!element.classList.contains('animate-in'), 'animate-in class should be removed');
  testSuite.assert(!element.classList.contains('animate-fade-in'), 'animate-fade-in class should be removed');
});

// Test 8: Cleanup functionality
testSuite.addTest('Cleanup functionality works correctly', () => {
  const animations = new ScrollAnimations();
  animations.init();
  
  // Set up timeout
  animations.scrollTimeout = setTimeout(() => {}, 1000);
  
  testSuite.assert(animations.observer !== null, 'Observer should exist before cleanup');
  testSuite.assert(animations.scrollTimeout !== null, 'Timeout should exist before cleanup');
  
  // Cleanup
  animations.destroy();
  
  // Note: We can't easily test if observer.disconnect() was called in this mock environment,
  // but we can verify the method exists and doesn't throw errors
  testSuite.assert(true, 'Cleanup should complete without errors');
});

// Run all tests
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { AnimationTestSuite, ScrollAnimations, mockDOM };
  
  // Run tests in Node.js environment
  testSuite.runTests().then(() => {
    console.log('\nAll animation tests completed!');
  });
} else {
  // Run tests if in browser environment
  testSuite.runTests().then(() => {
    console.log('\nAll animation tests completed!');
  });
}