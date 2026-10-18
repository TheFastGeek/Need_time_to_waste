from objects import *
from PIL.Image import open

pg.init()

WINDOW_W, WINDOW_H = 1280, 720
window = pg.display.set_mode((WINDOW_W, WINDOW_H))
pg.display.set_caption('Need time to waste')
clock = pg.time.Clock()
running = True
state = 'MENU'

MAIN_FONT = pg.font.Font('assets/fonts/PixelOperator.ttf', 25)
HP_FONT = pg.font.Font('assets/fonts/PixelOperator8_Bold.ttf', 18)

# Buttons
class Bouton:
    def __init__(self, texte, x, y, w, h):
        self.texte = texte
        self.rect = pg.Rect(x, y, w, h)
        self.couleur = (70, 70, 70)
        self.couleur_hover = (120, 120, 120)

    def draw(self, surface):
        souris = pg.mouse.get_pos()
        couleur = self.couleur_hover if self.rect.collidepoint(souris) else self.couleur

        pg.draw.rect(surface, couleur, self.rect)
        txt = MAIN_FONT.render(self.texte, True, (255, 255, 255))
        surface.blit(txt, (self.rect.x + 20, self.rect.y + 10))

    def clicked(self):
        return self.rect.collidepoint(pg.mouse.get_pos())

# Creating the three buttons in the menu
bouton_joueur = Bouton("Play", 200, 80, 200, 60)
bouton_aide   = Bouton("Help", 200, 160, 200, 60)
bouton_quit   = Bouton("Quit", 200, 240, 200, 60)

