/**
 * Cross-Browser Compatibility Test Suite
 * Tests for Chrome, Firefox, Safari, and Edge compatibility
 */

class BrowserCompatibilityTester {
  constructor() {
    this.browserInfo = this.detectBrowser();
    this.results = {
      browser: this.browserInfo,
      features: [],
      apis: [],
      css: [],
      performance: {},
      issues: []
    };
    this.init();
  }

  init() {
    console.log(`🌐 Testing compatibility for ${this.browserInfo.name} ${this.browserInfo.version}`);
    this.runAllTests();
  }

  detectBrowser() {
    const userAgent = navigator.userAgent;
    let browser = { name: 'Unknown', version: 'Unknown', engine: 'Unknown' };

    // Chrome
    if (userAgent.includes('Chrome') && !userAgent.includes('Edg')) {
      const match = userAgent.match(/Chrome\/(\d+)/);
      browser = {
        name: 'Chrome',
        version: match ? match[1] : 'Unknown',
        engine: 'Blink'
      };
    }
    // Firefox
    else if (userAgent.includes('Firefox')) {
      const match = userAgent.match(/Firefox\/(\d+)/);
      browser = {
        name: 'Firefox',
        version: match ? match[1] : 'Unknown',
        engine: 'Gecko'
      };
    }
    // Safari
    else if (userAgent.includes('Safari') && !userAgent.includes('Chrome')) {
      const match = userAgent.match(/Version\/(\d+)/);
      browser = {
        name: 'Safari',
        version: match ? match[1] : 'Unknown',
        engine: 'WebKit'
      };
    }
    // Edge
    else if (userAgent.includes('Edg')) {
      const match = userAgent.match(/Edg\/(\d+)/);
      browser = {
        name: 'Edge',
        version: match ? match[1] : 'Unknown',
        engine: 'Blink'
      };
    }

    return browser;
  }

  runAllTests() {
    console.log('\n📋 Running Browser Compatibility Tests...\n');

    // Test JavaScript features
    this.testJavaScriptFeatures();
    
    // Test Web APIs
    this.testWebAPIs();
    
    // Test CSS features
    this.testCSSFeatures();
    
    // Test performance APIs
    this.testPerformanceAPIs();
    
    // Test specific browser quirks
    this.testBrowserQuirks();
    
    // Generate report
    this.generateCompatibilityReport();
  }

  testJavaScriptFeatures() {
    console.log('🔧 Testing JavaScript Features...');

    const features = [
      {
        name: 'ES6 Arrow Functions',
        test: () => {
          try {
            const arrow = () => true;
            return typeof arrow === 'function' && arrow();
          } catch (e) { return false; }
        },
        critical: true
      },
      {
        name: 'ES6 Template Literals',
        test: () => {
          try {
            const test = 'world';
            return `hello ${test}` === 'hello world';
          } catch (e) { return false; }
        },
        critical: true
      },
      {
        name: 'ES6 Destructuring',
        test: () => {
          try {
            const [a, b] = [1, 2];
            const {x, y} = {x: 3, y: 4};
            return a === 1 && b === 2 && x === 3 && y === 4;
          } catch (e) { return false; }
        },
        critical: false
      },
      {
        name: 'ES6 Spread Operator',
        test: () => {
          try {
            const arr1 = [1, 2];
            const arr2 = [...arr1, 3];
            return arr2.length === 3 && arr2[2] === 3;
          } catch (e) { return false; }
        },
        critical: false
      },
      {
        name: 'ES6 Classes',
        test: () => {
          try {
            class TestClass {
              constructor() { this.value = 'test'; }
            }
            const instance = new TestClass();
            return instance.value === 'test';
          } catch (e) { return false; }
        },
        critical: true
      },
      {
        name: 'ES2017 Async/Await',
        test: () => {
          try {
            const asyncFn = async () => 'test';
            return typeof asyncFn === 'function';
          } catch (e) { return false; }
        },
        critical: true
      },
      {
        name: 'ES6 Promises',
        test: () => {
          try {
            return typeof Promise !== 'undefined' && 
                   typeof Promise.resolve === 'function';
          } catch (e) { return false; }
        },
        critical: true
      },
      {
        name: 'ES6 Map and Set',
        test: () => {
          try {
            const map = new Map();
            const set = new Set();
            return map instanceof Map && set instanceof Set;
          } catch (e) { return false; }
        },
        critical: false
      },
      {
        name: 'ES6 Symbol',
        test: () => {
          try {
            const sym = Symbol('test');
            return typeof sym === 'symbol';
          } catch (e) { return false; }
        },
        critical: false
      },
      {
        name: 'ES2018 Object Rest/Spread',
        test: () => {
          try {
            const obj1 = {a: 1, b: 2};
            const obj2 = {...obj1, c: 3};
            return obj2.a === 1 && obj2.c === 3;
          } catch (e) { return false; }
        },
        critical: false
      }
    ];

    features.forEach(feature => {
      const supported = feature.test();
      this.results.features.push({
        name: feature.name,
        supported,
        critical: feature.critical
      });
      
      const status = supported ? '✅' : '❌';
      const priority = feature.critical ? ' (CRITICAL)' : '';
      console.log(`  ${status} ${feature.name}${priority}`);
      
      if (!supported && feature.critical) {
        this.results.issues.push({
          type: 'critical',
          category: 'javascript',
          message: `Critical JavaScript feature not supported: ${feature.name}`
        });
      }
    });
  }

