#!/usr/bin/env python3

import argparse
from collections import Counter, namedtuple
import colorama
from itertools import combinations
import math
from operator import attrgetter, itemgetter
import os
import sys
import termcolor


ExpectedScore = namedtuple('ExpectedScore', ['word', 'greens', 'yellows', 'total'])


# Global Configuration
ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
ANSWERS_WORDLIST_FILE = 'wordlist_answers.txt'
COLOURED_OUTPUT = True
EXPECTED_GUESS_SCORES_CACHE_FILE = 'expected_guess_scores_cache.txt'
GREEN_MULTIPLIER = 2
LEGAL_GUESSES_WORDLIST_FILE = 'wordlist_guesses.txt'
MAX_DUPLICATE_GUESS_LETTERS = 0
PLANNED_GUESSES = []
PRINTING_BLOCK_SIZE = 5
PRINTING_NUM_WORDS = 15
WORD_LENGTH = 5


def parse_args(argv):
    global COLOURED_OUTPUT, GREEN_MULTIPLIER, MAX_DUPLICATE_GUESS_LETTERS, PLANNED_GUESSES, WORD_LENGTH
    parser = argparse.ArgumentParser(
        prog='wordle_stats',
        description='compute some basic wordle statistics'
    )
    parser.add_argument(
        '-w', '--word-length',
        default=WORD_LENGTH,
        type=int,
        help=f"length of answer and guess words (default = {WORD_LENGTH})",
    )
    parser.add_argument(
        '-d', '--max-duplicates',
        default=MAX_DUPLICATE_GUESS_LETTERS,
        type=int,
        help=f"maximum duplicate letters in guesses (default = {MAX_DUPLICATE_GUESS_LETTERS})",
    )
    parser.add_argument(
        '-x', '--green-multiplier',
        default=float(GREEN_MULTIPLIER),
        type=float,
        help=f"how many yellows a green should count as (default = {float(GREEN_MULTIPLIER) : 0.1f})"
    )
    parser.add_argument(
        '-a', '--only-guess-answers',
        action='store_true',
        help='only use valid answers as guesses',
    )
    parser.add_argument(
        '-C', '--no-colours',
        action='store_true',
        help='do not use coloured output',
    )
    parser.add_argument(
        '-O', '--seek-optimal-guesses',
        action='store_true',
        help='seek for optimal guesses (using the guess letters provided)',
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
    COLOURED_OUTPUT = not args.no_colours
    GREEN_MULTIPLIER = args.green_multiplier
    MAX_DUPLICATE_GUESS_LETTERS = args.max_duplicates
    PLANNED_GUESSES = args.planned_guesses
    WORD_LENGTH = args.word_length
    if COLOURED_OUTPUT:
        colorama.init()
    if PLANNED_GUESSES and len(PLANNED_GUESSES) == 0:
        PLANNED_GUESSES = None    
    return args
    

def coloured(string, *args, **kwargs):
    if COLOURED_OUTPUT:
        return termcolor.colored(string, *args, **kwargs)
    else:
        return string


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
    return ExpectedScore(guess_word, greens / len(answers), yellows / len(answers), (greens + yellows) / len(answers))


def get_all_expected_guess_scores(guesses, answers):
    '''
    Calculate the expected scores of every legal guess.
    
    This calculation can take some time. Once calculated, the scores as saved in a cache file for future use.
    If this cache files is present, the scores will be loaded from it instead of recalculated on subsequent runs.
    '''
    filename = EXPECTED_GUESS_SCORES_CACHE_FILE
    expected_guess_scores = []
    if os.path.exists(filename):
        print(f"Loading expected guess scores from '{filename}' (delete this file to recalculate)")
        with open(filename, 'r') as f:
            for line in f.readlines():
                fields = [f.strip() for f in line.split(',')]
                exp = ExpectedScore(fields[0], float(fields[1]), float(fields[2]), float(fields[3]))
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


def get_weighted_score(guess):
    '''
    Calculate the weighted score for a guess (given it's expected green and yellow scores).
    '''
    return guess.greens * GREEN_MULTIPLIER + guess.yellows


def get_ideal_weighted_guess_scores(expected_guess_scores):
    '''
    Calculate the sequence of 'ideal' guesses that maximize the total weighted score at each step
    and do not repeat letters from previous guesses. All legal guesses are considered.
    '''
    letters_used = set()
    best_guesses = []
    while True:
        top_scores = sorted(
                (guess for guess in expected_guess_scores if len(set(guess.word).intersection(letters_used)) == 0),
                key=get_weighted_score, reverse=True)
        if len(top_scores) == 0:
            break
        best_guesses.append(top_scores[0])
        for letter in top_scores[0].word:
            letters_used.add(letter)
    return best_guesses
    

def seek_optimal_guesses_within_constraints(expected_guess_scores, allowed_letters, limit_guesses_to=None):
    '''
    Try to determine what the optimal guesses would be within the given constraints.
    
    Guesses must use all of the allowed letters, without duplicating letters
    '''
    do_not_warn = False
    if allowed_letters == '':
        allowed_letters = ALPHABET
        do_not_warn = True
    allowed_letters = set(allowed_letters)
    print(coloured(f"\nSeeking optimal guesses using letters " + \
            f"{' '.join(l.upper() for l in sorted(allowed_letters))}", attrs=['bold']))
    if len(allowed_letters) % WORD_LENGTH != 0 and not do_not_warn:
        print(coloured(
                "WARNING: The set of allowed letters is not evenly divisible by the word length",
                'red', attrs=['bold']))
    num_guesses = int(len(allowed_letters) / WORD_LENGTH)

    # filter possible guesses to include only words that use only the required letters and have no duplicates
    possible_guesses = expected_guess_scores
    if limit_guesses_to:
        limit_guesses_to = set(limit_guesses_to)
        possible_guesses = [guess for guess in possible_guesses if guess.word in limit_guesses_to]
    possible_guesses = [guess for guess in possible_guesses
            if len(allowed_letters.intersection(set(guess.word))) == WORD_LENGTH]
    possible_guesses = sorted(possible_guesses, key=get_weighted_score, reverse=True)
    possible_guesses = [(set(g.word), g) for g in possible_guesses] # precompute letter sets for each guess
    print(f"Considering {len(possible_guesses)} possible guesses")

    best_combo_2 = None
    best_score_2 = 0
    letters_used_2 = set()
    best_combo_3 = None
    best_score_3 = 0
    letters_used_3 = set()
    need_line_break = False
    for idx, guess_data_1 in enumerate(possible_guesses):
        set1, guess1 = guess_data_1
        if idx % 10 == 0:
            if need_line_break:
                need_line_break = False
                sys.stdout.write("\n")
            sys.stdout.write(f"{(100 * idx / len(possible_guesses)):0.2f}% ")
            sys.stdout.flush()
        weighted_score_1 = get_weighted_score(guess1)
        for set2, guess2 in possible_guesses:
            if len(set1.intersection(set2)) > 0:
                continue
            weighted_score_2 = get_weighted_score(guess2)
            total_weighted_score_2 = weighted_score_1 + weighted_score_2
            if total_weighted_score_2 > best_score_2:
                best_combo_2 = (guess1, guess2)
                best_score_2 = total_weighted_score_2
                sys.stdout.write(coloured(f"\n{' '.join(g.word for g in best_combo_2)}: " + \
                        f"{total_weighted_score_2:0.6f}", attrs=['bold']))
                sys.stdout.flush()
                need_line_break = True
            
            set12 = set1.union(set2)
            for set3, guess3 in possible_guesses:
                if len(set12.intersection(set3)) > 0:
                    continue
                weighted_score_3 = get_weighted_score(guess3)
                total_weighted_score_3 = weighted_score_1 + weighted_score_2 + weighted_score_3
                if total_weighted_score_3 > best_score_3:
                    best_combo_3 = (guess1, guess2, guess3)
                    best_score_3 = total_weighted_score_3
                    sys.stdout.write(coloured(f"\n{' '.join(g.word for g in best_combo_3)}: " + \
                            f"{total_weighted_score_2:0.6f} -> {total_weighted_score_3:0.6f}", attrs=['bold']))
                    sys.stdout.flush()
                    need_line_break = True
    print('')
    result = best_combo_3 if best_combo_3 is not None else best_combo_2
    if result is None:
        return None
    return [r.word for r in result]


def print_letters_by_frequency(answer_letter_freqs):
    '''
    Display the letters of the alphabet, sorted by frequency of occurrence.
    
    Letter frequencies are displayed for their overall occurrence anywhere in the word,
    and for their occurrence in each specific position in the word.
    '''
    def format_letters_by_frequency(log_freqs, colour, highlight_letters=set(), join_on=" ", block_separator="     "):
        '''
        Format letters into sorted blocks (for display) ordered by frequency, with some letters highlighted.
    
        Highlighted letters are printed in upper case, while non-highlighted letters are printed in lowercase.
        '''
        def get_sorted_letters():
            sorted_letters = [letter for letter, _ in sorted(log_freqs.items(), key=itemgetter(1), reverse=True)]
            return [
                coloured(letter.upper(), colour, attrs=['bold']) if letter in highlight_letters
                        else coloured(letter.lower(), colour)
                for letter in sorted_letters]
        def format_letter_blocks(letters):
            if len(letters) < len(alphabet):
                letters += [' '] * (len(alphabet) - len(letters))
            out = []
            for i in range(0, len(letters), PRINTING_BLOCK_SIZE):
                out.append(join_on.join(letters[slice(i, i + PRINTING_BLOCK_SIZE, 1)]))
            if len(out) == PRINTING_BLOCK_SIZE + 1:
                out[PRINTING_BLOCK_SIZE - 1] += join_on + out[PRINTING_BLOCK_SIZE]
                del(out[PRINTING_BLOCK_SIZE])
            return block_separator.join(out)
        alphabet = set(ALPHABET)
        sorted_letters = format_letter_blocks(get_sorted_letters())
        missing_letters = " ".join(alphabet - set(log_freqs.keys()))
        missing_letters = coloured(f"[ {missing_letters} ]" if len(missing_letters) > 0 else '', 'red')
        return f"{sorted_letters}     {missing_letters}"

    planned_guess_letters = set()
    if PLANNED_GUESSES:
        for guess in PLANNED_GUESSES:
            for letter in guess:
                planned_guess_letters.add(letter)
    print(coloured("\nLetters in answer words, sorted by frequency from most to least " +
            "(letters in planned guesses are capitalized)", attrs=['bold']))
    formatted_letters = format_letters_by_frequency(
            answer_letter_freqs[0], colour='magenta', highlight_letters=planned_guess_letters)
    print(coloured(f"In any position:     {formatted_letters}", 'magenta'))
    for pos in range(1, 6):
        formatted_letters = format_letters_by_frequency(
                answer_letter_freqs[pos], colour='cyan', highlight_letters=planned_guess_letters)
        print(coloured(f"In position {pos}:       {formatted_letters}", 'cyan'))


def print_guesses_with_best_expected_scores(expected_guess_scores, answers, limit_guesses_to=None):
    '''
    Display possible guess words with the best expected scores.
    
    The best guesses are displayed based on words that will produce the most total greens only,
    the most total yellows only, and the most total hits (either yellow or green).
    As well, the best guesses are displayed based on a weighted score
    where each green is counted as more than one yellow.
    '''
    def format_score_summary(*guesses, ideal_weighted_score=None):
        w = sum(get_weighted_score(guess) for guess in guesses)
        g = sum(guess.greens for guess in guesses)
        y = sum(guess.yellows for guess in guesses)
        t = sum(guess.total for guess in guesses)
        weighted_score_diff = f" {w - ideal_weighted_score:0.2f}" if ideal_weighted_score else ''
        return coloured(f"{w:0.2f}{weighted_score_diff}", 'blue', attrs=['bold']) + " | " + \
                coloured(f"{g:0.2f}", 'green') + " + " + \
                coloured(f"{y:0.2f}", 'yellow') + " = " + \
                coloured(f"{t:0.2f}", 'cyan')
    
    # def format_planned_guesses(planned_guesses, count):
    #     formatted_planned_guesses = "' and '".join(PLANNED_GUESSES[0:count+1])
    
    print("")
    # only consider guesses that do not include too many duplicated letters
    possible_guesses = [guess for guess in expected_guess_scores
            if len(set(guess.word)) >= WORD_LENGTH - MAX_DUPLICATE_GUESS_LETTERS]
    # only consider guesses that are within the limited set, if specified
    if limit_guesses_to:
        limit_guesses_to = set(limit_guesses_to)
        possible_guesses = [guess for guess in possible_guesses if guess.word in limit_guesses_to]
    legal_guess_set = set(guess.word for guess in expected_guess_scores)
    print(f"Considering {len(possible_guesses)} possible guesses out of {len(legal_guess_set)} legal guesses")
    
    ideal_guesses = get_ideal_weighted_guess_scores(expected_guess_scores)
    print("Statistically ideal guesses are: '" + "' and '".join(g.word for g in ideal_guesses) + "'")
    
    print(coloured("\nTop scoring initial guesses:", attrs=['bold']))
    most_greens = [guess for guess in sorted(possible_guesses, key=attrgetter('greens'), reverse=True)]
    most_yellows = [guess for guess in sorted(possible_guesses, key=attrgetter('yellows'), reverse=True)]
    most_total = [guess for guess in sorted(possible_guesses, key=attrgetter('total'), reverse=True)]
    top_weighted = [guess for guess in sorted(possible_guesses, key=get_weighted_score, reverse=True)]
    print(f"Most Greens:             ({format_score_summary(most_greens[0])}) " + \
            f"{', '.join(g.word for g in most_greens[0:PRINTING_NUM_WORDS])}")
    print(f"Most Yellows:            ({format_score_summary(most_yellows[0])}) " + \
            f"{', '.join(g.word for g in most_yellows[0:PRINTING_NUM_WORDS])}")
    print(f"Most Total Hits:         ({format_score_summary(most_total[0])}) " + \
            f"{', '.join(g.word for g in most_total[0:PRINTING_NUM_WORDS])}")
    print(coloured(f"Best Weighted Score:", attrs=['underline']) + \
            f"     ({format_score_summary(top_weighted[0])}) " + \
            f"{', '.join(coloured(g.word, attrs=['underline']) for g in top_weighted[0:PRINTING_NUM_WORDS])}")
    
    if PLANNED_GUESSES:
        planned_guess_scores = [get_expected_guess_score(guess, answers) for guess in PLANNED_GUESSES]
        previous_guess_letters = set()
        for i in range(0, len(PLANNED_GUESSES)):
            ideal_weighted_score = sum(get_weighted_score(guess) for guess in ideal_guesses[0:i+1])
            print(ideal_weighted_score)
            next_guess = PLANNED_GUESSES[i]
            previous_guess_letters = previous_guess_letters.union(set(PLANNED_GUESSES[i]))
            most_greens_2 = [guess for guess in most_greens
                    if len(previous_guess_letters.intersection(set(guess.word))) == 0]
            most_yellows_2 = [guess for guess in most_yellows
                    if len(previous_guess_letters.intersection(set(guess.word))) == 0]
            most_total_2 = [guess for guess in most_total
                    if len(previous_guess_letters.intersection(set(guess.word))) == 0]
            top_weighted_2 = [guess for guess in top_weighted
                    if len(previous_guess_letters.intersection(set(guess.word))) == 0]
            formatted_planned_guesses = "' and '".join(PLANNED_GUESSES[0:i+1])
            print(coloured(f"\nTop scoring guesses after '{formatted_planned_guesses}'     ", attrs=['bold']) + \
                    format_score_summary(*planned_guess_scores[0:i+1], ideal_weighted_score=ideal_weighted_score) + ":")
            if len(top_weighted_2) == 0:
                print(coloured("No legal guesses remain that meet the chosen criteria", 'red'))
                break
            if not next_guess in legal_guess_set:
                print(coloured(
                        f"WARNING: planned guess '{next_guess}' is not in the set of legal guesses",
                        'red', attrs=['bold']))
            print(f"Most Greens:             ({format_score_summary(most_greens_2[0])}) " + \
                    f"{', '.join(g.word for g in most_greens_2[0:PRINTING_NUM_WORDS])}")
            print(f"Most Yellows:            ({format_score_summary(most_yellows_2[0])}) " + \
                    f"{', '.join(g.word for g in most_yellows_2[0:PRINTING_NUM_WORDS])}")
            print(f"Most Total Hits:         ({format_score_summary(most_total_2[0])}) " + \
                    f"{', '.join(g.word for g in most_total_2[0:PRINTING_NUM_WORDS])}")
            print(coloured(f"Best Weighted Score:", attrs=['underline']) + \
                    f"     ({format_score_summary(top_weighted_2[0])}) " + \
                    f"{', '.join(coloured(g.word, attrs=['underline']) for g in top_weighted_2[0:PRINTING_NUM_WORDS])}")


def main():
    global PLANNED_GUESSES
    args = parse_args(sys.argv[1:])
    print(coloured(f"Wordle Statistics.", 'green', attrs=['bold']))
    if PLANNED_GUESSES and not args.seek_optimal_guesses:
        print(f"Planned guesses: {' '.join(PLANNED_GUESSES)}")
    
    # load word data
    print(coloured("\nLoading data", attrs=['bold']))
    print("Loading word lists")
    answers = list(read_wordlist(ANSWERS_WORDLIST_FILE))
    guesses = list(read_wordlist(LEGAL_GUESSES_WORDLIST_FILE)) + answers
    expected_guess_scores = get_all_expected_guess_scores(guesses, answers)
    
    # Try to determine what the optimal guesses would be within the given constraints
    if args.seek_optimal_guesses:
        allowed_letters = [letter for word in PLANNED_GUESSES for letter in word] if PLANNED_GUESSES else ALPHABET
        PLANNED_GUESSES = seek_optimal_guesses_within_constraints(
                expected_guess_scores,
                allowed_letters,
                limit_guesses_to=answers if args.only_guess_answers else None)
    
    # compute and print statistics about the answer words
    letter_freqs_in_answers = [get_letter_log_freqs(answers, pos) for pos in [None, *range(0, WORD_LENGTH)]]
    print_letters_by_frequency(letter_freqs_in_answers)
    
    # compute and print statistics about the planned guesses
    print_guesses_with_best_expected_scores(
            expected_guess_scores,
            answers,
            limit_guesses_to=answers if args.only_guess_answers else None)
    

if __name__ == "__main__":
    main()
    