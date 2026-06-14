const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

(async () => {
  const htmlContent = fs.readFileSync('C:\\Users\\thadd\\.openclaw\\workspace\\temp_history_rhymes.html', 'utf8');
  
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  await page.setContent(htmlContent, { waitUntil: 'networkidle0' });
  
  const outputDir = 'C:\\Users\\thadd\\OneDrive\\Desktop\\Spocks Reports\\history_rhymes';
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  await page.pdf({
    path: path.join(outputDir, '2026-05-17_history_rhymes.pdf'),
    format: 'A4',
    printBackground: true,
    margin: { top: '20mm', right: '20mm', bottom: '20mm', left: '20mm' }
  });
  
  await browser.close();
  console.log('PDF generated successfully');
})();
