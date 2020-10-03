import random


class Card(object):
    def __init__(self, suit, name, value, deck):
        self.suit = suit
        self.name = name
        self.value = value
        self.deck = deck

    def show(self):
        print(self.name + " of " + self.suit + " (D: " + str(self.deck) + ")")


class Deck(object):
    def __init__(self):
        self.cards = [] 
        self.build()

    def build(self):
        suits = [
            "Spades", "Hearts",
            "Clubs", "Diamonds"
        ]
        names = [
            "Ace", "Two", "Three",
            "Four", "Five", "Six",
            "Seven", "Eight", "Nine",
            "Ten", "Jack", "Queen", "King",
        ]
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
        for i in range(4):
            for s in suits:
                for n in range(len(names)):
                    self.cards.append(Card(s, names[n], values[n], i + 1))

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        return self.cards.pop()

    def show(self):
        for c in self.cards:
            print(c.name + " of " + c.suit + " (D: " + str(c.deck) + ")")


class Player(object):
    def __init__(self, name):
        self.name = name
        self.hand = []

    def draw(self, deck):
        self.hand.append(deck.draw())
        return self # For chaining.

    def calcscore(self):
        score = 0
        for i in self.hand:
            score += i.value
        return score

    def show(self):
        for c in self.hand:
            c.show()


deck = Deck()
deck.shuffle()
# print(deck.show())

me = Player("Alexander")
# me.draw(deck).draw(deck)

while(me.calcscore() < 16):
    me.draw(deck)

me.show()

print(me.calcscore())
