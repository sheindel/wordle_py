from datetime import date, datetime
import random
from enum import Enum

import dateparser
from rich import print
from rich.prompt import Prompt

from wordle import words


def score_result(guess: str, solution: str):
    # positions_scored = set()
    guess_result = [GuessResult.WrongLetter] * len(guess)
    for index, letter in enumerate(guess):
        if letter == solution[index]:
            guess_result[index] = GuessResult.RightLetterRightPlace
            solution = solution[:index] + "!" + solution[index + 1 :]
            # print(index)
            # print(solution)
            # positions_scored.add(index)
        # elif letter in solution:
        #     guess_result.append(GuessResult.RightLetterWrongPlace)
        # else:
        #     guess_result.append(GuessResult.WrongLetter)

    for index, letter in enumerate(guess):
        if solution[index] != "!":
            if letter in solution:
                guess_result[index] = GuessResult.RightLetterWrongPlace
                correct_index = solution.index(letter)
                # print(correct_index)
                solution = solution[:correct_index] + " " + solution[correct_index + 1 :]
                # print(solution)
            else:
                guess_result[index] = GuessResult.WrongLetter

    return guess_result


def format_colorized_guess(guess, score, include_letters: bool = True):
    result = ""
    for index, letter in enumerate(guess):
        if score[index] == GuessResult.RightLetterRightPlace:
            result += f"[white on #135425 bold]{letter if include_letters else ' '}[/white on #135425 bold]"
        elif score[index] == GuessResult.RightLetterWrongPlace:
            result += f"[black on yellow bold]{letter if include_letters else ' '}[/black on yellow bold]"
        else:
            result += f"[black on grey bold]{letter if include_letters else ' '}[/black on grey bold]"

    return result


def print_game_history(guess_history, max_guesses, solution, include_letters: bool = True, include_guess_count=True):
    print("================")
    for index, guess in enumerate(guess_history):
        score = score_result(guess, solution)
        guess_output = format_colorized_guess(guess, score, include_letters)
        if include_guess_count:
            print(f"{index+1}/{max_guesses} {guess_output}")
        else:
            print(guess_output)


class GuessResult(Enum):
    WrongLetter = 0
    RightLetterWrongPlace = 1
    RightLetterRightPlace = 2


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


def select_date_for_word():
    while True:
        date_string = Prompt.ask("What date do you want to use?")
        try:
            date = dateparser.parse(date_string)
            return get_word_by_date(date.date())
        except:
            # TODO what exceptions to expect
            pass
