#!/bin/bash

URL=${1}
OUTPUT_FILE=${2}

function wgets()
{
  local H='--header'
  wget $H='Accept-Language: en-us,en;q=0.5' $H='Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' $H='Connection: keep-alive' -U 'Mozilla/5.0 (Windows NT 5.1; rv:10.0.2) Gecko/20100101 Firefox/10.0.2' --referer=https://www.askapache.com/ "$@";
}

echo "wgets ${URL} -O ${OUTPUT_FILE}"
wgets -O ${OUTPUT_FILE} ${URL}