running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        if event.type == pg.MOUSEBUTTONDOWN and state == 'MENU':
            if bouton_joueur.clicked():
                state = 'MAIN'
            if bouton_aide.clicked():
                state = 'HELP'
            if bouton_quit.clicked():
                running = False

    window.fill((50, 50, 50))

    txt = HP_FONT.render("Need Time To Waste", True, (255, 255, 255))
    txt_rect = txt.get_rect(center=(800, 300))
    window.blit(txt, txt_rect)

    txt = HP_FONT.render("By FastGeek", True, (255, 255, 255))
    txt_rect = txt.get_rect(center=(800, 330))
    window.blit(txt, txt_rect)

    txt = HP_FONT.render("For the GMTK Game Jam 2026", True, (255, 255, 255))
    txt_rect = txt.get_rect(center=(800, 360))
    window.blit(txt, txt_rect)

    if state == 'MENU':
        bouton_joueur.draw(window)
        bouton_aide.draw(window)
        bouton_quit.draw(window)

    if state == 'HELP':
        txt = MAIN_FONT.render("You start playing cards with your friends, but you don't really have time to do so...", True, (255, 255, 255))
        txt_rect = txt.get_rect(topleft=(5, 0))
        window.blit(txt, txt_rect)

        txt = MAIN_FONT.render("So your goal is not to run out of time !", True, (255, 255, 255))
        txt_rect = txt.get_rect(topleft=(5, 30))
        window.blit(txt, txt_rect)

        txt = MAIN_FONT.render("This game is like UNO. You have to play cards with same symbol or same color than the one on the stock.", True, (255, 255, 255))
        txt_rect = txt.get_rect(topleft=(5, 60))
        window.blit(txt, txt_rect)

        txt = MAIN_FONT.render("But don't worry if you run out of cards... and don't be happy either : you win only if you're the last player with remaining time.", True, (255, 255, 255))
        txt_rect = txt.get_rect(topleft=(5, 90))
        window.blit(txt, txt_rect)

        txt = MAIN_FONT.render("Card effects :", True, (255, 255, 255))
        txt_rect = txt.get_rect(topleft=(5, 125))
        window.blit(txt, txt_rect)

        txt = MAIN_FONT.render("- Cards with symbol '+' add you seconds.", True, (255, 255, 255))
        txt_rect = txt.get_rect(topleft=(30, 150))
        window.blit(txt, txt_rect)

        txt = MAIN_FONT.render("- Cards with symbol '-' remove seconds from your nearby opponent.", True, (255, 255, 255))
        txt_rect = txt.get_rect(topleft=(30, 190))
        window.blit(txt, txt_rect)

        txt = MAIN_FONT.render("- Cards with the interdiction symbol prevent your nearby opponent from playing.", True, (255, 255, 255))
        txt_rect = txt.get_rect(topleft=(30, 230))
        window.blit(txt, txt_rect)

        txt = MAIN_FONT.render("- Cards with the simple double arrow symbol change the direction of the game.", True, (255, 255, 255))
        txt_rect = txt.get_rect(topleft=(30, 270))
        window.blit(txt, txt_rect)

        txt = MAIN_FONT.render("- Cards with the double arrow symbol AND the clock swaps your time with the player with most seconds.", True, (255, 255, 255))
        txt_rect = txt.get_rect(topleft=(30, 310))
        window.blit(txt, txt_rect)

        txt = MAIN_FONT.render("- Cards with the bat symbol steals 5 seconds to every opponent.", True, (255, 255, 255))
        txt_rect = txt.get_rect(topleft=(30, 350))
        window.blit(txt, txt_rect)

        txt = MAIN_FONT.render("Have fun !", True, (255, 255, 255))
        txt_rect = txt.get_rect(topleft=(5, 500))
        window.blit(txt, txt_rect)

        txt = MAIN_FONT.render("Press [SPACE] to go back to main menu", True, (255, 255, 255))
        txt_rect = txt.get_rect(center=(640, 600))
        window.blit(txt, txt_rect)

        keys = pg.key.get_pressed()
        if keys[pg.K_SPACE]:
            state = 'MENU'

    if state == 'MAIN':
        AI_turn = False
        tm = 0
        cards_sheet = open('assets/graphics/cards_sheet.png')

        # Creating the deck
        bgn_deck = []                       # Creating the list of all cards
        cards_amounts = [8, 3, 2, 1, 8, 3, 1, 0, 8, 4, 1, 1]
        for color in range(4):
            for id in range(12): #len(cards_amounts)):
                for i in range(cards_amounts[id]):
                    bgn_deck.append(Card(color, id))

        deck = Deck(bgn_deck)               # Initializing the deck
        deck.shuffle()
        stock = Stock([deck.deck.pop(0)])   # The first card of the deck is placed as a reference card

        # Initializing the players
        player1 = Player(); ai1 = Ai(); ai2 = Ai(); ai3 = Ai()

        # Initializing the game
        game = Game([player1, ai1, ai2, ai3], deck, stock)
        # Deck drawing
        for i in range(7):
            for p in game.players:
                p.draw(deck, game)
        # Checking the ids
        for p in game.players:
            p.find_id(game)

        # This event acts as a countdown for everyone
        TICK_EVENT = pg.USEREVENT + 1
        pg.time.set_timer(TICK_EVENT, 1000)

        running_main = True
        while running_main:
            game.save()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    # Window closed
                    running_main = False
                    running = False
                    state = 'MENU'

                if event.type == TICK_EVENT:
                    # Each second, everyone looses one second
                    for p in game.players:
                        if p.alive:
                            p.update_time()
                        
                if event.type == pg.MOUSEBUTTONDOWN and game.current_player_id == 0 and player1.alive:
                    mx, my = pg.mouse.get_pos()
                    idx = player1.mouse(mx, my)
                    if idx is not None:
                        card = player1.hand[idx]
                        try:
                            player1.play_card(card, stock, game.players, game)
                        except False:
                            pass
                    elif -32 < mx - 490 < 32 and -48 < my - 360 < 48:
                        player1.draw(deck, game)
                        game.current_player_id = (game.current_player_id + game.direction) % len(game.players)

            # Checks who is alive among all the players
            for p in game.players:
                p.is_alive(deck, game)
                
            window.fill((50, 50, 50))  # Grey background

            game.draw_deck(window, cards_sheet)
            game.draw_stock(window, cards_sheet, stock)

            abc = HP_FONT.render(str(game.current_player_id), False, "White")
            abc_rect = abc.get_rect(topleft=(20, 20))
            window.blit(abc, abc_rect)

            #Main player hand drawing
            mx, my = pg.mouse.get_pos()
            player1.draw_hand(window, cards_sheet, mx, my)
            player1.draw_time_left(window, HP_FONT)

            #mx, my = pg.mouse.get_pos()
            # AIs hands drawing
            for i in range(1, 4):
                pos = ['right', 'top', 'left']
                game.draw_opponent(HP_FONT, window, game.players[i], pos[i-1], WINDOW_W, WINDOW_H, cards_sheet)

            # AI's turn handling when it's not the main player's turn
            if game.current_player_id != 0:
                # If it's AI turn, just change the variable to True
                if game.current_player_id == game.save_player_id and game.players[game.current_player_id].alive and not(AI_turn):
                    AI_turn = True
                if AI_turn:
                    # 1 second delay before the AI plays, so the game is "fairer"
                    if tm == 0:
                        tm = pg.time.get_ticks()
                    elif pg.time.get_ticks() - tm >= 1000:
                        game.players[game.current_player_id].ai_play(game, stock, deck)
                        tm = 0
                        AI_turn = False

            # Who's turn is it ? Tell us !
            if game.current_player_id == 0:
                txt_surf = HP_FONT.render("Your turn", False, 'white')
            elif game.current_player_id > 0:
                txt_surf = HP_FONT.render('AI ' + str(game.current_player_id) + "'s turn", False, 'white')
            txt_rect = txt_surf.get_rect(center=(WINDOW_W//2 + 420, WINDOW_H//2 + 200))
            window.blit(txt_surf, txt_rect)

            deck.no_cards(stock)                # In case there is no card left in the deck
            game.play_history(HP_FONT, window)  # History display
            game.alive_id()                     # Looking for the next player

            # Has someone won ?
            win = game.check_victory()
            if win != None:
                if win[0] == 0:
                    p = win[1][0]
                    if p.id == 0:
                        txt_surf = HP_FONT.render('Player won !', False, 'white')
                    else:
                        txt_surf = HP_FONT.render('AI ' + str(p.id) + ' won !', False, 'white')
                elif win[0] == 1:
                    txt_surf = HP_FONT.render('Draw !', False, 'white')
                txt_rect = txt_surf.get_rect(center=(WINDOW_W//2, WINDOW_H//2 + 100))
                window.blit(txt_surf, txt_rect)
                pg.display.flip()
                pg.time.delay(3500)
                running_main = False
                state = 'MENU'

            pg.display.flip()

        cards_sheet.close()
        for i in range(6):
            for j in range(12):
                filename = 'assets\\graphics\\card_' + str(i) + '_' + str(j) + '.png'
                if isfile(filename):
                    remove(filename)

    pg.display.flip()

pg.quit()