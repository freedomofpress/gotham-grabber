This is very ugly but it works for now. grabber.js is a script that uses Puppeteer to direct a headless Chrome to create a nice-looking PDF of a given url. It requires the arguments `--url`, the URL of the site you want to turn into a PDF, and `--outdir`, an existing directory in which to place that URL.

For the present purposes, this script is likely to be invoked programmatically. In my case, with a text file `TEXTFILE` containing a URL on each line, the following bash script may be helpful:

```bash
while read p; do
echo printing $p;
node grabber.js --url=$p --outdir=OUTDIR;
done < TEXTFILE
```
