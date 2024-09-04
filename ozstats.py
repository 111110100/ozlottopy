import os
import pandas as pd
from collections import Counter
from itertools import combinations
from rich.progress import Progress
from rich.console import Console
from rich.table import Table

console = Console()

def load_lotto_data():
    lotto_type = os.getenv('LOTTO')

    if lotto_type == 'tuesday':
        picknumber = 7
        maxnumber = 47
        filename = 'tuesday.csv'
        cols_to_use = ['#1', '#2', '#3', '#4', '#5', '#6', '#7']
    elif lotto_type == 'thursday':
        picknumber = 7
        maxnumber = 35
        maxnumberp = 20
        filename = 'thursday.csv'
        cols_to_use = ['#1', '#2', '#3', '#4', '#5', '#6', '#7', 'PB']
    elif lotto_type == 'saturday':
        picknumber = 6
        maxnumber = 45
        filename = 'saturday.csv'
        cols_to_use = ['#1', '#2', '#3', '#4', '#5', '#6']
    else:
        raise ValueError("Invalid LOTTO type specified.")

    data = pd.read_csv(filename, usecols=cols_to_use)
    return data, picknumber, maxnumber

def find_consecutive(draw, n):
    consecutive_count = 0
    for i in range(len(draw) - n + 1):
        if all(draw[i + j] + 1 == draw[i + j + 1] for j in range(n - 1)):
            consecutive_count += 1
    return consecutive_count

def historical_analysis():
    data, picknumber, maxnumber = load_lotto_data()

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

            # Count consecutive numbers
            has_2_consec = find_consecutive(draw, 2)
            has_3_consec = find_consecutive(draw, 3)

            total_draws_with_2_consec += 1 if has_2_consec >= 1 else 0
            total_draws_with_3_consec += 1 if has_3_consec >= 1 else 0
            total_draws_with_multiple_2_consec += 1 if has_2_consec > 1 else 0
            total_draws_with_2_and_3_consec += 1 if has_2_consec >= 1 and has_3_consec >= 1 else 0

            # Count consecutive pairs and triplets
            for i in range(len(draw) - 1):
                if draw[i] + 1 == draw[i + 1]:
                    consecutive_pairs[(draw[i], draw[i + 1])] += 1
                if i < len(draw) - 2 and draw[i] + 2 == draw[i + 2]:
                    consecutive_triplets[(draw[i], draw[i + 1], draw[i + 2])] += 1

            # Count all pairs and triplets
            all_pairs.update(combinations(draw, 2))
            all_triplets.update(combinations(draw, 3))

            progress.update(task, advance=1)

    number_frequency = Counter(all_numbers)
    least_often_picked = number_frequency.most_common()[-1:]
    cold_numbers = [num for num, count in number_frequency.items() if count == 0]

    console.rule("[bold red]Historical Analysis Results")

    # Print general stats
    console.print(f"Total draws analyzed: {draw_count}")
    console.print(f"Draws with at least 2 consecutive numbers: [green]{total_draws_with_2_consec}[/green] ([cyan]{total_draws_with_2_consec/draw_count:.2%}[/cyan])")
    console.print(f"Draws with at least 3 consecutive numbers: [green]{total_draws_with_3_consec}[/green] ([cyan]{total_draws_with_3_consec/draw_count:.2%}[/cyan])")
    console.print(f"Draws with multiple 2 consecutive numbers: [green]{total_draws_with_multiple_2_consec}[/green] ([cyan]{total_draws_with_multiple_2_consec/draw_count:.2%}[/cyan])")
    console.print(f"Draws with 2 consecutive and 3 consecutive numbers: [green]{total_draws_with_2_and_3_consec}[/green] ([cyan]{total_draws_with_2_and_3_consec/draw_count:.2%}[/cyan])")
    console.print()

    # Print least often picked numbers
    console.print(f"Least often picked numbers: [yellow]{least_often_picked}[/yellow]")
    
    # Print cold numbers
    console.print(f"Cold Numbers (not picked): [blue]{cold_numbers}[/blue]")
    console.print()

    # Print most common pairs
    table_pairs = Table(title="Most Common Pairs")
    table_pairs.add_column("Pair", justify="center", style="magenta")
    table_pairs.add_column("Frequency", justify="center", style="cyan")

    for pair, freq in all_pairs.most_common(5):
        table_pairs.add_row(f"{pair}", f"{freq}")
    console.print(table_pairs)

    # Print most common triplets
    table_triplets = Table(title="Most Common Triplets")
    table_triplets.add_column("Triplet", justify="center", style="magenta")
    table_triplets.add_column("Frequency", justify="center", style="cyan")

    for triplet, freq in all_triplets.most_common(5):
        table_triplets.add_row(f"{triplet}", f"{freq}")
    console.print(table_triplets)

    # Print most common consecutive pairs
    table_consec_pairs = Table(title="Most Common Consecutive Pairs")
    table_consec_pairs.add_column("Consecutive Pair", justify="center", style="magenta")
    table_consec_pairs.add_column("Frequency", justify="center", style="cyan")

    for consec_pair, freq in consecutive_pairs.most_common(5):
        table_consec_pairs.add_row(f"{consec_pair}", f"{freq}")
    console.print(table_consec_pairs)

    # Print most common consecutive triplets
    table_consec_triplets = Table(title="Most Common Consecutive Triplets")
    table_consec_triplets.add_column("Consecutive Triplet", justify="center", style="magenta")
    table_consec_triplets.add_column("Frequency", justify="center", style="cyan")

    for consec_triplet, freq in consecutive_triplets.most_common(5):
        table_consec_triplets.add_row(f"{consec_triplet}", f"{freq}")
    console.print(table_consec_triplets)

if __name__ == "__main__":
    historical_analysis()
