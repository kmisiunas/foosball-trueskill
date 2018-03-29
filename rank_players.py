## get team names
with open("teams.csv") as f:
    teams = f.readlines()

teams = [team.strip() for team in teams]

print("Found "+str(len(teams))+" teams")

## Infrastructure: Game class
class Game:
    def __init__(self, red, blue, scoreRed, scoreBlue):
        self.red = red
        self.blue = blue
        self.scoreRed = scoreRed
        self.scoreBlue = scoreBlue
    def won(self):
        if self.scoreRed > self.scoreBlue:
            return self.red
        else: 
            return self.blue
    def lost(self):
        if self.scoreRed < self.scoreBlue:
            return self.red
        else: 
            return self.blue
    def scoreRatio(self):
        if self.scoreRed > self.scoreBlue:
            return float(self.scoreRed)/float(self.scoreBlue)
        else:
            return float(self.scoreBlue)/float(self.scoreRed)
    def min_delta(self):  # returns score adjustment based on the difference
        return 0.0001
    def __str__(self):
        return self.red+" ("+str(self.scoreRed)+")  v  "+self.blue+" ("+str(self.scoreBlue)+")"
    def __repr__(self):
        return self.__str__()

## Get results from CSV

import csv

with open("Foosball tournament, 2015 - Games.csv") as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    games = []
    next( readCSV , None)
    for row in readCSV:
        teamRed = row[2].strip()
        teamBlue = row[3].strip()
        if  row[4].strip() == '' or row[5].strip() == '':
            print("Score was missing on "+row[0]+" teams: "+teamRed+" v "+teamBlue)
        else: 
            scoreRed = int(row[4].strip())
            scoreBlue = int(row[5].strip())
            games.append( Game(teamRed, teamBlue, scoreRed, scoreBlue) )

print("Found "+str(len(games))+" finished games")

## Compute Rating for all the teams

from trueskill import Rating, quality_1vs1, rate_1vs1

ratings = [] # store the ratings independently from names
for team in teams:
    ratings.append( Rating() )

# function for evaluating each rating 
def adjustRating(game):
    winnerId = teams.index( game.won() )
    looserId = teams.index( game.lost() )
    w = () 
    l = ()
    w, l = rate_1vs1(ratings[winnerId], ratings[looserId], 
            drawn=False )
    ratings[winnerId] = w
    ratings[looserId] = l

for game in reversed(games):
    adjustRating(game)


## Export results into CSV file

import csv

with open('ratings.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for id in range( len(teams) ):
        writer.writerow([teams[id] , ratings[id].mu,  ratings[id].sigma ])


## Estimate Suggested random pairing

from random import sample
from random import random

print(  '\n'.join( list(map(lambda i: str(i) +" -> "+teams[i], list( range( len(teams) ) ))) ) )
toPlay = list( range( len(teams) ) ) *2
toPlay = [1,2,3,4,5,6,8,9,10,11] *2
matches = []

while len(toPlay) > 2:
    # pick two teams
    pair = sample(toPlay, 2)
    if  pair[0] != pair[1] and \
        random() <= quality_1vs1(ratings[pair[0]], ratings[pair[1]]) :
        matches.append( [ teams[pair[0]], teams[pair[1]], 
            '{:.1%}'.format(quality_1vs1(ratings[pair[0]], ratings[pair[1]])) ] )
        toPlay.remove(pair[0])
        toPlay.remove(pair[1])


# save matches

import csv

with open('next_matches.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for pairing in matches:
        writer.writerow(pairing)

print("Done estimating ratings and pairing.")

# extra info

# print( "chance to draw = " + str( quality_1vs1(ratings[4], ratings[7]) ) )


