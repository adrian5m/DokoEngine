from cards import Card, Deck
from players import Player


class Round(object):
    """Class for handling the inner playing logic within each round"""
    def __init__(self, players: list[Player]) -> None:
        pass


class Game(object):
    """Game class that brings all classes together and handles the general procedure"""
    def __init__(self, deck: Deck, players: list[Player], rounds: int) -> None:
        """
        Args:
            deck (Deck): Doppelkopf deck 
            players (list[Player]): List of players which must equal 4 
            rounds (int): Number of rounds. Will be rounded up to a multiple of 4
        """
        self.deck = deck
        self.players = players
        
        if rounds <= 4:
            rounds = 4
        if rounds % 4 != 0:
            print(f"Rounds will be increases to {rounds + rounds % 4} so that every player starts the same amount of rounds")
        self.rounds = rounds + rounds % 4

    def shuffle_deck(self, rdn: float = None) -> None:
        """Shuffles the deck

        Args:
            rdn (float, optional): Random seed for reproducibility. Defaults to None.
        """
        self.deck.shuffle(rdn=rdn)

    def deal_cards(self) -> None:
        """Deals the cards from the deck equally to the players"""
        for idx, card in enumerate(self.deck.stack):
            target = idx % len(self.players)
            self.players[target].hand.append(card)

    def start_game(self) -> None:
        """Starts the game the specified number of rounds"""
        for round in range(self.rounds):
            self.shuffle_deck()
            self.deal_cards()
            Round(self.players)
            self.players = [player for player in self.players if player != self.players[0]] + [self.players[0]] # update the order of players so the next one gets to start


