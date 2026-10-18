import pygame as pg
from random import shuffle
from os.path import isfile
from os import remove, close
from copy import deepcopy

pg.mixer.init()

draw_sound = pg.mixer.Sound("assets/sounds/draw_card.mp3")
play_sound = pg.mixer.Sound("assets/sounds/playing_card.mp3")
vamp_card_sound = pg.mixer.Sound("assets/sounds/drain_card.mp3")
ch_dir_sound = pg.mixer.Sound("assets/sounds/change_dir.mp3")
block_sound = pg.mixer.Sound("assets/sounds/block.mp3")

ch_dir_sound.set_volume(0.65)

class Game:
    '''
    This class represents a game, with the players, the deck, the stock,
    the player whose turn it is, etC.
    '''
    def __init__(self, P, deck, stock):
        self.direction = 1                      # 1 : Anticlockwise; -1 : clockwise
        self.current_player_id = 0              # Player currently playing
        self.save_player_id = 0
        self.players = P                        # All players
        self.deck = deck
        self.stock = stock
        self.remaining_players = 3
        self.remaining_players_save = 3
        self.last_stuff_played = (None, -1)

    def save(self):
        # Save of the num of remaining players and the currently playing player
        self.remaining_players_save = self.remaining_players
        self.save_player_id = self.current_player_id

    def alive_id(self):
        # Looks for the next player that can still play
        if self.remaining_players > 0:
            while not self.players[self.current_player_id].alive:
                self.current_player_id = (self.current_player_id + self.direction) % len(self.players)
        
    def check_victory(self):
        # Checks if someone won
        alive = [p for p in self.players if p.alive]

        if len(alive) == 1:                     # If only one player remains, they win
            return 0, [alive[0]]
        elif len(alive) == 0:                   # If no one remains, that's a draw
            return 1, []
        else:                                   # Otherwise, the game continues
            return None
    
    def draw_deck(self, surface:pg.Surface, sheet, x0:int = 490, y0:int = 360):
        # Draws the deck on screen, showing the back of the card on its top
        im_name = 'assets\\graphics\\card_4_0.png'
        if not isfile(im_name):
            cropped = sheet.crop((4*64, 0, 64*5-1, 95))
            cropped.save(im_name)
        card_im = pg.image.load(im_name).convert_alpha()
        card_rect = card_im.get_rect(center=(x0, y0))
        surface.blit(card_im, card_rect)
    
    def draw_stock(self, surface:pg.Surface, sheet, stock, x0:int = 790, y0:int = 360):
        # Draws the stock, like in UNO (the last played card is on top)
        color, id  = stock.stock[0].color, stock.stock[0].id
        im_name = 'assets\\graphics\\card_' + str(color) + '_' + str(id) + '.png'
        if not isfile(im_name):
            cropped = sheet.crop((64*color, 96*id, 64*(1+color)-1, 96*(1+id)-1))
            cropped.save(im_name)
        card_im = pg.image.load(im_name).convert_alpha()
        card_rect = card_im.get_rect(center=(x0, y0))
        surface.blit(card_im, card_rect)

    def draw_opponent(self, font:pg.font, surface:pg.Surface, opponent, position:str, screen_width:int, screen_height:int, sheet):
        # Draws all the opponents (actually their hands)
        im_name = 'assets\\graphics\\card_5_0.png'
        if not isfile(im_name):
            cropped = sheet.crop((64*4, 0, 64*5-1, 95))
            cropped.save(im_name)
        card_im = pg.image.load(im_name).convert_alpha()

        hp_surf = font.render(str(opponent.time_left//1000), False, 'white')

        card_w, card_h = 64, 96
        offset = 30

        n = len(opponent.hand)

        # Determining opponents' positions
        if position == "top":
            total_width = card_w + offset * (n - 1)
            total_height = 96
            rotated = pg.transform.rotate(card_im, 180)
            rotate_hp = hp_surf
            x0 = (screen_width - total_width) // 2
            y0 = 50
            xhp = screen_width // 2
            yhp = 166
        elif position == "left":
            total_height = card_h + offset * (n - 1)
            total_width = 96
            rotated = pg.transform.rotate(card_im, -90)
            rotate_hp = pg.transform.rotate(hp_surf, -90)
            x0 = 50
            y0 = screen_height // 2 - total_height // 2
            xhp = 171
            yhp = screen_height // 2
        elif position == "right":
            total_height = card_h + offset * (n - 1)
            total_width = 96
            rotated = pg.transform.rotate(card_im, 90)
            rotate_hp = pg.transform.rotate(hp_surf, 90)
            x0 = screen_width - 50 - total_width
            y0 = screen_height // 2 - total_height // 2
            xhp = screen_width - 75 - 96
            yhp = screen_height // 2
        else:
            return None

        # Drawing the opponents' hands
        hp_rect = rotate_hp.get_rect(center=(xhp, yhp))
        surface.blit(rotate_hp, hp_rect)
        for i in range(n):
            if position == 'top':
                x = x0 + i * offset
                y = y0
            else:
                x = x0
                y = y0 + i * offset
            if n == 0:
                return None
            surface.blit(rotated, (x, y))

    def play_history(self, font:pg.font, surface:pg.Surface,):
        # Describes the last action done
        card, pl = self.last_stuff_played
        if pl == -1:                    # At the beginning, when nothing has already happened
            return None    
        if pl == 0:                     # Main player's action
            if card == None:
                txt = font.render("You drew a card.", False, "white")
            else:
                txt = font.render("You played " + card_name(card), False, "white")
        elif pl > 0:                    # AI's
            if card == None:
                txt = font.render("AI " + str(pl) + " drew a card.", False, "white")
            else:
                txt = font.render("AI " + str(pl) + " played " + card_name(card) + ".", False, "white")
        txt_rect = txt.get_rect(center=(1060, 590))
        surface.blit(txt, txt_rect)
        txt = font.render((self.direction == 1) * "anti" + "clockwise", False, "white")
        txt_rect = txt.get_rect(center=(1060, 30))
        surface.blit(txt, txt_rect)

class Card:
    '''
    This class represents a card. A card is basically just a color
    and an id (a symbol)
    '''
    def __init__(self, color:int, id:int):
        '''
        color :
            0 : white; 1 : black; 2 : grey; 3 : beige; 4 : all colors
        id :
            0 : +5s; 1 : +10s; 2 : +15s; 3 : +20s;
            4 : -5s; 5 : -10s; 6 : -15s; 7 : -20s;
            8 : Way Changer; 9 : Block;
            10 : Time Drain; 11 : Time Swap
        '''
        self.color = color
        self.id = id

class Deck:
    '''
    This class represents a deck. A deck is just a list of cards
    '''
    def __init__(self, deck:list[Card]):
        self.deck = deck

    def cmp_decks(self, deck:list[Card]):
        '''
        Compares two decks of cards and returns how much
        they are similar to each other
        '''
        l, deck_len = 0, len(self.deck)
        for i in range(deck_len):
            if self.deck[i] != deck[i]:
                l += 1
        return l/deck_len

    def shuffle(self):
        # Shuffles the deck
        tmp_deck = self.deck[::]
        while self.cmp_decks(tmp_deck) < 0.75:
            shuffle(self.deck)

    def no_cards(self, stock):
        # When theres no more cards in the deck, we take the ones in the stock
        if not len(self.deck):
            stock.back_to_deck(self)

class Stock:
    '''
    This class represents the stock. That means where all the
    already used cards go. It is also a list of cards
    '''
    def __init__(self, stock:list[Card]):
            self.stock = stock

    def back_to_deck(self, deck:Deck):
        # When there are not enough cards in deck, we take them in the stock
        deck.deck += self.stock[1::]
        self.stock = [self.stock[0]]
        deck.shuffle()

class Player:
    '''
    This class represents the main player
    '''
    def __init__(self):
        self.hand = []
        self.time_left = 60000
        self.alive = True
        self.id = 0

    def find_id(self, game:Game):
        # Determines the position of the player in the list of all of them
        self.id = game.players.index(self)

    def is_alive(self, deck:Deck, game:Game):
        '''
        When the player has no more time left. All their cards
        are put back in the deck, and we go to the next player
        '''
        if self.time_left < 1 and self.alive:
            self.alive = False
            self.time_left = 0
            deck.deck += self.hand[::]
            shuffle(deck.deck)
            self.hand = []
            game.remaining_players -= 1
            l = len(game.players)
            if game.remaining_players > 0:
                while not game.players[game.current_player_id].alive:
                    game.current_player_id = (game.current_player_id+1)%l
            
    def update_time(self):
        # Update player's time left each second
        self.time_left -= 1000

    def draw(self, deck:Deck, game:Game):
        # To draw a card
        self.hand.append(deck.deck.pop(0))
        game.last_stuff_played = (None, 0)
        draw_sound.play(0, 1000, 0)

    def check_stock(self, card:Card, stock:Stock):
        # Checks if the card is allowed to be played
        return (card.color == 4) or (card.color == stock.stock[0].color) or (card.id == stock.stock[0].id)

    def play_card(self, card:Card, stock:Stock, P:list, game:Game):
        # Play a card from the hand
        if self.check_stock(card, stock):
            self.hand.remove(card)
            stock.stock = [card] + stock.stock
            card_effect(card, P, game.current_player_id, game)
            game.last_stuff_played = (card, 0)
            card_sound(card)
        else:
            return False

    def mouse(self, mx:int, my:int, x0:int = 450, y0:int = 500, offset:int = 35):
        # Checks mouse position over cards
        x0 = 640 - (len(self.hand) * offset + 64) / 2
        for i, _ in enumerate(self.hand):
            if (i != len(self.hand) - 1 and 0 <= mx - x0 - i*offset < offset and 0 <= my - y0 <= 96) or ((i == len(self.hand) - 1 and 0 <= mx - x0 - i*offset < 64 and 0 <= my - y0 <= 96)):
                return i
        return None

    def draw_hand(self, surface:pg.Surface, sheet, mx:int, my:int, x0:int = 450, y0:int = 500, offset:int = 35):
        # Draws the hand of the player
        x0 = 640 - (len(self.hand) * offset + 64) / 2
        for i, card in enumerate(self.hand):
            color, id = card.color, card.id
            im_name = 'assets\\graphics\\card_' + str(card.color) + '_' + str(card.id) + '.png'
            if not isfile(im_name):
                cropped = sheet.crop((64*color, 96*id, 64*(1+color)-1, 96*(1+id)-1))
                cropped.save(im_name)
            card_im = pg.image.load(im_name).convert_alpha()
            card_rect = card_im.get_rect(topleft=(x0 + i*offset, y0 - 20*(self.mouse(mx, my) == i)))
            surface.blit(card_im, card_rect)

    def draw_time_left(self, surface:pg.Surface, font:pg.font.Font, x0:int = 640, y0:int = 640):
        # Draws "HP"
        text = font.render('Time left : ' + str(self.time_left//1000), False, 'white')
        text_rect = text.get_rect(center=(x0, y0))
        surface.blit(text, text_rect)

class Ai(Player):
    '''
    This class represents the AI. Some of its actions are similar to the
    main player's ones. This is why they inherit from the Player class
    '''
    def __init__(self):
        super().__init__()

    def get_playable_cards(self, stock:Stock):
        # Playable cards for AI, according to the stock
        return [c for c in self.hand if self.check_stock(c, stock)]

    def evaluate(self, P:list[Player], stock:Stock):
        '''
        AI Evaluation Fnct. The AI evaluates the state of a turn by
        checking : 
            - its own time left;
            - the time left for its remaining opponents;
            - its number of different cards, and its ability to play later;
            - its "kill power";
            - the "dagerousness" of its hand.
        '''

        # AI time left
        score = 1.0 * self.time_left//1000
        # Opponents' time left
        score -= 0.7 * sum(p.time_left//1000 for p in P if p != self)
        # Variety of cards and possibility to play later
        score += 0.2 * len({c.color for c in self.hand}) + 0.3 * len(self.get_playable_cards(stock))

        # Bonus if there's a kill
        for p in P:
            if p != self and p.time_left <= 0:
                score += 10.0

        # Bonus if gets a strong card
        score += 0.4 * sum(1 for c in self.hand if c.id in [10, 11])

        return score

    def evaluate_card(self, card:Card, game:Game, stock:Stock):
        # The AI evaluates a card by evaluating how good will be the turn after
        game_copy, stock_copy = deepcopy(game), deepcopy(stock)
        card_effect(card, game_copy.players, game_copy.current_player_id, game_copy)
        return self.evaluate(game_copy.players, stock_copy)

    def choose_card(self, game:Game, stock:Stock):
        # Chooses the best card to play
        playable = self.get_playable_cards(stock)
        if playable == []:
            return None

        # Returns the card that maximizes the outcome
        return max(playable, key=lambda c: self.evaluate_card(c, game, stock))


    def ai_play(self, game:Game, stock:Stock, deck:Deck):
        # When ai plays
        card = self.choose_card(game, stock)
        if card is None:
            self.draw(deck, game)
            game.current_player_id = (game.current_player_id + game.direction) % len(game.players)
            game.last_stuff_played = (None, self.id)
        else:
            self.play_card(card, stock, game.players, game)
            game.last_stuff_played = (card, self.id)
                
def card_effect(card:Card, P:list[Player], i:int, game:Game):
    # After playing, activates the effects of cards
    l, p = len(P), P[i]

    if card.id < 4:
        p.time_left = min(90000, p.time_left + 5000 * (card.id + 1))
        game.current_player_id = (game.current_player_id + game.direction) % l

    if 3 < card.id < 8:
        j = i + game.direction
        while not P[j%l].alive:
            j += game.direction
        P[j%l].time_left -= 5000 * ((card.id + 1) % 4)
        game.current_player_id = (game.current_player_id + game.direction) % l

    if card.id == 8:
        game.direction *= -1
        if game.remaining_players > 2:
            game.current_player_id = (game.current_player_id + game.direction) % l

    if card.id == 9:
        if game.remaining_players > 2:
            game.current_player_id = (game.current_player_id + 2*game.direction) % game.remaining_players

    if card.id == 10:
        for q in P:
            if q.alive and q != p:
                q.time_left -= 5000
                p.time_left = min(90000, p.time_left + 5000)
        game.current_player_id = (game.current_player_id + game.direction) % l

    if card.id == 11:
        q, t = p, 0
        for r in P:
            if r.alive and r.time_left > t:
                q, t = r, r.time_left
            p.time_left, r.time_left = r.time_left, p.time_left
        game.current_player_id = (game.current_player_id + game.direction) % l

def card_name(card:Card):
    # To display card names
    colors = ['black', 'white', 'grey', 'beige']
    name = ''
    if card.id < 4:
        name = '+' + str(5 * (card.id + 1))
    if 3 < card.id < 8:
        name = '-' + str(5 * ((card.id + 1) % 4))
    if card.id == 8:
        name = 'Direction changer'
    if card.id == 9:
        name = 'Block'
    if card.id == 10:
        name = 'Vampire card'
    if card.id == 11:
        name = 'Time swap'
    return colors[card.color] + ' ' + name

def card_sound(card:Card):
    # Play sound when card is played
    if card.id == 8:
        ch_dir_sound.play(0, 500, 0)
    if card.id == 9:
        block_sound.play(0, 500, 0)
    if card.id == 10 or card.id == 11:
        vamp_card_sound.play(0, 1000, 0)
    play_sound.play(0, 1000, 0)
    