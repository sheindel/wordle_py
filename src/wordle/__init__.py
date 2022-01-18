__version__ = "0.1.0"

from mimetypes import guess_extension
import sys
import random
from datetime import datetime, date
from typing import List

from rich import print
from rich.prompt import Prompt, Confirm
from wordle.player import Player
from wordle.bot import BasicBot
from wordle.util import GuessResult, get_random_word, get_word_by_date, score_result

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

    guess_history = []
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
            guess_history.append(guess)
            result = score_result(guess, solution)
            player.report_result(result)
            break

    player.game_end(False)
    return False


def cli(args=None):
    """Process command line arguments."""
    guesses = []
    results = []

    def did_win(result, guesses_needed):
        guesses.append(guesses_needed)
        results.append(result)

    # atone starting 500 / 500, wins: 500 ( 100.00%), min: 1, max: 9, avg: 4.458
    # raise starting 500 / 500, wins: 500 ( 100.00%), min: 2, max: 10, avg: 4.398

    play_wordle(Player())
    games_to_play = 1000
    # bot = BasicBot(["raise"], did_win)  # pirns risps
    # for i in range(1, games_to_play + 1):
    #     play_wordle(bot)
    #     wins = sum(results)
    #     # print(
    #     #     f"{i:5} / {games_to_play}, wins: {wins} ({wins / (i): 3.2%}), last: {'W' if results[-1] else 'L'} {guesses[-1]}, min: {min(guesses)}, max: {max(guesses)}, avg: {sum(guesses) / len(guesses):.3f}"
    #     # )
    # print(
    #     f"{i:5} / {games_to_play}, wins: {wins} ({wins / (i): 3.2%}), last: {'W' if results[-1] else 'L'} {guesses[-1]}, min: {min(guesses)}, max: {max(guesses)}, avg: {sum(guesses) / len(guesses):.3f}"
    # )


if __name__ == "__main__":
    play_wordle(Player())
