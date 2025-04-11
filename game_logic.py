import json
import os
import sys
import tempfile

# Helper function to find correct path for packaged resources
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Pi digits is a packaged resource
PI_DIGITS_FILE = resource_path('pi_digits.txt')

# High scores should be in user-writable location
# On Windows: %APPDATA%\piQ
# On macOS: ~/Library/Application Support/piQ
# On Linux: ~/.local/share/piQ
def get_user_data_dir():
    """Get platform-specific user data directory"""
    if sys.platform == 'win32':
        app_data = os.environ.get('APPDATA', '')
        if app_data:
            return os.path.join(app_data, 'piQ')
    elif sys.platform == 'darwin':  # macOS
        return os.path.expanduser('~/Library/Application Support/piQ')
    else:  # Linux/Unix
        return os.path.expanduser('~/.local/share/piQ')
    
    # Fallback to temp directory if we can't determine
    return os.path.join(tempfile.gettempdir(), 'piQ')

# Create user data directory if it doesn't exist
USER_DATA_DIR = get_user_data_dir()
os.makedirs(USER_DATA_DIR, exist_ok=True)
HIGH_SCORE_FILE = os.path.join(USER_DATA_DIR, 'high_scores.json')

class GameLogic:
    """Handles loading Pi digits and managing high scores."""

    def __init__(self):
        self.pi_digits = self._load_pi_digits()
        self.high_scores = self._load_high_scores()

    def _load_pi_digits(self) -> str:
        """Loads the digits of Pi from the text file, keeping the decimal point."""
        try:
            with open(PI_DIGITS_FILE, 'r') as f:
                # Read the file, strip whitespace, but KEEP the decimal point
                digits = f.read().strip()
                # Basic validation: Ensure it starts roughly correctly
                if not digits.startswith("3.14"):
                     print(f"Warning: {PI_DIGITS_FILE} does not seem to contain Pi starting with 3.14...")
                     # Provide a default that includes the decimal
                     return "3.1415926535"
                return digits
        except FileNotFoundError:
            print(f"Error: {PI_DIGITS_FILE} not found.")
            # Return a default short sequence WITH decimal
            return "3.14159"
        except Exception as e:
            print(f"Error reading {PI_DIGITS_FILE}: {e}")
            return "3.14159"

    def _load_high_scores(self) -> dict:
        """Loads high scores from the JSON file."""
        if not os.path.exists(HIGH_SCORE_FILE):
            # Create the file with default scores if it doesn't exist
            default_scores = {'Blitz': 0, 'Standard': 0, 'Unlimited': 0}
            self._save_high_scores(default_scores)
            return default_scores
        try:
            with open(HIGH_SCORE_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
            print(f"Error loading high scores from {HIGH_SCORE_FILE}: {e}")
            # Return default scores in case of error
            return {'Blitz': 0, 'Standard': 0, 'Unlimited': 0}

    def _save_high_scores(self, scores: dict):
        """Saves high scores to the JSON file."""
        try:
            with open(HIGH_SCORE_FILE, 'w') as f:
                json.dump(scores, f, indent=4)
        except Exception as e:
            print(f"Error saving high scores to {HIGH_SCORE_FILE}: {e}")

    def get_high_score(self, mode: str) -> int:
        """Gets the high score for a specific game mode."""
        return self.high_scores.get(mode, 0)

    def update_high_score(self, mode: str, score: int):
        """Updates the high score if the new score is higher."""
        if score > self.get_high_score(mode):
            self.high_scores[mode] = score
            self._save_high_scores(self.high_scores)

    def get_pi_digit(self, index: int) -> str | None:
        """Returns the Pi character (digit or '.') at the given index (0-based)."""
        if 0 <= index < len(self.pi_digits):
            return self.pi_digits[index]
        return None

    def get_pi_sequence_length(self) -> int:
        """Returns the total number of loaded Pi digits."""
        return len(self.pi_digits)

# Example usage (optional, for testing)
if __name__ == '__main__':
    logic = GameLogic()
    print(f"Loaded {logic.get_pi_sequence_length()} digits of Pi.")
    print(f"First 10 digits: {logic.pi_digits[:10]}")
    print(f"High scores: {logic.high_scores}")
    logic.update_high_score('Standard', 150)
    print(f"Updated Standard high score: {logic.get_high_score('Standard')}")
    print(f"Digit at index 0: {logic.get_pi_digit(0)}")
    print(f"Digit at index 5: {logic.get_pi_digit(5)}") 