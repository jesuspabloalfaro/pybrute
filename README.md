# PYBrute
PYBrute is a python-based password sprayer/credential stuffer to provide an easier and faster alternative to BurpSuite’s free-tier Intruder.

The problem with BurpSuite's Intruder is that it is extrememly slow. For those one-off tests where you need something quick and dirty, PYBrute can help by utilzing multithreaded performance and customizable form postings.
# Usage
```
usage: py-brute [-h] [--ssl] --form-name FORM_NAME --payload PAYLOAD [--threads THREADS] --output OUTPUT --input INPUT
py-brute: error: the following arguments are required: --form-name/-n, --payload/-p, --output/-o, --input/-i
```
