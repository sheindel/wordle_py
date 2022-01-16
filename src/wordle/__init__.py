__version__ = "0.1.0"

import sys
import random
from datetime import datetime, date

import dateparser
from rich import print
from rich.prompt import Prompt, Confirm

import wordle.words as words


def get_random_word():
    return random.choice(words.selection_words)


def get_word_by_date(chosen_date: date):
    start_date = datetime(2021, 6, 19)  # magic start date from app

    # TODO is there a better way to do this?
    chosen_date = datetime(chosen_date.year, chosen_date.month, chosen_date.day)

    # Multiply by 1000 to match JS timestamp
    start_timestamp = (chosen_date.timestamp() - start_date.timestamp()) * 1000

    # integer division by magic number
    index = round(start_timestamp // 864e5)
    return words.selection_words[index % len(words.selection_words)]


def get_todays_word() -> str:
    return get_word_by_date(datetime.now().date())


def exit():
    print("Goodbye!")
    sys.exit(0)


def get_colored_guess(solution, guess, include_letters: bool = True):
    result = ""
    for index, letter in enumerate(guess):
        if letter == solution[index]:
            result += f"[black on #135425 bold]{letter if include_letters else ' '}[/black on #135425 bold]"
        elif letter in solution:
            result += f"[black on yellow bold]{letter if include_letters else ' '}[/black on yellow bold]"
        else:
            result += f"[black on grey bold]{letter if include_letters else ' '}[/black on grey bold]"

    return result


def select_date_for_word():
    while True:
        date_string = Prompt.ask("What date do you want to use?")
        try:
            date = dateparser.parse(date_string)
            return get_word_by_date(date.date())
        except:
            # TODO what exceptions to expect
            pass


def main():
    MAX_GUESSES = 6
    guess = ""

    selections = dict(Today=get_todays_word, Random=get_random_word, Select=select_date_for_word)
    word_selection = Prompt.ask(
        "How do you want to select your word?", choices=list(selections.keys()), default="Today"
    )

    solution = selections[word_selection]()

    print("type 'exit' or an empty guess to exit")

    guess_history = []
    for guess_attempt in range(0, MAX_GUESSES):
        if guess == solution:
            print(f"You win! Solved in {guess_attempt} guesses")
            for index, guess in enumerate(guess_history):
                print(f"{index+1}/{MAX_GUESSES} {get_colored_guess(solution, guess, False)}")
            exit()

        print(f"Guess {guess_attempt+1} out of {MAX_GUESSES}")

        while True:
            guess = Prompt.ask("Enter your guess").strip().lower()
            if not guess:
                want_to_exit = Confirm.ask("You didn't enter anything. Do you want to exit?")
                if want_to_exit:
                    exit()
            if guess == "exit":
                exit()
            if len(guess) != 5:
                print("Error: Your guess must be 5 letters")
                continue
            if guess not in words.selection_words and guess not in words.other_words:
                print("Error: Not a valid word")
                continue
            guess_history.append(guess)
            print(get_colored_guess(solution, guess))
            break

    print("Sorry, you didn't guess the word.")
    for index, guess in enumerate(guess_history):
        print(f"{index+1}/{MAX_GUESSES} {get_colored_guess(solution, guess)}")
    print(f"Ans {get_colored_guess(solution, solution)}")
    exit()


def cli(args=None):
    """Process command line arguments."""
    main()


if __name__ == "__main__":
    main()
