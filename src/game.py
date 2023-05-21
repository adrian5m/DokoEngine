import numpy as np
from cards import Card, Deck
from players import Player


class Round(object):
    """Class for handling the inner playing logic within each round"""
    def __init__(self, players: list[Player]) -> None:
        """
        Args:
            players (list[Player]): List of players
        """
        self.players = players
        self.current_player = players[0]
        self.played_tricks = []
        self.round_finished = False
        self.play()
        
    def get_current_player(self) -> Player:
        """Returns the current player"""
        return self.current_player
    
    def assign_teams(self) -> None:
        """Assigns the teams based on the Queen of Clubs"""
        for player in self.players:
            player.team = 'Re' if 'QC' in [card.name for card in player.hand] else 'Contra'

    def eval_trick(self, trick: list[Card], start_idx: int) -> int:
        """Evaluate the trick and give the rewarding points to the winner

        Args:
            trick (list[Card]): Trick with the cards
            start_idx (int): Index of player who started the trick

        Returns:
            int: Resulting index of the player who has won
        """
        trick_points = sum([card.value for card in trick])
        trump_values = [card.trump_value for card in trick]
        max_trump_idx = np.flatnonzero(trump_values == np.max(trump_values))
        win_idx = 0
        
        if len(max_trump_idx) == 1:
            win_idx = max_trump_idx.item()
        
        elif len(max_trump_idx) == 2:
            win_idx = min(max_trump_idx)
        
        # note: it can not happen that 3 players have the same trump card, so this case does not need to be covered
        # else case for all non-trump tricks
        else:
            for idx in range(1, len(trick)):
                win_idx = idx if trick[idx].suit == trick[0].suit and trick[idx].value > trick[win_idx].value else win_idx

        result_idx = start_idx + win_idx
        if result_idx > 3: 
            result_idx -= 4

        self.players[result_idx].round_points += trick_points
        return result_idx
        
    def play(self):
        """Executes the round"""
        self.assign_teams()
        player_in_action = self.get_current_player()
        while not self.round_finished:
            starting_player = self.players.index(player_in_action)
            trick = []
            card = player_in_action.play_card(input(f"{player_in_action.name}: Play one of the following cards {[x.name for x in player_in_action.hand]}:"))
            suit_of_trick = 'Trump' if card.is_trump else card.suit
            trick.append(card)
            idx = starting_player + 1
            while len(trick) < 4:
                if idx > 3:
                    idx = 0
                self.current_player = self.players[idx]
                player_in_action = self.get_current_player()
                while True:
                    card = player_in_action.play_card(input(f"{player_in_action.name}: Play one of the following cards {[x.name for x in player_in_action.hand]}:"))
                    if suit_of_trick == 'Trump' and (card.is_trump or not any([x.is_trump for x in player_in_action.hand])):
                        break
                    elif suit_of_trick != 'Trump':
                        # residual cards of suit of the trick should be trump
                        residual_playable_cards = [x for x in player_in_action.hand if x.suit == suit_of_trick and not x.is_trump] 
                        if len(residual_playable_cards) == 0 or (card.suit == suit_of_trick and not card.is_trump):
                            break
                    print('Your card did not match the criteria for following the trick. Please play another card.')
                    player_in_action.hand.append(card)
                
                trick.append(card)
                idx += 1
            
            # evaluate trick and make the winner to the person who will start the next trick
            self.played_tricks.append(trick)
            winner_idx = self.eval_trick(trick=trick, start_idx=starting_player)
            self.current_player = self.players[winner_idx]
            player_in_action = self.get_current_player()
            
            if not len(player_in_action.hand):
                self.round_finished = True
                      
        for player in self.players:
            print(f'Player: {player.name} | Team: {player.team} | Points: {player.round_points}')    


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


