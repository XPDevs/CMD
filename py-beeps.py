import time
import sys
import json
import os
import random # Added for randomization

SEQUENCE_FILENAME = "beep_sequence.json"

def get_valid_float(prompt, min_val=0.0):
    """Helper function to get a validated float input."""
    while True:
        try:
            value = float(input(prompt))
            if value < min_val:
                print(f"Value must be {min_val} or greater.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a number (e.g., 0.5 or 2).")

def get_valid_int(prompt, min_val=1):
    """Helper function to get a validated integer input."""
    while True:
        try:
            value = int(input(prompt))
            if value < min_val:
                print(f"Value must be a whole number, {min_val} or greater.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a whole number.")

def create_new_sequence():
    """Interactively creates a new beep sequence configuration."""
    print("\n--- 1. CREATE NEW SEQUENCE ---")
    
    # 1. Initial Wait
    initial_wait = get_valid_float(
        "Enter wait time BEFORE the first beep (seconds, e.g., 2.0): "
    )

    # 2. Number of Beeps
    num_beeps = get_valid_int(
        "Enter the TOTAL number of beeps in the sequence (e.g., 5): "
    )
    
    delays = []
    if num_beeps > 1:
        print(f"\nNow enter the {num_beeps - 1} individual delays between the beeps:")
        for i in range(num_beeps - 1):
            delay = get_valid_float(
                f"  Delay between beep {i+1} and beep {i+2} (seconds): "
            )
            delays.append(delay)
    
    sequence = {
        "initial_wait": initial_wait,
        "num_beeps": num_beeps,
        "delays": delays
    }
    
    print("\nSequence created successfully.")
    print(f"Beeps: {num_beeps}. Initial Wait: {initial_wait}s. Delays: {delays}")
    return sequence

def create_random_sequence():
    """Generates a completely random beep sequence configuration."""
    print("\n--- 5. CREATE RANDOM SEQUENCE (SURPRISE!) ---")
    
    # Define reasonable ranges for randomization
    MIN_BEATS = 3
    MAX_BEATS = 15
    MIN_TIME = 0.1
    MAX_TIME = 5.0

    # 1. Random Initial Wait (rounded to two decimals for cleaner data)
    initial_wait = round(random.uniform(MIN_TIME, MAX_TIME), 2)

    # 2. Random Number of Beeps
    num_beeps = random.randint(MIN_BEATS, MAX_BEATS)
    
    delays = []
    if num_beeps > 1:
        for i in range(num_beeps - 1):
            # Random delay for each segment
            delay = round(random.uniform(MIN_TIME, MAX_TIME), 2)
            delays.append(delay)
    
    sequence = {
        "initial_wait": initial_wait,
        "num_beeps": num_beeps,
        "delays": delays
    }
    
    # Only report the count, keeping the timing secret, as requested
    print(f"\nRandom sequence created with {num_beeps} beeps. Get ready for a surprise!")
    return sequence


def save_sequence(sequence):
    """Saves the sequence to the predefined JSON file."""
    if not sequence:
        print("\nError: Cannot save. Please create a sequence first.")
        return

    try:
        with open(SEQUENCE_FILENAME, 'w') as f:
            json.dump(sequence, f, indent=4)
        print(f"\nSequence saved to {SEQUENCE_FILENAME}")
    except Exception as e:
        print(f"\nError saving file: {e}")

def load_sequence():
    """Loads the sequence from the predefined JSON file."""
    if not os.path.exists(SEQUENCE_FILENAME):
        print(f"\nError: File '{SEQUENCE_FILENAME}' not found. Please create and save a sequence first.")
        return None
    
    try:
        with open(SEQUENCE_FILENAME, 'r') as f:
            sequence = json.load(f)
            print(f"\nSequence loaded from {SEQUENCE_FILENAME}:")
            print(f"Beeps: {sequence.get('num_beeps', 0)}. Initial Wait: {sequence.get('initial_wait', 0.0)}s.")
            return sequence
    except json.JSONDecodeError:
        print(f"\nError: File '{SEQUENCE_FILENAME}' contains invalid JSON data.")
        return None
    except Exception as e:
        print(f"\nError loading file: {e}")
        return None

def execute_sequence(sequence):
    """
    Executes the beeping sequence using the PC speaker bell character.
    This relies on the terminal being configured to map \a to the speaker.
    """
    if not sequence:
        print("\nError: No sequence defined to run.")
        return

    initial_wait = sequence.get("initial_wait", 0.0)
    num_beeps = sequence.get("num_beeps", 0)
    delays = sequence.get("delays", [])

    if num_beeps == 0:
        print("\nSequence has 0 beeps. Doing nothing.")
        return

    print(f"\nExecuting sequence. Initial wait of {initial_wait} seconds...")
    time.sleep(initial_wait)

    for i in range(num_beeps):
        # Fire the beep (ASCII Bell character)
        sys.stdout.write('\a')
        sys.stdout.flush()

        print(f"  -> Beep {i + 1}/{num_beeps} fired.")

        # If this is not the last beep, wait for the specified delay
        if i < num_beeps - 1:
            delay = delays[i] if i < len(delays) else 0.5 # Fallback delay
            print(f"  -> Waiting {delay} seconds...")
            time.sleep(delay)
        
    print("\n--- Sequence finished ---")

def main_menu():
    """The main application loop and menu system."""
    current_sequence = None
    
    print("====================================")
    print(" TCore PC Speaker Sequence Controller")
    print("====================================")
    
    while True:
        print("\n--- MAIN MENU ---")
        if current_sequence:
            print(f"Current Sequence Loaded: {current_sequence['num_beeps']} beeps.")
        else:
            print("Current Sequence Loaded: None.")
            
        print("1. Create New Sequence (Interactive Input)")
        print(f"2. Save Current Sequence to file ({SEQUENCE_FILENAME})")
        print(f"3. Load Sequence from file ({SEQUENCE_FILENAME})")
        print("4. RUN Current Sequence")
        print("5. Create RANDOM Sequence (Surprise!)")
        print("6. Exit")
        
        choice = input("\nEnter choice (1-6): ")
        
        if choice == '1':
            current_sequence = create_new_sequence()
        
        elif choice == '2':
            save_sequence(current_sequence)
            
        elif choice == '3':
            loaded_seq = load_sequence()
            if loaded_seq:
                current_sequence = loaded_seq
                
        elif choice == '4':
            if current_sequence:
                execute_sequence(current_sequence)
            else:
                print("\nCannot run. Please create (1), load (3), or randomize (5) a sequence first.")

        elif choice == '5':
            current_sequence = create_random_sequence()

        elif choice == '6':
            print("\nExiting PC Speaker Controller. Goodbye!")
            break
            
        else:
            print("\nInvalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main_menu()
