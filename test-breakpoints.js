// Comprehensive responsive design test script
class ResponsiveDesignTester {
    constructor() {
        this.breakpoints = {
            mobile: { min: 320, max: 767 },
            tablet: { min: 768, max: 1023 },
            desktop: { min: 1024, max: 1439 },
            largeDesktop: { min: 1440, max: Infinity }
        };
        
        this.touchTargetMinSize = 44; // Minimum touch target size in pixels
        this.init();
    }
    
    init() {
        this.testBreakpoints();
        this.testTouchTargets();
        this.testFluidTypography();
        this.testLayoutBehavior();
        
        // Re-run tests on window resize
        window.addEventListener('resize', () => {
            this.testBreakpoints();
            this.testTouchTargets();
            this.testFluidTypography();
            this.testLayoutBehavior();
        });
    }
    
    testBreakpoints() {
        const width = window.innerWidth;
        const currentBreakpoint = this.getCurrentBreakpoint(width);
        
        console.log(`Current breakpoint: ${currentBreakpoint} (${width}px)`);
        
        // Test container padding
        const container = document.querySelector('.container');
        if (container) {
            const computedStyle = getComputedStyle(container);
            const padding = computedStyle.paddingLeft;
            console.log(`Container padding: ${padding}`);
        }
        
        // Test grid behavior
        this.testGridBehavior();
    }
    
    getCurrentBreakpoint(width) {
        for (const [name, range] of Object.entries(this.breakpoints)) {
            if (width >= range.min && width <= range.max) {
                return name;
            }
        }
        return 'unknown';
    }
    
    testTouchTargets() {
        const interactiveElements = document.querySelectorAll('.btn, .form__input, button, input, [role="button"]');
        const failedElements = [];
        
        interactiveElements.forEach(element => {
            const rect = element.getBoundingClientRect();
            const computedStyle = getComputedStyle(element);
            
            // Check minimum dimensions
            const minHeight = parseInt(computedStyle.minHeight) || rect.height;
            const minWidth = parseInt(computedStyle.minWidth) || rect.width;
            
            if (minHeight < this.touchTargetMinSize || minWidth < this.touchTargetMinSize) {
                failedElements.push({
                    element: element,
                    height: minHeight,
                    width: minWidth,
                    selector: this.getElementSelector(element)
                });
            }
        });
        
        if (failedElements.length > 0) {
            console.warn('Touch target failures:', failedElements);
        } else {
            console.log('✓ All touch targets meet minimum size requirements');
        }
        
        return failedElements;
    }
    
    testFluidTypography() {
        const textElements = document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, .text, .heading');
        const typographyData = [];
        
        textElements.forEach(element => {
            const computedStyle = getComputedStyle(element);
            const fontSize = parseFloat(computedStyle.fontSize);
            const lineHeight = computedStyle.lineHeight;
            
            typographyData.push({
                element: this.getElementSelector(element),
                fontSize: fontSize,
                lineHeight: lineHeight,
                fontFamily: computedStyle.fontFamily
            });
        });
        
        console.log('Typography scaling data:', typographyData);
        return typographyData;
    }
    
    testGridBehavior() {
        const gridElements = document.querySelectorAll('.grid');
        
        gridElements.forEach(grid => {
            const computedStyle = getComputedStyle(grid);
            const gridTemplateColumns = computedStyle.gridTemplateColumns;
            const gap = computedStyle.gap;
            
            console.log(`Grid behavior:`, {
                element: this.getElementSelector(grid),
                columns: gridTemplateColumns,
                gap: gap
            });
        });
    }
    
    testLayoutBehavior() {
        const width = window.innerWidth;
        const currentBreakpoint = this.getCurrentBreakpoint(width);
        
        // Test form layouts
        const heroForm = document.querySelector('.hero__form');
        const ctaForm = document.querySelector('.cta__form');
        
        if (heroForm) {
            const computedStyle = getComputedStyle(heroForm);
            console.log(`Hero form layout (${currentBreakpoint}):`, {
                flexDirection: computedStyle.flexDirection,
                gap: computedStyle.gap,
                maxWidth: computedStyle.maxWidth
            });
        }
        
        if (ctaForm) {
            const computedStyle = getComputedStyle(ctaForm);
            console.log(`CTA form layout (${currentBreakpoint}):`, {
                flexDirection: computedStyle.flexDirection,
                gap: computedStyle.gap,
                maxWidth: computedStyle.maxWidth
            });
        }
        
        // Test section spacing
        const sections = document.querySelectorAll('.section');
        sections.forEach((section, index) => {
            const computedStyle = getComputedStyle(section);
            if (index === 0) { // Only log first section to avoid spam
                console.log(`Section spacing (${currentBreakpoint}):`, {
                    paddingTop: computedStyle.paddingTop,
                    paddingBottom: computedStyle.paddingBottom
                });
            }
        });
    }
    
    getElementSelector(element) {
        if (element.id) return `#${element.id}`;
        if (element.className) return `.${element.className.split(' ')[0]}`;
        return element.tagName.toLowerCase();
    }
    
    // Test specific breakpoint by simulating window resize
    simulateBreakpoint(width) {
        // This would require more complex setup to actually change viewport
        console.log(`Simulating breakpoint at ${width}px`);
        const breakpoint = this.getCurrentBreakpoint(width);
        console.log(`Would be: ${breakpoint}`);
    }
    
    // Generate test report
    generateReport() {
        const report = {
            currentWidth: window.innerWidth,
            currentBreakpoint: this.getCurrentBreakpoint(window.innerWidth),
            touchTargetFailures: this.testTouchTargets(),
            typographyData: this.testFluidTypography(),
            timestamp: new Date().toISOString()
        };
        
        console.log('Responsive Design Test Report:', report);
        return report;
    }
}

// Initialize tester when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.responsiveTester = new ResponsiveDesignTester();
    });
} else {
    window.responsiveTester = new ResponsiveDesignTester();
}

// Expose testing functions globally for manual testing
window.testResponsive = {
    generateReport: () => window.responsiveTester.generateReport(),
    testTouchTargets: () => window.responsiveTester.testTouchTargets(),
    testTypography: () => window.responsiveTester.testFluidTypography(),
    simulateBreakpoint: (width) => window.responsiveTester.simulateBreakpoint(width)
};