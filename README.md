# OZ Lotto
Just for fun Oz Lotto (Australia) script. Generates lottory numbers based on probability to pick a set of numbers from a 6 numbered draw, with half of them odd and half of them even. There's a ***30%*** chance that the winning combination numbers contain half of them even and half of them odd numbers. There's a ***25%*** chance that 4 are odd, 2 are even and ***22%*** chance that 4 are even, and 2 are odd. If you have historical data of winning lotto numbers from other countries, you can use that as long as it follows the CSV format similar to the one in this repo.

## Historical draws
Historical draws were taken from the following sources
|Lotto|Source|
|-|-|
|Tuesday|[Oz Lotto](https://gnetwork.com.au/oz-lotto-results/)
|Thursday|[Powerball](https://gnetwork.com.au/powerball-results/)
|Saturday|[Tatts](https://gnetwork.com.au/lotto-results/)

## Text-based bar graph
The script also generates a bar graph with the drawn frequency of each number. These frequencies are used as weights to help suggest numbers. It also generates probability distribution of winning odd/even number combinations vs the actual drawn numbers.

## Environment variables
You can use a .env file with the following values:
|Key|Value|
|-|-|
|SUGGEST|5|
|LOTTO|tuesday/thursday/saturday|
|USEWEIGHT|true/false|

if ```USEWEIGHT``` is set to true, it will use the historical draws as weights to randomly select numbers.

## Command line
Or from the command line:
```bash
SUGGEST=10 python ozlottories.py
```

## Sample output
![Sample output of the script](https://raw.githubusercontent.com/111110100/ozlottopy/main/sample.png)