const { execSync } = require('child_process');

try {
  // Set Python 3.13.2 path
  process.env.PYTHON = "C:\\Users\\USER\\AppData\\Local\\Programs\\Python\\Python313\\python.exe";
  
  // Verify Python
  execSync(`${process.env.PYTHON} --version`, { stdio: 'inherit' });
  
  // Clean npm cache
  execSync('npm cache clean --force', { stdio: 'inherit' });
} catch (error) {
  console.error('Preinstall failed:', error);
  process.exit(1);
}