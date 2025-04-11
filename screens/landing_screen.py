from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty

class LandingScreen(Screen):
    """The main landing screen of the πQ application."""
    blitz_high_score_label = ObjectProperty(None)
    standard_high_score_label = ObjectProperty(None)
    unlimited_high_score_label = ObjectProperty(None)

    def on_enter(self, *args):
        """Called when the screen is entered. Updates high score display."""
        app = App.get_running_app()
        # Update labels using the ids defined in piq.kv (requires kv to be loaded)
        # Safely access ids after kv loading
        if self.ids:
            self.ids.blitz_high_score.text = f"Blitz High Score: {app.game_logic.get_high_score('Blitz')}"
            self.ids.standard_high_score.text = f"Standard High Score: {app.game_logic.get_high_score('Standard')}"
            self.ids.unlimited_high_score.text = f"Unlimited High Score: {app.game_logic.get_high_score('Unlimited')}"
        else:
            print("Warning: LandingScreen ids not found, check piq.kv loading.")

    def start_game(self, mode: str):
        """Transitions to the countdown screen with the selected mode."""
        app = App.get_running_app()
        # Store the selected mode in the app or pass it to the next screen
        app.selected_game_mode = mode 
        self.manager.current = 'countdown' 