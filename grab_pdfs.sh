#!/bin/bash

URL=$1

#./prepare-links.py $URL


URL_LIST=$1
OUT_DIR=$2 

while read p; do
echo printing $p;
node grabber.js --url $p --outdir $OUT_DIR;
done < $URL_LIST
