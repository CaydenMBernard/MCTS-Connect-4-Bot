import math
import random
import numpy as np
import pygame
import ctypes

class Connect4():
    def __init__(self):
        ctypes.windll.user32.SetProcessDPIAware()
        pygame.init()
        pygame.display.set_caption("Connect 4")

        self.rows = 6
        self.cols = 7
        self.cell_size =200
        self.width = self.cols * self.cell_size
        self.height = (self.rows + 1) * self.cell_size
        self.display = pygame.display.set_mode((self.width, self.height))
        self.font = pygame.font.Font(None, 100)
        self.board = np.zeros(([self.rows, self.cols]), dtype=int)
        self.cur_player = 1
        self.overselection = 0
        self.is_game_over = False
        self.play = True
        self.winner = None
        self.draw = False
        self.columnstatus = np.zeros(self.cols)

        self.colors = {
            "background": (78, 132, 198),
            "chips": [(0, 0, 0), (212, 98, 96), (255, 255, 105)]
        }

    def drawboard(self, player = 1, chip_position = 3):
        self.display.fill(self.colors["background"])
        if player == 1:
            pygame.draw.circle(self.display, self.colors["chips"][player],
                                   (chip_position * self.cell_size + self.cell_size // 2, self.cell_size // 2),
                                   self.cell_size // 2 - 5)
        for row in range(self.rows):
            for col in range(self.cols):
                pygame.draw.circle(self.display, self.colors["chips"][self.board[row, col]], 
                                   (col * self.cell_size + self.cell_size // 2, (row + 1) * self.cell_size + self.cell_size // 2), self.cell_size // 2 - 5)
        pygame.display.flip()

    def playermove(self, player):
        move = True
        chip_position = 3
        self.drawboard(player, chip_position)
        pygame.display.flip()

        while move:
            event = pygame.event.wait()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT and chip_position < 6:
                    chip_position += 1
                if event.key == pygame.K_LEFT and chip_position > 0:
                    chip_position -= 1
                if event.key == pygame.K_SPACE:
                    for row in range(0, self.rows - 1):
                        if self.board[row + 1, chip_position] != 0 and self.board[row, chip_position] == 0:
                            self.board[row, chip_position] = player
                            move = False
                            break
                    if self.board[5, chip_position] == 0:
                        self.board[5, chip_position] = player
                        move = False
            self.drawboard(player, chip_position)

    def botmove(self):
        self.drawboard(2)
        pygame.event.set_blocked(pygame.KEYDOWN)
        bot = MonteCarloBot(self.board.copy(), self)
        best_move = bot.mcts()
        self.board = best_move
        self.drawboard(2)
        pygame.event.set_allowed(pygame.KEYDOWN)

    def checkwinner(self, board):
        for row in range(0, self.rows):
            for col in range(0, self.cols-3):
                if (board[row, col] == board[row, col+1] and board[row, col] == board[row, col+2]
                     and board[row, col] == board[row, col+3]):
                    if board[row, col] != 0: 
                        return board[row, col]
        
        for row in range(0, self.rows-3):
            for col in range(0, self.cols):
                if (board[row, col] == board[row+1, col] and board[row, col] == board[row+2, col]
                     and board[row, col] == board[row+3, col]):
                    if board[row, col] != 0: 
                        return board[row, col]

        for row in range(0, self.rows-3):
            for col in range(0, self.cols-3):
                if (board[row, col] == board[row+1, col+1] and board[row, col] == board[row+2, col+2]
                     and board[row, col] == board[row+3, col+3]):
                    if board[row, col] != 0: 
                        return board[row, col]
        
        for row in range(0, self.rows-3):
            for col in range(2, self.cols):
                if (board[row, col] == board[row+1, col-1] and board[row, col] == board[row+2, col-2]
                     and board[row, col] == board[row+3, col-3]):
                    if board[row, col] != 0: 
                        return board[row, col]
        return None
    
    def isdraw(self, board):
        full = 1

        for row in range(self.rows):
            for col in range(self.cols):
                if board[row, col] == 0: full = 0

        if full == 1 and self.winner == None:
            return True
        return False

    
    def playagainscreen(self):
        if self.draw == False: 
            text_surface = self.font.render("PLAYER " + str(self.winner) + " IS THE WINNER!!", True, (180, 180, 180))
            text_rect = text_surface.get_rect(center=(self.width // 2, 300))
            self.display.blit(text_surface, text_rect)
        else:
            text_surface = self.font.render("DRAW!!", True, (180, 180, 180))
            text_rect = text_surface.get_rect(center=(self.width // 2, 300))
            self.display.blit(text_surface, text_rect)
        text_surface = self.font.render("PLAY AGAIN??", True, (180, 180, 180))
        text_rect = text_surface.get_rect(center=(self.width // 2, 500))
        self.display.blit(text_surface, text_rect)
        text_surface = self.font.render("YES", True, (80, 80, 80))
        text_rect = text_surface.get_rect(center=((self.width // 2) - 200, 700))
        self.display.blit(text_surface, text_rect)
        text_surface = self.font.render("NO", True, (180, 180, 180))
        text_rect = text_surface.get_rect(center=((self.width // 2) + 200, 700))
        self.display.blit(text_surface, text_rect)
        
        decide = True
        while decide:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        text_surface = self.font.render("YES", True, (180, 180, 180))
                        text_rect = text_surface.get_rect(center=((self.width // 2) - 200, 700))
                        self.display.blit(text_surface, text_rect)
                        text_surface = self.font.render("NO", True, (60, 60, 60))
                        text_rect = text_surface.get_rect(center=((self.width // 2) + 200, 700))
                        self.display.blit(text_surface, text_rect)
                        self.overselection = 1
                    if event.key == pygame.K_LEFT:
                        text_surface = self.font.render("YES", True,(60, 60, 60))
                        text_rect = text_surface.get_rect(center=((self.width // 2) - 200, 700))
                        self.display.blit(text_surface, text_rect)
                        text_surface = self.font.render("NO", True, (180, 180, 180))
                        text_rect = text_surface.get_rect(center=((self.width // 2) + 200, 700))
                        self.display.blit(text_surface, text_rect)
                        self.overselection = 0
                    if event.key == pygame.K_SPACE:
                        if self.overselection == 0:
                            self.board = np.zeros(([self.rows, self.cols]), dtype = int)
                            self.is_game_over = False
                            self.winner = None
                            self.draw = False
                            decide = False
                        else: 
                            self.play = False
                            decide = False
            pygame.display.flip()

    def run(self):
        self.drawboard(1, 3)
        while self.play == True:
            while self.is_game_over != True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.play = False 
                if self.cur_player == 1:
                    self.playermove(self.cur_player)
                else:
                    self.botmove()
                winner = self.checkwinner(self.board)
                if winner:
                    self.winner = winner
                    self.is_game_over = True
                    print(self.board)
                draw = self.isdraw(self.board)
                if draw:
                    self.draw = True
                    self.is_game_over = True
                    print(self.board)
                self.cur_player = 3 - self.cur_player
            self.playagainscreen()
        pygame.quit()

class Node():
    def __init__(self, gamestate, player, sims = 0, value = 0):
        self.prev = None
        self.gamestate = gamestate
        self.sims = sims
        self.value = np.float64(value)
        self.player = player
        self.terminal = False
        self.evaluated = False
        self.next = None

class MonteCarloBot():
    def __init__(self, gamestate, connect4):
        player = 1
        self.head = Node(gamestate, player)
        self.head.evaluated = True
        self.totalsims = 0
        self.connect4 = connect4

    def UCB1(self, node):
        if node.sims == 0:
            return float('inf')
        simvalue = 0
        if node.sims != 0 and self.totalsims != 0:
            simvalue = math.sqrt(math.log(self.totalsims) / node.sims)
        exploration_factor = 4.0 / math.sqrt(node.sims + 1)
        return node.value + exploration_factor * simvalue
    
    def getavailablemoves(self, gamestate, player):
        availablemoves = []
        rows, cols = 6, 7

        for row in range(rows - 1):
            for col in range(cols):
                if gamestate[row + 1, col] != 0 and gamestate[row, col] == 0:
                    new_gamestate = gamestate.copy()
                    new_gamestate[row, col] = player
                    availablemoves.append(new_gamestate)

        for col in range(cols):
            if gamestate[5, col] == 0:
                new_gamestate = gamestate.copy()
                new_gamestate[5, col] = player
                availablemoves.append(new_gamestate)

        return availablemoves

    
    def expansion(self, node):
        children = []
        player = 3 - node.player
        availablemoves = self.getavailablemoves(node.gamestate, player)

        for move in availablemoves:
            child = Node(move, player)
            child.prev = node
            winner = self.connect4.checkwinner(move)
            draw = self.connect4.isdraw(move)
            if winner:
                child.terminal = True
                child.value = 2 * winner - 3
                child.sims = 1
                child.evaluated = True
                self.backpropogation(child)
            if draw:
                child.terminal = True
                child.value = 0
                child.sims = 1
                child.evaluated = True
                self.backpropogation(child)
            children.append(child)
        
        node.next = children

    def backpropogation(self, node):
        while node is not self.head:
            if node.evaluated:
                node.prev.value = ((node.prev.value * node.prev.sims) + node.value) / (node.prev.sims + 1)
            node.prev.sims += 1
            node = node.prev
    
    def rollout(self, node):
        board = node.gamestate
        player = node.player

        while True:
            availablemoves = self.getavailablemoves(board, player)
            if availablemoves == []:
                return 0

            for move in availablemoves:
                winner = self.connect4.checkwinner(move)
                if winner: return winner * 2 - 3

            board = availablemoves[random.randint(0, len(availablemoves) - 1)]
            winner = self.connect4.checkwinner(board)
            draw = self.connect4.isdraw(board)
            if winner:
                return winner * 2 - 3
            if draw:
                return 0
            player = 3 - player

    def selection(self, node):
        if node.next is None:
            return node

        child_UCB1 = [self.UCB1(child) for child in node.next]

        best_value = max(child_UCB1)
        best_node_index = child_UCB1.index(best_value)
        best_node = node.next[best_node_index]

        return self.selection(best_node)
        
    def mcts(self):
        sim = 0

        while sim <= 1000:
            if sim > 1:
                print("Node values: " + " ".join([str(node.value) for node in self.head.next]), end = '\r')
            base = self.head
            node = self.selection(base)
            if node.terminal:
                node.sims += 1
                self.totalsims += 1
                if node.evaluated: self.backpropogation(node)
            elif node.sims > 0:
                self.expansion(node)
            else:
                value = self.rollout(node)
                node.value = value
                node.sims = 1
                self.totalsims += 1
                node.evaluated = True
                if node.evaluated: self.backpropogation(node)
            sim += 1
        
        first_moves_list = self.head.next
        first_moves_num_sims = [move.sims for move in first_moves_list]
        most_sims = max(first_moves_num_sims)
        best_move_index = first_moves_num_sims.index(most_sims)
        move = first_moves_list[best_move_index]

        return move.gamestate
        
if __name__ == "__main__":
    game = Connect4()
    game.run()