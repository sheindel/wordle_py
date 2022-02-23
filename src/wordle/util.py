from datetime import date, datetime
import itertools
import random
from enum import Enum
from typing import Iterable, List

import dateparser
from rich import print
from rich.console import Console
from rich.prompt import Prompt

from wordle import words


ALPHABET = set("abcdefghijklmnopqrstuvwxyz")


def score_result(guess: str, solution: str):
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


large_yellow_square = "\U0001F7E8"
large_green_square = "\U0001F7E9"
large_black_square = "\U00002B1B"


def format_colorized_guess(guess, score, include_letters: bool = True, use_emoji: bool = False):
    result = ""
    for index, letter in enumerate(guess):
        if score[index] == GuessResult.RightLetterRightPlace:
            result += (
                large_green_square
                if use_emoji
                else f"[white on #135425 bold]{letter if include_letters else ' '}[/white on #135425 bold]"
            )
        elif score[index] == GuessResult.RightLetterWrongPlace:
            result += (
                large_yellow_square
                if use_emoji
                else f"[black on yellow bold]{letter if include_letters else ' '}[/black on yellow bold]"
            )
        else:
            result += (
                large_black_square
                if use_emoji
                else f"[black on grey bold]{letter if include_letters else ' '}[/black on grey bold]"
            )

    return result


def print_game_history(
    guess_history, max_guesses, solution, include_letters: bool = True, include_guess_count=True, use_emoji: bool = False, header: str = None
):
    results = []
    for guess in guess_history:
        results.append(score_result(guess, solution))
    
    print_game_history_with_results(guess_history, max_guesses, results, include_letters, include_guess_count, use_emoji, header)
        


def print_game_history_with_results(
    guess_history, max_guesses, results, include_letters: bool = True, include_guess_count=True, use_emoji: bool = False, header: str = None
):
    if header:
        print(header)
    for index, guess in enumerate(guess_history):
        score = results[index]
        guess_output = format_colorized_guess(guess, score, include_letters, use_emoji=use_emoji)
        if include_guess_count:
            print(f"{index+1}/{max_guesses} {guess_output}")
        else:
            print(guess_output)

# Word/character weighting functions

# This gets the letters used in the word list. if given the list of words
# guessed, a user can be given a visual of what they've covered. Otherwise,
# it is used for a bot to determine what letters haven't been guessed with
# the inverse flag
def get_letter_list(word_list: List[str], reduce=False, weight=False) -> Iterable[str]:
    if weight and not reduce:
        print("Warning: incompatible options (weight and not reduce). Forcing reduce")
        reduce = True

    full_char_list = [list(word) for word in word_list]
    full_char_list = list(itertools.chain(*full_char_list))
    char_list = full_char_list

    # Force reduce first if requested
    if reduce:
        char_list = set(char_list)

    if weight:
        return {character: full_char_list.count(character) for character in char_list}

    return char_list


def sort_dict_by_value(dictionary: dict, reverse=False):
    return {k: v for k, v in sorted(dictionary.items(), key=lambda item: item[1], reverse=reverse)}


def weight_words_not_guessed(word_list, discovery=False):
    not_guessed_weighted_letters: dict[str, int] = get_letter_list(word_list, reduce=True, weight=True)
    # print(not_guessed_weighted_letters)

    weight_word = lambda word: sum(
        not_guessed_weighted_letters.get(char, 0) for char in word if (not discovery or len(set(word)) == 5)
    )
    word_weights = {word: weight_word(word) for word in word_list}
    # print(word_weights)
    return sort_dict_by_value(word_weights, True)


def get_networked_weight(word_list):
    weights = dict(zip(word_list, [0] * len(word_list)))
    for word in word_list:
        for char in list(word):
            for word in word_list:
                if char in word:
                    weights[word] += 1

    return weights


def get_character_lists(word_list: List[str], flatten=False):
    char_lists = [list(word) for word in word_list]
    if flatten:
        return list(itertools.chain(*char_lists))
    else:
        return char_lists


def get_letter_occurrences(word_list: List[str]):
    result = dict(zip(ALPHABET, [0] * len(ALPHABET)))
    char_lists = [list(word) for word in word_list]
    flat_chars = list(itertools.chain(*char_lists))
    for char in ALPHABET:
        result[char] = flat_chars.count(char)

    return result


class GuessResult(Enum):
    WrongLetter = 0
    RightLetterWrongPlace = 1
    RightLetterRightPlace = 2


def get_random_word():
    return random.choice(words.selection_words)


def get_word_index_by_date(chosen_date: date) -> int:
    start_date = datetime(2021, 6, 19)  # magic start date from app

    # TODO is there a better way to do this?
    chosen_date = datetime(chosen_date.year, chosen_date.month, chosen_date.day)

    # Multiply by 1000 to match JS timestamp
    start_timestamp = (chosen_date.timestamp() - start_date.timestamp()) * 1000

    # integer division by magic number
    index = round(start_timestamp // 864e5)

    return index % len(words.selection_words)


def get_word_by_date(chosen_date: date) -> str:
    return words.selection_words[get_word_index_by_date(chosen_date)]


def get_word_index(word: str) -> int:
    return words.selection_words.index(word)


def get_todays_word() -> str:
    return get_word_by_date(datetime.now().date())


def get_todays_index() -> int:
    return get_word_index_by_date(datetime.now().date())


def select_date_for_word():
    while True:
        date_string = Prompt.ask("What date do you want to use?")
        try:
            date = dateparser.parse(date_string)
            return get_word_by_date(date.date())
        except:
            # TODO what exceptions to expect
            pass
