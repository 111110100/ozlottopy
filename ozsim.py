import os
import random
from rich.console import Console
from rich.table import Table
from rich.progress import track, Progress
from collections import Counter

# Initialize rich console
console = Console()

# Division details
DIVISIONS = {
    "tuesday": [
        (1, 7, 0),  # 7 winning numbers
        (2, 6, 1),  # 6 winning + 1 supplementary
        (3, 6, 0),  # 6 winning numbers
        (4, 5, 1),  # 5 winning + 1 supplementary
        (5, 5, 0),  # 5 winning numbers
        (6, 4, 0),  # 4 winning numbers
        (7, 3, 1),  # 3 winning + 1 supplementary
    ],
    "thursday": [
        (1, 7, 1),  # 7 winning + powerball
        (2, 7, 0),  # 7 winning numbers
        (3, 6, 1),  # 6 winning + powerball
        (4, 6, 0),  # 6 winning numbers
        (5, 5, 1),  # 5 winning + powerball
        (6, 4, 1),  # 4 winning + powerball
        (7, 5, 0),  # 5 winning numbers
        (8, 3, 1),  # 3 winning + powerball
        (9, 2, 1),  # 2 winning + powerball
    ],
    "saturday": [
        (1, 6, 0),  # 6 winning numbers
        (2, 5, 1),  # 5 winning + 1 supplementary
        (3, 5, 0),  # 5 winning numbers
        (4, 4, 0),  # 4 winning numbers
        (5, 3, 1),  # 3 winning + 1 supplementary
        (6, 3, 0),  # 3 winning numbers
    ],
}

# Function to generate random numbers
def generate_numbers(count, max_number):
    return sorted(random.sample(range(1, max_number + 1), count))

# Function to generate tickets
def generate_tickets(ticket_count, picknumber, maxnumber, powerball_max=None):
    tickets = []
    with Progress() as progress:
        task = progress.add_task("[green]Generating tickets...", total=ticket_count)
        for _ in range(ticket_count):
            main_numbers = sorted(random.sample(range(1, maxnumber + 1), picknumber))
            tickets.append(main_numbers)
            progress.update(task, advance=1)
    if powerball_max:
        powerball = random.randint(1, powerball_max)
        tickets.append(main_numbers + [powerball])
    return tickets

# Function to check ticket divisions
def check_division(ticket, winning, supplementary, divisions):
    match_counts = Counter(ticket) & Counter(winning)
    winning_count = sum(match_counts.values())
    supplementary_count = sum(1 for num in ticket if num in supplementary)

    for division, req_winning, req_supp in divisions:
        if winning_count == req_winning and supplementary_count == req_supp:
            return division
    return None

# Function to simulate lotto
def simulate_lotto():
    lotto_type = os.getenv("LOTTO", "tuesday").lower()
    winning_numbers = os.getenv("WINNING")
    ticket_count = int(os.getenv("TICKETS", 100000))
    drawn_tickets = ticket_count

    # Lotto-specific settings
    if lotto_type == "tuesday":
        picknumber, maxnumber, supplementary_count = 7, 47, 3
    elif lotto_type == "thursday":
        picknumber, maxnumber, supplementary_count = 7, 35, 1
    elif lotto_type == "saturday":
        picknumber, maxnumber, supplementary_count = 6, 45, 2
    else:
        console.print("[red]Invalid LOTTO type specified.[/red]")
        return

    # Generate or parse winning numbers
    if winning_numbers:
        winning_numbers = list(map(int, winning_numbers.split(",")))
        winning = winning_numbers[:picknumber]
        supplementary = winning_numbers[picknumber: picknumber + supplementary_count]
    else:
        winning = generate_numbers(picknumber, maxnumber)
        if lotto_type == "thursday":
            supplementary = generate_numbers(supplementary_count, 20)
        else:
            supplementary = generate_numbers(supplementary_count, maxnumber)
            while set(supplementary).intersection(set(winning)):
                supplementary = generate_numbers(supplementary_count, maxnumber)

    # Generate random tickets
    if lotto_type == "thursday":
        tickets = generate_tickets(ticket_count, picknumber, maxnumber, powerball_max=20)
    else:
        tickets = generate_tickets(ticket_count, picknumber, maxnumber)

    # Simulate results
    results = Counter()
    for ticket in track(tickets, description="Checking tickets..."):
        division = check_division(ticket, winning, supplementary, DIVISIONS[lotto_type])
        if division:
            results[division] += 1

    # Display results
    console.rule(f"[bold green]Lotto Simulation Results ({lotto_type.capitalize()} Draw)[/bold green]")
    table = Table(title="Division Results")
    table.add_column("Division", justify="right")
    table.add_column("Winning Tickets", justify="right")
    table.add_column("Representation", justify="left")

    # Add rows for all divisions, even if no winners
    winning_tix = 0
    for division, req_winning, req_supp in DIVISIONS[lotto_type]:
        ticket_count = results.get(division, 0)
        winning_tix += ticket_count
        blue_dots = "●" * req_winning
        red_dots = "●" * req_supp
        table.add_row(str(division), f"{ticket_count:,}", f"[blue]{blue_dots}[/blue][red]{red_dots}[/red]")

    console.print(table)

    # Display winning combination
    console.print(f"\n[bold yellow]Winning Numbers:[/bold yellow] {winning}")
    console.print(f"[bold yellow]Supplementary/Powerball Number:[/bold yellow] {supplementary}")
    console.print(f"[bold yellow]Total winning tickets:[/bold yellow] {winning_tix:,}")
    console.print(f"[bold yellow]Number of tickets drawn:[/bold yellow] {drawn_tickets:,}")
    console.print(f"[bold yellow]Total non-winning tickets:[/bold yellow] {drawn_tickets - winning_tix:,}")

# Main block
if __name__ == "__main__":
    simulate_lotto()
