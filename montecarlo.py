import math
import random
import numpy as np
import pygame
import ctypes

class Connect4():
    """
    Class to manage the Connect 4 game state and user interaction.

    Attributes:
        rows (int): Number of rows in the game board.
        cols (int): Number of columns in the game board.
        cell_size (int): Size of each cell in pixels.
        width (int): Width of the game window in pixels.
        height (int): Height of the game window in pixels.
        display (pygame.Surface): Pygame display surface for the game.
        font (pygame.Font): Pygame font for rendering text.
        board (np.ndarray): Current state of the game board.
        cur_player (int): Current player (1 or 2).
        overselection (int): Variable to track menu navigation.
        is_game_over (bool): Flag indicating if the game is over.
        play (bool): Flag to control the main game loop.
        winner (int or None): Winner of the game, if any.
        draw (bool): Flag indicating if the game ended in a draw.
        colors (dict): Color mapping for game elements.
    """
    def __init__(self):
        """Initialize game attributes and pygame settings."""
        ctypes.windll.user32.SetProcessDPIAware()
        pygame.init()
        pygame.display.set_caption("Connect 4")

        self.rows = 6
        self.cols = 7
        self.cell_size = 100
        self.width = self.cols * self.cell_size
        self.height = (self.rows + 1) * self.cell_size
        self.display = pygame.display.set_mode((self.width, self.height))
        self.font = pygame.font.Font(None, 50)
        self.board = np.zeros(([self.rows, self.cols]), dtype=int)
        self.cur_player = 1
        self.overselection = 0
        self.is_game_over = False
        self.play = True
        self.winner = None
        self.draw = False

        self.colors = {
            "background": (78, 132, 198),
            "chips": [(0, 0, 0), (212, 98, 96), (255, 255, 105)]
        }

    def drawboard(self, player = 1, chip_position = 3):
        """
        Draw the game board and player chips.

        Args:
            player (int): Number to indicate which player's chip to draw (default is 1).
            chip_position (int): Column index for the chip position (default is 3).
        """
        self.display.fill(self.colors["background"])
        if player == 1:
            pygame.draw.circle(self.display, self.colors["chips"][player],
                                   (chip_position * self.cell_size + self.cell_size // 2, 
                                    self.cell_size // 2),
                                   self.cell_size // 2 - 5)
        for row in range(self.rows):
            for col in range(self.cols):
                pygame.draw.circle(self.display,
                                   self.colors["chips"][self.board[row, col]], 
                                   (col * self.cell_size + self.cell_size // 2, 
                                    (row + 1) * self.cell_size + self.cell_size // 2), 
                                    self.cell_size // 2 - 5)
        pygame.display.flip()

    def playermove(self, player):
        """
        Handle player input and update the board.

        Args:
            player (int): The current player making a move.
        """
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
                        if (self.board[row + 1, chip_position] != 0 
                            and self.board[row, chip_position] == 0):
                            self.board[row, chip_position] = player
                            move = False
                            break
                    if self.board[5, chip_position] == 0:
                        self.board[5, chip_position] = player
                        move = False
            self.drawboard(player, chip_position)

    def botmove(self):
        """
        Handle the bot's move using the Monte Carlo Tree Search class.
        """
        self.drawboard(2)
        pygame.event.set_blocked(pygame.KEYDOWN)
        bot = MonteCarloBot(self.board.copy(), self)
        best_move = bot.mcts()
        self.board = best_move
        self.drawboard(2)
        pygame.event.set_allowed(pygame.KEYDOWN)

    def checkwinner(self, board):
        """
        Check if there's a winner on the board.

        Args:
            board (np.ndarray): Current game board state.

        Returns:
            int or None: Player number if a winner is found, otherwise None.
        """
        for row in range(0, self.rows):
            for col in range(0, self.cols-3):
                if (board[row, col] == board[row, col+1] 
                    and board[row, col] == board[row, col+2]
                    and board[row, col] == board[row, col+3]):
                    if board[row, col] != 0: 
                        return board[row, col]
        
        for row in range(0, self.rows-3):
            for col in range(0, self.cols):
                if (board[row, col] == board[row+1, col] 
                    and board[row, col] == board[row+2, col]
                    and board[row, col] == board[row+3, col]):
                    if board[row, col] != 0: 
                        return board[row, col]

        for row in range(0, self.rows-3):
            for col in range(0, self.cols-3):
                if (board[row, col] == board[row+1, col+1] 
                    and board[row, col] == board[row+2, col+2]
                    and board[row, col] == board[row+3, col+3]):
                    if board[row, col] != 0: 
                        return board[row, col]
        
        for row in range(0, self.rows-3):
            for col in range(2, self.cols):
                if (board[row, col] == board[row+1, col-1] 
                    and board[row, col] == board[row+2, col-2]
                    and board[row, col] == board[row+3, col-3]):
                    if board[row, col] != 0: 
                        return board[row, col]
        return None
    
    def isdraw(self, board):
        """
        Check if the game is a draw.

        Args:
            board (np.ndarray): Current game board state.

        Returns:
            bool: True if the game is a draw, otherwise False.
        """
        return np.all(board != 0) and self.winner == None

    
    def playagainscreen(self):
        """
        Display the play again screen and handle input to restart or quit.
        """
        if self.draw == False: 
            text_surface = self.font.render("PLAYER " + str(self.winner) + " IS THE WINNER!!", True, (180, 180, 180))
            text_rect = text_surface.get_rect(center=(self.width // 2, 150))
            self.display.blit(text_surface, text_rect)
        else:
            text_surface = self.font.render("DRAW!!", True, (180, 180, 180))
            text_rect = text_surface.get_rect(center=(self.width // 2, 150))
            self.display.blit(text_surface, text_rect)
        text_surface = self.font.render("PLAY AGAIN??", True, (180, 180, 180))
        text_rect = text_surface.get_rect(center=(self.width // 2, 250))
        self.display.blit(text_surface, text_rect)
        text_surface = self.font.render("YES", True, (80, 80, 80))
        text_rect = text_surface.get_rect(center=((self.width // 2) - 100, 350))
        self.display.blit(text_surface, text_rect)
        text_surface = self.font.render("NO", True, (180, 180, 180))
        text_rect = text_surface.get_rect(center=((self.width // 2) + 100, 350))
        self.display.blit(text_surface, text_rect)
        
        decide = True
        while decide:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        text_surface = self.font.render("YES", True, (180, 180, 180))
                        text_rect = text_surface.get_rect(center=((self.width // 2) - 100, 350))
                        self.display.blit(text_surface, text_rect)
                        text_surface = self.font.render("NO", True, (60, 60, 60))
                        text_rect = text_surface.get_rect(center=((self.width // 2) + 100, 350))
                        self.display.blit(text_surface, text_rect)
                        self.overselection = 1
                    if event.key == pygame.K_LEFT:
                        text_surface = self.font.render("YES", True,(60, 60, 60))
                        text_rect = text_surface.get_rect(center=((self.width // 2) - 100, 350))
                        self.display.blit(text_surface, text_rect)
                        text_surface = self.font.render("NO", True, (180, 180, 180))
                        text_rect = text_surface.get_rect(center=((self.width // 2) + 100, 350))
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
        """
        Main game loop to control game flow and transitions.
        """
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
    """
    Class to represent a node in the Monte Carlo Tree.

    Attributes:
        prev (Node or None): Reference to the parent node.
        gamestate (np.ndarray): Game state at this node.
        sims (int): Number of simulations run for this node.
        value (float): Value of the node from simulations.
        player (int): Player whose turn it is in this state.
        terminal (bool): Flag indicating if this node is terminal.
        evaluated (bool): Flag indicating if the node has been evaluated.
        next (list of Node or None): List of child nodes.
    """
    def __init__(self, gamestate, player, sims = 0, value = 0):
        """
        Initialize a Node instance.

        Args:
            gamestate (np.ndarray): Game state for this node.
            player (int): Player making a move at this node.
            sims (int): Number of simulations run for this node (default is 0).
            value (float): Value of the node (default is 0).
        """
        self.prev = None
        self.gamestate = gamestate
        self.sims = sims
        self.value = float(value)
        self.player = player
        self.terminal = False
        self.evaluated = False
        self.next = None

class MonteCarloBot():
    """
    Class to implement Monte Carlo Tree Search for Connect 4.

    Attributes:
        head (Node): Root node of the Monte Carlo Tree.
        totalsims (int): Total number of simulations run.
        connect4 (Connect4): Reference to the Connect4 game instance.
    """
    def __init__(self, gamestate, connect4):
        """
        Initialize the Monte Carlo Bot.

        Args:
            gamestate (np.ndarray): Initial game state.
            connect4 (Connect4): Reference to the Connect4 game instance.
        """
        player = 1
        self.head = Node(gamestate, player)
        self.head.evaluated = True
        self.totalsims = 0
        self.connect4 = connect4

    def UCB1(self, node):
        """
        Calculate the UCB1 value for a node.

        Args:
            node (Node): Node to calculate UCB1 for.

        Returns:
            float: UCB1 value of the node.
        """
        if node.sims == 0:
            return float('inf')
        simvalue = 0
        if node.sims != 0 and self.totalsims != 0:
            simvalue = math.sqrt(math.log(self.totalsims) / node.sims)
        exploration_factor = 4.0 / math.sqrt(node.sims + 1)
        return node.value + exploration_factor * simvalue
    
    def getavailablemoves(self, gamestate, player):
        """
        Get all possible moves for a player.

        Args:
            gamestate (np.ndarray): Current game state.
            player (int): Player making the move.

        Returns:
            list of np.ndarray: List of possible game states.
        """
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
        """
        Expand a node by generating child nodes.

        Args:
            node (Node): Node to expand.
        """
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
        """
        Backpropagate simulation results through the tree.

        Args:
            node (Node): Node to start backpropagation from.
        """
        while node is not self.head:
            if node.evaluated:
                node.prev.value = ((node.prev.value * node.prev.sims) + node.value) / (node.prev.sims + 1)
            node.prev.sims += 1
            node = node.prev
    
    def rollout(self, node):
        """
        Perform a random simulation (rollout) from the node.

        Args:
            node (Node): Node to perform the rollout from.

        Returns:
            float: Simulation result value.
        """
        board = node.gamestate
        player = node.player

        while True:
            availablemoves = self.getavailablemoves(board, player)
            if availablemoves == []:
                return 0

            """
            Additional setting to have random sim always make potetntial winning
            moves, makes algorithm much better at short term thinking but worse at
            long term thinking. Also increases run time by a lot.
            """
            #for move in availablemoves:
            #    winner = self.connect4.checkwinner(move)
            #    if winner: return winner * 2 - 3

            board = availablemoves[random.randint(0, len(availablemoves) - 1)]
            winner = self.connect4.checkwinner(board)
            draw = self.connect4.isdraw(board)
            if winner:
                return winner * 2 - 3
            if draw:
                return 0
            player = 3 - player

    def selection(self, node):
        """
        Select the best child node using UCB1.

        Args:
            node (Node): Node to select a child from.

        Returns:
            Node: Best child node.
        """
        if node.next is None:
            return node

        child_UCB1 = [self.UCB1(child) for child in node.next]

        best_value = max(child_UCB1)
        best_node_index = child_UCB1.index(best_value)
        best_node = node.next[best_node_index]

        return self.selection(best_node)
        
    def mcts(self):
        """
        Perform Monte Carlo Tree Search to determine the best move.

        Returns:
            np.ndarray: Game state after the best move.
        """
        sim = 0

        while sim <= 10000:
            #if sim > 1:
                #print("Node values: " + " ".join([str(node.value) for node in self.head.next]), end = '\r')
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
        #print('')

        
        first_moves_list = self.head.next
        first_moves_num_sims = [move.sims for move in first_moves_list]
        most_sims = max(first_moves_num_sims)
        best_move_index = first_moves_num_sims.index(most_sims)
        move = first_moves_list[best_move_index]

        return move.gamestate
        
if __name__ == "__main__":
    """
    Entry point for the Connect 4 game.
    """
    game = Connect4()
    game.run()
