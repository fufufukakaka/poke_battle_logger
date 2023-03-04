// This is a Prettier configuration file.
//
// Docs: https://prettier.io/docs/en/index.html

module.exports = {
    // Prefer single-quoted string because we often use double quotes in a string.
    singleQuote: true,
  
    // Add trailing comma where ES5 allows, for reducing diff.
    trailingComma: 'es5',
  
    // Override configuration for the specific files.
    overrides: [
      // In config files, if at least one property in an object requires quotes, quote all properties.
      // Because it looks nice, and more diff lines is not much of a problem in config files.
      {
        files: ['*.config.js', '.*.js'],
        quoteProps: 'consistent',
      },
    ],
  };
  