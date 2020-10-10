import random
import math
import multiprocessing
import time


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
        NUM_DECKS = 4

        for i in range(NUM_DECKS):
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
    def __init__(self, name, num_players):
        self.name = name
        self.num_players = num_players
        self.deck = Deck()
        self.deck.shuffle()
        self.players = []
        self.scoreboard = []
        self.build()

    def build(self):
        self.players.append(Player("Dealer"))
        for i in range(self.num_players):
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
        for p in self.players:
            p.hand.clear()
            p.score = 0
            p.status = ""

        # Reshuffle if needed (< 50 cards).
        MIN_CARDS_LEFT = 50
        if len(self.deck.cards) < MIN_CARDS_LEFT:
            self.deck = Deck()

        # Dealer.
        dealer = self.players[0]

        # Hit untill 17 or higher.
        while dealer.score < 17:
            dealer.draw(self.deck)
            self.update_score()

        # Dealer status.
        if dealer.score > 21:
            dealer.status = "bust"
        elif dealer.score == 21 and len(dealer.hand) == 2:
            dealer.status = "blackjack"
        else:
            dealer.status = "good"

        # Players (skip dealer [1:]).
        for p in self.players[1:]:
            for _ in range(2):
                p.draw(self.deck)
                self.update_score()

            # Calculate when to draw another card.
            if (dealer.hand[0].value >= 7 and p.score - 10 <= dealer.hand[0].value) or p.score <= 11:
                while p.score - 10 <= dealer.hand[0].value and p.score < 17:
                    p.draw(self.deck)
                    self.update_score()

            # Player status.
            if (p.score <= 21 and dealer.score > 21) or (p.score <= 21 and p.score > dealer.score):
                p.status = "win"
            elif p.score > 21:
                p.status = "bust"
            elif p.score == dealer.score:
                p.status = "push"
            else:
                p.status = "lose"

            # Blackjack.
            if p.score == 21 and len(p.hand) == 2:
                p.status = "blackjack"

            # Result.
            if p.status == "blackjack" and dealer.status != "blackjack":
                p.status = "win"
            if p.status != "blackjack" and dealer.status == "blackjack" or p.status == "bust":
                p.status = "lose"
            if p.status == "blackjack" and dealer.status == "blackjack":
                p.status = "push"

            self.scoreboard.append(p.status)

    def show(self):
        print(self.scoreboard)
        for p in self.players:
            p.show()


def simulate(queue, batch_size, num_players):
    win = 0
    push = 0
    lose = 0

    table = Table("Table", num_players)

    for _ in range(0, batch_size):
        table.play()
        for s in table.scoreboard:
            if s == "win":
                win += 1
            if s == "push":
                push += 1
            if s == "lose":
                lose += 1

    # Add to final results.
    queue.put([win, push, lose])


if __name__ == "__main__":
    start_time = time.time()

    NUM_PLAYERS = 5
    SIMULATIONS = 1000
    CPUS = multiprocessing.cpu_count()
    BATCH_SIZE = int(math.ceil(SIMULATIONS / float(CPUS)))
    queue = multiprocessing.Queue()

    processes = []

    for _ in range(0, CPUS):
        process = multiprocessing.Process(
            target=simulate, args=(queue, BATCH_SIZE, NUM_PLAYERS))
        processes.append(process)
        process.start()

    for p in processes:
        p.join()

    finish_time = time.time() - start_time

    # Get total.
    win = 0
    push = 0
    lose = 0

    for i in range(0, CPUS):
        results = queue.get()
        win += results[0]
        push += results[1]
        lose += results[2]

    print("\n")
    print(f"Cores used: {CPUS}")
    print(f"Simulations: {SIMULATIONS}")
    print(f"Wins: {win / SIMULATIONS}")
    print(f"Push percentage: {push / SIMULATIONS}")
    print(f"Lose percentage: {lose / SIMULATIONS}")
    print("\n")
