import random


class Card(object):
    def __init__(self, suit, name, value, deck):
        self.suit = suit
        self.name = name
        self.value = value
        self.deck = deck

    def show(self):
        print(
            f"{self.name} of {self.suit} (value: {self.value}) (deck: {str(self.deck)})")


class Deck(object):
    def __init__(self):
        self.cards = []
        self.build()
        self.shuffle()

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
        self.status = ""

    def draw(self, deck):
        self.hand.append(deck.draw())
        return self  # For chaining.

    def calc_score(self):
        self.score = sum(c.value for c in self.hand)

    def show(self):
        print(self.name)
        for c in self.hand:
            c.show()
        print(f"Score: {self.score}, status: {self.status}")
        print("\n")


class Table(object):
    def __init__(self, name):
        self.name = name
        self.deck = Deck()
        self.deck.shuffle()
        self.players = []
        self.build()

    def build(self):
        self.players.append(Player("Dealer"))
        for i in range(3):
            self.players.append(Player(f"Player {i + 1}"))

    def update_score(self):
        for p in self.players:
            p.calc_score()
            for c in p.hand:
                if c.value == 1 and p.score <= 11:
                    c.value = 11
                    p.calc_score()
                if c.value == 11 and p.score > 21:
                    c.value = 1
                    p.calc_score()

    def play(self):
        dealer = self.players[0]

        while dealer.score < 17:  # Dealer has to stop at 17 or higher.
            dealer.draw(self.deck)
            self.update_score()

        # Dealer status.
        if dealer.score > 21:
            dealer.status = "bust"
        elif dealer.score == 21 and len(dealer.hand) == 2:
            dealer.status = "blackjack"
        else:
            dealer.status = "good"

        # Players.
        for p in self.players[1:]:
            for _ in range(2):
                p.draw(self.deck)  # Players draw 2 cards.
                self.update_score()

            # Calculate when to draw another card.
            if (dealer.hand[0].value >= 7 and p.score - 10 <= dealer.hand[0].value) or p.score <= 11:
                # Something goes wrong here!
                while p.score - 10 <= dealer.hand[0].value and p.score < 17:
                    p.draw(self.deck)
                    self.update_score()

            # Player status.
            if (p.score < 22 and dealer.score > 21) or (p.score < 22 and p.score > dealer.score):
                p.status = "win"
            elif p.score > 21:
                p.status = "bust"
            elif p.score == dealer.score:
                p.status = "push"
            else:
                p.status = "lost"

            if p.score == 21 and len(p.hand) == 2:
                p.status = "blackjack"
            # if(self.dealer.status != "blackjack" and p.status == "blackjack"):
                # p.status = "win"
            if dealer.status == "blackjack" and p.status != "blackjack":
                p.status = "lost"
            if dealer.status == "blackjack" and p.status == "blackjack":
                p.status = "push"

        if len(self.deck.cards) < 50:
            self.deck = Deck()

    def show(self):
        for p in self.players:
            p.show()


t1 = Table("T1")
t1.play()
t1.show()
