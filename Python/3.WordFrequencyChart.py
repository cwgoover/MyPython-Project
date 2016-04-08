import re
import sys

# Build an ASCII chart of the most commonly used words in a given text
# http://stackoverflow.com/a/3170549/4710864
# command:
# $ python WordFrequencyChart.py the and of to a i it in or is <"Alice's Adventures in Wonderland.txt"

# Make sure these bars (plus space-word-space) always fit:
#  bar + [space] + word + [space] should be always <= 80 characters
# 77 = 80 - [space]*2 - '|' (the most right of the char)
#
# The bar width represents the number of occurences (frequency) of
# the word (proportionally). Append one space and print the word.


t = re.split('\W+', sys.stdin.read().lower())
r = sorted((-t.count(w), w) for w in set(t) - set(sys.argv))[:22]
h = min(9 * l / (77 - len(w)) for l, w in r)
print'', 9 * r[0][0] / h * '_'
for l, w in r:
    print'|' + 9 * l / h * '_' + '|', w
