#!/usr/bin/env python3

import argparse
from collections import Counter, namedtuple
import math
from operator import attrgetter, itemgetter
import os
import sys


ScoreExpectation = namedtuple('ScoreExpectation', ['word', 'greens', 'yellows', 'total'])


# Global Configuration
ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
ANSWERS_WORDLIST_FILE = 'wordlist_answers.txt'
EXPECTED_GUESS_SCORES_CACHE_FILE = 'expected_guess_scores_cache.txt'
LEGAL_GUESSES_WORDLIST_FILE = 'wordlist_guesses.txt'
MAX_DUPLICATE_GUESS_LETTERS = 0
PLANNED_GUESSES = []
PRINTING_BLOCK_SIZE = 5
PRINTING_NUM_WORDS = 15
WORD_LENGTH = 5


def parse_args(argv):
    global WORD_LENGTH, MAX_DUPLICATE_GUESS_LETTERS, PLANNED_GUESSES
    parser = argparse.ArgumentParser(
        prog='wordle_stats',
        description='compute some basic wordle statistics'
    )
    parser.add_argument(
        '-w', '--word-length',
        default=WORD_LENGTH,
        type=int,
        help="length of answer and guess words (default = 5)",
    )
    parser.add_argument(
        '-d', '--max-duplicates',
        default=MAX_DUPLICATE_GUESS_LETTERS,
        type=int,
        help="maximum duplicate letters in guesses (default = 0)",
    )
    planned_guesses_string = "'" + "', '".join(PLANNED_GUESSES or []) + "'"
    parser.add_argument(
        'planned_guesses',
        action='store',
        type=str,
        nargs='*',
        help="possible guesses to evaluate " +
                (f"(default = {planned_guesses_string})" if PLANNED_GUESSES and len(PLANNED_GUESSES) > 0 else '')
    )
    args = parser.parse_args(argv)
    WORD_LENGTH = args.word_length
    MAX_DUPLICATE_GUESS_LETTERS = args.max_duplicates
    PLANNED_GUESSES = args.planned_guesses
    if PLANNED_GUESSES and len(PLANNED_GUESSES) == 0:
        PLANNED_GUESSES = None


def read_wordlist(filename):
    '''
    Read words from a file.
    
    Blank lines are skipped, and multiple words per line are allowed, separated by commas.
    Only words of length WORD_LENGTH will be returned. All letters will be converted to lower case.
    '''
    with open(filename, 'r') as f:
        lines = f.readlines()
        return (word.strip().lower() for line in lines for word in line.split(',') if len(word.strip()) == WORD_LENGTH)


def get_letter_log_freqs(words, position=None):
    '''
    Calculate the log frequency of letters in the list of words,
        either in any position, or in a specific position within the word.
    
    Duplicate words are ignored and will not effect the calculation of letter frequencies.
    '''
    counts = Counter(
        letter for word in set(words) for pos, letter in enumerate(word)
        if pos == position or position == None
    )
    log_total = math.log(sum(counts.values()))
    return {letter: math.log(count) - log_total for letter, count in counts.items()}


def get_specific_guess_score(guess_word, answer_word):
    '''
    Calculate the score for a guess word relative to an answer word.
    
    A score consists of the number of green tiles, the number of yellow tiles,
    and the total number of green and yellow tiles that the guess would receive
    (independent of position).
    '''
    guess_word = list(guess_word)
    answer_word = list(answer_word)
    result = ['.'] * WORD_LENGTH
    # first pass, look for greens
    for i in range(0, WORD_LENGTH):
        if guess_word[i] == answer_word[i]:
            result[i] = 'G'
            guess_word[i] = None
            answer_word[i] = None
    # second pass, look for yellows
    answer_letter_counts = Counter(answer_word)
    del(answer_letter_counts[None])
    for i in range(0, WORD_LENGTH):
        if answer_letter_counts[guess_word[i]] > 0:
            answer_letter_counts[guess_word[i]] -= 1
            result[i] = 'y'
    return ''.join(result)


def get_expected_guess_score(guess_word, answers):
    '''
    Calculate the expected score of a guess word relative to all the possible answer words.
    '''
    greens = 0
    yellows = 0
    for answer_word in answers:
        score = Counter(get_specific_guess_score(guess_word, answer_word))
        greens += score['G']
        yellows += score['y']
    return ScoreExpectation(guess_word, greens / len(answers), yellows / len(answers), (greens + yellows) / len(answers))


def get_all_expected_guess_scores(guesses, answers):
    filename = EXPECTED_GUESS_SCORES_CACHE_FILE
    expected_guess_scores = []
    if os.path.exists(filename):
        print(f"Loading expected guess scores from '{filename}' (delete this file to recalculate)")
        with open(filename, 'r') as f:
            for line in f.readlines():
                fields = [f.strip() for f in line.split(',')]
                exp = ScoreExpectation(fields[0], float(fields[1]), float(fields[2]), float(fields[3]))
                expected_guess_scores.append(exp)
    else:
        with open(filename + '~', 'w') as out:
            print(f"Calculating expected guess scores (saving to '{filename}')")
            one_percent = int(len(guesses) / 100)
            for idx, guess_word in enumerate(guesses):
                if idx % one_percent == 0:
                    sys.stdout.write(f"{int(idx / one_percent)}% ")
                    sys.stdout.flush()
                exp = get_expected_guess_score(guess_word, answers)
                out.write(f"{exp.word}, {exp.greens}, {exp.yellows}, {exp.total}\n")
                expected_guess_scores.append(exp)
        os.rename(filename + '~', filename)
    return expected_guess_scores


