import random


class Card(object):
    """French-suited playing card with certain suit, face and value as reward"""
    def __init__(self, suit: str, face: str, value: int):
        """
        Args:
            suit (str): Suit of the card
            face (str): Face of the card
            value (int): The card's reward at the end of a round
        """
        self.suit = suit
        self.face = face
        self.value = value
        self.name = f'{suit[0]}{face if len(face) < 3 else face[0]}'
        self.is_trump = False
        self.trump_value = 0
        

    def __repr__(self):
        return f'{self.face} of {self.suit}s'


class Deck(object):
    """Doppelkopf card deck"""
    SUITS = ['Clubs', 'Spades', 'Hearts', 'Diamonds']
    VALUES = {'9': 0, '10': 10, 'Jack': 2, 'Queen': 3, 'King': 4, 'Ace': 11}
    TRUMPS = {'Hearts 10': 13,
              'Clubs Queen': 12,
              'Spades Queen': 11,
              'Hearts Queen': 10,
              'Diamonds Queen': 9,
              'Clubs Jack': 8,
              'Spades Jack': 7,
              'Hearts Jack': 6,
              'Diamonds Jack': 5,
              'Diamonds Ace': 4,
              'Diamonds 10': 3,
              'Diamonds King': 2,
              'Diamonds 9': 1
              }

    def __init__(self, card: Card, exclude_nine: bool = False):
        """
        Args:
            card (Card): Playing card
            exclude_nine (bool, optional): Flag for excluding all the "nine" cards
        """
        self.stack = []
        for suit in self.SUITS:
            for face, reward in self.VALUES.items():
                if exclude_nine and face == '9':
                    continue

                current_card = card(suit, face, reward)
                if f'{suit} {face}' in self.TRUMPS:
                    current_card.is_trump = True
                    current_card.trump_value = self.TRUMPS[f'{suit} {face}']

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