  testWebAPIs() {
    console.log('\n🔌 Testing Web APIs...');

    const apis = [
      {
        name: 'IntersectionObserver',
        test: () => 'IntersectionObserver' in window,
        critical: true,
        fallback: 'Scroll event listeners'
      },
      {
        name: 'ResizeObserver',
        test: () => 'ResizeObserver' in window,
        critical: false,
        fallback: 'Window resize events'
      },
      {
        name: 'PerformanceObserver',
        test: () => 'PerformanceObserver' in window,
        critical: false,
        fallback: 'Basic performance.now()'
      },
      {
        name: 'requestAnimationFrame',
        test: () => 'requestAnimationFrame' in window,
        critical: true,
        fallback: 'setTimeout fallback'
      },
      {
        name: 'Fetch API',
        test: () => 'fetch' in window,
        critical: true,
        fallback: 'XMLHttpRequest'
      },
      {
        name: 'FormData',
        test: () => 'FormData' in window,
        critical: true,
        fallback: 'Manual form serialization'
      },
      {
        name: 'localStorage',
        test: () => {
          try {
            localStorage.setItem('test', 'test');
            localStorage.removeItem('test');
            return true;
          } catch (e) { return false; }
        },
        critical: false,
        fallback: 'Session storage or cookies'
      },
      {
        name: 'sessionStorage',
        test: () => {
          try {
            sessionStorage.setItem('test', 'test');
            sessionStorage.removeItem('test');
            return true;
          } catch (e) { return false; }
        },
        critical: false,
        fallback: 'Cookies or memory storage'
      },
      {
        name: 'History API',
        test: () => 'pushState' in history,
        critical: false,
        fallback: 'Hash-based routing'
      },
      {
        name: 'Geolocation API',
        test: () => 'geolocation' in navigator,
        critical: false,
        fallback: 'IP-based location'
      },
      {
        name: 'Notification API',
        test: () => 'Notification' in window,
        critical: false,
        fallback: 'In-page notifications'
      },
      {
        name: 'Service Worker',
        test: () => 'serviceWorker' in navigator,
        critical: false,
        fallback: 'No offline support'
      }
    ];

    apis.forEach(api => {
      const supported = api.test();
      this.results.apis.push({
        name: api.name,
        supported,
        critical: api.critical,
        fallback: api.fallback
      });
      
      const status = supported ? '✅' : '❌';
      const priority = api.critical ? ' (CRITICAL)' : '';
      const fallbackInfo = !supported ? ` - Fallback: ${api.fallback}` : '';
      console.log(`  ${status} ${api.name}${priority}${fallbackInfo}`);
      
      if (!supported && api.critical) {
        this.results.issues.push({
          type: 'critical',
          category: 'api',
          message: `Critical Web API not supported: ${api.name}`,
          fallback: api.fallback
        });
      }
    });
  }

