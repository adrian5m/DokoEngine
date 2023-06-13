from cards import Card


class Player(object):
    def __init__(self, name: str):
        """
        Args:
            name (str): Name of the player
        """
        self.name = name
        self.hand = []
        self.tricks = []
        self.round_points = 0
        self.game_points = 0
        self.team = None
        self.game_state: dict = None

    def __repr__(self):
        return self.name

    def play_card(self, card: str) -> Card:
        """Play a card

        Args:
            card (str): Name of the card to play

        Returns:
            Card
        """
        self.__sanity_check(card)
        played_card = next((x for x in self.hand if x.name == card), None)
        self.hand.remove(played_card)
        return played_card
    
    def set_game_state(self, game_state: dict):
        self.game_state = game_state
    
    def __sanity_check(self, played_card: str):
        """Checks if the card is in the player's hand

        Args:
            played_card (str): Name of the card to play
        """
        assert played_card in [card.name for card in self.hand], "The selected card is not in your hand"
