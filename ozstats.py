import os
import pandas as pd
from collections import Counter
from itertools import combinations
from rich.progress import Progress
from rich.console import Console
from rich.table import Table
from math import comb

console = Console()

def load_lotto_data():
    """
    Loads lottery data based on the LOTTO environment variable.
    Returns the DataFrame, picknumber, maxnumber, and a list of number columns.
    """
    lotto_type = os.getenv('LOTTO')

    if lotto_type == 'tuesday':
        picknumber = 7
        maxnumber = 47
        filename = 'tuesday.csv'
        cols_to_use = ['#1', '#2', '#3', '#4', '#5', '#6', '#7']
    elif lotto_type == 'thursday':
        picknumber = 7
        maxnumber = 35
        filename = 'thursday.csv'
        cols_to_use = ['#1', '#2', '#3', '#4', '#5', '#6', '#7']
    elif lotto_type == 'saturday':
        picknumber = 6
        maxnumber = 45
        filename = 'saturday.csv'
        cols_to_use = ['#1', '#2', '#3', '#4', '#5', '#6']
    else:
        raise ValueError("Invalid LOTTO type specified. Choose from 'tuesday', 'thursday', or 'saturday'.")

    try:
        data = pd.read_csv(filename, usecols=cols_to_use)
    except FileNotFoundError:
        console.print(f"[red]Error: File '{filename}' not found.[/red]")
        raise
    except Exception as e:
        console.print(f"[red]Error loading data: {e}[/red]")
        raise

    return data, picknumber, maxnumber

def find_consecutive(draw, n):
    consecutive_count = 0
    for i in range(len(draw) - n + 1):
        if all(draw[i + j] + 1 == draw[i + j + 1] for j in range(n - 1)):
            consecutive_count += 1
    return consecutive_count

def analyze_draws(data):
    draw_count = len(data)
    total_draws_with_2_consec = 0
    total_draws_with_3_consec = 0
    total_draws_with_multiple_2_consec = 0
    total_draws_with_2_and_3_consec = 0
    all_numbers = []
    consecutive_pairs = Counter()
    consecutive_triplets = Counter()
    all_pairs = Counter()
    all_triplets = Counter()

    with Progress() as progress:
        task = progress.add_task("[green]Analyzing draws...", total=draw_count)

        for _, row in data.iterrows():
            draw = sorted(row.dropna().astype(int).values)
            all_numbers.extend(draw)

            has_2_consec = find_consecutive(draw, 2)
            has_3_consec = find_consecutive(draw, 3)

            total_draws_with_2_consec += 1 if has_2_consec >= 1 else 0
            total_draws_with_3_consec += 1 if has_3_consec >= 1 else 0
            total_draws_with_multiple_2_consec += 1 if has_2_consec > 1 else 0
            total_draws_with_2_and_3_consec += 1 if has_2_consec >= 1 and has_3_consec >= 1 else 0

            for i in range(len(draw) - 1):
                if draw[i] + 1 == draw[i + 1]:
                    consecutive_pairs[(draw[i], draw[i + 1])] += 1
                if i < len(draw) - 2 and draw[i] + 2 == draw[i + 2]:
                    consecutive_triplets[(draw[i], draw[i + 1], draw[i + 2])] += 1

            all_pairs.update(combinations(draw, 2))
            all_triplets.update(combinations(draw, 3))

            progress.update(task, advance=1)

    return {
        "draw_count": draw_count,
        "total_draws_with_2_consec": total_draws_with_2_consec,
        "total_draws_with_3_consec": total_draws_with_3_consec,
        "total_draws_with_multiple_2_consec": total_draws_with_multiple_2_consec,
        "total_draws_with_2_and_3_consec": total_draws_with_2_and_3_consec,
        "all_numbers": all_numbers,
        "consecutive_pairs": consecutive_pairs,
        "consecutive_triplets": consecutive_triplets,
        "all_pairs": all_pairs,
        "all_triplets": all_triplets,
    }

def calculate_frequency(all_numbers):
    return Counter(all_numbers)

def find_least_often_picked(number_frequency):
    return number_frequency.most_common()[-1:]

def find_cold_numbers(number_frequency, maxnumber):
    return [num for num in range(1, maxnumber + 1) if num not in number_frequency]

