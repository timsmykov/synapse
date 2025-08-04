# Testing Guide - Synapse Landing Page

This document provides comprehensive information about testing the Synapse Landing Page, covering unit tests, cross-browser compatibility, responsive design, and accessibility testing.

## Overview

The testing suite ensures the landing page meets all requirements:
- **Unit Tests**: JavaScript functions, form validation, animation utilities
- **Cross-Browser Compatibility**: Chrome, Firefox, Safari, Edge support
- **Responsive Design**: Mobile, tablet, desktop viewport testing
- **Accessibility**: WCAG AA compliance and screen reader compatibility

## Quick Start

### Run All Tests
```bash
# Install dependencies (optional)
npm install

# Run comprehensive test suite
npm test

# Or run directly
node run-tests.js
```

### Run Specific Test Categories
```bash
# Unit tests only
npm run test:unit

# Responsive design tests
npm run test:responsive

# Accessibility tests
npm run test:accessibility

# Individual test files
npm run test:email
npm run test:animations
```

### Browser Testing
```bash
# Start local server
npm run serve

# Open in browser
open http://localhost:8000/test-runner.html
```

## Test Files Structure

```
├── test-suite.js                    # Main comprehensive test suite
├── test-runner.html                 # Browser-based test interface
├── run-tests.js                     # Node.js test executor
├── package.json                     # Test scripts and dependencies
├── TESTING.md                       # This documentation
│
├── Unit Tests/
│   ├── test-email-validation.js     # Email validation functions
│   ├── test-animations.js           # Animation utilities
│   └── test-forms.html              # Form testing interface
│
├── Browser Compatibility/
│   ├── test-browser-compatibility.js # Cross-browser feature detection
│   └── test-performance.html        # Performance optimization tests
│
├── Responsive Design/
│   ├── test-responsive.html         # Responsive design testing
│   ├── test-breakpoints.js          # Breakpoint behavior tests
│   └── validate-responsive.js       # Responsive validation
│
├── Accessibility/
│   ├── accessibility-checklist.md   # WCAG AA compliance checklist
│   └── test-scroll-animations.html  # Animation accessibility tests
│
└── Validation/
    ├── validate-css.js              # CSS validation
    └── validate-responsive.js       # Responsive validation
```

## Unit Tests

### Email Validation Tests
Tests the `EmailCapture` class and `FormUtils` functions:

```bash
node test-email-validation.js
```

**Coverage:**
- Email format validation (RFC 5322 compliance)
- Input sanitization (XSS prevention)
- Domain validation
- Error handling and retry mechanisms
- Form state management

**Test Cases:**
- Valid emails: `test@example.com`, `user.name@domain.co.uk`
- Invalid emails: `invalid`, `@example.com`, `test@`
- Edge cases: Empty strings, special characters, Unicode

### Animation Tests
Tests the `ScrollAnimations` class and related utilities:

```bash
node test-animations.js
```

**Coverage:**
- Intersection Observer functionality
- Scroll progress calculation
- Easing functions
- Viewport detection
- Animation state management
- Performance optimizations

## Cross-Browser Compatibility

### Supported Browsers
- **Chrome**: 90+ (Blink engine)
- **Firefox**: 88+ (Gecko engine)
- **Safari**: 14+ (WebKit engine)
- **Edge**: 90+ (Chromium-based)

### Testing Process
1. Open `test-runner.html` in each target browser
2. Run browser compatibility tests
3. Review feature support matrix
4. Check for critical issues and fallbacks

### Feature Detection
The test suite checks for:
- **JavaScript**: ES6+ features, async/await, Promises
- **Web APIs**: IntersectionObserver, Fetch, FormData
- **CSS**: Grid, Flexbox, Custom Properties, Transforms

### Browser-Specific Quirks
- **Safari iOS**: Viewport units and UI bars
- **Firefox**: Date input support variations
- **Chrome**: Autofill styling requirements
- **Edge**: Legacy compatibility considerations

## Responsive Design Testing

### Breakpoints
- **Mobile**: 320px - 767px
- **Tablet**: 768px - 1023px
- **Desktop**: 1024px - 1439px
- **Large Desktop**: 1440px+

