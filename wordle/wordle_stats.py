#!/usr/bin/env python3

from collections import Counter, namedtuple
import math
from operator import attrgetter, itemgetter
import os
import sys


ScoreExpectation = namedtuple('ScoreExpectation', ['guess_word', 'greens', 'yellows', 'total'])



def read_wordlist(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        return (word.strip() for line in lines for word in line.split(',') if len(word.strip()) > 0)
    
def get_letter_log_freqs(words, position=None):
    counts = Counter(
        letter for word in words for pos, letter in enumerate(word)
        if pos == position or position == None
    )
    log_total = math.log(sum(counts.values()))
    return {letter: math.log(count) - log_total for letter, count in counts.items()}
    

def format_letters_by_freq(log_freqs, b=5):    
    def get_sorted_letters():
        return [letter for letter, _ in sorted(log_freqs.items(), key=itemgetter(1), reverse=True)]
    def format_letter_blocks(letters, join_on=" ", separator="     "):
        out = []
        for i in range(0, len(letters), b):
            out.append(join_on.join(letters[slice(i, i+b, 1)]))
        if len(out) == 6:
            out[4] += join_on + out[5]
            del(out[5])
        return separator.join(out)
    alphabet = set([*'abcdefghijklmnopqrstuvwxyz'])
    sorted_letters = format_letter_blocks(get_sorted_letters())
    missing_letters = " ".join(alphabet - set(log_freqs.keys()))
    missing_letters = f"[ {missing_letters} ]" if len(missing_letters) > 0 else ''
    return f"{sorted_letters:71} {missing_letters}"


def print_letters_by_answer_frequency(answer_letter_freqs):
    print("\nLetters in answer words, sorted by frequency from most to least")
    print(f"In any position:     {format_letters_by_freq(answer_letter_freqs[0])}")
    for pos in range(1, 6):
        print(f"In position {pos}:       {format_letters_by_freq(answer_letter_freqs[pos])}")


def score_guess(guess_word, answer_word):
    guess_word = list(guess_word)
    answer_word = list(answer_word)
    result = ['.'] * 5
    # first pass, look for greens
    for i in range(0, 5):
        if guess_word[i] == answer_word[i]:
            result[i] = 'G'
            guess_word[i] = None
            answer_word[i] = None
    # second pass, look for yellows
    answer_letter_counts = Counter(answer_word)
    del(answer_letter_counts[None])
    for i in range(0, 5):
        if answer_letter_counts[guess_word[i]] > 0:
            answer_letter_counts[guess_word[i]] -= 1
            result[i] = 'y'
    return ''.join(result)


def get_score_expectation(guess_word, answers):
    greens = 0
    yellows = 0
    for answer_word in answers:
        score = Counter(score_guess(guess_word, answer_word))
        greens += score['G']
        yellows += score['y']
    return ScoreExpectation(guess_word, greens / len(answers), yellows / len(answers), (greens + yellows) / len(answers))


def get_all_score_expectations(guesses, answers):
    expected_guess_scores = []
    if os.path.exists('expected_guess_scores.txt'):
        print("\nLoading expected guess scores")
        with open('expected_guess_scores.txt', 'r') as f:
            for line in f.readlines():
                fields = [f.strip() for f in line.split(',')]
                exp = ScoreExpectation(fields[0], float(fields[1]), float(fields[2]), float(fields[3]))
                expected_guess_scores.append(exp)
    else:
        with open('expected_guess_scores.txt', 'w') as out:
            print("\nCalculating expected guess scores")
            for idx, guess_word in enumerate(guesses):
                if idx % 100 == 0:
                    sys.stdout.write(f"{idx} ")
                    sys.stdout.flush()
                exp = get_score_expectation(guess_word, answers)
                out.write(f"{exp.guess_word}, {exp.greens}, {exp.yellows}, {exp.total}\n")
                expected_guess_scores.append(exp)
    return expected_guess_scores


def print_best_score_expectations(score_expectations):
    print("\nTop scoring initial guesses:")
    most_greens = [guess.guess_word for guess in sorted(score_expectations, key=attrgetter('greens'), reverse=True)]
    most_yellows = [guess.guess_word for guess in sorted(score_expectations, key=attrgetter('yellows'), reverse=True)]
    most_total = [guess.guess_word for guess in sorted(score_expectations, key=attrgetter('total'), reverse=True)]
    print(f"Most Greens:         {', '.join(most_greens[0:15])}")
    print(f"Most Yellows:        {', '.join(most_yellows[0:15])}")
    print(f"Most Total Hits:     {', '.join(most_total[0:15])}")
    
    first_word = 'orate'
    first_word_letters = set(first_word)
    most_greens_2 = [word for word in most_greens if len(first_word_letters.intersection(set(word))) == 0]
    most_yellows_2 = [word for word in most_yellows if len(first_word_letters.intersection(set(word))) == 0]
    most_total_2 = [word for word in most_total if len(first_word_letters.intersection(set(word))) == 0]
    print(f"\nSecond guess, after '{first_word}'")
    print(f"Most Greens 2:       {', '.join(most_greens_2[0:15])}")
    print(f"Most Yellows 2:      {', '.join(most_yellows_2[0:15])}")
    print(f"Most Total Hits 2:   {', '.join(most_total_2[0:15])}")


    second_word = 'sling'
    second_word_letters = set(first_word).union(set(second_word))
    most_greens_3 = [word for word in most_greens if len(second_word_letters.intersection(set(word))) == 0]
    most_yellows_3 = [word for word in most_yellows if len(second_word_letters.intersection(set(word))) == 0]
    most_total_3 = [word for word in most_total if len(second_word_letters.intersection(set(word))) == 0]
    print(f"\nThird guess, after '{first_word}' and '{second_word}'")
    print(f"Most Greens 3:       {', '.join(most_greens_3[0:15])}")
    print(f"Most Yellows 3:      {', '.join(most_yellows_3[0:15])}")
    print(f"Most Total Hits 3:   {', '.join(most_total_3[0:15])}")
    
    

def main():
    answers = list(read_wordlist('wordlist_answers.txt'))
    guesses = list(read_wordlist('wordlist_guesses.txt')) + answers
    answer_letter_freqs = [get_letter_log_freqs(answers, pos) for pos in [None, *range(0,5)]]
    print_letters_by_answer_frequency(answer_letter_freqs)
    
    
    score_expectations = get_all_score_expectations(guesses, answers)
    print_best_score_expectations(score_expectations)
    
    # expected_guess_scores = [get_score_expectation(guess_word, answers) for guess_word in guesses[0:10]]
    # guess = expected_guess_scores[2]
    # print(f"{guess.guess_word}, {guess.greens}, {guess.yellows}, {guess.total}")
    # # print_best_score_expectations(score_expectations)
    

if __name__ == "__main__":
    main()
    