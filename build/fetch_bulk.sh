#!/bin/sh
# Download the openFDA Drugs@FDA bulk file used by enrich.fda_profile
set -e
mkdir -p /home/claude/build/bulk && cd /home/claude/build/bulk
curl -sL -o drugsfda.zip https://download.open.fda.gov/drug/drugsfda/drug-drugsfda-0001-of-0001.json.zip
unzip -o -q drugsfda.zip && ls -la