### Testing Process
```bash
# Open responsive test page
open test-responsive.html

# Or run validation
node validate-responsive.js
```

### Test Coverage
- **Layout Adaptation**: Grid and flexbox behavior
- **Touch Targets**: Minimum 44px × 44px requirement
- **Typography**: Fluid scaling with clamp() functions
- **Images**: Responsive sizing and optimization
- **Forms**: Mobile-friendly input and button sizing

### Validation Criteria
- All interactive elements meet touch target requirements
- Text remains readable at 200% zoom
- No horizontal scrolling on mobile devices
- Layout adapts gracefully across all breakpoints

## Accessibility Testing

### WCAG AA Compliance
The landing page targets WCAG 2.1 AA compliance. See `accessibility-checklist.md` for detailed requirements.

### Testing Tools
- **Automated**: axe-core, WAVE, Lighthouse
- **Manual**: Screen readers, keyboard navigation
- **Checklist**: Comprehensive WCAG criteria review

### Screen Reader Testing
- **NVDA** (Windows, free)
- **JAWS** (Windows, commercial)
- **VoiceOver** (macOS/iOS, built-in)
- **TalkBack** (Android, built-in)

### Keyboard Navigation
- Tab order follows logical sequence
- All interactive elements are focusable
- Focus indicators are clearly visible
- Escape key closes modals/overlays

### Color and Contrast
- Text contrast ratios meet WCAG AA standards
- Information not conveyed by color alone
- High contrast mode compatibility

## Performance Testing

### Core Web Vitals
- **LCP** (Largest Contentful Paint): < 2.5s
- **FID** (First Input Delay): < 100ms
- **CLS** (Cumulative Layout Shift): < 0.1

### Testing Process
```bash
open test-performance.html
```

### Optimization Features
- Reduced motion support (`prefers-reduced-motion`)
- Low-end device detection and adaptation
- Graceful degradation for older browsers
- Error handling with retry mechanisms

## Continuous Integration

### GitHub Actions Example
```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm test
      - uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: test-results.*
```

### Test Reports
- **JSON**: `test-results.json` (detailed results)
- **JUnit XML**: `test-results.xml` (CI/CD integration)
- **Console**: Real-time progress and summary

## Manual Testing Checklist

### Before Release
- [ ] All automated tests pass
- [ ] Manual browser testing complete
- [ ] Responsive design verified on real devices
- [ ] Accessibility tested with screen readers
- [ ] Performance metrics meet targets
- [ ] Error handling scenarios tested

### Device Testing
- [ ] iPhone (Safari)
- [ ] Android (Chrome)
- [ ] iPad (Safari)
- [ ] Desktop (Chrome, Firefox, Safari, Edge)
- [ ] High-DPI displays
- [ ] Touch and mouse interactions

### Network Conditions
- [ ] Fast 3G connection
- [ ] Slow 3G connection
- [ ] Offline behavior
- [ ] Connection interruption recovery

## Troubleshooting

### Common Issues

**Tests fail in Node.js but pass in browser:**
- Check for browser-specific APIs
- Verify DOM mocking is correct
- Ensure proper async handling

**Responsive tests show false positives:**
- Test on actual devices
- Check for CSS loading issues
- Verify viewport meta tag

**Accessibility tests miss issues:**
- Supplement with manual testing
- Use multiple testing tools
- Test with real assistive technology

### Debug Mode
```bash
# Run tests with verbose output
DEBUG=true npm test

# Run specific test with debugging
node --inspect test-email-validation.js
```

### Getting Help
- Check browser console for errors
- Review test output for specific failures
- Verify all dependencies are loaded
- Test in isolation to identify conflicts

## Contributing

### Adding New Tests
1. Create test file following naming convention
2. Add to appropriate category in `package.json`
3. Update this documentation
4. Ensure tests are deterministic and isolated

### Test Standards
- Tests should be fast and reliable
- Mock external dependencies
- Use descriptive test names
- Include both positive and negative cases
- Document complex test logic

### Code Coverage
While not enforced, aim for high coverage of:
- Critical user paths
- Error handling scenarios
- Cross-browser compatibility features
- Accessibility requirements

---

For questions or issues with testing, please refer to the project documentation or create an issue in the repository.