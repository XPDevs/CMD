import random
import time
import sys
import threading
from collections import defaultdict

# --- Core Utility Functions ---

def generate_code_segment(length):
    """Generates a random alphanumeric string segment."""
    # Using alphanumeric characters (excluding '0' and 'O' to minimize confusion)
    # The character '2' has been added back to the pool.
    data_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"
    return "".join(random.choice(data_chars) for _ in range(length))

def generate_full_code():
    """Generates a full gift code in the format: XXXX-XXXXXX-XXXXX"""
    return generate_code_segment(4) + "-" + generate_code_segment(6) + "-" + generate_code_segment(5)


# --- Visual Animation Function ---

def code_animation(duration=0.5, speed=0.02):
    """
    Simulates a complex generation process by displaying a rapid, randomized 
    placeholder sequence over the current line for a short duration.
    """
    start_time = time.time()
    code_format = "####-######-#####"
    
    while time.time() - start_time < duration:
        # Generate a random, high-entropy placeholder string that matches the code format
        # This makes it look like data is being rapidly processed.
        temp_code = ""
        for char in code_format:
            if char == '-':
                temp_code += '-'
            else:
                # Use a mix of characters and symbols for a "hacking" or "processing" look
                temp_code += random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$&*")
        
        # Use \r to return to the start of the line and overwrite the previous output
        sys.stdout.write(f"\r[PROCESSING] GENERATING CODE... {temp_code}")
        sys.stdout.flush()
        time.sleep(speed)
        
    # Clear the animation line before printing the final code
    # We use a long line of spaces followed by \r to ensure full clearance
    sys.stdout.write('\r' + ' ' * 100 + '\r')
    sys.stdout.flush()


# --- Infinite Generation Task ---

# Global flag to control the infinite loop (though it's intended to run forever)
stop_generation = False
# Counter to track how many codes have been generated
code_count = 0

def infinite_code_generator_task():
    """
    Runs the animation, generates a code, and prints the result indefinitely.
    """
    global code_count, stop_generation
    
    # Run the generation loop forever
    while not stop_generation:
        # 1. Run the visual animation to simulate "doing something amazing"
        code_animation()
        
        # 2. Generate the actual code
        code = generate_full_code()
        code_count += 1
        
        # 3. Print the final result
        print(f"Generated Code {code_count:,}: {code}")
        
        # Wait a small amount of time before the next generation starts
        time.sleep(0.5) 
        
# --- Main Program Logic (MODIFIED for Infinite Generation) ---

def main():
    print("--- Infinite Code Generation Mode ---")
    print("This will retreive all Amazon claim codes.")
    print("Press Ctrl+C to stop the process.")
    print("-" * 55)

    # 1. Start the infinite generation task
    generation_thread = threading.Thread(target=infinite_code_generator_task)
    # Allows the program to exit even if this thread is running
    generation_thread.daemon = True 
    generation_thread.start()

    try:
        # Keep the main thread alive indefinitely to allow the background thread to run
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        global stop_generation
        stop_generation = True
        print("\n\n--- Generation stopped by user. ---")
        print(f"Total codes generated this session: {code_count:,}")
        
if __name__ == "__main__":
    main()