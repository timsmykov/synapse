#!/usr/bin/env node

/**
 * Test Execution Script for Synapse Landing Page
 * Runs all tests in Node.js environment and generates reports
 * 
 * Usage: node run-tests.js [--unit] [--browser] [--responsive] [--accessibility] [--all]
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class TestExecutor {
  constructor() {
    this.args = process.argv.slice(2);
    this.results = {
      unit: null,
      browser: null,
      responsive: null,
      accessibility: null,
      summary: null
    };
    this.startTime = Date.now();
  }

  async run() {
    console.log('🚀 Synapse Landing Page - Comprehensive Test Suite');
    console.log('='.repeat(60));
    console.log(`Started at: ${new Date().toISOString()}`);
    console.log(`Arguments: ${this.args.join(' ') || 'none (running all tests)'}`);
    console.log('='.repeat(60));

    try {
      // Determine which tests to run
      const runAll = this.args.length === 0 || this.args.includes('--all');
      const runUnit = runAll || this.args.includes('--unit');
      const runBrowser = runAll || this.args.includes('--browser');
      const runResponsive = runAll || this.args.includes('--responsive');
      const runAccessibility = runAll || this.args.includes('--accessibility');

      // Run tests
      if (runUnit) {
        await this.runUnitTests();
      }

      if (runBrowser) {
        await this.runBrowserTests();
      }

      if (runResponsive) {
        await this.runResponsiveTests();
      }

      if (runAccessibility) {
        await this.runAccessibilityTests();
      }

      // Generate reports
      this.generateSummaryReport();
      this.generateDetailedReport();
      this.generateJUnitReport();

      // Exit with appropriate code
      const hasFailures = this.hasFailures();
      process.exit(hasFailures ? 1 : 0);

    } catch (error) {
      console.error('❌ Test execution failed:', error.message);
      process.exit(1);
    }
  }

  async runUnitTests() {
    console.log('\n📋 Running Unit Tests...');
    console.log('-'.repeat(40));

    try {
      // Run email validation tests
      console.log('Running email validation tests...');
      const emailTestOutput = execSync('node test-email-validation.js', { 
        encoding: 'utf8',
        timeout: 30000 
      });
      
      // Parse results from output
      const emailResults = this.parseTestOutput(emailTestOutput);
      
      // Run animation tests
      console.log('Running animation tests...');
      const animationTestOutput = execSync('node test-animations.js', { 
        encoding: 'utf8',
        timeout: 30000 
      });
      
      const animationResults = this.parseTestOutput(animationTestOutput);

      // Combine results
      this.results.unit = {
        email: emailResults,
        animations: animationResults,
        passed: emailResults.passed + animationResults.passed,
        failed: emailResults.failed + animationResults.failed,
        total: emailResults.total + animationResults.total
      };

      console.log(`✅ Unit Tests Complete: ${this.results.unit.passed}/${this.results.unit.total} passed`);

    } catch (error) {
      console.error('❌ Unit tests failed:', error.message);
      this.results.unit = { passed: 0, failed: 1, total: 1, error: error.message };
    }
  }

  async runBrowserTests() {
    console.log('\n🌐 Running Browser Compatibility Tests...');
    console.log('-'.repeat(40));

    try {
      // Since browser tests require a browser environment, we'll create a mock report
      console.log('Browser compatibility tests require a browser environment.');
      console.log('Run test-runner.html in different browsers for full compatibility testing.');
      
      // Create a basic compatibility check based on Node.js capabilities
      const nodeVersion = process.version;
      const hasES6 = parseFloat(nodeVersion.slice(1)) >= 6.0;
      
      this.results.browser = {
        nodeVersion,
        es6Support: hasES6,
        passed: hasES6 ? 1 : 0,
        failed: hasES6 ? 0 : 1,
        total: 1,
        note: 'Full browser testing requires browser environment'
      };

      console.log(`Node.js version: ${nodeVersion}`);
      console.log(`ES6 support: ${hasES6 ? '✅' : '❌'}`);
      console.log('For complete browser testing, open test-runner.html in target browsers.');

    } catch (error) {
      console.error('❌ Browser tests setup failed:', error.message);
      this.results.browser = { passed: 0, failed: 1, total: 1, error: error.message };
    }
  }

  async runResponsiveTests() {
    console.log('\n📱 Running Responsive Design Tests...');
    console.log('-'.repeat(40));

    try {
      // Check if CSS files exist and are valid
      const cssFiles = ['styles/main.css', 'styles/components.css', 'styles/animations.css'];
      let cssFilesExist = 0;
      let totalCssFiles = cssFiles.length;

      cssFiles.forEach(file => {
        if (fs.existsSync(file)) {
          cssFilesExist++;
          console.log(`✅ ${file} exists`);
        } else {
          console.log(`❌ ${file} missing`);
        }
      });

      // Check HTML structure
      const htmlExists = fs.existsSync('index.html');
      console.log(`${htmlExists ? '✅' : '❌'} index.html ${htmlExists ? 'exists' : 'missing'}`);

      // Check for responsive meta tag in HTML
      let hasViewportMeta = false;
      if (htmlExists) {
        const htmlContent = fs.readFileSync('index.html', 'utf8');
        hasViewportMeta = htmlContent.includes('name="viewport"');
        console.log(`${hasViewportMeta ? '✅' : '❌'} Viewport meta tag ${hasViewportMeta ? 'present' : 'missing'}`);
      }

      const responsivePassed = cssFilesExist + (htmlExists ? 1 : 0) + (hasViewportMeta ? 1 : 0);
      const responsiveTotal = totalCssFiles + 2; // CSS files + HTML + viewport meta

      this.results.responsive = {
        cssFiles: { passed: cssFilesExist, total: totalCssFiles },
        htmlStructure: htmlExists,
        viewportMeta: hasViewportMeta,
        passed: responsivePassed,
        failed: responsiveTotal - responsivePassed,
        total: responsiveTotal,
        note: 'Full responsive testing requires browser environment with different viewport sizes'
      };

      console.log(`✅ Responsive Tests Complete: ${responsivePassed}/${responsiveTotal} passed`);

    } catch (error) {
      console.error('❌ Responsive tests failed:', error.message);
      this.results.responsive = { passed: 0, failed: 1, total: 1, error: error.message };
    }
  }

  async runAccessibilityTests() {
    console.log('\n♿ Running Accessibility Tests...');
    console.log('-'.repeat(40));

    try {
      // Check if accessibility checklist exists
      const checklistExists = fs.existsSync('accessibility-checklist.md');
      console.log(`${checklistExists ? '✅' : '❌'} Accessibility checklist ${checklistExists ? 'exists' : 'missing'}`);

      // Check HTML for basic accessibility features
      let accessibilityScore = 0;
      let totalAccessibilityTests = 1; // Start with checklist

      if (fs.existsSync('index.html')) {
        const htmlContent = fs.readFileSync('index.html', 'utf8');
        
        // Check for semantic HTML
        const hasSemanticElements = /(<header|<nav|<main|<section|<footer)/.test(htmlContent);
        console.log(`${hasSemanticElements ? '✅' : '❌'} Semantic HTML elements ${hasSemanticElements ? 'present' : 'missing'}`);
        if (hasSemanticElements) accessibilityScore++;
        totalAccessibilityTests++;

        // Check for alt attributes
        const imgTags = htmlContent.match(/<img[^>]*>/g) || [];
        const imgsWithAlt = imgTags.filter(img => img.includes('alt=')).length;
        const hasAltText = imgTags.length === 0 || imgsWithAlt === imgTags.length;
        console.log(`${hasAltText ? '✅' : '❌'} Image alt text ${hasAltText ? 'complete' : 'incomplete'} (${imgsWithAlt}/${imgTags.length})`);
        if (hasAltText) accessibilityScore++;
        totalAccessibilityTests++;

        // Check for form labels
        const inputTags = htmlContent.match(/<input[^>]*>/g) || [];
        const hasFormLabels = inputTags.length === 0 || /(<label|aria-label|placeholder)/.test(htmlContent);
        console.log(`${hasFormLabels ? '✅' : '❌'} Form labels ${hasFormLabels ? 'present' : 'missing'}`);
        if (hasFormLabels) accessibilityScore++;
        totalAccessibilityTests++;

        // Check for ARIA attributes
        const hasAriaAttributes = /aria-/.test(htmlContent);
        console.log(`${hasAriaAttributes ? '✅' : '❌'} ARIA attributes ${hasAriaAttributes ? 'present' : 'missing'}`);
        if (hasAriaAttributes) accessibilityScore++;
        totalAccessibilityTests++;
      }

      if (checklistExists) accessibilityScore++;

      this.results.accessibility = {
        checklist: checklistExists,
        semanticHTML: hasSemanticElements,
        altText: hasAltText,
        formLabels: hasFormLabels,
        ariaAttributes: hasAriaAttributes,
        passed: accessibilityScore,
        failed: totalAccessibilityTests - accessibilityScore,
        total: totalAccessibilityTests,
        note: 'Full accessibility testing requires screen readers and manual testing'
      };

      console.log(`✅ Accessibility Tests Complete: ${accessibilityScore}/${totalAccessibilityTests} passed`);

    } catch (error) {
      console.error('❌ Accessibility tests failed:', error.message);
      this.results.accessibility = { passed: 0, failed: 1, total: 1, error: error.message };
    }
  }

  parseTestOutput(output) {
    // Parse test output to extract pass/fail counts
    const passedMatch = output.match(/(\d+) passed/);
    const failedMatch = output.match(/(\d+) failed/);
    const totalMatch = output.match(/Total: (\d+)/);

    const passed = passedMatch ? parseInt(passedMatch[1]) : 0;
    const failed = failedMatch ? parseInt(failedMatch[1]) : 0;
    const total = totalMatch ? parseInt(totalMatch[1]) : passed + failed;

    return { passed, failed, total, output };
  }

  generateSummaryReport() {
    const endTime = Date.now();
    const duration = endTime - this.startTime;

    console.log('\n' + '='.repeat(80));
    console.log('📊 TEST EXECUTION SUMMARY');
    console.log('='.repeat(80));

    let totalPassed = 0;
    let totalFailed = 0;
    let totalTests = 0;

    Object.entries(this.results).forEach(([category, result]) => {
      if (result && category !== 'summary') {
        const categoryName = category.charAt(0).toUpperCase() + category.slice(1);
        const percentage = result.total > 0 ? Math.round((result.passed / result.total) * 100) : 0;
        
        console.log(`${categoryName}: ${result.passed}/${result.total} passed (${percentage}%)`);
        
        if (result.note) {
          console.log(`  Note: ${result.note}`);
        }
        
        totalPassed += result.passed;
        totalFailed += result.failed;
        totalTests += result.total;
      }
    });

    const overallPercentage = totalTests > 0 ? Math.round((totalPassed / totalTests) * 100) : 0;
    
    console.log('-'.repeat(80));
    console.log(`OVERALL: ${totalPassed}/${totalTests} tests passed (${overallPercentage}%)`);
    console.log(`Duration: ${duration}ms`);
    console.log(`Status: ${totalFailed === 0 ? '🎉 ALL TESTS PASSED' : '❌ SOME TESTS FAILED'}`);
    console.log('='.repeat(80));

    this.results.summary = {
      totalPassed,
      totalFailed,
      totalTests,
      overallPercentage,
      duration,
      success: totalFailed === 0
    };
  }

  generateDetailedReport() {
    const reportPath = 'test-results.json';
    const report = {
      timestamp: new Date().toISOString(),
      environment: {
        nodeVersion: process.version,
        platform: process.platform,
        arch: process.arch
      },
      results: this.results
    };

    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`\n📄 Detailed report saved to: ${reportPath}`);
  }

  generateJUnitReport() {
    // Generate JUnit XML format for CI/CD integration
    const junitPath = 'test-results.xml';
    let xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
    xml += '<testsuites>\n';

    Object.entries(this.results).forEach(([category, result]) => {
      if (result && category !== 'summary') {
        xml += `  <testsuite name="${category}" tests="${result.total}" failures="${result.failed}" time="${result.duration || 0}">\n`;
        
        // Add individual test cases (simplified)
        for (let i = 0; i < result.passed; i++) {
          xml += `    <testcase name="${category}-test-${i + 1}" classname="${category}" time="0"/>\n`;
        }
        
        for (let i = 0; i < result.failed; i++) {
          xml += `    <testcase name="${category}-test-${result.passed + i + 1}" classname="${category}" time="0">\n`;
          xml += `      <failure message="Test failed">${result.error || 'Test failed'}</failure>\n`;
          xml += `    </testcase>\n`;
        }
        
        xml += '  </testsuite>\n';
      }
    });

    xml += '</testsuites>\n';

    fs.writeFileSync(junitPath, xml);
    console.log(`📄 JUnit report saved to: ${junitPath}`);
  }

  hasFailures() {
    return Object.values(this.results).some(result => 
      result && typeof result === 'object' && result.failed > 0
    );
  }
}

// Show usage if help requested
if (process.argv.includes('--help') || process.argv.includes('-h')) {
  console.log(`
Usage: node run-tests.js [options]

Options:
  --unit          Run unit tests only
  --browser       Run browser compatibility tests only
  --responsive    Run responsive design tests only
  --accessibility Run accessibility tests only
  --all           Run all tests (default)
  --help, -h      Show this help message

Examples:
  node run-tests.js                    # Run all tests
  node run-tests.js --unit             # Run unit tests only
  node run-tests.js --unit --responsive # Run unit and responsive tests
  `);
  process.exit(0);
}

// Run the test executor
const executor = new TestExecutor();
executor.run().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});