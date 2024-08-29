import os
import random
import csv
import json
from collections import Counter
from math import comb
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set default values based on LOTTO
LOTTO = os.getenv("LOTTO", "").lower()

if LOTTO == "tuesday":
    PICKNUMBER = 7
    MAXNUMBER = 47
    MAXNUMBERP = None  # Not applicable for Tuesday
    POWERBALL = False
elif LOTTO == "thursday":
    PICKNUMBER = 7
    MAXNUMBER = 35
    MAXNUMBERP = 20
    POWERBALL = True
elif LOTTO == "saturday":
    PICKNUMBER = 6
    MAXNUMBER = 45
    MAXNUMBERP = None  # Not applicable for Saturday
    POWERBALL = False
else:
    raise ValueError("Invalid value for LOTTO. Choose between 'tuesday', 'thursday', or 'saturday'.")

SUGGEST = int(os.getenv("SUGGEST", 1))

def load_lotto_data(lotto_type):
    frequency = Counter()
    powerball_frequency = Counter()
    draws = []

    if lotto_type == "tuesday":
        csv_file = "tuesday.csv"
        columns = ["#1", "#2", "#3", "#4", "#5", "#6", "#7"]
    elif lotto_type == "thursday":
        csv_file = "thursday.csv"
        columns = ["#1", "#2", "#3", "#4", "#5", "#6", "#7", "PB"]
    elif lotto_type == "saturday":
        csv_file = "saturday.csv"
        columns = ["#1", "#2", "#3", "#4", "#5", "#6"]
    else:
        return frequency, powerball_frequency

    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            draw = []
            for col in columns:
                draw.append(int(row[col]))
                if col != "PB":
                    frequency[int(row[col])] += 1
                else:
                    powerball_frequency[int(row[col])] += 1

            draws.append(draw)

    return frequency, powerball_frequency, draws

def generate_numbers(picknumber, maxnumber, powerball=False, maxnumberp=20, frequency=None, powerball_frequency=None):
    suggested_numbers = []

    for _ in range(SUGGEST):
        # Determine odd and even count based on PICKNUMBER
        if picknumber % 2 == 0:
            odd_count, even_count = picknumber // 2, picknumber // 2
        else:
            odd_count, even_count = random.choice([(picknumber // 2 + 1, picknumber // 2), (picknumber // 2, picknumber // 2 + 1)])
        
        # Generate odd and even numbers using frequency as weight, ensuring no repeats
        odds = [num for num in range(1, maxnumber+1) if num % 2 != 0]
        evens = [num for num in range(1, maxnumber+1) if num % 2 == 0]
        
        chosen_odds = random.sample(odds, odd_count)
        chosen_evens = random.sample(evens, even_count)
        
        numbers = sorted(chosen_odds + chosen_evens)
        
        # Add powerball number if required, ensuring no repeat
        if powerball:
            available_powerballs = set(range(1, maxnumberp + 1)) - set(numbers)
            powerball_num = random.choices(list(available_powerballs), weights=[powerball_frequency.get(num, 1) for num in available_powerballs], k=1)[0]
            numbers.append(f"Powerball: {powerball_num}")
        
        suggested_numbers.append(numbers)

    return suggested_numbers

def count_odd_even_distribution(data, picknumber):
    odd_even_counts = Counter()

    for row in data:
        odds = sum(1 for num in row if num % 2 != 0)
        evens = picknumber - odds
        odd_even_counts[(odds, evens)] += 1

    return odd_even_counts

def draw_frequency_graph(frequency):
    max_freq = max(frequency.values())
    for number in sorted(frequency.keys()):
        bar = "#" * (frequency[number] * 50 // max_freq)  # Scale bar length to a max of 50
        print(f"{number:2}: {bar} ({frequency[number]})")

def draw_powerball_frequency_graph(powerball_frequency):
    if not powerball_frequency:
        print("No Powerball frequency data available.")
        return

    max_freq = max(powerball_frequency.values())
    for number in sorted(powerball_frequency.keys()):
        bar = "#" * (powerball_frequency[number] * 50 // max_freq)  # Scale bar length to a max of 50
        print(f"{number:2}: {bar} ({powerball_frequency[number]})")

def draw_distribution_graph(distribution):
    max_prob = max(distribution.values())
    for key in sorted(distribution.keys()):
        bar = "#" * int(distribution[key] * 50 / max_prob)  # Scale bar length to a max of 50
        print(f"{key[0]} odd, {key[1]} even: {bar} ({distribution[key]:.4f})")

def probability_distribution(picknumber):
    total_possibilities = 2 ** picknumber

    distribution = {}
    for odd_count in range(0, picknumber + 1):
        even_count = picknumber - odd_count
        probability = comb(picknumber, odd_count) / total_possibilities
        distribution[(odd_count, even_count)] = probability

    return distribution

def draw_odd_even_distribution_graph(odd_even_counts, picknumber):
    max_count = max(odd_even_counts.values())

    print(f"\nOdd-Even Distribution for PICKNUMBER={picknumber} based from previous draws:")
    for odd_count in range(picknumber + 1):
        even_count = picknumber - odd_count
        count = odd_even_counts.get((odd_count, even_count), 0)
        bar = "#" * (count * 50 // max_count)  # Scale bar length to a max of 50
        print(f"{odd_count} odd, {even_count} even: {bar} ({count})")

# Load lottery data based on LOTTO value
frequency, powerball_frequency, draws = load_lotto_data(LOTTO)

# Generate and display lottery numbers
lottery_numbers = generate_numbers(PICKNUMBER, MAXNUMBER, POWERBALL, MAXNUMBERP, frequency, powerball_frequency)
print(f"Suggested lottery numbers: {json.dumps(lottery_numbers, indent=4)}")

# Draw frequency graph
print("\nFrequency Graph:")
draw_frequency_graph(frequency)

if POWERBALL:
    print("\nPowerball Frequency Graph:")
    draw_powerball_frequency_graph(powerball_frequency)

# Calculate and display distribution probabilities
distribution = probability_distribution(PICKNUMBER)
print("\nProbability Distribution Graph:")
draw_distribution_graph(distribution)

# Count the odd/even distribution
odd_even_counts = count_odd_even_distribution(draws, PICKNUMBER)

# Draw the odd/even distribution graph
draw_odd_even_distribution_graph(odd_even_counts, PICKNUMBER)