# πQ Memory Game

A memory game challenging users to recall digits of Pi.

## Project Structure

```
piQ/
├── animations.py         # Handles game animations
├── build.py              # Script to build standalone executable
├── game_logic.py         # Core game logic, Pi digits, high scores
├── main.py               # Main application entry point
├── pi_digits.txt         # Contains the first 5000 digits of Pi
├── piQ.spec              # PyInstaller specification file
├── piq.kv                # Kivy language file for UI layout and styling
├── requirements.txt      # Project dependencies
├── screens/
│   ├── __init__.py
│   ├── landing_screen.py  # Logic for the landing screen
│   ├── countdown_screen.py# Logic for the countdown screen
│   └── game_screen.py     # Logic for the main game screen
└── README.md             # Project overview and instructions
```

## Setup and Running (Development)

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the Application:**
    ```bash
    python main.py
    ```

## Packaging as Standalone Executable

You can create a standalone executable that works without Python installation:

1. **Using the build script:**
   ```bash
   python build.py
   ```
   This will:
   - Install required dependencies
   - Create a simple app icon if none exists
   - Run PyInstaller to package the application
   - Place the executable in the `dist` directory

2. **Manual packaging with PyInstaller:**
   ```bash
   # Install PyInstaller and dependencies
   pip install pyinstaller kivy_deps.sdl2 kivy_deps.glew
   
   # Run PyInstaller with the spec file
   pyinstaller piQ.spec
   ```

The packaged executable will:
- Run without requiring Python or dependencies
- Save high scores in the user's application data directory
- Include all necessary resources

## How to Play

1.  Launch the application.
2.  From the landing page, select a game mode:
    *   **Blitz:** 30-second challenge.
    *   **Standard:** 3-minute challenge.
    *   **Unlimited:** Game ends after 3 mistakes.
3.  After a 3-second countdown, the game begins.
4.  Type the digits of Pi (starting with `3.14159...`) using your keyboard.
5.  Correct digits increase your score and combo, triggering positive feedback animations.
6.  Incorrect digits reset the combo and trigger negative feedback. You must enter the correct digit to proceed.
7.  The game ends when the timer runs out (Blitz, Standard) or after 3 mistakes (Unlimited).
8.  Your high score is saved and displayed on the landing screen. 