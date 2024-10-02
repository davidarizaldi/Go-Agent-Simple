import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QMessageBox
from PyQt5.QtCore import Qt
from go import (
    initialize_board, display_board, is_valid_move, switch_player,
    capture_stones, minimax_ai_move, calculate_score, no_valid_moves
)

class GoGame(QMainWindow):
    def __init__(self, size=5):
        super().__init__()
        self.size = size
        self.board = initialize_board(size)
        self.current_player = 'X'
        self.prisoners = {'X': 0, 'O': 0}
        self.passes = 0

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Go Game')
        self.setGeometry(100, 100, 400, 400)

        self.grid_layout = QGridLayout()
        self.buttons = [[None for _ in range(self.size)] for _ in range(self.size)]

        for x in range(self.size):
            for y in range(self.size):
                button = QPushButton('')
                button.setFixedSize(50, 50)
                button.clicked.connect(lambda checked, x=x, y=y: self.make_move(x, y))
                self.buttons[x][y] = button
                self.grid_layout.addWidget(button, x, y)

        self.pass_button = QPushButton('Pass')
        self.pass_button.clicked.connect(self.pass_turn)
        self.grid_layout.addWidget(self.pass_button, self.size, 0, 1, self.size)

        container = QWidget()
        container.setLayout(self.grid_layout)
        self.setCentralWidget(container)

        self.update_board()

    def make_move(self, x, y):
        if is_valid_move(self.board, x, y, self.current_player):
            self.board[x][y] = self.current_player
            capture_stones(self.board, x, y, self.current_player, self.prisoners)
            self.current_player = switch_player(self.current_player)
            self.passes = 0
            self.update_board()
            self.check_game_over()
            self.ai_move()

    def pass_turn(self):
        self.passes += 1
        self.current_player = switch_player(self.current_player)
        self.update_board()
        self.check_game_over()
        self.ai_move()

    def ai_move(self):
        if self.current_player == 'O':
            move = minimax_ai_move(self.board, self.prisoners)
            if move != 'pass':
                x, y = move
                self.make_move(x, y)
            else:
                self.pass_turn()

    def update_board(self):
        for x in range(self.size):
            for y in range(self.size):
                button = self.buttons[x][y]
                if self.board[x][y] == 'X':
                    button.setStyleSheet("background-color: black;")
                elif self.board[x][y] == 'O':
                    button.setStyleSheet("background-color: white;")
                else:
                    button.setStyleSheet("")

    def check_game_over(self):
        if self.passes == 2:
            QMessageBox.information(self, "Game Over", "Both players passed!")
            self.calculate_final_scores()
        if no_valid_moves(self.board, switch_player(self.current_player)):
            QMessageBox.information(self, "Game Over", "No valid moves left! Game over!")
            self.calculate_final_scores()

    def calculate_final_scores(self):
        final_scores = calculate_score(self.board, self.prisoners)
        QMessageBox.information(self, "Final Scores", f"Final Scores:\nX: {final_scores['X']}\nO: {final_scores['O']}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = GoGame(size=5)  # Change the size as needed
    game.show()
    sys.exit(app.exec_())