import kivy
kivy.require('2.3.0') # Replace with your Kivy version if needed

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.resources import resource_add_path
import os
import sys

# Import game_logic with its resource_path helper function
from game_logic import GameLogic, resource_path
# Import screen classes
from screens.landing_screen import LandingScreen
from screens.countdown_screen import CountdownScreen
from screens.game_screen import GameScreen

# Placeholders removed, all screens imported

class PiQApp(App):
    """Main application class for the πQ game."""

    selected_game_mode = None # To store the mode chosen by the user

    def build(self):
        """Initializes the application and sets up the screen manager."""
        self.game_logic = GameLogic()
        self.title = 'πQ - Pi Memory Game'
        # Set a fixed window size for more consistent display
        Window.size = (500, 700) 
        Window.softinput_mode = 'below_target' # Helps keep keyboard from covering input area

        # Add resource paths for Kivy
        if hasattr(sys, '_MEIPASS'):
            resource_add_path(os.path.join(sys._MEIPASS))
        
        # Load the Kivy language file using resource_path
        kv_file = resource_path('piq.kv')
        Builder.load_file(kv_file)

        # Create the screen manager
        sm = ScreenManager()
        # Use the imported screens
        sm.add_widget(LandingScreen(name='landing'))
        sm.add_widget(CountdownScreen(name='countdown'))
        sm.add_widget(GameScreen(name='game'))

        # LandingScreen.on_enter handles high score display

        return sm

if __name__ == '__main__':
    PiQApp().run() 