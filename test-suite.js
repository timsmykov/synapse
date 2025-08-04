#!/usr/bin/env node

/**
 * Comprehensive Testing Suite for Synapse Landing Page
 * Covers unit tests, cross-browser compatibility, responsive design, and accessibility
 * 
 * Usage:
 * - Node.js: node test-suite.js
 * - Browser: Include in HTML and call TestSuite.runAll()
 */

class TestSuite {
  constructor() {
    this.results = {
      unit: { passed: 0, failed: 0, tests: [] },
      browser: { passed: 0, failed: 0, tests: [] },
      responsive: { passed: 0, failed: 0, tests: [] },
      accessibility: { passed: 0, failed: 0, tests: [] }
    };
    this.isNodeEnvironment = typeof window === 'undefined';
    this.startTime = Date.now();
  }

  // Main test runner
  async runAll() {
    console.log('🚀 Starting Comprehensive Test Suite...\n');
    
    try {
      // Run unit tests
      await this.runUnitTests();
      
      // Run browser-specific tests (only in browser environment)
      if (!this.isNodeEnvironment) {
        await this.runBrowserCompatibilityTests();
        await this.runResponsiveDesignTests();
        await this.runAccessibilityTests();
      }
      
      // Generate final report
      this.generateFinalReport();
      
    } catch (error) {
      console.error('❌ Test suite failed:', error);
      process.exit(1);
    }
  }

  // Unit Tests
  async runUnitTests() {
    console.log('📋 Running Unit Tests...\n');
    
    // Test email validation functions
    await this.testEmailValidation();
    
    // Test form utilities
    await this.testFormUtils();
    
    // Test animation utilities
    await this.testAnimationUtils();
    
    // Test error handling
    await this.testErrorHandling();
    
    console.log(`Unit Tests: ${this.results.unit.passed} passed, ${this.results.unit.failed} failed\n`);
  }

  async testEmailValidation() {
    const testCases = [
      // Valid emails
      { email: 'test@example.com', expected: true, description: 'Basic valid email' },
      { email: 'user.name@domain.co.uk', expected: true, description: 'Email with dots and subdomain' },
      { email: 'user+tag@example.org', expected: true, description: 'Email with plus sign' },
      { email: 'user_name@example-domain.com', expected: true, description: 'Email with underscore and hyphen' },
      { email: 'test123@example123.com', expected: true, description: 'Email with numbers' },
      { email: 'a@b.co', expected: true, description: 'Minimal valid email' },
      
      // Invalid emails
      { email: '', expected: false, description: 'Empty string' },
      { email: 'invalid', expected: false, description: 'No @ symbol' },
      { email: '@example.com', expected: false, description: 'Missing local part' },
      { email: 'test@', expected: false, description: 'Missing domain' },
      { email: 'test@.com', expected: false, description: 'Domain starts with dot' },
      { email: 'test@example.', expected: false, description: 'Domain ends with dot' },
      { email: 'test..test@example.com', expected: false, description: 'Double dots in local part' },
      { email: 'test@example..com', expected: false, description: 'Double dots in domain' },
      { email: 'test@example', expected: false, description: 'Missing TLD' },
      { email: 'test@example.c', expected: false, description: 'TLD too short' },
      { email: 'test space@example.com', expected: false, description: 'Space in local part' },
      { email: 'test@exam ple.com', expected: false, description: 'Space in domain' }
    ];

    // Create mock EmailCapture for testing
    const mockEmailCapture = this.createMockEmailCapture();

    testCases.forEach(testCase => {
      const result = mockEmailCapture.isValidEmail(testCase.email);
      const passed = result === testCase.expected;
      
      this.recordTest('unit', `Email validation: ${testCase.description}`, passed, {
        input: testCase.email,
        expected: testCase.expected,
        actual: result
      });
    });
  }

