import random
from enum import Enum

class Suit(Enum):
    CLUBS = 'Clubs'
    SPADES = 'Spades'
    HEARTS = 'Hearts'
    DIAMONDS = 'Diamonds'

class Face(Enum):
    NINE = 0
    TEN = 10
    JACK = 2
    QUEEN = 3
    KING = 4
    ACE = 11

class Card(object):
    """French-suited playing card with certain suit, face and value as reward"""
    def __init__(self, suit: Suit, face: Face):
        """
        Args:
            suit (str): Suit of the card
            face (str): Face of the card
            value (int): The card's reward at the end of a round
        """
        self.suit = suit.name
        self.face = face.name
        self.value = face.value
        self.name = f'{self.suit[0]}{self.face if len(self.face) < 3 else self.face[0]}'
        self.is_trump = False
        self.trump_value = 0
        

    def __repr__(self):
        return f'{self.face} of {self.suit}'


class Deck(object):
    """Doppelkopf card deck"""
    TRUMPS = {'TEN of HEARTS': 13,
              'QUEEN of CLUBS': 12,
              'QUEEN of SPADES': 11,
              'QUEEN of HEARTS': 10,
              'QUEEN of DIAMONDS': 9,
              'JACK of CLUBS': 8,
              'JACK of SPADES': 7,
              'JACK of HEARTS': 6,
              'JACK of DIAMONDS': 5,
              'ACE of DIAMONDS': 4,
              'TEN of DIAMONDS': 3,
              'KING of DIAMONDS': 2,
              'NINE of DIAMONDS': 1
              }

    def __init__(self, card: Card, exclude_nine: bool = False, suits = Suit, faces = Face):
        """
        Args:
            card (Card): Playing card
            exclude_nine (bool, optional): Flag for excluding all the "nine" cards
        """
        self.suits = suits
        self.faces = faces
        self.stack = []
        for suit in self.suits:
            for face in self.faces:
                if exclude_nine and face.name == 'NINE':
                    continue

                current_card = card(suit, face)
                if str(current_card) in self.TRUMPS:
                    current_card.is_trump = True
                    current_card.trump_value = self.TRUMPS[str(current_card)]

                self.stack.append(current_card)
                self.stack.append(current_card)

    def __repr__(self):
        return f'Doppelkopf deck containing {len(self.stack)} cards'

    def shuffle(self, rdn: float = None):
        """Shuffles the deck

        Args:
            rdn (float, optional): value for the random seed. Defaults to None
        """
        if rdn is not None:
            random.seed(rdn)  # todo add timestamp for randomness

        random.shuffle(self.stack)
