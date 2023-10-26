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


def wait_until_keyboard_interrupt() -> None:
    """Wait until a keyboard interrupt occurs."""
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass