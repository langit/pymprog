#!/bin/bash
ZIPF=`pwd`/$1-$(date +"%H%M%S").zip
git archive --format zip --output $ZIPF master
echo $ZIPF
