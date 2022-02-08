import os
from typing import List

from rich import print
from rich.prompt import Prompt

from wordle.util import (
    GuessResult,
    get_random_word,
    get_todays_word,
    format_colorized_guess,
    get_word_index,
    print_game_history,
    select_date_for_word,
)


class Player:
    def __init__(self):
        self.last_guess = None
        self.guess_history = []
        self.result_history = []
        self.silent = False
        self.max_guesses = 0
        self.solution = ""

    def start_game(self, max_guesses):
        self.last_guess = None
        self.guess_history = []
        self.max_guesses = max_guesses
        selections = dict(today=get_todays_word, random=get_random_word, select=select_date_for_word)
        self.word_selection = (
            Prompt.ask("How do you want to select your word?", choices=list(selections.keys()), default="random")
            .strip()
            .lower()
        )

        self.solution = selections[self.word_selection]()

        print("type 'exit' or an empty guess to exit")

        return self.solution

    def ask_for_word_guess(self, attempt, prompt: str = ""):
        self.last_guess = input(prompt).strip().lower()
        return self.last_guess

    def accept_guess_as_valid(self):
        self.guess_history.append(self.last_guess)

    def report_result(self, play_result: List[GuessResult]):
        self.result_history.append(play_result)
        print_game_history(self.guess_history, self.max_guesses, self.solution, header="=========")

    def game_end(self, won):
        if won:
            print(f"You win! Solved in {len(self.guess_history)} guesses")
            print_game_history(
                self.guess_history,
                self.max_guesses,
                self.solution,
                include_letters=False,
                include_guess_count=False,
                use_emoji=True,
                header=f"Wordle {get_word_index(self.solution)} {len(self.guess_history)}/{self.max_guesses}{os.linesep}",
            )
        else:
            print("Sorry, you didn't guess the word.")
            print_game_history(self.guess_history, self.max_guesses, self.solution)
            print_game_history(
                self.guess_history,
                self.max_guesses,
                self.solution,
                include_letters=False,
                include_guess_count=False,
                use_emoji=True,
                header=f"Solution: {self.solution}{os.linesep}Wordle {get_word_index(self.solution)} X/{self.max_guesses}{os.linesep}",
            )
