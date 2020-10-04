import random


class Card(object):
    def __init__(self, suit, name, value, deck):
        self.suit = suit
        self.name = name
        self.value = value
        self.deck = deck

    def show(self):
        print(f"{self.name} of {self.suit} (Deck: {str(self.deck)})")


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
            c.show()


class Player(object):
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.score = 0

    def draw(self, deck):
        self.hand.append(deck.draw())
        return self  # For chaining.

    def calcscore(self):
        for c in self.hand:
            self.score += c.value

    def show(self):
        print(self.name)
        for c in self.hand:
            c.show()
        print(self.score)
        print("\n")


class Table(object):
    def __init__(self, name):
        self.name = name
        self.deck = Deck()
        self.dealer = Player("Dealer")
        self.players = []
        self.build()

    def build(self):
        self.players.append(self.dealer)
        for i in range(3):
            self.players.append(Player(f"Player{i + 1}"))

    def play(self):
        self.deck.shuffle()
        for p in self.players:
            for _ in range(2):
                p.draw(self.deck)
            p.calcscore()

    def show(self):
        for p in self.players:
            p.show()


t1 = Table("T1")
print(str((len(t1.deck.cards))))
t1.play()
t1.show()
print(str((len(t1.deck.cards))))
