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

def generate_numbers(picknumber, maxnumber, powerball=False, maxnumberp=20):
    suggested_numbers = []
    for _ in range(SUGGEST):
        numbers = []
        odd_count, even_count = 0, 0
        
        while len(numbers) < picknumber:
            num = random.randint(1, maxnumber)
            if num not in numbers:
                numbers.append(num)
                if num % 2 == 0:
                    even_count += 1
                else:
                    odd_count += 1
                
                # Adjust for minimum 3 odd and 3 even numbers
                if len(numbers) == picknumber - 1:
                    if odd_count < 3:
                        num = random.choice([n for n in range(1, maxnumber+1) if n % 2 != 0 and n not in numbers])
                        numbers.append(num)
                        odd_count += 1
                    elif even_count < 3:
                        num = random.choice([n for n in range(1, maxnumber+1) if n % 2 == 0 and n not in numbers])
                        numbers.append(num)
                        even_count += 1
        
        numbers.sort()
        
        # Add powerball number if required
        if powerball:
            powerball_num = random.randint(1, maxnumberp)
            numbers.append(powerball_num)
        
        suggested_numbers.append(numbers)
    
    return suggested_numbers

def probability_more_odds(picknumber):
    total_odd = picknumber // 2 + 1
    total_even = picknumber - total_odd
    
    # Calculate probabilities
    prob_odd = sum(comb(picknumber, k) for k in range(total_odd, picknumber + 1))
    prob_even = 2 ** picknumber
    return prob_odd / prob_even

# Generate and display lottery numbers
lottery_numbers = generate_numbers(PICKNUMBER, MAXNUMBER, POWERBALL, MAXNUMBERP)
print(f"Suggested lottery numbers: {lottery_numbers}")

# Calculate and display probability if PICKNUMBER > 6
if PICKNUMBER > 6:
    prob = probability_more_odds(PICKNUMBER)
    print(f"Probability of having more odd numbers than even numbers: {prob:.4f}")
