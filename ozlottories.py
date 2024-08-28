import os
import random
from math import comb
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set default values from environment variables
POWERBALL = os.getenv("POWERBALL", "False") == "True"
PICKNUMBER = int(os.getenv("PICKNUMBER", 6))
MAXNUMBER = int(os.getenv("MAXNUMBER", 45))
MAXNUMBERP = int(os.getenv("MAXNUMBERP", 20))
SUGGEST = int(os.getenv("SUGGEST", 1))

def probability_distribution(picknumber):
    total_possibilities = 2 ** picknumber
    
    distribution = {}
    for odd_count in range(0, picknumber + 1):
        even_count = picknumber - odd_count
        probability = comb(picknumber, odd_count) / total_possibilities
        distribution[(odd_count, even_count)] = probability
    
    return distribution

def generate_numbers(picknumber, maxnumber, powerball=False, maxnumberp=20):
    suggested_numbers = []

    for _ in range(SUGGEST):
        # Determine odd and even count based on PICKNUMBER
        if picknumber % 2 == 0:
            odd_count, even_count = picknumber // 2, picknumber // 2
        else:
            odd_count, even_count = random.choice([(picknumber // 2 + 1, picknumber // 2), (picknumber // 2, picknumber // 2 + 1)])
        
        # Generate odd and even numbers
        odds = [num for num in range(1, maxnumber+1) if num % 2 != 0]
        evens = [num for num in range(1, maxnumber+1) if num % 2 == 0]
        
        chosen_odds = random.sample(odds, odd_count)
        chosen_evens = random.sample(evens, even_count)
        
        numbers = sorted(chosen_odds + chosen_evens)
        
        # Add powerball number if required
        if powerball:
            powerball_num = random.randint(1, maxnumberp)
            numbers.append(f"P:{powerball_num}")
        
        suggested_numbers.append(numbers)
    
    return suggested_numbers

# Generate and display lottery numbers
lottery_numbers = generate_numbers(PICKNUMBER, MAXNUMBER, POWERBALL, MAXNUMBERP)
print(f"Suggested lottery numbers: {lottery_numbers}")

# Calculate and display distribution probabilities
distribution = probability_distribution(PICKNUMBER)
print("Probability distribution for odd/even splits:")
for key, probability in distribution.items():
    print(f"{key}: {probability:.4f}")
