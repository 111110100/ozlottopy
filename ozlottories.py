import os
import random
import csv
from collections import Counter
from math import comb
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# Load environment variables
load_dotenv()

console = Console()

# Set default values based on LOTTO
LOTTO = os.getenv("LOTTO", "").lower()
USEWEIGHTS = os.getenv("USEWEIGHTS", "false").lower() == "true"

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
            numbers.append(powerball_num)

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
    table_frequency = Table(title="Odd-Even Frequency Graph")
    table_frequency.add_column("Number", justify="center", style="magenta")
    table_frequency.add_column("Frequency", justify="left", style="cyan")
    max_freq = max(frequency.values())
    for number in sorted(frequency.keys()):
        bar = "#" * (frequency[number] * 50 // max_freq)  # Scale bar length to a max of 50
        table_frequency.add_row(f"{number}", f"{bar} ({frequency[number]})")
    console.print(table_frequency)

def draw_powerball_frequency_graph(powerball_frequency):
    if not powerball_frequency:
        print("No Powerball frequency data available.")
        return

    table_powerball_frequency = Table(title="Powerball Frequency Graph")
    table_powerball_frequency.add_column("Powerball Number", justify="center", style="magenta")
    table_powerball_frequency.add_column("Frequency", justify="left", style="cyan")
    max_freq = max(powerball_frequency.values())
    for number in sorted(powerball_frequency.keys()):
        bar = "#" * (powerball_frequency[number] * 50 // max_freq)  # Scale bar length to a max of 50
        table_powerball_frequency.add_row(f"{number}", f"{bar} ({powerball_frequency[number]})")
    console.print(table_powerball_frequency)

def draw_distribution_graph(distribution):
    table_distribution_graph = Table(title="Odd-Even Distribution Graph Probability")
    table_distribution_graph.add_column("Odd Count", justify="center", style="magenta")
    table_distribution_graph.add_column("Even Count", justify="center", style="cyan")
    table_distribution_graph.add_column("Probability", justify="left", style="green")
    max_prob = max(distribution.values())
    for key in sorted(distribution.keys()):
        bar = "#" * int(distribution[key] * 50 / max_prob)  # Scale bar length to a max of 50
        table_distribution_graph.add_row(f"{key[0]}", f"{key[1]}", f"{bar} ({distribution[key] * 100:.2f}%)")
    console.print(table_distribution_graph)

def probability_distribution(picknumber):
    total_possibilities = 2 ** picknumber

    distribution = {}
    for odd_count in range(0, picknumber + 1):
        even_count = picknumber - odd_count
        probability = comb(picknumber, odd_count) / total_possibilities
        distribution[(odd_count, even_count)] = probability

    return distribution

def draw_odd_even_distribution_graph(odd_even_counts, picknumber):
    table_odd_even_distribution = Table(title="Odd-Even Distribution from Previous Draws")
    table_odd_even_distribution.add_column("Odd Count", justify="center", style="magenta")
    table_odd_even_distribution.add_column("Even Count", justify="center", style="cyan")
    table_odd_even_distribution.add_column("Actual drawn", justify="left", style="green")
    max_count = max(odd_even_counts.values())

    for odd_count in range(picknumber + 1):
        even_count = picknumber - odd_count
        count = odd_even_counts.get((odd_count, even_count), 0)
        bar = "#" * (count * 50 // max_count)  # Scale bar length to a max of 50
        table_odd_even_distribution.add_row(f"{odd_count}", f"{even_count}", f"{bar} ({count})")
    console.print(table_odd_even_distribution)

def display_suggested_numbers(lotto_numbers, count=3):
    table_suggested_numbers = Table(title="Suggested Lottery Numbers")
    table_suggested_numbers.add_column("Odd Count", justify="center", style="magenta")
    table_suggested_numbers.add_column("Even Count", justify="center", style="cyan")
    table_suggested_numbers.add_column("Suggested Numbers", justify="left", style="green")
    table_suggested_numbers.add_column("Powerball Number", justify="left", style="blue")
    table_suggested_numbers.add_column("Consecutive Count", justify="left", style="yellow")

    row = 1
    for numbers in lotto_numbers:
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

        if row % 2 == 0:
            odd_count_s = f"[b]{odd_count}[/b]"
            even_count_s = f"[b]{len(numbers) - odd_count}[/b]"
            numbers_s = f"[b]{numbers}[/b]"
            powerball_num_s = f"[b]{powerball_num}[/b]" if POWERBALL else ""
            consecutive_count_s = f"[b]{consecutive_count}[/b]" if consecutive_count >= count else ""
        else:
            odd_count_s = f"{odd_count}"
            even_count_s = f"{len(numbers) - odd_count}"
            numbers_s = f"{numbers}"
            powerball_num_s = f"{powerball_num}" if POWERBALL else ""
            consecutive_count_s = f"{consecutive_count}" if consecutive_count >= count else ""

        table_suggested_numbers.add_row(
            odd_count_s,
            even_count_s,
            numbers_s,
            powerball_num_s,
            consecutive_count_s
        )

        row += 1

    console.print(table_suggested_numbers)


def factorial(n):
    final_product = 1
    for i in range(n, 0, -1):
        final_product *= i
    return final_product


def combinatons(n, k):
    numerator = factorial(n)
    denominator = factorial(k) * factorial(n-k)
    return numerator / denominator


def ticket_probability(tickets_played):
    console.rule("[bold red]Probabilty of winning")
    total_outcomes = combinatons(MAXNUMBER, PICKNUMBER)
    combinations_simplified = round(total_outcomes / tickets_played)
    console.print(f"Chances of winning with [red]{SUGGEST}[/red] tickets is [blue]1[/blue] in [green]{combinations_simplified:,}[/green]")


# Load lottery data based on LOTTO value
frequency, powerball_frequency, draws = load_lotto_data(LOTTO)

# Draw frequency graph
draw_frequency_graph(frequency)

if POWERBALL:
    draw_powerball_frequency_graph(powerball_frequency)

# Calculate and display distribution probabilities
distribution = probability_distribution(PICKNUMBER)
draw_distribution_graph(distribution)

# Count the odd/even distribution
odd_even_counts = count_odd_even_distribution(draws, PICKNUMBER)

# Draw the odd/even distribution graph
draw_odd_even_distribution_graph(odd_even_counts, PICKNUMBER)

# Generate and display lottery numbers
lottery_numbers = generate_numbers(PICKNUMBER, MAXNUMBER, POWERBALL, MAXNUMBERP, frequency, powerball_frequency, draws)
display_suggested_numbers(lottery_numbers)

# Show probability of winning
ticket_probability(SUGGEST)