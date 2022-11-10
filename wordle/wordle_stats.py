#!/usr/bin/env python3

from collections import Counter
import math
from operator import itemgetter


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
    

def main():
    answers = list(read_wordlist('./wordlist_answers.txt'))
    guesses = list(read_wordlist('./wordlist_guesses.txt')) + answers
    answer_letter_freqs = [get_letter_log_freqs(answers, pos) for pos in [None, *range(0,5)]]
    print_letters_by_answer_frequency(answer_letter_freqs)


if __name__ == "__main__":
    main()
    