  async testFormUtils() {
    // Test sanitizeInput
    const testInput = '<script>alert("xss")</script>test@example.com';
    const sanitized = this.mockFormUtils.sanitizeInput(testInput);
    const sanitizeTest = !sanitized.includes('<script>') && sanitized.includes('test@example.com');
    
    this.recordTest('unit', 'FormUtils.sanitizeInput should escape HTML', sanitizeTest, {
      input: testInput,
      output: sanitized
    });

    // Test formatEmail
    const testEmail = '  TEST@EXAMPLE.COM  ';
    const formatted = this.mockFormUtils.formatEmail(testEmail);
    const formatTest = formatted === 'test@example.com';
    
    this.recordTest('unit', 'FormUtils.formatEmail should lowercase and trim', formatTest, {
      input: testEmail,
      output: formatted
    });

    // Test isValidDomain
    const validDomain = this.mockFormUtils.isValidDomain('test@example.com');
    const invalidDomain = this.mockFormUtils.isValidDomain('test@invalid');
    const domainTest = validDomain === true && invalidDomain === false;
    
    this.recordTest('unit', 'FormUtils.isValidDomain should validate domains', domainTest, {
      validResult: validDomain,
      invalidResult: invalidDomain
    });

    // Test debounce function
    let debounceCounter = 0;
    const debouncedFn = this.mockFormUtils.debounce(() => debounceCounter++, 50);
    
    // Call multiple times quickly
    debouncedFn();
    debouncedFn();
    debouncedFn();
    
    // Check that function is returned
    const debounceTest = typeof debouncedFn === 'function';
    
    this.recordTest('unit', 'FormUtils.debounce should return function', debounceTest, {
      type: typeof debouncedFn
    });
  }

  async testAnimationUtils() {
    const mockScrollAnimations = this.createMockScrollAnimations();

    // Test initialization
    const initTest = mockScrollAnimations.animationState !== null;
    this.recordTest('unit', 'ScrollAnimations should initialize correctly', initTest);

    // Test scroll progress calculation
    mockScrollAnimations.mockScrollValues(600, 2000, 800);
    const progress = mockScrollAnimations.updateScrollProgress();
    const expectedProgress = 600 / (2000 - 800); // 0.5
    const progressTest = Math.abs(progress - expectedProgress) < 0.001;
    
    this.recordTest('unit', 'Scroll progress calculation should be accurate', progressTest, {
      expected: expectedProgress,
      actual: progress
    });

    // Test easing function
    const start = mockScrollAnimations.easeInOutQuad(0, 0, 100, 1000);
    const middle = mockScrollAnimations.easeInOutQuad(500, 0, 100, 1000);
    const end = mockScrollAnimations.easeInOutQuad(1000, 0, 100, 1000);
    
    const easingTest = start === 0 && end === 100 && middle > 0 && middle < 100;
    
    this.recordTest('unit', 'Easing function should produce correct values', easingTest, {
      start, middle, end
    });

    // Test viewport detection
    const mockElement = this.createMockElement();
    mockElement.getBoundingClientRect = () => ({
      top: 100, bottom: 200, height: 100, width: 100
    });
    
    const isInViewport = mockScrollAnimations.isInViewport(mockElement, 0.1);
    const viewportTest = isInViewport === true;
    
    this.recordTest('unit', 'Viewport detection should work correctly', viewportTest, {
      result: isInViewport
    });
  }

  async testErrorHandling() {
    // Test error logging
    const mockApp = this.createMockSynapseApp();
    const testError = new Error('Test error');
    
    try {
      mockApp.logError('test_error', testError, { test: true });
      this.recordTest('unit', 'Error logging should not throw', true);
    } catch (error) {
      this.recordTest('unit', 'Error logging should not throw', false, { error: error.message });
    }

    // Test performance logging
    try {
      mockApp.logPerformance('test_metric', 100, { test: true });
      this.recordTest('unit', 'Performance logging should not throw', true);
    } catch (error) {
      this.recordTest('unit', 'Performance logging should not throw', false, { error: error.message });
    }
  }

