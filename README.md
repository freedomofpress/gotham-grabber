# gotham grabber

`gotham-grabber` is a set of scripts that can take the URL of a writer page on a site in the Gothamist/DNAinfo network and produce a collection of attractive PDFs of each article. It was created after the sites were abruptly shut down on Thursday, November 2, 2017. The former editor-in-chief of one of the Gothamist sites, LAist, has [written about the significance of that shutdown](https://www.citylab.com/life/2017/11/gothamist-dnainfo-joe-ricketts-shutdown/545069/).

An outer Python script, `gotham-grabber.py`, takes an author page URL as an argument with the flag `--url`, creates a directory in the `out` subfolder where it runs, and saves a list of article URLs. (If that list of URLs already exists, `gotham-grabber.py` can take it as input, using the `-t` or `--textfile` option.) It then invokes `grabber.js`, a node script that drives a headless Chrome instance to capture and format articles as PDFs.

`grabber.js` can be invoked independently. It requires an argument with the flag `--url` and accepts an argument with the flag `--outdir`.

Each script requires installation. To install, clone this repo and run:

```bash
npm install
pip install -r requirements.txt
```

The scripts should then be ready to run.
