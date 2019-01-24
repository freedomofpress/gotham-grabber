const puppeteer = require('puppeteer');
const argv = require('minimist')(process.argv.slice(2));

const url = argv.url;
const outdir = argv.outdir || '.';
if (url.includes('.com')) {
    offset = url.indexOf('.com');
} else if (url.includes('.net')) {
    offset = url.indexOf('.net');
} else {
    offset = 3;
}

let filename = url.substring(offset + 5).replace(/\//g,'-');

if (filename.endsWith('.php')) {
    filename = filename.slice(0,-4);
}

if (filename.endsWith('-')) {
    filename = filename.slice(0,-1);
}

(async () => {
    const browser = await puppeteer.launch({ignoreHTTPSErrors:true});
    const page = await browser.newPage();

    await page.setUserAgent('gothamgrabber (a project of freedom.press)');

    await page.setJavaScriptEnabled(false);

    await page.emulateMedia('screen');

    try {
        const res = await page.goto(url, {timeout:3000});
        if (res.ok() !== true) {
            console.log('Server returned status code ' + res.status());
            process.exitCode = 1;
            await browser.close();
            return;
        }
    } catch (e) {
        console.log(e);
        process.exitCode = 1;
        await browser.close();
        return;
    }

    let pdf_options = {displayHeaderFooter: true, margin: {top: '.5in', bottom: '.5in', left: '.5in', right: '.5in'}, printBackground: true, path: outdir + '/' + filename + '.pdf'}

    if (url.includes('dnainfo.com')) {
        await page.addStyleTag({path: 'tweaks/dnainfo.css'})
    }

    if (url.includes('laweekly.com')) {
		    await page.setViewport({width: 500, height: 800})
        pdf_options.scale = .75;
        pdf_options.printBackground = false;
        await page.addStyleTag({path: 'tweaks/laweekly.css'})
    }

    if (url.includes('the-toast.net')) {
        await page.addStyleTag({path: 'tweaks/thetoast.css'})
		await page.setViewport({width:500, height:600});
    }

    if (url.includes('newsweek.com')) {
        await page.addStyleTag({path: 'tweaks/newsweek.css'});
        await page.setViewport({width:500, height: 600});
    }

    try {
    await page.pdf(pdf_options);
    } catch (e) {
        console.log(e);
        process.exitCode = 1;
        await browser.close();
        return;
    }

    await browser.close();
})();
