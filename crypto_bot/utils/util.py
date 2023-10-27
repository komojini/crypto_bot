import json
import os
import time 



def get_yes_or_no_input(prompt: str) -> bool:
    """Get yes or no input from the user.

    Args:
        prompt (str): The prompt to display to the user.
    Returns:
        bool: True if the user enters 'y', False if the user enters 'n'.
    """
    while True:
        user_input = input(prompt).strip().lower()
        if user_input == "y":
            return True
        elif user_input == "n":
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")


def repeat_running_until_keyboard_interrupt(
        fn: callable = None,
        interval: float = 1.0,
) -> None:
    """Wait until a keyboard interrupt occurs."""
    
    while True:
        try:
            if fn is not None:
                fn()
            time.sleep(interval)

        except KeyboardInterrupt:
            break
        
        except Exception as e:
            time.sleep(interval)