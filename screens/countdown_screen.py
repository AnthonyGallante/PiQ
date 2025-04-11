from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
# from kivy.properties import ObjectProperty # Removed - not strictly needed
from kivy.app import App

class CountdownScreen(Screen):
    """Screen displaying a countdown before the game starts."""
    # countdown_label = ObjectProperty(None) # Removed

    def on_enter(self, *args):
        """Starts the countdown when the screen is entered."""
        self.countdown_value = 3
        # Consistently use self.ids to access the label defined in kv
        if self.ids.countdown_label:
            self.ids.countdown_label.text = str(self.countdown_value)
        else:
            print("Error: CountdownScreen countdown_label id not found.")
            # Potentially switch back to landing if UI isn't ready
            self.manager.current = 'landing'
            return

        # Schedule the countdown update
        Clock.schedule_interval(self.update_countdown, 1)

    def update_countdown(self, dt):
        """Decrements the countdown timer each second."""
        self.countdown_value -= 1
        # Update text via ids
        if self.ids.countdown_label:
             self.ids.countdown_label.text = str(self.countdown_value)
        else: # Should ideally not happen if on_enter check passes
             print("Error: CountdownScreen countdown_label id not found during update.")
             Clock.unschedule(self.update_countdown) # Stop the clock
             self.manager.current = 'landing'
             return

        if self.countdown_value <= 0: # Changed to <= 0 for safety
            # Stop the countdown clock
            Clock.unschedule(self.update_countdown)
            # Transition to the game screen
            self.manager.current = 'game'

    def on_leave(self, *args):
        """Ensure the clock is unscheduled when leaving the screen prematurely."""
        Clock.unschedule(self.update_countdown) 