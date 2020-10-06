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
        values = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
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

    def calcscore(self):
        self.score = 0  # Set score back to 0.
        for c in self.hand:
            self.score += c.value  # Calc total.

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
        self.dealer = Player("Dealer")
        self.players = []
        self.build()

    def build(self):
        # self.players.append(self.dealer)
        for i in range(3):
            self.players.append(Player(f"Player {i + 1}"))

    def play(self):
        self.deck.shuffle()  # Shuffle the deck.

        # Dealer.
        d = self.dealer
        for _ in range(2):
            d.draw(self.deck)  # Dealer draws 2 cards.
        d.calcscore()  # Calculate score.

        # When dealt 2 aces.
        if(d.score == 22 and len(d.hand) == 2):
            d.hand[1].val = 1
            d.calcscore()

        while(d.score < 17):  # Dealer has to stop at 17 or higher.
            d.draw(self.deck)
            d.calcscore()

            # Check for aces when busting.
            if(d.score > 21):
                for c in d.hand:
                    if(c.val == 11):
                        c.val = 1
                        d.calcscore()

        # Dealer status.
        if (d.score > 21):
            d.status = "bust"
        elif(d.score == 21 and len(d.hand) == 2):
            d.status = "blackjack"
        else:
            d.status = "good"

        # Players.
        for p in self.players:
            for _ in range(2):
                p.draw(self.deck)  # Players draw 2 cards.
            p.calcscore()  # Calculate score.

            if (p.score == 2 and len(p.hand) == 2):
                p.hand[1].val = 1
                p.calcscore()

            # Calculate when to draw another card.
            if ((d.hand[0].value >= 7 and p.score - 10 <= d.hand[0].value) or p.score <= 11):
                # Something goes wrong here!
                while p.score - 10 <= d.hand[0].value and p.score < 17:
                    p.draw(self.deck)
                    p.calcscore()

                    # Check for aces when busting.
                    if (p.score > 21):
                        for c in p.hand:
                            if (c.val == 11):
                                c.val = 1
                                p.calcscore()

            # Player status.
            if((p.score < 22 and d.score > 21) or (p.score < 22 and p.score > d.score)):
                p.status = "win"
            elif(p.score > 21):
                p.status = "bust"
            elif(p.score == d.score):
                p.status = "push"
            else:
                p.status = "lost"

            if(p.score == 21 and len(p.hand) == 2):
                p.status = "blackjack"
            # if(self.dealer.status != "blackjack" and p.status == "blackjack"):
                # p.status = "win"
            if(d.status == "blackjack" and p.status != "blackjack"):
                p.status = "lost"
            if (d.status == "blackjack" and p.status == "blackjack"):
                p.status = "push"

    def show(self):
        self.dealer.show()
        for p in self.players:
            p.show()


t1 = Table("T1")
t1.play()
t1.show()