  testCSSFeatures() {
    console.log('\n🎨 Testing CSS Features...');

    const testElement = document.createElement('div');
    document.body.appendChild(testElement);

    const cssFeatures = [
      {
        name: 'CSS Grid',
        test: () => {
          testElement.style.display = 'grid';
          return testElement.style.display === 'grid';
        },
        critical: true,
        fallback: 'Flexbox layout'
      },
      {
        name: 'CSS Flexbox',
        test: () => {
          testElement.style.display = 'flex';
          return testElement.style.display === 'flex';
        },
        critical: true,
        fallback: 'Float-based layout'
      },
      {
        name: 'CSS Custom Properties',
        test: () => {
          testElement.style.setProperty('--test-var', 'test');
          return testElement.style.getPropertyValue('--test-var') === 'test';
        },
        critical: true,
        fallback: 'Sass variables'
      },
      {
        name: 'CSS Transforms',
        test: () => {
          testElement.style.transform = 'translateX(10px)';
          return testElement.style.transform !== '';
        },
        critical: true,
        fallback: 'Position-based animations'
      },
      {
        name: 'CSS Transitions',
        test: () => {
          testElement.style.transition = 'all 0.3s ease';
          return testElement.style.transition !== '';
        },
        critical: true,
        fallback: 'JavaScript animations'
      },
      {
        name: 'CSS Animations',
        test: () => {
          testElement.style.animation = 'test 1s ease';
          return testElement.style.animation !== '';
        },
        critical: false,
        fallback: 'CSS transitions'
      },
      {
        name: 'CSS calc()',
        test: () => {
          testElement.style.width = 'calc(100% - 20px)';
          return testElement.style.width.includes('calc');
        },
        critical: false,
        fallback: 'Fixed dimensions'
      },
      {
        name: 'CSS clamp()',
        test: () => {
          testElement.style.fontSize = 'clamp(1rem, 2vw, 2rem)';
          return testElement.style.fontSize.includes('clamp');
        },
        critical: false,
        fallback: 'Media query breakpoints'
      },
      {
        name: 'CSS backdrop-filter',
        test: () => {
          testElement.style.backdropFilter = 'blur(10px)';
          return testElement.style.backdropFilter !== '';
        },
        critical: false,
        fallback: 'Solid backgrounds'
      },
      {
        name: 'CSS object-fit',
        test: () => {
          testElement.style.objectFit = 'cover';
          return testElement.style.objectFit === 'cover';
        },
        critical: false,
        fallback: 'Background images'
      }
    ];

    cssFeatures.forEach(feature => {
      const supported = feature.test();
      this.results.css.push({
        name: feature.name,
        supported,
        critical: feature.critical,
        fallback: feature.fallback
      });
      
      const status = supported ? '✅' : '❌';
      const priority = feature.critical ? ' (CRITICAL)' : '';
      const fallbackInfo = !supported ? ` - Fallback: ${feature.fallback}` : '';
      console.log(`  ${status} ${feature.name}${priority}${fallbackInfo}`);
      
      if (!supported && feature.critical) {
        this.results.issues.push({
          type: 'critical',
          category: 'css',
          message: `Critical CSS feature not supported: ${feature.name}`,
          fallback: feature.fallback
        });
      }
    });

    document.body.removeChild(testElement);
  }

  testPerformanceAPIs() {
    console.log('\n⚡ Testing Performance APIs...');

    const performanceTests = [
      {
        name: 'Performance.now()',
        test: () => typeof performance.now === 'function',
        critical: true
      },
      {
        name: 'Performance.mark()',
        test: () => typeof performance.mark === 'function',
        critical: false
      },
      {
        name: 'Performance.measure()',
        test: () => typeof performance.measure === 'function',
        critical: false
      },
      {
        name: 'Performance.getEntries()',
        test: () => typeof performance.getEntries === 'function',
        critical: false
      },
      {
        name: 'Performance.memory',
        test: () => 'memory' in performance,
        critical: false
      },
      {
        name: 'Navigation Timing',
        test: () => performance.getEntriesByType('navigation').length > 0,
        critical: false
      }
    ];

    performanceTests.forEach(test => {
      const supported = test.test();
      this.results.performance[test.name] = supported;
      
      const status = supported ? '✅' : '❌';
      const priority = test.critical ? ' (CRITICAL)' : '';
      console.log(`  ${status} ${test.name}${priority}`);
    });
  }

  testBrowserQuirks() {
    console.log('\n🔍 Testing Browser-Specific Quirks...');

    const quirks = [
      {
        name: 'Safari iOS viewport units bug',
        test: () => {
          // Test if 100vh includes Safari's UI bars
          return !(this.browserInfo.name === 'Safari' && /iPhone|iPad/.test(navigator.userAgent));
        },
        browser: 'Safari iOS',
        workaround: 'Use JavaScript to set --vh custom property'
      },
      {
        name: 'IE11 flexbox bugs',
        test: () => !navigator.userAgent.includes('Trident'),
        browser: 'IE11',
        workaround: 'Use flexbox polyfill or alternative layouts'
      },
      {
        name: 'Firefox date input support',
        test: () => {
          const input = document.createElement('input');
          input.type = 'date';
          return input.type === 'date';
        },
        browser: 'Firefox (older versions)',
        workaround: 'Use date picker library'
      },
      {
        name: 'Chrome autofill styling',
        test: () => this.browserInfo.name === 'Chrome',
        browser: 'Chrome',
        workaround: 'Use -webkit-autofill pseudo-selector'
      },
      {
        name: 'Safari smooth scrolling',
        test: () => {
          const testEl = document.createElement('div');
          testEl.style.scrollBehavior = 'smooth';
          return testEl.style.scrollBehavior === 'smooth';
        },
        browser: 'Safari (older versions)',
        workaround: 'Use JavaScript smooth scrolling'
      }
    ];

    quirks.forEach(quirk => {
      const hasQuirk = !quirk.test();
      const status = hasQuirk ? '⚠️' : '✅';
      console.log(`  ${status} ${quirk.name}`);
      
      if (hasQuirk) {
        this.results.issues.push({
          type: 'quirk',
          category: 'browser-specific',
          message: `Browser quirk detected: ${quirk.name}`,
          browser: quirk.browser,
          workaround: quirk.workaround
        });
      }
    });
  }