def display_analysis_results(analysis, number_frequency, maxnumber):
    console.rule("[bold red]Historical Analysis Results")

    console.print(f"Total draws analyzed: {analysis['draw_count']}")
    console.print(f"Draws with at least 2 consecutive numbers: [green]{analysis['total_draws_with_2_consec']}[/green] ([cyan]{analysis['total_draws_with_2_consec']/analysis['draw_count']:.2%}[/cyan])")
    console.print(f"Draws with at least 3 consecutive numbers: [green]{analysis['total_draws_with_3_consec']}[/green] ([cyan]{analysis['total_draws_with_3_consec']/analysis['draw_count']:.2%}[/cyan])")
    console.print(f"Draws with multiple 2 consecutive numbers: [green]{analysis['total_draws_with_multiple_2_consec']}[/green] ([cyan]{analysis['total_draws_with_multiple_2_consec']/analysis['draw_count']:.2%}[/cyan])")
    console.print(f"Draws with 2 consecutive and 3 consecutive numbers: [green]{analysis['total_draws_with_2_and_3_consec']}[/green] ([cyan]{analysis['total_draws_with_2_and_3_consec']/analysis['draw_count']:.2%}[/cyan])")
    console.print()

    least_often_picked = find_least_often_picked(number_frequency)
    cold_numbers = find_cold_numbers(number_frequency, maxnumber)

    console.print(f"Least often picked numbers: [yellow]{least_often_picked}[/yellow]")
    console.print(f"Cold Numbers (not picked): [blue]{cold_numbers}[/blue]")
    console.print()

    # Calculate the odd/even distribution
    odd_even_distribution = Counter()

    for _, row in data.iterrows():
        odds = sum(1 for num in row if num % 2 != 0)
        evens = picknumber - odds
        odd_even_distribution[(odds, evens)] += 1

    # Calculate the frequency of each number
    number_frequency = Counter()
    for _, row in data.iterrows():
        numbers = row.values
        number_frequency.update(numbers)

    # Draw the odd/even distribution graph
    distribution = probability_distribution(picknumber)
    display_distribution_graph(distribution)
    display_odd_even_distribution_graph(odd_even_distribution, picknumber)

    display_common_pairs(analysis['all_pairs'])
    display_common_triplets(analysis['all_triplets'])
    display_common_consecutive_pairs(analysis['consecutive_pairs'])
    display_common_consecutive_triplets(analysis['consecutive_triplets'])

def display_odd_even_distribution_graph(odd_even_counts, picknumber):
    table_odd_even_distribution = Table(title="Odd-Even Distribution from Previous Draws")
    table_odd_even_distribution.add_column("Odd Count", justify="center", style="magenta")
    table_odd_even_distribution.add_column("Even Count", justify="center", style="cyan")
    table_odd_even_distribution.add_column("Frequency", justify="left", style="green")
    max_count = max(odd_even_counts.values())

    for odd_count in range(picknumber + 1):
        even_count = picknumber - odd_count
        count = odd_even_counts.get((odd_count, even_count), 0)
        bar = "#" * (count * 50 // max_count)  # Scale bar length to a max of 50
        table_odd_even_distribution.add_row(f"{odd_count}", f"{even_count}", f"{bar} ({count})")
    console.print(table_odd_even_distribution)

def probability_distribution(picknumber):
    total_possibilities = 2 ** picknumber

    distribution = {}
    for odd_count in range(0, picknumber + 1):
        even_count = picknumber - odd_count
        probability = comb(picknumber, odd_count) / total_possibilities
        distribution[(odd_count, even_count)] = probability

    return distribution

def display_distribution_graph(distribution):
    table_distribution_graph = Table(title="Distribution Graph Probability")
    table_distribution_graph.add_column("Odd Count", justify="center", style="magenta")
    table_distribution_graph.add_column("Even Count", justify="center", style="cyan")
    table_distribution_graph.add_column("Probability", justify="left", style="green")
    max_prob = max(distribution.values())
    for key in sorted(distribution.keys()):
        bar = "#" * int(distribution[key] * 50 / max_prob)  # Scale bar length to a max of 50
        #table_distribution_graph.add_row(f"{key[0]}", f"{key[1]}", f"{bar} ({distribution[key]:.4f})")
        table_distribution_graph.add_row(f"{key[0]}", f"{key[1]}", f"{bar} ({distribution[key] * 100:.2f}%)")
    console.print(table_distribution_graph)

def display_common_pairs(all_pairs):
    table_pairs = Table(title="Most Common Pairs")
    table_pairs.add_column("Pair", justify="center", style="magenta")
    table_pairs.add_column("Frequency", justify="center", style="cyan")

    for pair, freq in all_pairs.most_common(5):
        table_pairs.add_row(f"{pair}", f"{freq}")
    console.print(table_pairs)

def display_common_triplets(all_triplets):
    table_triplets = Table(title="Most Common Triplets")
    table_triplets.add_column("Triplet", justify="center", style="magenta")
    table_triplets.add_column("Frequency", justify="center", style="cyan")

    for triplet, freq in all_triplets.most_common(5):
        table_triplets.add_row(f"{triplet}", f"{freq}")
    console.print(table_triplets)

def display_common_consecutive_pairs(consecutive_pairs):
    table_consec_pairs = Table(title="Most Common Consecutive Pairs")
    table_consec_pairs.add_column("Consecutive Pair", justify="center", style="magenta")
    table_consec_pairs.add_column("Frequency", justify="center", style="cyan")

    for consec_pair, freq in consecutive_pairs.most_common(5):
        table_consec_pairs.add_row(f"{consec_pair}", f"{freq}")
    console.print(table_consec_pairs)

def display_common_consecutive_triplets(consecutive_triplets):
    table_consec_triplets = Table(title="Most Common Consecutive Triplets")
    table_consec_triplets.add_column("Consecutive Triplet", justify="center", style="magenta")
    table_consec_triplets.add_column("Frequency", justify="center", style="cyan")

    for consec_triplet, freq in consecutive_triplets.most_common(5):
        table_consec_triplets.add_row(f"{consec_triplet}", f"{freq}")
    console.print(table_consec_triplets)

if __name__ == "__main__":
    data, picknumber, maxnumber = load_lotto_data()
    analysis = analyze_draws(data)
    number_frequency = calculate_frequency(analysis['all_numbers'])
    display_analysis_results(analysis, number_frequency, maxnumber)
