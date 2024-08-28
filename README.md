# OZ Lotto
Just for fun Oz Lotto script. Generates lottory numbers based on probability to pick an even set of numbers, with half of them odd and half of them even. There's a ***33.484590659%*** chance that the winning combination numbers contain half even and half are odd numbers. There's a ***25%*** chance that 4 are odd, 2 are even and ***22%*** chance that 4 are even, and 2 are odd.

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