  generateCompatibilityReport() {
    console.log('\n' + '='.repeat(80));
    console.log('📊 BROWSER COMPATIBILITY REPORT');
    console.log('='.repeat(80));
    
    console.log(`Browser: ${this.browserInfo.name} ${this.browserInfo.version} (${this.browserInfo.engine})`);
    console.log(`User Agent: ${navigator.userAgent}`);
    console.log(`Platform: ${navigator.platform}`);
    console.log(`Screen: ${screen.width}x${screen.height}`);
    console.log(`Viewport: ${window.innerWidth}x${window.innerHeight}`);
    
    // Feature support summary
    const jsSupported = this.results.features.filter(f => f.supported).length;
    const jsTotal = this.results.features.length;
    const apiSupported = this.results.apis.filter(a => a.supported).length;
    const apiTotal = this.results.apis.length;
    const cssSupported = this.results.css.filter(c => c.supported).length;
    const cssTotal = this.results.css.length;
    
    console.log('\n📈 Feature Support Summary:');
    console.log(`JavaScript Features: ${jsSupported}/${jsTotal} (${Math.round(jsSupported/jsTotal*100)}%)`);
    console.log(`Web APIs: ${apiSupported}/${apiTotal} (${Math.round(apiSupported/apiTotal*100)}%)`);
    console.log(`CSS Features: ${cssSupported}/${cssTotal} (${Math.round(cssSupported/cssTotal*100)}%)`);
    
    // Critical issues
    const criticalIssues = this.results.issues.filter(i => i.type === 'critical');
    if (criticalIssues.length > 0) {
      console.log('\n🚨 Critical Issues:');
      criticalIssues.forEach(issue => {
        console.log(`  ❌ ${issue.message}`);
        if (issue.fallback) {
          console.log(`     Fallback: ${issue.fallback}`);
        }
      });
    } else {
      console.log('\n✅ No critical compatibility issues detected!');
    }
    
    // Browser quirks
    const quirks = this.results.issues.filter(i => i.type === 'quirk');
    if (quirks.length > 0) {
      console.log('\n⚠️  Browser Quirks:');
      quirks.forEach(quirk => {
        console.log(`  ⚠️  ${quirk.message}`);
        console.log(`     Workaround: ${quirk.workaround}`);
      });
    }
    
    // Recommendations
    this.generateRecommendations();
    
    console.log('='.repeat(80));
    
    // Store results globally for access
    window.browserCompatibilityResults = this.results;
    
    return this.results;
  }

  generateRecommendations() {
    console.log('\n💡 Recommendations:');
    
    const criticalIssues = this.results.issues.filter(i => i.type === 'critical');
    
    if (criticalIssues.length === 0) {
      console.log('  ✅ Browser is fully compatible with the landing page');
    } else {
      console.log('  🔧 Consider implementing the following:');
      
      // JavaScript polyfills
      const jsIssues = criticalIssues.filter(i => i.category === 'javascript');
      if (jsIssues.length > 0) {
        console.log('    • Add JavaScript polyfills for missing ES6+ features');
        console.log('    • Consider using Babel for broader browser support');
      }
      
      // CSS fallbacks
      const cssIssues = criticalIssues.filter(i => i.category === 'css');
      if (cssIssues.length > 0) {
        console.log('    • Implement CSS fallbacks for unsupported features');
        console.log('    • Use progressive enhancement approach');
      }
      
      // API fallbacks
      const apiIssues = criticalIssues.filter(i => i.category === 'api');
      if (apiIssues.length > 0) {
        console.log('    • Add polyfills for missing Web APIs');
        console.log('    • Implement graceful degradation');
      }
    }
    
    // Browser-specific recommendations
    if (this.browserInfo.name === 'Safari') {
      console.log('  🍎 Safari-specific:');
      console.log('    • Test viewport units on iOS devices');
      console.log('    • Verify smooth scrolling behavior');
    }
    
    if (this.browserInfo.name === 'Firefox') {
      console.log('  🦊 Firefox-specific:');
      console.log('    • Test form input types');
      console.log('    • Verify CSS Grid behavior');
    }
    
    if (this.browserInfo.name === 'Edge') {
      console.log('  🌐 Edge-specific:');
      console.log('    • Test legacy Edge compatibility if needed');
      console.log('    • Verify Chromium-based features');
    }
  }
}

// Auto-run when page loads
document.addEventListener('DOMContentLoaded', () => {
  window.browserCompatibilityTester = new BrowserCompatibilityTester();
});

// Expose for manual testing
window.testBrowserCompatibility = () => {
  return new BrowserCompatibilityTester();
};

// Export for Node.js testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = BrowserCompatibilityTester;
}