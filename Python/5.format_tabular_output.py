#!/usr/bin/python
import numpy as np

teams_list = ["Man Utd", "Man City", "T Hotspur"]
data = np.array([[1, 2, 1],
                 [0, 1, 0],
                 [2, 4, 2]])

# it will generate four string of "{:>15}", just like
# "{:>15}{:>15}{:>15}{:>15}".format(a, b, c, d)
row_format = "{:>15}" * (len(teams_list) + 1)
print row_format.format("", *teams_list)
# zip: ("Man Utd", [1, 2, 1]) => team, row
# the numbers of the zip's parameter is the length of the tuple
for team, row in zip(teams_list, data):
    print row_format.format(team, *row)
