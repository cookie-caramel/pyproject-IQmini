# Pyproject-IQmini
A tile-based puzzle game with auto-solving functionality. Designed as a school project for practicing path-finding algorithms and UI logic implementation.

## Features
- 5x5 tile grid with obstacle support
- Block rotation and placement
- Real-time solvability hint system (can find a solution for about 70% puzzles at the beginning)
- Simple GUI (Pygame)
- Save and load possible
- Score Board

## Tech Stack
- Language: Python 3.x
- Libraries: Pygame, json
To install Pygame:
```bash
pip install pygme
```

## Auto-solving System
The solver uses backtracking with constraints (illegal positions, shape matching, and dead-end pruning).

## How to Run
```bash
python main.py