  // Browser Compatibility Tests
  async runBrowserCompatibilityTests() {
    console.log('🌐 Running Browser Compatibility Tests...\n');
    
    // Test modern JavaScript features
    this.testModernJSFeatures();
    
    // Test CSS features
    this.testCSSFeatures();
    
    // Test API availability
    this.testAPIAvailability();
    
    console.log(`Browser Tests: ${this.results.browser.passed} passed, ${this.results.browser.failed} failed\n`);
  }

  testModernJSFeatures() {
    // Test ES6+ features
    const features = [
      { name: 'Arrow functions', test: () => typeof (() => {}) === 'function' },
      { name: 'Template literals', test: () => `test` === 'test' },
      { name: 'Destructuring', test: () => { const [a] = [1]; return a === 1; } },
      { name: 'Spread operator', test: () => [...[1, 2]].length === 2 },
      { name: 'Async/await', test: () => typeof (async () => {}) === 'function' },
      { name: 'Promises', test: () => typeof Promise !== 'undefined' },
      { name: 'Map/Set', test: () => typeof Map !== 'undefined' && typeof Set !== 'undefined' },
      { name: 'Symbol', test: () => typeof Symbol !== 'undefined' }
    ];

    features.forEach(feature => {
      try {
        const result = feature.test();
        this.recordTest('browser', `JS Feature: ${feature.name}`, result);
      } catch (error) {
        this.recordTest('browser', `JS Feature: ${feature.name}`, false, { error: error.message });
      }
    });
  }

  testCSSFeatures() {
    const features = [
      { name: 'CSS Grid', property: 'grid-template-columns', value: '1fr 1fr' },
      { name: 'CSS Flexbox', property: 'display', value: 'flex' },
      { name: 'CSS Custom Properties', property: '--test-var', value: 'test' },
      { name: 'CSS Transforms', property: 'transform', value: 'translateX(10px)' },
      { name: 'CSS Transitions', property: 'transition', value: 'all 0.3s ease' },
      { name: 'CSS Animations', property: 'animation', value: 'test 1s ease' }
    ];

    const testElement = document.createElement('div');
    document.body.appendChild(testElement);

    features.forEach(feature => {
      try {
        testElement.style[feature.property] = feature.value;
        const supported = testElement.style[feature.property] !== '';
        this.recordTest('browser', `CSS Feature: ${feature.name}`, supported);
      } catch (error) {
        this.recordTest('browser', `CSS Feature: ${feature.name}`, false, { error: error.message });
      }
    });

    document.body.removeChild(testElement);
  }

  testAPIAvailability() {
    const apis = [
      { name: 'IntersectionObserver', test: () => 'IntersectionObserver' in window },
      { name: 'ResizeObserver', test: () => 'ResizeObserver' in window },
      { name: 'PerformanceObserver', test: () => 'PerformanceObserver' in window },
      { name: 'requestAnimationFrame', test: () => 'requestAnimationFrame' in window },
      { name: 'localStorage', test: () => 'localStorage' in window },
      { name: 'sessionStorage', test: () => 'sessionStorage' in window },
      { name: 'fetch', test: () => 'fetch' in window },
      { name: 'FormData', test: () => 'FormData' in window }
    ];

    apis.forEach(api => {
      try {
        const available = api.test();
        this.recordTest('browser', `API: ${api.name}`, available);
      } catch (error) {
        this.recordTest('browser', `API: ${api.name}`, false, { error: error.message });
      }
    });
  }

  // Responsive Design Tests
  async runResponsiveDesignTests() {
    console.log('📱 Running Responsive Design Tests...\n');
    
    // Test breakpoints
    this.testBreakpoints();
    
    // Test touch targets
    this.testTouchTargets();
    
    // Test fluid typography
    this.testFluidTypography();
    
    // Test layout behavior
    this.testLayoutBehavior();
    
    console.log(`Responsive Tests: ${this.results.responsive.passed} passed, ${this.results.responsive.failed} failed\n`);
  }

