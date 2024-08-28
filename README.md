# OZ Lotto
Just a fun Oz Lotto script. Generates lottory numbers based on probability that to pick an even set of numbers, with half of them odd and half of them even.

## Environment variables
You can use a .env file with the following values:
|Key|Value|
|-|-|
|POWERBALL|False|
|PICKNUMBER|7|
|MAXNUMBER|47|
|MAXNUMBERP|20|
|SUGGEST|5|

## Command line
Or from the command line:
```bash
POWERBALL=True PICKNUMBER=7 MAXNUMBER=35 SUGGEST=10 ozlottories.py
```