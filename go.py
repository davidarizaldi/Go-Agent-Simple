import random

def initialize_board(size):
    """Initialize an empty Go board."""
    return [['.' for _ in range(size)] for _ in range(size)]

def display_board(board, prisoners):
    """Display the current state of the board."""
    size = len(board)
    print("  " + " ".join(str(i) for i in range(size)))
    for idx, row in enumerate(board):
        print(idx, " ".join(row))
    print(f"Prisoners - X: {prisoners['X']}, O: {prisoners['O']}")

def switch_player(current_player):
    """Switch the current player."""
    return 'O' if current_player == 'X' else 'X'

def is_valid_move(board, x, y, current_player):
    """Check if the move is valid (not out of bounds, not on an occupied space, and not suicidal)."""
    size = len(board)
    if x < 0 or x >= size or y < 0 or y >= size:
        return False
    if board[x][y] != '.':
        return False

    # Temporarily place the stone to check for liberties
    board[x][y] = current_player
    if is_group_captured(board, x, y, current_player):
        board[x][y] = '.'  # Remove the temporary stone
        return False

    # Restore the board state
    board[x][y] = '.'
    return True

def capture_stones(board, x, y, current_player, prisoners):
    """Capture opponent's stones and update the prisoners count."""
    opponent = 'O' if current_player == 'X' else 'X'
    captured = 0
    size = len(board)

    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < size and 0 <= ny < size and board[nx][ny] == opponent:
            if is_group_captured(board, nx, ny, opponent):
                captured += remove_group(board, nx, ny, opponent)

    prisoners[current_player] += captured
    return captured

def is_group_captured(board, x, y, player):
    """Check if a group of stones is captured (no liberties)."""
    visited = set()
    return not has_liberties(board, x, y, player, visited)

def has_liberties(board, x, y, player, visited):
    """Check if a group has any liberties."""
    if (x, y) in visited:
        return False
    visited.add((x, y))
    size = len(board)
    if board[x][y] == '.':
        return True
    if board[x][y] != player:
        return False

    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < size and 0 <= ny < size:
            if has_liberties(board, nx, ny, player, visited):
                return True
    return False

def remove_group(board, x, y, player):
    """Remove a group of stones from the board."""
    queue = [(x, y)]
    captured = 0
    while queue:
        cx, cy = queue.pop()
        if board[cx][cy] == player:
            board[cx][cy] = '.'
            captured += 1
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < len(board) and 0 <= ny < len(board) and board[nx][ny] == player:
                    queue.append((nx, ny))
    return captured

def random_ai_move(board):
    """Generate a random valid move for the AI."""
    size = len(board)
    if random.randint(1, 100) < 1:
        return 'pass'
    while True:
        x = random.randint(0, size - 1)
        y = random.randint(0, size - 1)
        if is_valid_move(board, x, y, 'O'):
            return x, y

def count_empty_areas(board, player):
    size = len(board)
    visited = set()
    score = 0

    def dfs(x, y):
        nonlocal surrounded
        if x < 0 or x >= size or y < 0 or y >= size or (x, y) in visited:
            return
        if board[x][y] == '.':
            visited.add((x, y))
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                dfs(x + dx, y + dy)
        else:
            if board[x][y] == player:
                surrounded = True

    for x in range(size):
        for y in range(size):
            if board[x][y] == '.' and (x, y) not in visited:
                surrounded = False
                dfs(x, y)
                if surrounded:
                    score += 1  # Count this area as a point

    return score

def calculate_score(board, prisoners):
    score = {'X': 0, 'O': 0}
    
    score['X'] += prisoners['X']
    score['O'] += prisoners['O']
    
    score['X'] += count_empty_areas(board, 'X')
    score['O'] += count_empty_areas(board, 'O')
    
    return score

def no_valid_moves(board, current_player):
    """Check if there are no valid moves left for the current player."""
    size = len(board)
    for x in range(size):
        for y in range(size):
            if is_valid_move(board, x, y, current_player):
                return False
    return True

def play_game(size=9):
    """Main function to play the Go game."""
    board = initialize_board(size)
    current_player = 'X'
    prisoners = {'X': 0, 'O': 0}
    passes = 0  # Count the number of consecutive passes

    while True:
        display_board(board, prisoners)
        if current_player == 'X':
            move_input = input(f"Player {current_player}, enter your move (row col) or 'pass' to skip: ")
            if move_input.lower() == 'pass':
                move = 'pass'
            else:
                try:
                    x, y = map(int, move_input.split())
                    move = (x, y)
                except ValueError:
                    print("Invalid input! Please enter row and column numbers or 'pass'.")
                    continue
        else:
            move = random_ai_move(board)
            if move != 'pass':
                x, y = move
                print(f"AI {current_player} plays at ({x}, {y})")

        if move == 'pass':
            print(f"Player {current_player} passes.")
            passes += 1
            current_player = switch_player(current_player)
        elif is_valid_move(board, x, y, current_player):
            board[x][y] = current_player
            capture_stones(board, x, y, current_player, prisoners)
            passes = 0
            current_player = switch_player(current_player)
        else:
            print("Invalid move! Try again.")
        
        if no_valid_moves(board, switch_player(current_player)):
            print(f"No valid moves left for {current_player}. Game over!")
            break
        
        # Check for consecutive passes
        if passes >= 2:
            print("Both players passed. Game over!")
            break

    # Calculate and display the final scores
    display_board(board, prisoners)
    final_scores = calculate_score(board, prisoners)
    print(f"Final Scores: X: {final_scores['X']}, O: {final_scores['O']}")

if __name__ == "__main__":
    play_game(5)