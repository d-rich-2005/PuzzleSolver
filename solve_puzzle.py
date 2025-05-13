import requests
import chess
import chess.engine
import pyautogui
import cv2
import numpy as np
import tkinter as tk
import time
import threading
import os
import webbrowser
from pathlib import Path
from dotenv import load_dotenv
from cairosvg import svg2png
from io import BytesIO, StringIO
from PIL import Image, ImageTk
from bs4 import BeautifulSoup
import json
import re
import chess.pgn

# Load environment variables
load_dotenv()

# Configuration
STOCKFISH_PATH = os.getenv('STOCKFISH_PATH', '/usr/local/bin/stockfish')
RECORDING_FPS = int(os.getenv('RECORDING_FPS', '12'))
MOVE_DELAY = float(os.getenv('MOVE_DELAY', '1.0'))
PIECES_DIR = Path(os.getenv('PIECES_DIR', 'images'))

def load_svg_as_photoimage(svg_path, size):
    """Load an SVG file and convert it to a PhotoImage."""
    with open(svg_path, 'rb') as svg_file:
        png_data = svg2png(file_obj=svg_file, output_width=size, output_height=size)
        image = Image.open(BytesIO(png_data))
        return ImageTk.PhotoImage(image)

def fetch_puzzle_data(url):
    """Fetch puzzle data from Chess.com API."""
    try:
        # Use the public puzzle API endpoint
        api_url = "https://api.chess.com/pub/puzzle"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://www.chess.com',
            'Referer': 'https://www.chess.com/'
        }
        
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        
        puzzle_data = response.json()
        if puzzle_data and 'fen' in puzzle_data:
            print(f"\nPuzzle Title: {puzzle_data.get('title', 'Untitled')}")
            return puzzle_data
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print("\nAccess to the puzzle API is restricted. Falling back to manual input.")
        else:
            print(f"Error fetching puzzle data: {e}")
        return None
    except Exception as e:
        print(f"Error fetching puzzle data: {e}")
        return None

def open_daily_puzzle():
    """Open the chess puzzle in the default web browser and get puzzle data."""
    # Try to fetch puzzle data automatically
    puzzle_data = fetch_puzzle_data(None)  # No URL needed for public API
    if puzzle_data:
        fen = puzzle_data['fen']
        url = puzzle_data.get('url', 'https://www.chess.com/daily-chess-puzzle')
        print(f"\nSuccessfully fetched puzzle data!")
        print(f"Opening puzzle in browser: {url}")
        webbrowser.open(url)
        return fen
    
    # Fallback to manual FEN input if automatic fetch fails
    print("\nCould not automatically fetch puzzle data.")
    print("Please get the FEN manually:")
    print("1. Click on the puzzle board")
    print("2. Click the 'Share' button")
    print("3. Click 'Copy FEN'")
    print("4. Paste the FEN below when prompted")
    
    fen = input("\nPaste the FEN here and press Enter when ready to see the solution: ")
    return fen

# Function to solve the puzzle using Stockfish
def solve_puzzle(fen):
    board = chess.Board(fen)
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    solution_moves = []

    while not board.is_game_over():
        result = engine.play(board, chess.engine.Limit(time=1.0))
        move = result.move
        if move is None:
            break
        solution_moves.append(move)
        board.push(move)

    engine.quit()
    return solution_moves

# Function to display the board using tkinter
def display_board(moves, fen, flip=False):
    try:
        board = chess.Board(fen)
        root = tk.Tk()
        root.title("Chess Puzzle Solution")
        canvas = tk.Canvas(root, width=480, height=480)
        canvas.pack()

        square_size = 60

        # Load images for pieces
        pieces_images = {}
        pieces = ['r', 'n', 'b', 'q', 'k', 'p']
        colors = ['w', 'b']
        
        for color in colors:
            for piece in pieces:
                filename = PIECES_DIR / f"{color}{piece}.svg"
                if not filename.exists():
                    raise FileNotFoundError(f"Image file {filename} not found")
                pieces_images[color + piece] = load_svg_as_photoimage(filename, square_size)

        def draw_board():
            colors = ["#F0D9B5", "#B58863"]
            for row in range(8):
                for col in range(8):
                    x1 = col * square_size
                    y1 = row * square_size
                    x2 = x1 + square_size
                    y2 = y1 + square_size
                    color = colors[(row + col) % 2]
                    canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)

        def draw_pieces():
            for row in range(8):
                for col in range(8):
                    if flip:
                        square = chess.square(col, row)
                    else:
                        square = chess.square(col, 7 - row)
                    piece = board.piece_at(square)
                    if piece:
                        color = 'w' if piece.color == chess.WHITE else 'b'
                        piece_type = piece.symbol().lower()
                        img = pieces_images.get(color + piece_type)
                        if img:
                            x = col * square_size
                            y = row * square_size
                            canvas.create_image(x, y, anchor=tk.NW, image=img)

        def update_board():
            if moves:
                move = moves.pop(0)
                board.push(move)
                draw_board()
                draw_pieces()
                root.after(int(MOVE_DELAY * 1000), update_board)
            else:
                print("Solution complete.")

        draw_board()
        draw_pieces()
        root.after(int(MOVE_DELAY * 1000), update_board)
        root.mainloop()
    except Exception as e:
        print(f"Error during board display: {e}")

# Function to record the screen
def record_screen(duration, output_file):
    try:
        screen_size = pyautogui.size()
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Use mp4v for MP4 files
        out = cv2.VideoWriter(output_file, fourcc, RECORDING_FPS, screen_size)

        start_time = time.time()
        while True:
            img = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            out.write(frame)
            if time.time() - start_time > duration:
                break

        out.release()
        print(f"Recording saved to {output_file}")
    except Exception as e:
        print(f"Error during screen recording: {e}")
        if 'out' in locals():
            out.release()

def extract_solution_moves_from_pgn(pgn_str):
    """Extract the solution moves from the PGN string."""
    pgn_io = StringIO(pgn_str)
    game = chess.pgn.read_game(pgn_io)
    moves = []
    board = game.board()
    for move in game.mainline_moves():
        moves.append(move)
        board.push(move)
    return moves, game.headers.get('FEN', board.fen())

# Main function
def main():
    # Fetch puzzle data from Chess.com API
    puzzle_data = fetch_puzzle_data(None)
    if puzzle_data:
        pgn = puzzle_data.get('pgn')
        if pgn:
            moves, fen = extract_solution_moves_from_pgn(pgn)
            print(f"\nUsing Chess.com official solution moves.")
        else:
            print("No PGN found in puzzle data. Exiting...")
            return
    else:
        # Fallback to manual FEN input and Stockfish solution
        fen = open_daily_puzzle()
        if not fen:
            print("No FEN provided. Exiting...")
            return
        moves = solve_puzzle(fen)
        if not moves:
            print("No solution found.")
            return

    # Start screen recording in a separate thread
    duration = len(moves) * 1.5  # Estimate duration
    output_file = "puzzle_solution.mp4"
    recording_thread = threading.Thread(target=record_screen, args=(duration, output_file))
    recording_thread.start()

    # Display the board and solution
    # Always show the board flipped upside down (rank 8 at the bottom)
    flip = True
    display_board(moves, fen, flip=flip)

    recording_thread.join()

if __name__ == "__main__":
    main()