def print_letters_by_frequency(answer_letter_freqs):
    '''
    ...
    '''
    def format_letters_by_frequency(log_freqs, highlight_letters=set(), join_on=" ", block_separator="     "):
        '''
        Format letters into sorted blocks (for display) ordered by frequency, with some letters highlighted.
    
        Highlighted letters are printed in upper case, while non-highlighted letters are printed in lowercase.
        '''
        def get_sorted_letters():
            sorted_letters = [letter for letter, _ in sorted(log_freqs.items(), key=itemgetter(1), reverse=True)]
            return [letter.upper() if letter in highlight_letters else letter.lower() for letter in sorted_letters]
        def format_letter_blocks(letters):
            out = []
            for i in range(0, len(letters), PRINTING_BLOCK_SIZE):
                out.append(join_on.join(letters[slice(i, i + PRINTING_BLOCK_SIZE, 1)]))
            if len(out) == PRINTING_BLOCK_SIZE + 1:
                out[PRINTING_BLOCK_SIZE - 1] += join_on + out[PRINTING_BLOCK_SIZE]
                del(out[PRINTING_BLOCK_SIZE])
            return block_separator.join(out)
        alphabet = set([*ALPHABET])
        sorted_letters = format_letter_blocks(get_sorted_letters())
        missing_letters = " ".join(alphabet - set(log_freqs.keys()))
        missing_letters = f"[ {missing_letters} ]" if len(missing_letters) > 0 else ''
        return f"{sorted_letters:71} {missing_letters}"

    planned_guess_letters = set()
    if PLANNED_GUESSES:
        for guess in PLANNED_GUESSES:
            for letter in guess:
                planned_guess_letters.add(letter)
    print("\nLetters in answer words, sorted by frequency from most to least (letters in planned guesses are capitalized)")
    formatted_letters = format_letters_by_frequency(answer_letter_freqs[0], highlight_letters=planned_guess_letters)
    print(f"In any position:     {formatted_letters}")
    for pos in range(1, 6):
        formatted_letters_by_freq = format_letters_by_frequency(
                answer_letter_freqs[pos], highlight_letters=planned_guess_letters)
        print(f"In position {pos}:       {formatted_letters}")


def print_guesses_with_best_expected_scores(possible_guesses):
    print("")
    # only consider guesses that do not include duplicated letters
    possible_guesses = [guess for guess in possible_guesses if len(set(guess.word)) == WORD_LENGTH]
    
    print("Top scoring initial guesses:")
    most_greens = [guess.word for guess in sorted(possible_guesses, key=attrgetter('greens'), reverse=True)]
    most_yellows = [guess.word for guess in sorted(possible_guesses, key=attrgetter('yellows'), reverse=True)]
    most_total = [guess.word for guess in sorted(possible_guesses, key=attrgetter('total'), reverse=True)]
    print(f"Most Greens:         ({'score'}) {', '.join(most_greens[0:PRINTING_NUM_WORDS])}")
    print(f"Most Yellows:        {', '.join(most_yellows[0:PRINTING_NUM_WORDS])}")
    print(f"Most Total Hits:     {', '.join(most_total[0:PRINTING_NUM_WORDS])}")
    
    if PLANNED_GUESSES:
        previous_guess_letters = set()
        for i in range(0, min(2, len(PLANNED_GUESSES))):
            previous_guess_letters = previous_guess_letters.union(set(PLANNED_GUESSES[i]))
            most_greens_2 = [word for word in most_greens if len(previous_guess_letters.intersection(set(word))) == 0]
            most_yellows_2 = [word for word in most_yellows if len(previous_guess_letters.intersection(set(word))) == 0]
            most_total_2 = [word for word in most_total if len(previous_guess_letters.intersection(set(word))) == 0]
            formatted_planned_guesses = "' and '".join(PLANNED_GUESSES[0:i+1])
            print(f"\nTop scoring guesses after '{formatted_planned_guesses}'")
            print(f"Most Greens:         {', '.join(most_greens_2[0:PRINTING_NUM_WORDS])}")
            print(f"Most Yellows:        {', '.join(most_yellows_2[0:PRINTING_NUM_WORDS])}")
            print(f"Most Total Hits:     {', '.join(most_total_2[0:PRINTING_NUM_WORDS])}")


def main():
    parse_args(sys.argv[1:])
    print(f"Some Wordle Statistics.")
    if PLANNED_GUESSES:
        print(f"Planned guesses: {' '.join(PLANNED_GUESSES)}")
    
    # load word data
    print("\nLoading word lists")
    answers = list(read_wordlist(ANSWERS_WORDLIST_FILE))
    guesses = list(read_wordlist(LEGAL_GUESSES_WORDLIST_FILE)) + answers
    expected_guess_scores = get_all_expected_guess_scores(guesses, answers)
    
    # compute and print statistics
    letter_freqs_in_answers = [get_letter_log_freqs(answers, pos) for pos in [None, *range(0, WORD_LENGTH)]]
    print_letters_by_frequency(letter_freqs_in_answers)
    print_guesses_with_best_expected_scores(expected_guess_scores)
    

if __name__ == "__main__":
    main()
    