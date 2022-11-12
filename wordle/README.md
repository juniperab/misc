# Wordle


### Usage

```
./wordle_stats.py -h
usage: wordle_stats [-h] [-w WORD_LENGTH] [-d MAX_DUPLICATES] [-x GREEN_MULTIPLIER] [-a] [-C] [-O] [planned_guesses ...]

compute some basic wordle statistics

positional arguments:
  planned_guesses       possible guesses to evaluate

optional arguments:
  -h, --help            show this help message and exit
  -w WORD_LENGTH, --word-length WORD_LENGTH
                        length of answer and guess words (default = 5)
  -d MAX_DUPLICATES, --max-duplicates MAX_DUPLICATES
                        maximum duplicate letters in guesses (default = 0)
  -x GREEN_MULTIPLIER, --green-multiplier GREEN_MULTIPLIER
                        how many yellows a green should count as (default = 2.0)
  -a, --only-guess-answers
                        only use valid answers as guesses
  -C, --no-colours      do not use coloured output
  -O, --seek-optimal-guesses
                        seek for optimal guesses (using the guess letters provided)
```

### Examples

Evaluating a sequence of guesses (with greens counting for 3 yellows).
```
 ./wordle_stats.py -x3 hello world
 Wordle Statistics.
 Planned guesses: hello world

 Loading data
 Loading word lists
 Loading expected guess scores from 'expected_guess_scores_cache.txt' (delete this file to recalculate)

 Letters in answer words, sorted by frequency from most to least (letters in planned guesses are capitalized)
 In any position:     E a R O t     L i s n c     u y D H p     m g b f k     W v z x q j
 In position 1:       s c b t p     a f g D m     R L W E H     v O n i u     q k j y z       [ x ]
 In position 2:       a O R E i     L u H n t     p W c m y     D s b v x     g k f q z j
 In position 3:       a i O E u     R n L t s     D g m p b     c v y W f     k x z H j q
 In position 4:       E n s a L     i R c t O     u g D m k     p v f H W     b z x y j       [ q ]
 In position 5:       E y t R L     H n D k a     O p m g s     c f W i b     x z u           [ v j q ]

 Considering 9365 possible guesses out of 14855 legal guesses
 Statistically ideal guesses are: 'soare' and 'clint' and 'pudgy'

 Top scoring initial guesses:
 Most Greens:             (2.97 | 0.67 + 0.97 = 1.63) saine, soare, saice, slane, soily, slate, soave, samey, sauce, slice, savey, shale, saute, share, souce
 Most Yellows:            (2.02 | 0.18 + 1.49 = 1.66) estro, retia, terai, eyras, aeros, escar, entia, teras, arets, earls, opera, acers, etnas, recta, laers
 Most Total Hits:         (2.64 | 0.43 + 1.36 = 1.79) oater, orate, roate, realo, retia, terai, tiare, irate, artel, ratel, taler, alert, alter, later, ariel
 Best Weighted Score:     (3.09 | 0.66 + 1.11 = 1.77) soare, saine, slate, slane, stare, sater, saice, roate, saner, snare, raile, raise, salet, arise, crate
 3.0866175833694243

 Top scoring guesses after 'hello'     1.78 -1.31 | 0.28 + 0.94 = 1.22:
 Most Greens:             (2.65 | 0.59 + 0.87 = 1.47) saint, saury, saucy, snary, saunt, stary, briny, sarky, suint, spacy, sandy, spiny, scary, rainy, fairy
 Most Yellows:            (1.95 | 0.19 + 1.37 = 1.56) intra, astir, airts, artis, nrtya, tarsi, naris, antis, rants, stria, ratus, airns, tiars, raits, arnis
 Most Total Hits:         (2.18 | 0.29 + 1.30 = 1.59) airts, artis, astir, raits, sitar, stria, tarsi, tiars, stair, intra, riant, train, rants, starn, tarns
 Best Weighted Score:     (2.65 | 0.59 + 0.87 = 1.47) saint, stary, saury, stair, snary, rainy, sarin, sitar, surat, saunt, stray, scart, riant, scary, spart
 5.317020355132092

 Top scoring guesses after 'hello' and 'world'     3.65 -1.67 | 0.63 + 1.77 = 2.40:
 Most Greens:             (2.65 | 0.59 + 0.87 = 1.47) saint, saucy, saunt, suint, spacy, spiny, spicy, saick, stagy, snaky, paint, scant, spait, canty, stimy
 Most Yellows:            (1.93 | 0.23 + 1.24 = 1.47) antis, incas, natis, aitus, astun, tinas, antic, actus, actin, uncia, nipas, nsima, ngati, aspic, aunts
 Most Total Hits:         (1.93 | 0.23 + 1.24 = 1.47) antis, natis, tains, tians, tinas, saint, satin, stain, aitus, asity, tuina, actin, canti, antic, astun
 Best Weighted Score:     (2.65 | 0.59 + 0.87 = 1.47) saint, saunt, saucy, satin, scant, spait, stain, suint, tansy, paint, maist, canst, stagy, canty, tains
```

