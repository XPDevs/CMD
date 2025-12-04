import random
import time
import sys
import threading
from collections import defaultdict
import os # NEW: Import os for screen clearing

# The required pool size of codes to generate.
CANDIDATE_POOL_SIZE = 10000 
FINAL_CODE_COUNT = 10 

# Global flag to control the spinner loop
stop_spinner = False
# Global variables to store the results
unique_codes = []
initial_duplicate_count = 0
filtered_code_count = 0

# --- Utility Function for Clearing Screen ---
def clear_screen():
    """Clears the console screen based on the operating system."""
    # 'nt' is Windows, 'posix' is Linux/macOS
    os.system('cls' if os.name == 'nt' else 'clear')

# --- Core Utility Functions ---

def generate_code_segment(length):
    """Generates a random alphanumeric string segment."""
    # Using alphanumeric characters (excluding '0' and 'O' to minimize confusion)
    data_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ13456789" # Excluded 2 to reduce visual similarity to Z
    return "".join(random.choice(data_chars) for _ in range(length))

def generate_full_code():
    """Generates a full gift code in the format: XXXX-XXXXXX-XXXXX"""
    return generate_code_segment(4) + "-" + generate_code_segment(6) + "-" + generate_code_segment(5)


# --- Threading and Animation Functions ---

def spinner(pool_size):
    """
    Displays a spinning line animation and live progress until the stop_spinner flag is True.
    """
    global stop_spinner
    frames = ['|', '/', '-', '\\']
    # Messages for the three main steps
    step_messages = [
        f'1. Generating {pool_size:,} Codes... ',
        '2. Removing Exact Duplicates... ',
        '3. Filtering by First Character...'
    ]
    
    # Simple state tracking for the user to see progress
    step = 0
    current_message = step_messages[0]
    
    while not stop_spinner:
        # Update the message based on the progress step
        if step < 40: # Generation step
            current_message = step_messages[0]
        elif step < 80: # Deduplication step
            current_message = step_messages[1]
        else: # Filtering step
            current_message = step_messages[2]
        
        for frame in frames:
            if stop_spinner:
                break
            # Update the display
            sys.stdout.write(f'\r{current_message}{frame}')
            sys.stdout.flush()
            time.sleep(0.05)
        step += 1
    
    # Clear the spinner line after the duration is finished
    sys.stdout.write('\r' + ' ' * 100 + '\r')
    sys.stdout.flush()


def process_and_analyze_codes_task(pool_size):
    """
    Generates, de-duplicates, and filters the codes to keep only one per
    unique starting character.
    """
    global unique_codes, initial_duplicate_count, filtered_code_count, stop_spinner
    
    # Reset globals for the new run
    unique_codes = []
    initial_duplicate_count = 0
    filtered_code_count = 0
    stop_spinner = False
    
    all_codes = []

    # --- Step 1: Generation ---
    for _ in range(pool_size):
        all_codes.append(generate_full_code())
    
    # --- Step 2: Exact De-duplication ---
    unique_set = set(all_codes)
    unique_codes_list = list(unique_set)
    initial_duplicate_count = len(all_codes) - len(unique_codes_list)

    # --- Step 3: Filter by First Character ---
    filtered_codes_by_start = {}
    
    for code in unique_codes_list:
        first_char = code[0]
        filtered_codes_by_start[first_char] = code 
        
    unique_codes = sorted(list(filtered_codes_by_start.values()))
    filtered_code_count = len(unique_codes_list) - len(unique_codes)

    # Set the flag to stop the spinner when processing is complete
    stop_spinner = True

# --- Main Program Logic (MODIFIED WITH LOOP) ---

def main():
    while True:
        # NEW: Clear the screen at the start of every loop iteration
        clear_screen()
        
        # Reset stop_spinner flag at the start of each loop iteration
        global stop_spinner
        stop_spinner = False
        
        # --- USER INPUT: POOL SIZE SELECTION ---
        print("\n" + "=" * 55)
        print("GIFT CODE GENERATOR MENU")
        print("=" * 55)
        print("1. Select Number of Codes to Generate")
        while True:
            try:
                print(f"1. Preset Pool Size: 10,000 codes")
                print(f"2. Preset Pool Size: 50,000 codes")
                print(f"3. Custom Pool Size")
                pool_choice = input("Enter choice (1, 2, or 3): ")
                
                if pool_choice == '1':
                    pool_size = 10000
                    break
                elif pool_choice == '2':
                    pool_size = 50000
                    break
                elif pool_choice == '3':
                    while True:
                        try:
                            pool_size = int(input("Enter custom number of codes (e.g., 100000): "))
                            if pool_size > 0:
                                break
                            else:
                                print("Please enter a positive number.")
                        except ValueError:
                            print("Invalid input. Please enter a whole number.")
                    break
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")
            except ValueError:
                print("Invalid input. Please enter a number.")
                
        # --- PROCESSING START ---
        
        # The monetary value is always Random £5.00 to £250.00
        print("-" * 55)
        print(f"Selected Pool Size: {pool_size:,} codes.")
        print("Selected Value: Random £5.00 to £250.00")
        print(f"1. Generating a pool of {pool_size:,} codes.")
        print(f"2. Removing exact duplicates.")
        print(f"3. Filtering: Keeping only one code per unique starting character.")
        print("-" * 55)

        # 1. Start the analysis task in a separate thread
        analysis_thread = threading.Thread(target=process_and_analyze_codes_task, args=(pool_size,))
        analysis_thread.start()

        # 2. Run the spinner animation on the main thread
        spinner(pool_size)

        # 3. Wait for the analysis thread to fully complete
        analysis_thread.join()

        # 4. Assign monetary values to the final unique codes (Always random £5-£250)
        final_codes_with_value = []
        
        for code in unique_codes:
            # Assign random integer amount between 5 and 250
            assigned_amount = random.randint(5, 250)
            final_codes_with_value.append((code, float(assigned_amount)))
                
        # --- RESULTS ---

        print("\n\nPROCESSING COMPLETE")
        print(f"Total Codes Generated: {pool_size:,}")
        print(f"Exact Duplicates Found: {initial_duplicate_count:,}")
        print(f"Codes filtered by starting character: {filtered_code_count:,}")
        print(f"Total Final Unique Codes: {len(unique_codes):,}")
        
        print("-" * 55)

        # Print ALL of the final unique codes with their assigned values
        if final_codes_with_value:
            codes_to_print = len(final_codes_with_value) 
            
            header = "Random £5.00 to £250.00"
                 
            print(f"\n--- ALL {codes_to_print} FINAL UNIQUE CODES ({header}) ---\n")
            
            # Iterate through the (code, amount) tuples
            for code, value in final_codes_with_value: 
                print(f"{code} - £{value:.2f}") 
        else:
            print("No codes were generated or kept after filtering.")

        print("\nProcess complete!")
        time.sleep(1)

        # --- LOOP CONTROL ---
        # Wait for user input to either loop or exit
        control_input = input("\n[DONE] Press Enter to return to the menu, or type 'exit' and press Enter to quit: ").strip().lower()
        if control_input == 'exit':
            break

if __name__ == "__main__":
    main()