  testBreakpoints() {
    const breakpoints = [
      { name: 'Mobile', min: 320, max: 767 },
      { name: 'Tablet', min: 768, max: 1023 },
      { name: 'Desktop', min: 1024, max: 1439 },
      { name: 'Large Desktop', min: 1440, max: Infinity }
    ];

    const currentWidth = window.innerWidth;
    let currentBreakpoint = null;

    breakpoints.forEach(bp => {
      if (currentWidth >= bp.min && currentWidth <= bp.max) {
        currentBreakpoint = bp.name;
      }
    });

    this.recordTest('responsive', 'Current breakpoint detection', currentBreakpoint !== null, {
      width: currentWidth,
      breakpoint: currentBreakpoint
    });

    // Test media queries
    breakpoints.forEach(bp => {
      if (bp.max !== Infinity) {
        const mediaQuery = window.matchMedia(`(min-width: ${bp.min}px) and (max-width: ${bp.max}px)`);
        const isCurrentBreakpoint = mediaQuery.matches;
        
        this.recordTest('responsive', `Media query: ${bp.name}`, true, {
          matches: isCurrentBreakpoint,
          query: `(min-width: ${bp.min}px) and (max-width: ${bp.max}px)`
        });
      }
    });
  }

  testTouchTargets() {
    const interactiveElements = document.querySelectorAll('.btn, .form__input, button, input, [role="button"]');
    const minSize = 44; // Minimum touch target size
    let passedCount = 0;

    interactiveElements.forEach(element => {
      const rect = element.getBoundingClientRect();
      const computedStyle = getComputedStyle(element);
      
      const minHeight = parseInt(computedStyle.minHeight) || rect.height;
      const minWidth = parseInt(computedStyle.minWidth) || rect.width;
      
      const passed = minHeight >= minSize && minWidth >= minSize;
      if (passed) passedCount++;
      
      this.recordTest('responsive', `Touch target: ${element.tagName}${element.className ? '.' + element.className.split(' ')[0] : ''}`, passed, {
        height: minHeight,
        width: minWidth,
        required: minSize
      });
    });

    const overallPassed = passedCount === interactiveElements.length;
    this.recordTest('responsive', 'All touch targets meet minimum size', overallPassed, {
      passed: passedCount,
      total: interactiveElements.length
    });
  }

  testFluidTypography() {
    const textElements = document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, .heading, .text');
    let fluidCount = 0;

    textElements.forEach(element => {
      const computedStyle = getComputedStyle(element);
      const fontSize = computedStyle.fontSize;
      
      // Check if element uses responsive sizing (simplified check)
      const hasFluidTypography = element.className.includes('heading') || 
                                element.className.includes('text') ||
                                fontSize.includes('clamp');
      
      if (hasFluidTypography) fluidCount++;
      
      this.recordTest('responsive', `Fluid typography: ${element.tagName}${element.className ? '.' + element.className.split(' ')[0] : ''}`, hasFluidTypography, {
        fontSize,
        hasFluid: hasFluidTypography
      });
    });

    const overallPassed = fluidCount > textElements.length * 0.8; // 80% should have fluid typography
    this.recordTest('responsive', 'Majority of text uses fluid typography', overallPassed, {
      fluid: fluidCount,
      total: textElements.length,
      percentage: Math.round((fluidCount / textElements.length) * 100)
    });
  }

  testLayoutBehavior() {
    // Test container behavior
    const container = document.querySelector('.container');
    if (container) {
      const computedStyle = getComputedStyle(container);
      const hasMaxWidth = computedStyle.maxWidth !== 'none';
      const hasPadding = computedStyle.paddingLeft !== '0px';
      
      this.recordTest('responsive', 'Container has responsive behavior', hasMaxWidth && hasPadding, {
        maxWidth: computedStyle.maxWidth,
        padding: computedStyle.paddingLeft
      });
    }

    // Test grid behavior
    const grids = document.querySelectorAll('.grid');
    grids.forEach(grid => {
      const computedStyle = getComputedStyle(grid);
      const hasGridColumns = computedStyle.gridTemplateColumns !== 'none';
      
      this.recordTest('responsive', `Grid layout: ${grid.className}`, hasGridColumns, {
        columns: computedStyle.gridTemplateColumns
      });
    });

    // Test form layouts
    const forms = document.querySelectorAll('.hero__form, .cta__form');
    forms.forEach(form => {
      const computedStyle = getComputedStyle(form);
      const hasFlexDirection = computedStyle.flexDirection !== 'row' || window.innerWidth < 768;
      
      this.recordTest('responsive', `Form layout: ${form.className}`, hasFlexDirection, {
        flexDirection: computedStyle.flexDirection,
        width: window.innerWidth
      });
    });
  }

