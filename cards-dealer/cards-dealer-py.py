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

    # Print data.
    def show(self):
        print(
            f'{self.name} of {self.suit} (value: {self.value}) (deck: {str(self.deck)})')


class Deck(object):
    def __init__(self):
        self.cards = []
        self.build() # Build and shuffle on init.
        self.shuffle() 

    def build(self):
        suits = [
            'Spades', 'Hearts',
            'Clubs', 'Diamonds'
        ]
        names = [
            'Ace', 'Two', 'Three',
            'Four', 'Five', 'Six',
            'Seven', 'Eight', 'Nine',
            'Ten', 'Jack', 'Queen', 'King',
        ]
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
        NUM_DECKS = 4 # Number of decks to play with.

        for i in range(NUM_DECKS):
            for s in suits:
                for n in range(len(names)):
                    # Append each card to cards.
                    self.cards.append(Card(s, names[n], values[n], i + 1))

    def shuffle(self):
        random.shuffle(self.cards) # Shuffle.

    def draw(self):
        return self.cards.pop() # Pop card when drawing.

    # Print data.
    def show(self):
        for c in self.cards:
            c.show() 


class Player(object):
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.score = 0
        self.status = ''

    def draw(self, deck):
        self.hand.append(deck.draw()) # Append drawed card to hand.
        return self  # For chaining.

    def calc_score(self):
        self.score = sum(c.value for c in self.hand) # Calc sum of card values.

    # Print data.
    def show(self):
        print(self.name)
        for c in self.hand:
            c.show()
        print(f'Score: {self.score}, status: {self.status}')
        print('\n')


class Table(object):
    def __init__(self, name, num_players):
        self.name = name
        self.num_players = num_players
        self.players = [] 
        self.scoreboard = []
        self.deck = Deck() # Fresh deck and build on init.
        self.build()

    def build(self):
        self.players.append(Player('Dealer')) # Add dealer to players list.
        for i in range(self.num_players):
            self.players.append(Player(f'Player {i + 1}')) # Add number of players.

    def update_score(self):
        for p in self.players:
            p.calc_score() # Call calc (for sum).
            for c in p.hand:
                if c.value == 1 and p.score <= 11:
                    c.value = 11 # Increase value when needed.
                    p.calc_score() # Recalc.
                if c.value == 11 and p.score > 21:
                    c.value = 1 # Decrease value when needed.
                    p.calc_score()

    def play(self):
        # Clear hand, score and status.
        for p in self.players:
            p.hand.clear()
            p.score = 0
            p.status = ''
        
        self.scoreboard.clear() # Clear scoreboard.

        min_num_cards = 50 # Min number of cards.
        if len(self.deck.cards) < min_num_cards:
            self.deck = Deck() # Rebuild deck.

        dealer = self.players[0] # Dealer.

        # Hit untill 17 or higher.
        while dealer.score < 17:
            dealer.draw(self.deck)
            self.update_score()

        # Dealer status.
        if dealer.score > 21:
            dealer.status = 'bust'
        elif dealer.score == 21 and len(dealer.hand) == 2:
            dealer.status = 'blackjack'
        else:
            dealer.status = 'good'

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
                p.status = 'win'
            elif p.score > 21:
                p.status = 'bust'
            elif p.score == dealer.score:
                p.status = 'push'
            else:
                p.status = 'lose'

            # Blackjack.
            if p.score == 21 and len(p.hand) == 2:
                p.status = 'blackjack'

            # Result.
            if p.status == 'blackjack' and dealer.status != 'blackjack':
                p.status = 'win'
            if p.status != 'blackjack' and dealer.status == 'blackjack' or p.status == 'bust':
                p.status = 'lose'
            if p.status == 'blackjack' and dealer.status == 'blackjack':
                p.status = 'push'

            self.scoreboard.append(p.status) # Append status to scoreboard.

    # Print data.
    def show(self):
        print(self.scoreboard)
        for p in self.players:
            p.show()


def simulate(queue, batch_size, table):
    win = 0
    push = 0
    lose = 0

    for _ in range(0, batch_size):
        table.play() # Play hands.
        # For each score in scoreboard.
        for s in table.scoreboard:
            if s == 'win':
                win += 1
            if s == 'push':
                push += 1
            if s == 'lose':
                lose += 1

    # Add to final results.
    queue.put([win, push, lose])

def process_games(table, simulations):
    num_players = table.num_players

    # Determining specs.
    cpus = multiprocessing.cpu_count()
    batch_size = int(math.ceil(simulations / float(cpus)))
    queue = multiprocessing.Queue()

    # Min and max num of players.
    min_players = 2
    max_players = 7

    if num_players > max_players or num_players < min_players:
        print(f'{min_players} to {max_players} players per table.')
        return False

    start_time = time.time() # Record time.

    processes = []

    for _ in range(0, cpus):
        # Create process for specified target.
        process = multiprocessing.Process(
            target=simulate, args=(queue, batch_size, table))
        processes.append(process) # Append to processes list.
        process.start() # Start process.

    for p in processes:
        p.join() # Join processes.

    finish_time = time.time() - start_time # Calc finish time.

    win = 0
    push = 0
    lose = 0

    for _ in range(0, cpus):
        results = queue.get() # Get results from que.
        win += results[0] # Add to wins / pushes / loses.
        push += results[1]  
        lose += results[2]

    # Calc percentages.
    win_percentage = win / float(simulations) * 100 / num_players 
    push_percentage = push / float(simulations) * 100 / num_players
    lose_percentage = lose / float(simulations) * 100 / num_players

    # Print data.
    print('\n')
    print(f'For table: {table.name}, {num_players} players.')
    print('-------------------------------')
    print(f'Cores used: {cpus}')
    print(f'Simulations: {simulations}')
    print(f'Simulations/s: {round(float(simulations) / finish_time, 2)}')
    print(f'Execution time: {round(finish_time, 2)} s')
    print(f'Wins: {round(win_percentage, 2)}%')
    print(f'Pushes: {round(push_percentage, 2)}%')
    print(f'Losses: {round(lose_percentage, 2)}%')
    print('-------------------------------')
    print('\n')

if __name__ == '__main__':
    tA1 = Table('A1', 6) # Create table.
    simulations = 1000 # Amount of simulations.

    process_games(tA1, simulations) # Process games with args.