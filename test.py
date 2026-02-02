def print_board(board):
    for r in range(9):
        if r % 3 == 0 and r != 0:
            print("-" * 21)

        for c in range(9):
            if c % 3 == 0 and c != 0:
                print("|", end=" ")

            print(board[r][c] if board[r][c] != 0 else ".", end=" ")
        print()


def find_empty(board):
    """Finds an empty cell (0 means empty). Returns (row, col) or None."""
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return r, c
    return None


def is_valid(board, row, col, num):
    """Checks if placing num at (row, col) is valid."""

    # Check row
    if num in board[row]:
        return False

    # Check column
    for r in range(9):
        if board[r][col] == num:
            return False

    # Check 3x3 subgrid
    start_row = (row // 3) * 3
    start_col = (col // 3) * 3

    for r in range(start_row, start_row + 3):
        for c in range(start_col, start_col + 3):
            if board[r][c] == num:
                return False

    return True


def solve_sudoku(board):
    """Solves Sudoku using backtracking. Returns True if solved."""
    empty = find_empty(board)

    # If no empty cell, sudoku solved
    if not empty:
        return True

    row, col = empty

    for num in range(1, 10):
        if is_valid(board, row, col, num):
            board[row][col] = num

            if solve_sudoku(board):
                return True

            # Backtrack
            board[row][col] = 0

    return False


if __name__ == "__main__":
    board = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],

        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],

        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]

    print("Before solving:\n")
    print_board(board)

    if solve_sudoku(board):
        print("\n✅ Solved Sudoku:\n")
        print_board(board)
    else:
        print("\n❌ No solution exists.")