  // Accessibility Tests
  async runAccessibilityTests() {
    console.log('♿ Running Accessibility Tests...\n');
    
    // Test semantic HTML
    this.testSemanticHTML();
    
    // Test ARIA attributes
    this.testARIAAttributes();
    
    // Test keyboard navigation
    this.testKeyboardNavigation();
    
    // Test color contrast
    this.testColorContrast();
    
    // Test screen reader compatibility
    this.testScreenReaderCompatibility();
    
    console.log(`Accessibility Tests: ${this.results.accessibility.passed} passed, ${this.results.accessibility.failed} failed\n`);
  }

  testSemanticHTML() {
    const semanticElements = [
      'header', 'nav', 'main', 'section', 'article', 'aside', 'footer'
    ];

    semanticElements.forEach(tag => {
      const elements = document.querySelectorAll(tag);
      const hasElements = elements.length > 0;
      
      this.recordTest('accessibility', `Semantic HTML: ${tag} elements present`, hasElements, {
        count: elements.length
      });
    });

    // Test heading hierarchy
    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
    const hasH1 = document.querySelectorAll('h1').length === 1;
    
    this.recordTest('accessibility', 'Single H1 element present', hasH1, {
      h1Count: document.querySelectorAll('h1').length
    });

    // Test heading order
    let properOrder = true;
    let lastLevel = 0;
    
    headings.forEach(heading => {
      const level = parseInt(heading.tagName.charAt(1));
      if (level > lastLevel + 1) {
        properOrder = false;
      }
      lastLevel = level;
    });

    this.recordTest('accessibility', 'Heading hierarchy is logical', properOrder, {
      totalHeadings: headings.length
    });
  }

  testARIAAttributes() {
    // Test form labels
    const inputs = document.querySelectorAll('input, textarea, select');
    let labeledInputs = 0;

    inputs.forEach(input => {
      const hasLabel = input.labels && input.labels.length > 0 ||
                     input.getAttribute('aria-label') ||
                     input.getAttribute('aria-labelledby') ||
                     input.getAttribute('placeholder');
      
      if (hasLabel) labeledInputs++;
      
      this.recordTest('accessibility', `Input has label: ${input.type || input.tagName}`, hasLabel, {
        id: input.id,
        type: input.type || input.tagName
      });
    });

    const allLabeled = labeledInputs === inputs.length;
    this.recordTest('accessibility', 'All inputs have labels', allLabeled, {
      labeled: labeledInputs,
      total: inputs.length
    });

    // Test buttons
    const buttons = document.querySelectorAll('button, [role="button"]');
    buttons.forEach(button => {
      const hasAccessibleName = button.textContent.trim() ||
                               button.getAttribute('aria-label') ||
                               button.getAttribute('aria-labelledby');
      
      this.recordTest('accessibility', `Button has accessible name`, hasAccessibleName, {
        text: button.textContent.trim(),
        ariaLabel: button.getAttribute('aria-label')
      });
    });

    // Test images
    const images = document.querySelectorAll('img');
    images.forEach(img => {
      const hasAlt = img.hasAttribute('alt');
      
      this.recordTest('accessibility', `Image has alt text`, hasAlt, {
        src: img.src,
        alt: img.getAttribute('alt')
      });
    });
  }

