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
        self.game_state = {
            'players': players,
            'teams': ['', '', '', ''],
            'current_player': players[0],
            're_calls': [],
            'contra_calls': [],
            'trick': [],
            'last_trick': [],
            '_played_tricks': [], 
            'wedding': False,
            'solo': False,
            'solo_type': None   
        }
        self.round_finished = False
        self.play()
    
    def get_public_game_state(self) -> dict:
        """Parses the public game state for the players"""
        public_state = {key: value for key, value in self.game_state.items() if not key.startswith('_')}
        for player in public_state['players']:
            player.team = None
        # todo: maybe hide the round points of each player
        return public_state
    
    def brodcast_game_state(self) -> None:
        """Brodcast the game state to all players"""
        for player in self.game_state['players']:
            player.set_game_state(self.get_public_game_state())
    
    def update_game_state(self, idx: int, trick: list[Card] = None, card: Card = None, call = None) -> None:
        """Updates the game state based on a played card, trick or made call
        Args:
            idx (int): index is dependent on the other arguments. If trick, idx means the idx of the starting player, if card or call is done then idx indicates the current players idx
            trick (list[Card]): Trick containing 4 cards. Defaults to None.
            card (Card, optional): Played card. Defaults to None.
            call (_type_, optional): Made Call. Defaults to None.

        Raises:
            ValueError: When trick and card are parsed simultaneously
        """
        if trick is not None and card is not None:
            raise ValueError("the game state should not be updated for a card and a trick simultaneously")
        
        elif card is not None:
            self.game_state['trick'].append(card)
            if str(card) == 'QUEEN of CLUBS' and not self.game_state['solo']:
                self.game_state['teams'][idx] = 'Re'
                # check if the other team mate is already known and update other player's team accordingly
                if self.game_state['teams'].count('Re') == 2:
                    self.game_state['teams'] = list(map(lambda x: 'Contra' if x == '' else x, self.game_state['teams']))
                
                # special case for a silent wedding 
                elif self.game_state.get('_first_re_card', False) and self.game_state.get('_first_re_card', False) == self.game_state['current_player'].name:
                    self.game_state['teams'] = list(map(lambda x: 'Contra' if x == '' else x, self.game_state['teams']))
                    self.game_state.update({'solo': True,
                                            'solo_type': 'Trump Solo'})
                
                self.game_state.update({'_first_re_card': self.game_state['current_player'].name})
        
        elif trick is not None:
            # evaluate trick. make winner start next trick
            # update played tricks, last trick, current player
            # todo implement evaluation of card based bonus points
            self.game_state['_played_tricks'].append(self.game_state['trick'])
            winner_idx, round_points = self.eval_trick(trick=self.game_state['trick'], start_idx=idx)
            self.game_state['players'][winner_idx].round_points += round_points
            self.game_state.update({'last_trick': (self.game_state['players'][winner_idx].name, self.game_state['trick'])})
            self.game_state['trick'].clear()
            self.game_state['current_player'] = self.game_state['players'][winner_idx]
            
        if call is not None:
            self.game_state['re_calls'].append(call) if self.game_state['players'][idx].team == 'Re' else self.game_state['re_calls']
            self.game_state['teams'][idx] = self.game_state['players'][idx].team
            if self.game_state['teams'].count(self.game_state['players'][idx].team) == 2:
                    self.game_state['teams'] = [player.team for player in self.game_state['players']]
                
    def get_current_player(self) -> Player:
        """Returns the current player"""
        return self.game_state['current_player']
    
    def assign_teams(self) -> None:
        """Assigns the teams based on the Queen of Clubs"""
        for player in self.game_state['players']:
            player.team = 'Re' if 'CQ' in [card.name for card in player.hand] else 'Contra'

    def eval_trick(self, trick: list[Card], start_idx: int) -> tuple[int, int]:
        """Evaluate the trick and give the rewarding points to the winner

        Args:
            trick (list[Card]): Trick with the cards
            start_idx (int): Index of player who started the trick

        Returns:
            tuple[int, int]: Tuple of the winner's index and the round points  
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

        return result_idx, trick_points
    
    def play(self):
        """Executes the round"""
        self.assign_teams()
        player_in_action = self.get_current_player()
        self.brodcast_game_state()
        while not self.round_finished:
            starting_player = self.game_state['players'].index(player_in_action)
            cards_on_hand = {idx: c for idx, c in enumerate(player_in_action.hand)}
            card_to_play = cards_on_hand[int(input(f"{player_in_action.name}: Play one of the following cards {cards_on_hand}:"))]
            card = player_in_action.play_card(card_to_play.name)
            suit_of_trick = 'Trump' if card.is_trump else card.suit
            self.update_game_state(idx=starting_player, card=card, call=None)
            self.brodcast_game_state()
            idx = starting_player + 1
            while len(self.game_state['trick']) < 4:
                if idx > 3:
                    idx = 0
                self.game_state['current_player'] = self.game_state['players'][idx]
                player_in_action = self.get_current_player()
                self.brodcast_game_state()
                while True:
                    cards_on_hand = {idx: c for idx, c in enumerate(player_in_action.hand)}
                    card_to_play = cards_on_hand[int(input(f"{player_in_action.name}: Play one of the following cards {cards_on_hand}:"))]
                    card = player_in_action.play_card(card_to_play.name)
                    if suit_of_trick == 'Trump' and (card.is_trump or not any([x.is_trump for x in player_in_action.hand])):
                        break
                    elif suit_of_trick != 'Trump':
                        # residual cards of suit of the trick should be trump
                        residual_playable_cards = [x for x in player_in_action.hand if x.suit == suit_of_trick and not x.is_trump] 
                        if len(residual_playable_cards) == 0 or (card.suit == suit_of_trick and not card.is_trump):
                            break
                    print('Your card did not match the criteria for following the trick. Please play another card.')
                    player_in_action.hand.append(card)
                
                # todo update game state when a call is made
                self.update_game_state(idx=idx, card=card, call=None)
                self.brodcast_game_state()
                idx += 1
            
            self.update_game_state(idx=starting_player, trick=self.game_state['trick'])
            self.brodcast_game_state()
            player_in_action = self.get_current_player()
            
            if not len(player_in_action.hand):
                self.round_finished = True
                      
        for player in self.game_state['players']:
            print(f'Player: {player.name}\t|\tTeam: {player.team}\t|\tPoints: {player.round_points}')    
        
        game_results, winner = self.on_round_end()
        round_game_points = sum([x[1] for x in game_results])
        for player in self.game_state['players']:
            player.game_points += round_game_points if player.team == winner else -round_game_points
        self.brodcast_game_state()
        print(f'\nWinner:\t{winner}\n ---------------------- \n')
        for result in game_results:
            print(f'{result[0]} \t {result[1]}')
        print(f'Sum:\t{round_game_points}')

    def on_round_end(self) -> tuple[tuple[str, int], str]:
        # check for announcements of Re or Contra etc.
        re_points = sum([player.round_points for player in self.game_state['players'] if player.team == 'Re'])
        contra_points = sum([player.round_points for player in self.game_state['players'] if player.team == 'Contra']) # could also be 240 - re_points
        top_re_call = min(self.game_state['re_calls']) if len(self.game_state['re_calls']) else None
        top_contra_call = min(self.game_state['contra_calls']) if len(self.game_state['contra_calls']) else None
        game_points = [('Won', 1)]
        threshold = 121
        if top_re_call is not None and top_contra_call is not None:
            if contra_points >= top_re_call and re_points >= top_contra_call: # special case now only the team with the higher points get game points based on their round points and game points will be added/subtracted if the team reaches 30 over the announcement of the other team 
                # 30 point steps against call of the other team
                contra_game_points = (contra_points - top_re_call) // 30 if (contra_points - top_re_call) // 30 > 0 else 0
                re_game_points = (re_points - top_contra_call) // 30 if (re_points - top_contra_call) // 30 > 0 else 0
                
                contra_game_points = -contra_game_points if re_points > contra_points else contra_points
                re_game_points = -re_game_points if re_points < contra_points else re_points
                
                if contra_game_points != 0:
                    game_points.append((f'Contra got +{30*abs(contra_game_points)} against no {top_re_call}', contra_game_points))
                if re_game_points != 0:
                    game_points.append((f'Re got +{30*abs(re_game_points)} against no {top_contra_call}', re_game_points))
                
                self.game_state['re_calls'].clear
                self.game_state['contra_calls'].clear            
            else:
                re_won = re_points >= top_contra_call and contra_points < top_re_call
            # check which team has the lower call
        elif top_re_call is not None:
            game_points.append(('Re called', 1))
            threshold = top_re_call
            re_won = contra_points >= threshold
        elif top_contra_call is not None:
            game_points.append(('Contra called', 1))
            threshold = top_contra_call
            re_won = re_points >= threshold            
        else:
            re_won = re_points >= threshold
        
        re_calls_game_points = len(self.game_state['re_calls']) - 1
        contra_calls_game_points = len(self.game_state['contra_calls']) - 1
        if re_calls_game_points > 0:
            game_points.append((f'No {120 - re_calls_game_points*30} called', re_calls_game_points))
        if contra_calls_game_points > 0:
            game_points.append((f'No {120 - contra_calls_game_points*30} called', contra_calls_game_points))
        
        winner_points = re_points    
        if not re_won:
            winner_points = contra_points
            game_points.append(('Against the elders', 1))
        
        points_game_points = (winner_points - 120) // 30 
        if points_game_points > 0:
            game_points.append((f'No {120 - points_game_points*30} achieved', points_game_points))
        
        # reset the player's round points
        for player in self.game_state['players']:
            player.round_points = 0
           
        return (game_points, 'Re') if re_won else (game_points, 'Contra')
         
        
        # check for bonus points 
        

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
