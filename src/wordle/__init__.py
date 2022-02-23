__version__ = "0.1.0"

from mimetypes import guess_extension
import sys
import random
from datetime import datetime, date
from typing import Dict, List

from rich import print
from rich.prompt import Prompt, Confirm
import numpy as np

from wordle.player import Player
from wordle.bot import BasicBot
from wordle.util import GuessResult, get_random_word, get_word_by_date, print_game_history_with_results, score_result

import wordle.words as words


# Contstants
MAX_GUESSES = 6


def exit():
    print("Goodbye!")
    # sys.exit(0)


def play_wordle(player: Player):
    guess = ""

    solution = player.start_game(MAX_GUESSES)

    def update_status(message):
        if not player.silent:
            print(message)

    for guess_attempt in range(0, MAX_GUESSES):
        if guess == solution:
            player.game_end(True)
            return True

        while True:
            guess = player.ask_for_word_guess(guess_attempt + 1, f"{guess_attempt+1}/{MAX_GUESSES} ")
            if not guess:
                want_to_exit = Confirm.ask("You didn't enter anything. Do you want to exit?")
                if want_to_exit:
                    return False
            if guess == "exit":
                return False
            if len(guess) != 5:
                print("Error: Your guess must be 5 letters")
                continue
            if guess not in words.selection_words and guess not in words.other_words:
                print("Error: Not a valid word")
                continue
            player.accept_guess_as_valid()
            result = score_result(guess, solution)
            player.report_result(result)
            break

    player.game_end(False)
    return False


def human_player():
    play_wordle(Player())


def bot_single_run():
    play_wordle(BasicBot(["samey", "round"]))


def bot_multi_run():
    # Bot running template
    guesses = []
    results = []

    def did_win(result, guesses_needed):
        guesses.append(guesses_needed)
        results.append(result)

    games_to_play = 100
    bot = BasicBot(["samey", "round"], did_win)  # pirns risps
    for i in range(1, games_to_play + 1):
        play_wordle(bot)
        wins = sum(results)
        print(
            f"{i: 5} / {games_to_play}, wins: {wins} ({wins / (i): 3.2%}), last: {'W' if results[-1] else 'L'} {guesses[-1]}, min: {min(guesses)}, max: {max(guesses)}, avg: {sum(guesses) / len(guesses):.3f}"
        )


guess_result_lookup = {"n": 0, "y": 1, "g": 2}


def possible_words_char(guesses: Dict[str, List[GuessResult]]):
    possible_words(
        {guess: results for (guess, results) in guesses.items()}
    )


def possible_words_int(guesses: Dict[str, List[int]]):
    possible_words({guess: [GuessResult(i) for i in results] for (guess, results) in guesses.items()})


def possible_words(guesses: Dict[str, List[GuessResult]]):
    exact_letters = {}
    misplaced_letters = {}
    wrong_letters = set()
    for guess in guesses:
        result = guesses[guess]
        for index, letter in enumerate(list(guess)):
            if result[index] == GuessResult.RightLetterRightPlace:
                exact_letters[index] = letter
            elif result[index] == GuessResult.WrongLetter:
                wrong_letters.add(letter)
            else:  # GuessResult.RightLetterWrongPlace
                misplaced_letters[index] = letter

    # print(exact_letters)
    # print(misplaced_letters)
    # print(wrong_letters)
    wordle_stats(exact_letters, misplaced_letters, wrong_letters)


def wordle_stats(exact_letters={}, misplaced_letters={}, wrong_letters=[], print_letters=False):
    np_words = np.array([list(word) for word in words.all_words])
    ALPHABET = list("abcdefghijklmnopqrstuvwxyz")
    filtered_list = np_words
    for position in exact_letters:
        filtered_list = filtered_list[(filtered_list[:, position] == exact_letters[position])]
    for position in misplaced_letters:
        letter = misplaced_letters[position]
        filtered_list = filtered_list[(filtered_list[:, position] != letter)]
        filtered_list = filtered_list[
            (filtered_list[:, 0] == letter)
            | (filtered_list[:, 1] == letter)
            | (filtered_list[:, 2] == letter)
            | (filtered_list[:, 3] == letter)
            | (filtered_list[:, 4] == letter)
        ]
    for letter in wrong_letters:
        if letter not in exact_letters.values() and letter not in misplaced_letters.values():
            filtered_list = filtered_list[
                (filtered_list[:, 0] != letter)
                & (filtered_list[:, 1] != letter)
                & (filtered_list[:, 2] != letter)
                & (filtered_list[:, 3] != letter)
                & (filtered_list[:, 4] != letter)
            ]
    possible_word_count = len(filtered_list)
    max_words_to_show = 30
    print(f"{possible_word_count} possible words, showing {max_words_to_show}")
    # Print first 30 words
    possible_words = ["".join(word) for word in filtered_list]
    print(
        f"{possible_words[:min(max_words_to_show, len(possible_words))]}{'...' if len(possible_words) >= max_words_to_show else ''}"
    )

    if print_letters:
        print(" \t1\t2\t3\t4\t5")
        for l in ALPHABET:
            print(l, end="\t")
            for i in range(0, 5):
                print(len(filtered_list[(filtered_list[:, i] == l)]), end="\t")
            print("")

    alphabet_lists = [{}, {}, {}, {}, {}]
    for l in ALPHABET:
        numbers = []
        for i in range(0, 5):
            alphabet_lists[i][l] = len(filtered_list[(filtered_list[:, i] == l)])
            # print(len(filtered_list[(filtered_list[:, i] == l)]), end="\t")

    sorted_lists = []
    for i in range(0, 5):
        sorted_lists.append(sorted(alphabet_lists[i].items(), key=lambda kv: (kv[1], kv[0]), reverse=True))

    if print_letters:
        for i in range(0, len(ALPHABET)):
            for j in range(0, 5):
                letter, value = sorted_lists[j][i]
                print(f"{letter}:{value}", end="\t")
            print("")


def wordle_helper():
    history = {}
    print("Enter your word and then your result")
    print("N = None")
    print("Y = Yellow")
    print("G = Green")
    print("When entering your score, enter 5 letters in a row")
    print("Example: GNNYN")
    while True:
        print_game_history_with_results(history.keys(), 10, list(history.values()))
        guess = input("Tell me the word you guessed [exit/restart]: ").lower().strip()
        if guess == "exit":
            break
        if guess == "restart":
            history = {}
            continue
        if len(guess) != 5 or guess not in words.all_words:
            print("Not a valid word")
            continue

        result = None
        while True:
            result = input("Enter your result (e.g. GYNNY) [cancel]: ").lower().strip()
            if result == "cancel":
                result = None
                break
            if len(result) != 5:
                print("Error: Your result must have 5 indicators")
                continue

            break

        if result == None:
            continue

        history[guess] = [GuessResult(guess_result_lookup[i]) for i in result]
        result = None

        possible_words_char(history)


def print_help_and_exit():
    print("wordle (helper|bot|multibot)")
    exit()


def cli(args=None):
    """Process command line arguments."""

    if not args:
        args = sys.argv[1:]

    if not args:
        human_player()
    else:
        command = args[0]
        if "--help" in args:
            print_help_and_exit()
        elif command == "helper":
            wordle_helper()
        elif command == "bot":
            bot_single_run()
        elif command == "multibot":
            bot_multi_run()
        else:
            print(f"Unknown command: {command}")
            print_help_and_exit()


if __name__ == "__main__":
    play_wordle(Player())