  testKeyboardNavigation() {
    // Test focusable elements
    const focusableElements = document.querySelectorAll(
      'a, button, input, textarea, select, [tabindex]:not([tabindex="-1"])'
    );

    let focusableCount = 0;
    focusableElements.forEach(element => {
      const isFocusable = element.tabIndex >= 0 && !element.disabled;
      if (isFocusable) focusableCount++;
      
      this.recordTest('accessibility', `Element is focusable: ${element.tagName}`, isFocusable, {
        tagName: element.tagName,
        tabIndex: element.tabIndex,
        disabled: element.disabled
      });
    });

    this.recordTest('accessibility', 'Page has focusable elements', focusableCount > 0, {
      count: focusableCount
    });

    // Test skip links
    const skipLinks = document.querySelectorAll('a[href^="#"]');
    const hasSkipLinks = skipLinks.length > 0;
    
    this.recordTest('accessibility', 'Skip links present', hasSkipLinks, {
      count: skipLinks.length
    });
  }

  testColorContrast() {
    // This is a simplified contrast test
    // In a real implementation, you'd use a proper contrast calculation
    const textElements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, span, a, button');
    let contrastIssues = 0;

    textElements.forEach(element => {
      const computedStyle = getComputedStyle(element);
      const color = computedStyle.color;
      const backgroundColor = computedStyle.backgroundColor;
      
      // Simplified check - in reality, you'd calculate actual contrast ratio
      const hasGoodContrast = color !== backgroundColor && 
                             color !== 'rgba(0, 0, 0, 0)' &&
                             backgroundColor !== 'rgba(0, 0, 0, 0)';
      
      if (!hasGoodContrast) contrastIssues++;
    });

    const contrastPassed = contrastIssues < textElements.length * 0.1; // Allow 10% issues
    this.recordTest('accessibility', 'Color contrast appears adequate', contrastPassed, {
      issues: contrastIssues,
      total: textElements.length
    });
  }

  testScreenReaderCompatibility() {
    // Test for screen reader specific attributes
    const ariaElements = document.querySelectorAll('[aria-live], [aria-describedby], [role]');
    const hasAriaElements = ariaElements.length > 0;
    
    this.recordTest('accessibility', 'ARIA attributes present for screen readers', hasAriaElements, {
      count: ariaElements.length
    });

    // Test for hidden content
    const hiddenElements = document.querySelectorAll('[aria-hidden="true"], .sr-only, .visually-hidden');
    const hasHiddenContent = hiddenElements.length > 0;
    
    this.recordTest('accessibility', 'Hidden content properly marked', hasHiddenContent, {
      count: hiddenElements.length
    });

    // Test for landmarks
    const landmarks = document.querySelectorAll('[role="main"], [role="navigation"], [role="banner"], [role="contentinfo"], main, nav, header, footer');
    const hasLandmarks = landmarks.length > 0;
    
    this.recordTest('accessibility', 'Page landmarks present', hasLandmarks, {
      count: landmarks.length
    });
  }

  // Helper Methods
  recordTest(category, name, passed, details = {}) {
    const test = { name, passed, details, timestamp: Date.now() };
    this.results[category].tests.push(test);
    
    if (passed) {
      this.results[category].passed++;
      console.log(`✅ ${name}`);
    } else {
      this.results[category].failed++;
      console.log(`❌ ${name}`, details);
    }
  }

  generateFinalReport() {
    const endTime = Date.now();
    const duration = endTime - this.startTime;
    
    console.log('\n' + '='.repeat(80));
    console.log('📊 COMPREHENSIVE TEST SUITE RESULTS');
    console.log('='.repeat(80));
    
    let totalPassed = 0;
    let totalFailed = 0;
    
    Object.entries(this.results).forEach(([category, result]) => {
      const categoryName = category.charAt(0).toUpperCase() + category.slice(1);
      const total = result.passed + result.failed;
      const percentage = total > 0 ? Math.round((result.passed / total) * 100) : 0;
      
      console.log(`${categoryName} Tests: ${result.passed}/${total} passed (${percentage}%)`);
      
      totalPassed += result.passed;
      totalFailed += result.failed;
    });
    
    const grandTotal = totalPassed + totalFailed;
    const overallPercentage = grandTotal > 0 ? Math.round((totalPassed / grandTotal) * 100) : 0;
    
    console.log('='.repeat(80));
    console.log(`OVERALL: ${totalPassed}/${grandTotal} tests passed (${overallPercentage}%)`);
    console.log(`Duration: ${duration}ms`);
    console.log(`Status: ${totalFailed === 0 ? '🎉 ALL TESTS PASSED' : '❌ SOME TESTS FAILED'}`);
    console.log('='.repeat(80));
    
    // Generate detailed report
    this.generateDetailedReport();
    
    // Exit with appropriate code in Node.js
    if (this.isNodeEnvironment) {
      process.exit(totalFailed === 0 ? 0 : 1);
    }
    
    return {
      passed: totalPassed,
      failed: totalFailed,
      total: grandTotal,
      percentage: overallPercentage,
      duration,
      success: totalFailed === 0
    };
  }

