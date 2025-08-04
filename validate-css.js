// Simple CSS validation script to check for common issues
class CSSValidator {
    constructor() {
        this.errors = [];
        this.warnings = [];
    }
    
    validateCSS(cssText, filename) {
        console.log(`🔍 Validating ${filename}...`);
        
        // Check for common CSS issues
        this.checkBraces(cssText, filename);
        this.checkSemicolons(cssText, filename);
        this.checkUnknownProperties(cssText, filename);
        this.checkDuplicateSelectors(cssText, filename);
        
        return {
            errors: this.errors,
            warnings: this.warnings,
            isValid: this.errors.length === 0
        };
    }
    
    checkBraces(cssText, filename) {
        const openBraces = (cssText.match(/\{/g) || []).length;
        const closeBraces = (cssText.match(/\}/g) || []).length;
        
        if (openBraces !== closeBraces) {
            this.errors.push({
                file: filename,
                type: 'syntax',
                message: `Mismatched braces: ${openBraces} opening, ${closeBraces} closing`
            });
        }
    }
    
    checkSemicolons(cssText, filename) {
        // Check for missing semicolons (simplified check)
        const lines = cssText.split('\n');
        lines.forEach((line, index) => {
            const trimmed = line.trim();
            if (trimmed && 
                !trimmed.startsWith('/*') && 
                !trimmed.endsWith('*/') &&
                !trimmed.startsWith('@') &&
                !trimmed.includes('{') &&
                !trimmed.includes('}') &&
                trimmed.includes(':') &&
                !trimmed.endsWith(';') &&
                !trimmed.endsWith(',')) {
                this.warnings.push({
                    file: filename,
                    line: index + 1,
                    type: 'syntax',
                    message: `Possible missing semicolon: ${trimmed}`
                });
            }
        });
    }
    
    checkUnknownProperties(cssText, filename) {
        // Check for properties that might cause warnings
        const problematicProperties = [
            'overflow-scrolling',
            'tap-highlight-color'
        ];
        
        problematicProperties.forEach(prop => {
            if (cssText.includes(prop) && !cssText.includes(`-webkit-${prop}`)) {
                this.warnings.push({
                    file: filename,
                    type: 'compatibility',
                    message: `Non-standard property '${prop}' should be prefixed with -webkit-`
                });
            }
        });
    }
    
    checkDuplicateSelectors(cssText, filename) {
        const selectors = [];
        const lines = cssText.split('\n');
        
        lines.forEach((line, index) => {
            const trimmed = line.trim();
            if (trimmed.includes('{') && !trimmed.startsWith('/*')) {
                const selector = trimmed.replace('{', '').trim();
                if (selectors.includes(selector)) {
                    this.warnings.push({
                        file: filename,
                        line: index + 1,
                        type: 'duplication',
                        message: `Duplicate selector: ${selector}`
                    });
                }
                selectors.push(selector);
            }
        });
    }
    
    async validateFiles(filePaths) {
        const results = {};
        
        for (const filePath of filePaths) {
            try {
                const response = await fetch(filePath);
                const cssText = await response.text();
                results[filePath] = this.validateCSS(cssText, filePath);
                
                // Reset for next file
                this.errors = [];
                this.warnings = [];
            } catch (error) {
                console.error(`Error reading ${filePath}:`, error);
                results[filePath] = {
                    errors: [{ message: `Could not read file: ${error.message}` }],
                    warnings: [],
                    isValid: false
                };
            }
        }
        
        return results;
    }
    
    printResults(results) {
        let totalErrors = 0;
        let totalWarnings = 0;
        
        Object.entries(results).forEach(([file, result]) => {
            console.log(`\n📄 ${file}:`);
            
            if (result.errors.length > 0) {
                console.log('❌ Errors:');
                result.errors.forEach(error => {
                    console.log(`   ${error.message}`);
                    totalErrors++;
                });
            }
            
            if (result.warnings.length > 0) {
                console.log('⚠️  Warnings:');
                result.warnings.forEach(warning => {
                    console.log(`   Line ${warning.line || '?'}: ${warning.message}`);
                    totalWarnings++;
                });
            }
            
            if (result.errors.length === 0 && result.warnings.length === 0) {
                console.log('✅ No issues found');
            }
        });
        
        console.log(`\n📊 Summary: ${totalErrors} errors, ${totalWarnings} warnings`);
        
        if (totalErrors === 0) {
            console.log('🎉 All CSS files are valid!');
        }
        
        return { totalErrors, totalWarnings };
    }
}

// Auto-run validation when page loads
document.addEventListener('DOMContentLoaded', async () => {
    const validator = new CSSValidator();
    const cssFiles = ['styles/main.css', 'styles/components.css'];
    
    console.log('🚀 Starting CSS validation...');
    const results = await validator.validateFiles(cssFiles);
    const summary = validator.printResults(results);
    
    // Store results globally for manual access
    window.cssValidationResults = results;
    window.cssValidationSummary = summary;
});

// Expose validation function for manual testing
window.validateCSS = async () => {
    const validator = new CSSValidator();
    const cssFiles = ['styles/main.css', 'styles/components.css'];
    
    const results = await validator.validateFiles(cssFiles);
    return validator.printResults(results);
};