Seeking an optimal sequence of guesses, from only the set of valid answers, using the 15 most frequent letters in the
answer set. (Greens count as 2 yellow, the default).
```
 ./wordle_stats.py -a -O earotlisncuyfhp
 Wordle Statistics.

 Loading data
 Loading word lists
 Loading expected guess scores from 'expected_guess_scores_cache.txt' (delete this file to recalculate)

 Seeking optimal guesses using letters A C D E H I L N O P R S T U Y
 Considering 526 possible guesses
 0.00%
 stare could: 3.858380
 stare phony lucid: 3.824166 -> 5.195756
 arose unity: 3.875271
 raise count: 3.980511
 slate irony: 4.126029
 saner pouty child: 3.871373 -> 5.331745
 1.90% 3.80% 5.70% 7.60% 9.51%
 slice party hound: 3.936769 -> 5.338242
 11.41% 13.31% 15.21% 17.11%
 drape shiny clout: 3.720225 -> 5.392811
 19.01%
 plier shady count: 3.722391 -> 5.396709
 shade point curly: 3.736683 -> 5.412733
 20.91% 22.81% 24.71% 26.62% 28.52% 30.42% 32.32% 34.22% 36.12% 38.02% 39.92% 41.83% 43.73% 45.63% 47.53% 49.43% 51.33% 53.23% 55.13% 57.03% 58.94% 60.84% 62.74% 64.64% 66.54% 68.44% 70.34% 72.24% 74.14% 76.05% 77.95% 79.85% 81.75% 83.65% 85.55% 87.45% 89.35% 91.25% 93.16% 95.06% 96.96% 98.86%

 Letters in answer words, sorted by frequency from most to least (letters in planned guesses are capitalized)
 In any position:     E A R O T     L I S N C     U Y D H P     m g b f k     w v z x q j
 In position 1:       S C b T P     A f g D m     R L w E H     v O N I U     q j k Y z       [ x ]
 In position 2:       A O R E I     L U H N T     P w C m Y     D S b v x     g k f q z j
 In position 3:       A I O E U     R N L T S     D g m P C     b v Y w f     x k z H j q
 In position 4:       E N S A L     I C R T O     U g D m k     P v f H w     b z Y x j       [ q ]
 In position 5:       E Y T R L     H N D k A     O P m g S     C f w I b     x z U           [ v q j ]

 Considering 1562 possible guesses out of 14855 legal guesses
 Statistically ideal guesses are: 'soare' and 'clint' and 'pudgy'
 
 Top scoring initial guesses:
 Most Greens:             (2.30 | 0.62 + 1.06 = 1.68) slate, sauce, slice, shale, saute, share, shine, suite, crane, saint, soapy, shone, saucy, shire, saner
 Most Yellows:            (1.86 | 0.21 + 1.44 = 1.65) opera, renal, alert, alter, extra, eclat, ocean, later, learn, ideal, ethos, inert, earth, regal, ratio
 Most Total Hits:         (2.28 | 0.51 + 1.27 = 1.78) irate, alert, alter, later, arose, stare, arise, raise, learn, renal, saner, snare, cater, crate, react
 Best Weighted Score:     (2.34 | 0.57 + 1.19 = 1.77) stare, arose, raise, arise, slate, saner, snare, irate, crate, stale, trace, share, crane, scare, later
 2.4274577739281074

 Top scoring guesses after 'shade'     2.00 -0.42 | 0.57 + 0.87 = 1.44:
 Most Greens:             (1.81 | 0.54 + 0.72 = 1.26) crony, briny, corny, point, print, truly, irony, pouty, privy, forty, front, grimy, count, curly, glory
 Most Yellows:            (1.65 | 0.19 + 1.27 = 1.46) intro, lyric, incur, until, optic, micro, unlit, turbo, orbit, curio, ingot, lingo, robin, tonic, twirl
 Most Total Hits:         (1.65 | 0.19 + 1.27 = 1.46) intro, irony, orbit, court, broil, curio, print, truly, groin, flirt, minor, lyric, twirl, tonic, pilot
 Best Weighted Score:     (1.82 | 0.47 + 0.88 = 1.35) irony, crony, print, truly, court, corny, broil, front, flirt, point, briny, glory, groin, grout, forty
 4.18189692507579

 Top scoring guesses after 'shade' and 'point'     3.74 -0.45 | 1.05 + 1.63 = 2.69:
 Most Greens:             (1.68 | 0.46 + 0.75 = 1.21) curly, burly, curvy, bulky, murky, mucky, lucky, rugby, crumb
 Most Yellows:            (1.68 | 0.46 + 0.75 = 1.21) curly, crumb, burly, rugby, lucky, curvy, murky, bulky, mucky
 Most Total Hits:         (1.68 | 0.46 + 0.75 = 1.21) curly, burly, crumb, curvy, rugby, murky, lucky, bulky, mucky
 Best Weighted Score:     (1.68 | 0.46 + 0.75 = 1.21) curly, burly, curvy, murky, rugby, crumb, lucky, bulky, mucky
 5.362927674317886

 Top scoring guesses after 'shade' and 'point' and 'curly'     5.41 0.05 | 1.52 + 2.38 = 3.90:
 No legal guesses remain that meet the chosen criteria
```

##### Sources

- wordlist_guesses.txt: [cfreshman/wordle-nyt-allowed-guesses-update-12546.txt](https://gist.github.com/cfreshman/d5fb56316158a1575898bba1eed3b5da)
- wordlist_answers.txt: [cfreshman/wordle-nyt-answers-alphabetical.txt](https://gist.github.com/cfreshman/a7b776506c73284511034e63af1017ee)