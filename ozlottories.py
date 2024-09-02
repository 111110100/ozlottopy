import os
import random
import csv
from collections import Counter
from math import comb
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set default values based on LOTTO
LOTTO = os.getenv("LOTTO", "").lower()
USEWEIGHTS = os.getenv("USEWEIGHTS", "false").lower() == "true"
RESHUFFLE = os.getenv("RESHUFFLE", "false").lower() == "true"

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
                if col != "PB":
                    frequency[int(row[col])] += 1
                    draw.append(int(row[col]))
                else:
                    powerball_frequency[int(row[col])] += 1

            draws.append(draw)

    return frequency, powerball_frequency, draws

def calculate_historical_distribution(data, picknumber):
    odd_even_counts = Counter()

    for row in data:
        odds = sum(1 for num in row if num % 2 != 0)
        evens = picknumber - odds

        # Filter out distributions where either odd or even count is less than 2
        if odds >= 2 and evens >= 2:
            odd_even_counts[(odds, evens)] += 1

    # Calculate probabilities based on historical data
    total_draws = sum(odd_even_counts.values())
    probabilities = {k: v / total_draws for k, v in odd_even_counts.items()}

    return probabilities

def reshuffle_numbers(lottery_numbers):
    reshuffled_numbers = []

    # Flatten the list of lists into a single list of numbers
    all_numbers = [num for sublist in lottery_numbers for num in sublist]
    picknumber = len(lottery_numbers[0])  # Assume all sets have the same length

    for _ in range(len(lottery_numbers)):
        valid_combination_found = False

        while not valid_combination_found:
            # Randomly select numbers
            selected_numbers = random.sample(all_numbers, picknumber)

            # Calculate the odd and even counts
            odd_count = sum(1 for num in selected_numbers if num % 2 != 0)
            even_count = picknumber - odd_count

            # Check that there are at least 2 odd and 2 even numbers
            if odd_count >= 2 and even_count >= 2:
                reshuffled_numbers.append(selected_numbers)
                valid_combination_found = True

    return reshuffled_numbers

def generate_numbers(picknumber, maxnumber, powerball=False, maxnumberp=20, frequency=None, powerball_frequency=None, historical_data=None):
    suggested_numbers = []

    for _ in range(SUGGEST):
        # Calculate historical odd/even distribution for each set of numbers
        if historical_data:
            odd_even_distribution = calculate_historical_distribution(historical_data, picknumber)
            
            # Ensure that at least 2 odd and 2 even numbers are included
            valid_distributions = {k: v for k, v in odd_even_distribution.items() if k[0] >= 2 and k[1] >= 2}
            
            if not valid_distributions:
                raise ValueError("No valid odd/even distributions found in historical data.")
            
            selected_distribution = random.choices(list(valid_distributions.keys()), weights=list(valid_distributions.values()), k=1)[0]
            odd_count, even_count = selected_distribution
        else:
            # Fallback to equal distribution if no historical data is provided
            if picknumber % 2 == 0:
                odd_count, even_count = picknumber // 2, picknumber // 2
            else:
                odd_count, even_count = random.choice([(picknumber // 2 + 1, picknumber // 2), (picknumber // 2, picknumber // 2 + 1)])

            # Ensure at least 2 odd and 2 even numbers
            if odd_count < 2 or even_count < 2:
                odd_count, even_count = max(odd_count, 2), max(even_count, 2)

        # Filter odd and even numbers
        odds = [num for num in range(1, maxnumber + 1) if num % 2 != 0]
        evens = [num for num in range(1, maxnumber + 1) if num % 2 == 0]
        
        # Use frequency as weights to select odd and even numbers
        if USEWEIGHTS:
            chosen_odds = random.choices(odds, weights=[frequency.get(num, 1) for num in odds], k=odd_count)
            chosen_evens = random.choices(evens, weights=[frequency.get(num, 1) for num in evens], k=even_count)
        else:
            chosen_odds = random.choices(odds, k=odd_count)
            chosen_evens = random.choices(evens, k=even_count)
        
        # Ensure no duplicates in the chosen numbers
        chosen_odds = list(set(chosen_odds))
        chosen_evens = list(set(chosen_evens))
        
        # If duplicates were removed and the list lengths are short, replenish with random choices
        while len(chosen_odds) < odd_count:
            new_odd = random.choices(odds, weights=[frequency.get(num, 1) for num in odds], k=1)[0]
            if new_odd not in chosen_odds:
                chosen_odds.append(new_odd)
                
        while len(chosen_evens) < even_count:
            new_even = random.choices(evens, weights=[frequency.get(num, 1) for num in evens], k=1)[0]
            if new_even not in chosen_evens:
                chosen_evens.append(new_even)
        
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

    for odd_count in range(picknumber + 1):
        even_count = picknumber - odd_count
        count = odd_even_counts.get((odd_count, even_count), 0)
        bar = "#" * (count * 50 // max_count)  # Scale bar length to a max of 50
        print(f"{odd_count} odd, {even_count} even: {bar} ({count})")

def distribution_consecutive_check(numbers, count=3):
    # Sort the numbers to ensure they are in ascending order
    if POWERBALL:
        powerball_num = numbers[-1]
        numbers.pop(-1)
    numbers.sort()

    # Initialize a counter for consecutive numbers
    consecutive_count = 1

    # Iterate through the sorted list and check for consecutive sequences
    for i in range(1, len(numbers)):
        if numbers[i] == numbers[i - 1] + 1:
            consecutive_count += 1
            if consecutive_count >= count:
                break
        else:
            consecutive_count = 1  # Reset counter if the sequence breaks

    # Count the number of odd numbers
    odd_count = 0
    for pick in numbers:
        if pick % 2 != 0:
            odd_count += 1

    s = ""
    if odd_count >= 1:
        s = f"{odd_count} odd, {len(numbers) - odd_count} even: {numbers}"
    if POWERBALL:
        s += f" {powerball_num}"
    if consecutive_count >= count:
        s += " (" + str(consecutive_count) + " consecutive numbers found)"
    return s

# Load lottery data based on LOTTO value
frequency, powerball_frequency, draws = load_lotto_data(LOTTO)

# Draw frequency graph
print("\nFrequency Graph:")
draw_frequency_graph(frequency)

if POWERBALL:
    print("\nPowerball Frequency Graph:")
    draw_powerball_frequency_graph(powerball_frequency)

# Calculate and display distribution probabilities
distribution = probability_distribution(PICKNUMBER)
print(f"\nProbability Distribution Graph for PICKNUMBER={PICKNUMBER}:")
draw_distribution_graph(distribution)

# Count the odd/even distribution
odd_even_counts = count_odd_even_distribution(draws, PICKNUMBER)

# Draw the odd/even distribution graph
print(f"\nOdd-Even Distribution for PICKNUMBER={PICKNUMBER} based from previous draws:")
draw_odd_even_distribution_graph(odd_even_counts, PICKNUMBER)

# Generate and display lottery numbers
lottery_numbers = generate_numbers(PICKNUMBER, MAXNUMBER, POWERBALL, MAXNUMBERP, frequency, powerball_frequency, draws)
if RESHUFFLE and not POWERBALL:
    lottery_numbers = reshuffle_numbers(lottery_numbers)
print(f"\nSuggested lottery numbers, reshuffled ({RESHUFFLE}), weights ({USEWEIGHTS}):")
for lottery_number in lottery_numbers:
    print(distribution_consecutive_check(lottery_number))
