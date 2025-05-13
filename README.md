# Chess Puzzle Solver

This program fetches daily chess puzzles from Chess.com, solves them using Stockfish, and creates a visual recording of the solution.

## Prerequisites

- Python 3.8 or higher
- Stockfish chess engine installed
- Chess piece images in the `images` directory

## Setup

1. Install the required Python packages:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with the following variables:
```
STOCKFISH_PATH=/path/to/your/stockfish
RECORDING_FPS=12
MOVE_DELAY=1.0
PIECES_DIR=images
```

3. Ensure you have chess piece images in the `images` directory with the following naming convention:
- White pieces: `wp.png`, `wn.png`, `wb.png`, `wq.png`, `wk.png`, `wr.png`
- Black pieces: `bp.png`, `bn.png`, `bb.png`, `bq.png`, `bk.png`, `br.png`

## Usage

Run the program:
```bash
python solve_puzzle.py
```

The program will:
1. Fetch the daily puzzle from Chess.com
2. Solve it using Stockfish
3. Display the solution in a graphical interface
4. Record the solution to `puzzle_solution.avi`

## Features

- Fetches daily puzzles from Chess.com
- Uses Stockfish engine for solving
- Visual board display with piece movement animation
- Screen recording of the solution
- Configurable settings via environment variables

## Error Handling

The program includes error handling for:
- Failed API requests
- Missing piece images
- Screen recording issues
- Invalid puzzle data 