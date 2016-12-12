#!/bin/bash
python setup.py --long-description | rst2html.py > temp_output.html
