import random
from typing import List
import itertools

from rich import print
import numpy as np

from wordle.player import Player
from wordle.util import (
    ALPHABET,
    GuessResult,
    format_colorized_guess,
    get_letter_occurrences,
    get_networked_weight,
    get_random_word,
    score_result,
    weight_words_not_guessed,
)
import wordle.words as words


class BasicBot(Player):
    def __init__(self, starting_words, supervisor=None):
        self.all_words = words.selection_words + words.other_words
        self.np_all_words = np.array([list(word) for word in self.all_words])
        self.char_lists = [list(word) for word in self.all_words]
        self.lookup_lists = list(zip(*self.char_lists))
        self.silent = True
        self.max_guesses = 0
        self.supervisor = supervisor
        self.starting_words = starting_words
        self.reset_bot_state()

    def reset_bot_state(self):
        self.last_guess = []
        self.ignore_mask = [False] * len(self.all_words)
        self.guess_history = []
        self.result_history: List[List[GuessResult]] = []
        self.solution = ""

    def start_game(self, max_guesses):
        self.reset_bot_state()
        self.max_guesses = max_guesses

        self.solution = get_random_word()
        # print(f"Solution: {self.solution}")
        return self.solution

    def ask_for_word_guess(self, guess_number: int, prompt: str = ""):
        if guess_number <= len(self.starting_words):
            self.last_guess = self.starting_words[guess_number - 1]
        # elif guess_number == len(self.starting_words) + 1:
        #     word_list = self.get_possible_words()
        #     word_char_weights = self.get_not_guessed_word_weight(word_list)
        #     weights = word_char_weights.values()
        #     self.last_guess = list(word_char_weights.keys())[list(weights).index(max(weights))]
        else:
            first_non_starting_guess = guess_number == len(self.starting_words) + 1
            word_list = self.get_possible_words()
            # print(word_list)

            char_list = get_letter_occurrences(word_list)
            # self.last_guess = weight_words_not_guessed(word_list)[0]
            word_char_weights = weight_words_not_guessed(word_list, True)
            highest_word, highest_weight = next(iter(word_char_weights.items()))
            # print(highest_word)
            # print(highest_weight)
            # 500   500 / 500, wins: 500 ( 100.00%), last: W 3, min: 2, max: 10, avg: 4.468
            # 1000  500 / 500, wins: 499 ( 99.80%), last: W 4, min: 2, max: 11, avg: 4.468
            # 50    500 / 500, wins: 500 ( 100.00%), last: W 6, min: 2, max: 8, avg: 4.408
            # 40    500 / 500, wins: 499 ( 99.80%), last: W 4, min: 2, max: 11, avg: 4.392
            # 30,

            # Word vs Char strategy
            # Word: 500 / 500, wins: 499 ( 99.80%), last: W 4, min: 2, max: 11, avg: 4.490
            # Char: 500 / 500, wins: 500 ( 100.00%), last: W 3, min: 2, max: 10, avg: 4.824
            if first_non_starting_guess and highest_weight >= 200:
                # print(highest_weight)
                # print(highest_word)
                # print(highest_weight)
                self.last_guess = highest_word
                # print(f"Highest score {self.last_guess} = {max(weights)}")
            else:
                # Word network weight strategy
                word_weights = get_networked_weight(word_list)
                weights = word_weights.values()
                self.last_guess = list(word_weights.keys())[list(weights).index(max(weights))]

            # Character weight strategy
            ## char_list = self.get_letter_occurrences(word_list)
            # self.last_guess = self.choose_word_with_letter_preference(word_list, char_list)
            # self.last_guess = random.choice(self.get_possible_words())

        # print(format_colorized_guess(self.last_guess, score_result(self.last_guess, self.solution)))

        # Player class adds to guess_history now
        # self.guess_history.append(self.last_guess)
        return self.last_guess

    def choose_word_with_letter_preference(self, word_list, char_list: dict[str, int]):
        top_letter_count = max(char_list.values())
        for letter in char_list:
            if char_list[letter] == top_letter_count:
                for word in word_list:
                    if letter in word:
                        return word

    def get_possible_words(self) -> List[str]:
        word_pairs = sorted(zip(self.ignore_mask, self.all_words))
        result = list(zip(*word_pairs[: len(self.all_words) - sum(self.ignore_mask)]))[1]
        return result

    def report_result(self, play_result: List[GuessResult]):
        self.result_history.append(play_result)
        known_positions = set()
        # Round one: Determine all definitively known positions from all guesses
        for guess_result in self.result_history:
            for result_index, result in enumerate(guess_result):
                if result == GuessResult.RightLetterRightPlace:
                    known_positions.add(result_index)

        # Round two
        for guess_index, result in enumerate(play_result):
            # Eliminate words that have a character which isn't in the puzzle
            # Beware: If our guess has duplicate letters, this can be misleading
            guess_letter = self.last_guess[guess_index]
            character_guess_count = self.last_guess.count(guess_letter)

            if result == GuessResult.WrongLetter:
                if character_guess_count > 1:
                    # Confirm that all are grey
                    # If not, then we know occurrences of this letter are limited
                    # to non-grey results
                    # print("Uh oh")

                    pass
                else:
                    indexes = [index for index, word in enumerate(self.all_words) if guess_letter in word]
                    for index in indexes:
                        self.ignore_mask[index] = True

            # Eliminate any words that don't have the maybe place characters
            if result == GuessResult.RightLetterWrongPlace:
                # print("Right letter, wrong place")
                lookup_list = self.lookup_lists[guess_index]
                indexes = [index for index, character in enumerate(lookup_list) if character == guess_letter]
                for index in indexes:
                    self.ignore_mask[index] = True
                # print(f"1 Eliminated {len(indexes)} words")

                indexes = [
                    index
                    for index, word in enumerate(self.all_words)
                    if guess_letter not in word
                    or (
                        character_guess_count == 1
                        and guess_letter in word
                        and word.index(guess_letter) in known_positions
                    )
                ]

                for index in indexes:
                    self.ignore_mask[index] = True

            # Eliminate words that don't have our exact letter in the right place
            if result == GuessResult.RightLetterRightPlace:
                # print("Right letter, right place")
                lookup_list = self.lookup_lists[guess_index]
                indexes = [index for index, character in enumerate(lookup_list) if character != guess_letter]
                for index in indexes:
                    self.ignore_mask[index] = True
                # print(f"3 Eliminated {len(indexes)} words")

        # print(self.get_letters_guessed())
        # print(self.get_letters_not_guessed())
        # print(f"{len(self.all_words) - sum(self.ignore_mask)} eligible words remain")
        # print(self.get_letter_occurrences(self.get_possible_words()))

    def game_end(self, won):

        if self.supervisor:
            self.supervisor(won, len(self.guess_history))
        else:
            if won:
                print(
                    f":smile: Bot got the word {format_colorized_guess(self.solution, [GuessResult.RightLetterRightPlace] * 5)} in {len(self.guess_history)} guesses"
                )
            else:
                print(
                    f":slightly_frowning_face: Bot lost, answer was {format_colorized_guess(self.solution, [GuessResult.RightLetterRightPlace] * 5)} in {len(self.guess_history)}"
                )
