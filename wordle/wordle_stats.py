#!/usr/bin/env python3

from collections import Counter
from operator import itemgetter


def read_wordlist():
    with open('./wordlist.txt', 'r') as f:
        lines = f.readlines()
        return (word.strip() for line in lines for word in line.split(',') if len(word.strip()) > 0)
            
def get_letters(words):
    return ((letter, position) for word in words for position, letter in enumerate(word))

def get_letter_counts(letters):
    overall = Counter(letter[0] for letter in letters)
    by_position = [
        Counter(letter[0] for letter in letters if letter[1] == pos)
        for pos in range(0,5)
    ]
    return [overall] + by_position

def print_letter_counts(letter_counts):
    def get_sorted_letters(counts):
        return [letter[0] for letter in sorted(counts.items(), key=itemgetter(1), reverse=True)]
    print("Overall: %s" % ' '.join(get_sorted_letters(letter_counts[0])))
    for pos in range(1, 6):
        print("Pos %d: %s" % (pos, ' '.join(get_sorted_letters(letter_counts[pos]))))

def main():
    words = list(read_wordlist())
    letters = list(get_letters(words))
    letter_counts = get_letter_counts(letters)
    print_letter_counts(letter_counts)

    # print("%d words" % len(wordlist))
    # print("%d letters" % len(letters))
    # print(letter_counts)

if __name__ == "__main__":
    main()
    