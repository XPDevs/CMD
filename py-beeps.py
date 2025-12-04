import time
import sys
import json
import os
import random # Added for randomization

SEQUENCE_FILENAME = "beep_sequence.json"

# Morse Code Dictionary for commonly used characters
MORSE_CODE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
    '.': '.-.-.-', ',': '--..--', '?': '..-..', '/': '-..-.', '-': '-....-',
    '(': '-.--.', ')': '-.--.-', ' ': ' ' # Space is handled separately
}

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
    Executes the custom sequence using the PC speaker bell character.
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

def text_to_morse_speaker():
    """Gets user input for text and WPM, then executes the Morse sequence."""
    print("\n--- 6. TEXT-TO-MORSE SPEAKER (EXPERIMENTAL) ---")
    
    text = input("Enter text to translate (A-Z, 0-9, limited punctuation): ").upper()
    
    wpm = get_valid_int(
        "Enter playback speed (Words Per Minute, e.g., 20 WPM): ", min_val=5
    )
    
    execute_morse_sequence(text, wpm)


def execute_morse_sequence(text, wpm):
    """
    Converts text to Morse Code and executes the beep sequence based on WPM timing.
    Paris standard timing used: Dot = T, Dash = 3T, Element Space = T, Char Space = 3T, Word Space = 7T.
    T (dot duration) = 1.2 / WPM (seconds)
    """
    print(f"\nTranslating '{text}' at {wpm} WPM...")
    
    # Calculate the base time unit (T) for the dot
    T = 1.2 / wpm
    
    # Define timing constants
    DUR_DOT = T
    DUR_DASH = 3 * T
    WAIT_ELEMENT = T       # Wait between dots/dashes within a letter
    WAIT_CHAR = 3 * T      # Wait between letters
    WAIT_WORD = 7 * T      # Wait between words
    
    print(f"Base Dot Duration (T): {DUR_DOT:.3f}s. Starting transmission...")

    for i, char in enumerate(text):
        if char == ' ':
            print("  [Word Space]")
            time.sleep(WAIT_WORD)
            continue

        morse = MORSE_CODE.get(char)
        if morse is None:
            print(f"  [Skipping unknown character: {char}]")
            continue
            
        print(f"  Character '{char}' ({morse}):")
        
        # Transmit the Morse sequence for the character
        for j, element in enumerate(morse):
            # 1. Produce Sound (Beep)
            if element == '.':
                duration = DUR_DOT
                print(f"    - Dot ({duration:.3f}s)")
            elif element == '-':
                duration = DUR_DASH
                print(f"    - Dash ({duration:.3f}s)")
            else:
                continue # Should not happen with valid Morse

            # The PC speaker beep is instant, so we just signal it and wait for the duration
            sys.stdout.write('\a')
            sys.stdout.flush()
            time.sleep(duration)
            
            # 2. Produce Gap between elements
            if j < len(morse) - 1:
                time.sleep(WAIT_ELEMENT)
        
        # 3. Produce Gap between characters
        time.sleep(WAIT_CHAR)
        
    print("\n--- Morse Transmission finished ---")


def main_menu():
    """The main application loop and menu system with TUI."""
    current_sequence = None
    
    while True:
        # Clear screen placeholder (print many newlines)
        print('\n' * 50) 

        # TUI Header and Status
        print("╔═════════════════════════════════════════════════════════════╗")
        print("║          TCore PC Speaker Sequence Controller (TUI)         ║")
        print("╠═════════════════════════════════════════════════════════════╣")
        
        if current_sequence:
            status = f"STATUS: Active Sequence - {current_sequence['num_beeps']} total beeps."
        else:
            status = "STATUS: No sequence loaded."

        print(f"║ {status:<57} ║")
        print("╠═════════════════════════════════════════════════════════════╣")
        
        # Menu Options
        print("║ 1. Create New Sequence (Interactive Input)                  ║")
        print(f"║ 2. Save Current Sequence to file ({SEQUENCE_FILENAME})             ║")
        print(f"║ 3. Load Sequence from file ({SEQUENCE_FILENAME})                   ║")
        print("║ 4. RUN Custom Sequence                                      ║")
        print("║ 5. Create RANDOM Sequence (Surprise!)                       ║")
        print("║ 6. Text-to-Morse Speaker (Experimental)                     ║")
        print("║ 7. Exit                                                     ║")
        print("╚═════════════════════════════════════════════════════════════╝")
        
        choice = input("\n[ACTION] Enter choice (1-7) and press Enter: ")
        
        print("\n" + "="*70) # Separator for action output

        # Handle user choice
        if choice == '1':
            current_sequence = create_new_sequence()
            input("\n[PAUSE] Press Enter to return to the menu...")
        
        elif choice == '2':
            save_sequence(current_sequence)
            input("\n[PAUSE] Press Enter to return to the menu...")
            
        elif choice == '3':
            loaded_seq = load_sequence()
            if loaded_seq:
                current_sequence = loaded_seq
            input("\n[PAUSE] Press Enter to return to the menu...")
                
        elif choice == '4':
            if current_sequence:
                execute_sequence(current_sequence)
            else:
                print("\n[ERROR] Cannot run. Please create (1), load (3), or randomize (5) a sequence first.")
            input("\n[PAUSE] Press Enter to return to the menu...")

        elif choice == '5':
            current_sequence = create_random_sequence()
            input("\n[PAUSE] Press Enter to return to the menu...")

        elif choice == '6':
            # New Morse Code function
            text_to_morse_speaker()
            input("\n[PAUSE] Press Enter to return to the menu...")

        elif choice == '7':
            print("\nExiting PC Speaker Controller. Goodbye!")
            break
            
        else:
            print(f"\n[ERROR] Invalid choice '{choice}'. Please enter a number between 1 and 7.")
            input("\n[PAUSE] Press Enter to continue...")


if __name__ == "__main__":
    main_menu()
