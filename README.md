# OZ Lotto
Just for fun Oz Lotto script. Generates lottory numbers based on probability to pick an even set of numbers, with half of them odd and half of them even. There's a ***33.484590659%*** chance that the winning combination numbers contain half even and half are odd numbers. There's a ***25%*** chance that 4 are odd, 2 are even and ***22%*** chance that 4 are even, and 2 are odd.

## Historical draws
Historical draws were taken from the following sources
|Lotto|Source|
|-|-|
|Tuesday|[Oz Lotto](https://gnetwork.com.au/oz-lotto-results/)
|Thursday|[Powerball](https://gnetwork.com.au/powerball-results/)
|Saturday|[Tatts](https://gnetwork.com.au/lotto-results/)

## Environment variables
You can use a .env file with the following values:
|Key|Value|
|-|-|
|SUGGEST|5|
|LOTTO|tuesday/thursday/saturday|

## Command line
Or from the command line:
```bash
SUGGEST=10 python ozlottories.py
```