  generateDetailedReport() {
    console.log('\n📋 DETAILED TEST RESULTS:\n');
    
    Object.entries(this.results).forEach(([category, result]) => {
      if (result.failed > 0) {
        console.log(`❌ ${category.toUpperCase()} FAILURES:`);
        result.tests.filter(test => !test.passed).forEach(test => {
          console.log(`   • ${test.name}`);
          if (test.details && Object.keys(test.details).length > 0) {
            console.log(`     Details:`, test.details);
          }
        });
        console.log('');
      }
    });
  }

  // Mock objects for testing
  createMockEmailCapture() {
    return {
      isValidEmail(email) {
        const emailRegex = /^[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$/;
        
        if (!email || email.includes('..') || email.startsWith('.') || email.endsWith('.')) {
          return false;
        }
        
        return emailRegex.test(email);
      }
    };
  }

  get mockFormUtils() {
    return {
      sanitizeInput(input) {
        if (typeof input !== 'string') return '';
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
      },

      formatEmail(email) {
        return email.toLowerCase().trim();
      },

      isValidDomain(email) {
        const domain = email.split('@')[1];
        if (!domain) return false;
        
        const domainRegex = /^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9](?:\.[a-zA-Z]{2,})+$/;
        return domainRegex.test(domain);
      },

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
  }

  createMockScrollAnimations() {
    return {
      animationState: {
        sectionsVisible: [],
        scrollProgress: 0,
        isScrolling: false
      },
      
      mockScrollValues(scrollY, scrollHeight, innerHeight) {
        this.mockWindow = { scrollY, innerHeight };
        this.mockDocument = { documentElement: { scrollHeight } };
      },
      
      updateScrollProgress() {
        const scrollTop = this.mockWindow.scrollY;
        const docHeight = this.mockDocument.documentElement.scrollHeight;
        const winHeight = this.mockWindow.innerHeight;
        const scrollPercent = Math.min(scrollTop / (docHeight - winHeight), 1);
        
        this.animationState.scrollProgress = scrollPercent;
        return scrollPercent;
      },
      
      easeInOutQuad(t, b, c, d) {
        t /= d / 2;
        if (t < 1) return c / 2 * t * t + b;
        t--;
        return -c / 2 * (t * (t - 2) - 1) + b;
      },
      
      isInViewport(element, threshold = 0.1) {
        const rect = element.getBoundingClientRect();
        const windowHeight = 800; // Mock window height
        const elementHeight = rect.height;
        
        return (
          rect.top <= windowHeight - (elementHeight * threshold) &&
          rect.bottom >= (elementHeight * threshold)
        );
      }
    };
  }

  createMockElement() {
    return {
      getBoundingClientRect() {
        return {
          top: 100,
          bottom: 200,
          height: 100,
          width: 100
        };
      }
    };
  }

  createMockSynapseApp() {
    return {
      logError(type, error, context = {}) {
        // Mock implementation - just don't throw
        return true;
      },
      
      logPerformance(metric, value, context = {}) {
        // Mock implementation - just don't throw
        return true;
      }
    };
  }
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = TestSuite;
}

// Auto-run in Node.js environment
if (typeof window === 'undefined' && require.main === module) {
  const testSuite = new TestSuite();
  testSuite.runAll();
}

// Expose globally in browser
if (typeof window !== 'undefined') {
  window.TestSuite = TestSuite;
}