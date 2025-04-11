from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, ListProperty
from kivy.app import App
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.metrics import dp
from kivy.animation import Animation
import random
import math

# Import animations
from animations import shake_animation, particle_effect

class DigitLabel(Label):
    """ Custom Label for displaying digits with background color. """
    background_color = ListProperty([0, 0, 0, 0]) # Default transparent

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure font size is appropriate - Significantly Increased font size
        self.font_size = '90sp' # Drastically increased from 30sp
        self.size_hint_x = None
        # Adjust width calculation - Needs dynamic update based on texture
        self.width = dp(50) # Start with an estimated width, will be updated
        self.bind(texture_size=self._update_width)
        self.bind(size=self._update_bg, pos=self._update_bg)

        with self.canvas.before:
            self.bg_color = Color(rgba=self.background_color)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)

    def _update_width(self, instance, size):
        """ Dynamically update width based on texture size. """
        # Add some padding to the actual texture width
        self.width = size[0] + dp(10)

    def on_background_color(self, instance, value):
        self.bg_color.rgba = value

    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

class GameScreen(Screen):
    """The main game screen where users input Pi digits."""
    digits_display = ObjectProperty(None)
    timer_label = ObjectProperty(None)
    score_label = ObjectProperty(None)
    combo_label = ObjectProperty(None)
    mistakes_label = ObjectProperty(None)
    scroll_view = ObjectProperty(None)

    score = NumericProperty(0)
    combo = NumericProperty(0)
    mistakes = NumericProperty(0)
    time_remaining = NumericProperty(0)
    current_digit_index = NumericProperty(0)
    game_mode = StringProperty('')
    game_active = False
    current_line_widget = None
    line_digit_count = 0
    MAX_LINES_DISPLAYED = 5
    DIGITS_PER_LINE = 10

    # --- Background Animation Constants ---
    MAX_BG_CIRCLES = 15
    BG_CIRCLE_MIN_SIZE = dp(10)
    BG_CIRCLE_MAX_SIZE = dp(80)
    BG_CIRCLE_MIN_SPEED = dp(10)
    BG_CIRCLE_MAX_SPEED = dp(50)
    BG_CIRCLE_MIN_ALPHA = 0.05
    BG_CIRCLE_MAX_ALPHA = 0.2
    # --- End Constants --- 

    # Colors
    CORRECT_COLOR = [0.1, 0.8, 0.1, 1] # Bright Green
    INCORRECT_COLOR = [0.5, 0.5, 0.5, 1] # Grey
    CURSOR_COLOR = [0.2, 0.6, 0.8, 1] # Professional Blue

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = None
        # Add background layer *first* (drawn behind)
        self.background_animation_layer = Widget()
        self.add_widget(self.background_animation_layer)
        # Particle layout added *after* background (drawn above background)
        self.particle_layout = BoxLayout(size_hint=(1, 1))
        self.add_widget(self.particle_layout)

        self.background_circles = [] # List to store circle data dictionaries
        self._game_setup_scheduled = False

    def on_enter(self, *args):
        """Schedules the game setup shortly after entering the screen."""
        # Schedule setup_game to run after a very short delay (e.g., next frame)
        # Ensure it only runs once per entry
        if not self._game_setup_scheduled:
            self._game_setup_scheduled = True
            Clock.schedule_once(self.setup_game, 0)

    def setup_game(self, dt):
        """Sets up the game state after widgets are loaded."""
        app = App.get_running_app()
        self.game_logic = app.game_logic
        self.game_mode = app.selected_game_mode

        # Ensure ids are available
        if not self.ids or not self.ids.digits_display:
             print("Error: GameScreen ids not available during setup_game.")
             # Attempt to go back to landing if UI failed
             self.manager.current = 'landing'
             self._game_setup_scheduled = False # Allow setup on re-entry
             return

        # Ensure background layer is behind particle layer if order got messed up
        self.remove_widget(self.background_animation_layer)
        self.add_widget(self.background_animation_layer, index=len(self.children))
        self.remove_widget(self.particle_layout)
        self.add_widget(self.particle_layout)
        self.particle_layout.clear_widgets()
        self.background_animation_layer.canvas.clear()
        self.background_circles.clear()

        # Initialize background circles
        for _ in range(self.MAX_BG_CIRCLES):
            self.background_circles.append(self._create_background_circle(initial=True))
        
        # Schedule background animation update
        Clock.schedule_interval(self.update_background_animation, 1.0 / 60.0)

        # Reset game state
        self.score = 0
        self.combo = 0
        self.mistakes = 0
        self.current_digit_index = 0
        self.game_active = True
        self.ids.digits_display.clear_widgets()
        self.current_line_widget = None
        self.line_digit_count = 0

        self._setup_initial_display() # Safe to call now
        self._request_keyboard()      # Safe to call now

        # Set up timer and labels based on mode
        # Cancel previous timer just in case on_leave wasn't called properly
        Clock.unschedule(self.update_timer)
        if self.game_mode == 'Blitz':
            self.time_remaining = 30
            self.ids.mistakes_label.opacity = 0
            Clock.schedule_interval(self.update_timer, 1)
        elif self.game_mode == 'Standard':
            self.time_remaining = 180 # 3 minutes
            self.ids.mistakes_label.opacity = 0
            Clock.schedule_interval(self.update_timer, 1)
        elif self.game_mode == 'Unlimited':
            self.time_remaining = 0 # Not used, but set
            self.ids.timer_label.text = 'Time: ∞'
            self.ids.mistakes_label.opacity = 1
            self.ids.mistakes_label.text = f'Mistakes: {self.mistakes}/3'

        self.update_ui_labels() # Safe to call now
        self._game_setup_scheduled = False # Reset flag for next entry

    def _request_keyboard(self):
        """Requests the keyboard for input handling."""
        # Check if keyboard is already requested
        if self._keyboard:
            return
        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text'
        )
        if not self._keyboard:
             print("Error: Could not get keyboard")
             return
        if self._keyboard.widget:
            # If it exists, this widget is a different keyboard than self._keyboard
            self._keyboard.widget.focus = True
        self._keyboard.bind(on_key_down=self._on_key_down)
        print("Keyboard requested")

    def _keyboard_closed(self):
        """Handles keyboard closing."""
        print("Keyboard closed")
        if self._keyboard:
             self._keyboard.unbind(on_key_down=self._on_key_down)
             self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        """Handles key press events, including numpad and decimal points."""
        if not self.game_active:
            return False # Don't process input if game isn't active

        numeric_keycode, key_str = keycode
        char_to_handle = None

        # Check standard number keys
        if key_str.isdigit():
            char_to_handle = key_str
        # Check numpad number keys (common keycodes)
        elif 256 <= numeric_keycode <= 265:
            # Numpad 0 is 256, Numpad 9 is 265
            digit_map = {256: '0', 257: '1', 258: '2', 259: '3', 260: '4',
                         261: '5', 262: '6', 263: '7', 264: '8', 265: '9'}
            char_to_handle = digit_map.get(numeric_keycode)
        # Check standard period key
        elif key_str == '.':
             char_to_handle = '.'
        # Check common numpad decimal keycode (KP_Decimal)
        elif numeric_keycode == 266:
             char_to_handle = '.'

        # Only proceed if the input is relevant (digit or decimal)
        # and if the expected character is actually a decimal when a decimal is pressed
        if char_to_handle is not None:
            # Special check: only allow decimal input if it's expected
            expected_char = self.game_logic.get_pi_digit(self.current_digit_index)
            if char_to_handle == '.' and expected_char != '.':
                 print("Decimal point entered, but not expected.")
                 # Trigger error feedback maybe? For now, just ignore.
                 shake_animation(self.ids.digits_display, intensity=5, duration=0.15, type='error')
                 return True # Consume the event but do nothing else
            elif char_to_handle != '.' and expected_char == '.':
                 print(f"Digit {char_to_handle} entered, but decimal point expected.")
                 # Trigger error feedback
                 shake_animation(self.ids.digits_display, intensity=5, duration=0.15, type='error')
                 return True # Consume the event but do nothing else
            
            # If it's a digit, or it's a decimal and a decimal is expected, handle it
            self.handle_input(char_to_handle)
            return True # Consume the event

        # Allow backspace for potential future correction (optional)
        # elif key_str == 'backspace':
        #     # Handle backspace if needed
        #     return True

        return False # Don't consume other keys

    def _setup_initial_display(self):
        """ Adds only the initial cursor to the display. """
        # self.add_digit_to_display('3', self.CORRECT_COLOR) # REMOVED
        # self.add_digit_to_display('.', [1, 1, 1, 1]) # REMOVED
        self.add_cursor() # Start with just the cursor

    def add_digit_to_display(self, digit_char: str, color: list):
        """Adds a digit (or cursor) label to the current line. Turns previous line grey on wrap."""
        previous_line_widget = None # Store reference to the line being completed
        if self.current_line_widget is not None and self.line_digit_count >= self.DIGITS_PER_LINE:
             previous_line_widget = self.current_line_widget

        if self.current_line_widget is None or self.line_digit_count >= self.DIGITS_PER_LINE:
            # Create a new line (BoxLayout)
            new_line_height = dp(100)
            self.current_line_widget = BoxLayout(orientation='horizontal', size_hint_y=None, height=new_line_height, spacing=dp(5))
            # Add the new line *before* modifying the previous one to keep order
            self.ids.digits_display.add_widget(self.current_line_widget)
            self.line_digit_count = 0
            # Enforce max lines displayed
            if len(self.ids.digits_display.children) > self.MAX_LINES_DISPLAYED + 1:
                 oldest_line = self.ids.digits_display.children[-1]
                 self.ids.digits_display.remove_widget(oldest_line)

            # --- Change previous line to grey --- 
            if previous_line_widget is not None:
                 # Iterate through children (DigitLabels) of the completed line
                 # Children list is in reverse order of addition
                 for label_widget in reversed(previous_line_widget.children):
                     if isinstance(label_widget, DigitLabel):
                         # Keep decimal point white, grey out digits
                         if label_widget.text != '.':
                             label_widget.color = self.INCORRECT_COLOR # Use the defined grey color
                         # Remove background color for completed lines
                         label_widget.background_color = [0,0,0,0] # Transparent
            # --- End change previous line --- 

        # Create and add the digit label to the *current* line
        digit_label = DigitLabel(text=digit_char, color=color if digit_char != '.' else [1,1,1,1])
        if digit_char.isdigit():
            digit_label.background_color = color[:3] + [0.2]
        elif digit_char == '_' or digit_char == '.':
            digit_label.background_color = [0,0,0,0]

        # Ensure current_line_widget exists before adding
        if self.current_line_widget:
            self.current_line_widget.add_widget(digit_label)
            self.line_digit_count += 1
        else:
            # This case should ideally not happen if logic above is correct
            print("Error: current_line_widget is None when trying to add digit.")
            return # Avoid further errors

        # Schedule the scroll adjustment to happen slightly later
        Clock.schedule_once(self._adjust_scroll, 0)

    def _adjust_scroll(self, dt):
        """ Adjusts the scroll view scroll_y property using an animation. """
        if self.ids and self.ids.scroll_view:
            # Animate scroll_y to 0 over a short duration
            anim = Animation(scroll_y=0, duration=0.1, transition='out_quad')
            anim.start(self.ids.scroll_view)
            # print(f"Started animation to scroll_y=0") # Optional debug print
        else:
            print("Warning: scroll_view not found in ids during _adjust_scroll.")

    def remove_cursor(self):
         """ Removes the placeholder cursor label. """
         if self.current_line_widget and self.current_line_widget.children:
             last_widget = self.current_line_widget.children[0] # Kivy adds children in reverse
             if isinstance(last_widget, DigitLabel) and last_widget.text == '_':
                 self.current_line_widget.remove_widget(last_widget)
                 self.line_digit_count -= 1

    def add_cursor(self):
         """ Adds a visual cursor to indicate the next input position. """
         self.add_digit_to_display('_', self.CURSOR_COLOR)

    def handle_input(self, entered_digit: str):
        """Processes the user's digit input. Incorrect digits give feedback but don't display."""
        if not self.game_active:
            return

        # Special case for the decimal point after '3'
        if self.current_digit_index == 1: # After entering '3'
             correct_char = '.'
             # Allow player to just type the next digit '1' and skip decimal? No, requirement is 3.14...
             # For now, let's assume the logic should handle the decimal correctly via get_pi_digit
             # We just need to ensure '.' isn't checked with isdigit later
             pass # Let existing logic handle it

        # Get the correct character (digit or '.')
        # Need to adjust game_logic.py to NOT strip the decimal
        correct_char = self.game_logic.get_pi_digit(self.current_digit_index)
        
        last_digit_pos = self.center # Default position
        current_cursor_widget = None

        # Find current cursor position more reliably
        if self.current_line_widget and self.current_line_widget.children:
            # Assuming cursor is always the last added widget (first in children list)
            last_widget = self.current_line_widget.children[0]
            if isinstance(last_widget, DigitLabel) and last_widget.text == '_':
                current_cursor_widget = last_widget
                last_digit_pos = last_widget.center
            # If no cursor found, maybe take center of last digit instead?
            elif isinstance(last_widget, DigitLabel):
                 last_digit_pos = last_widget.center

        if entered_digit == correct_char:
            # Remove the placeholder cursor BEFORE adding the correct digit
            self.remove_cursor()

            self.score += 1
            self.combo += 1
            self.current_digit_index += 1
            self.add_digit_to_display(entered_digit, self.CORRECT_COLOR)
            
            # --- Shake the digits display layout --- 
            shake_animation(self.ids.digits_display, intensity=3, duration=0.1, type='correct') # Target layout inside ScrollView
            # --- End Shake Change --- 
            
            # Use cursor position for particle effect origin
            particle_effect(last_digit_pos, self.particle_layout, type='correct', combo=self.combo)
            print(f"Correct! Score: {self.score}, Combo: {self.combo}") # Debug

            # Add the cursor back for the next digit
            self.add_cursor()
        else:
            # Incorrect digit: Reset combo, trigger feedback, DO NOT display digit
            self.combo = 0
            
            # --- Shake the digits display layout --- 
            shake_animation(self.ids.digits_display, intensity=8, duration=0.2, type='error') # Target layout inside ScrollView
            # --- End Shake Change --- 
            
            # Use cursor position for particle effect origin
            particle_effect(last_digit_pos, self.particle_layout, type='error')
            print(f"Incorrect! Expected: {correct_char}") # Debug

            if self.game_mode == 'Unlimited':
                self.mistakes += 1
                if self.mistakes >= 3:
                    self.end_game("Too many mistakes!")
                    return # Stop further processing
            # Do NOT add the incorrect digit to the display
            # Cursor remains in the same place (or is re-added if it was somehow removed)
            if not current_cursor_widget or current_cursor_widget.parent is None:
                self.remove_cursor() # Clean up just in case
                self.add_cursor()

        # Update UI labels regardless of correct/incorrect
        self.update_ui_labels()

        # Check if Pi sequence is exhausted (only after correct entry)
        if entered_digit == correct_char and self.current_digit_index >= self.game_logic.get_pi_sequence_length():
             self.end_game("Congratulations! You memorized all loaded digits!")

    def update_timer(self, dt):
        """Updates the game timer each second."""
        if not self.game_active:
            return

        self.time_remaining -= 1
        self.update_ui_labels()

        if self.time_remaining <= 0:
            self.end_game("Time's up!")

    def update_ui_labels(self):
        """Updates the score, combo, timer, and mistakes labels."""
        if self.ids:
            self.ids.score_label.text = f"Score: {self.score}"
            self.ids.combo_label.text = f"Combo: {self.combo}"
            if self.game_mode != 'Unlimited':
                 minutes = int(self.time_remaining) // 60
                 seconds = int(self.time_remaining) % 60
                 self.ids.timer_label.text = f"Time: {minutes:02d}:{seconds:02d}"
            if self.game_mode == 'Unlimited':
                self.ids.mistakes_label.text = f"Mistakes: {self.mistakes}/3"
        else:
            print("Warning: GameScreen ids not found during UI update.")

    def end_game(self, message: str):
        """Handles the end of the game round."""
        if not self.game_active:
            return # Avoid ending multiple times

        print(f"Game Over: {message}")
        self.game_active = False
        self._keyboard_closed() # Release keyboard
        Clock.unschedule(self.update_timer)

        # Update high score
        app = App.get_running_app()
        app.game_logic.update_high_score(self.game_mode, self.score)

        # TODO: Show a game over popup/screen instead of just returning
        # For now, just transition back to landing screen
        self.manager.current = 'landing'

    def on_leave(self, *args):
        """Cleans up when leaving the screen."""
        print("Leaving Game Screen")
        self.game_active = False
        # Cancel any pending setup call
        Clock.unschedule(self.setup_game)
        # Unschedule background animation
        Clock.unschedule(self.update_background_animation)
        self._game_setup_scheduled = False # Reset flag
        self._keyboard_closed()
        Clock.unschedule(self.update_timer)
        # Clear widgets safely, checking if ids exist
        if hasattr(self, 'ids') and self.ids and self.ids.digits_display:
            self.ids.digits_display.clear_widgets()
        if hasattr(self, 'particle_layout'):
            self.particle_layout.clear_widgets()
        # Clear background animation elements
        if hasattr(self, 'background_animation_layer'):
             self.background_animation_layer.canvas.clear()
        self.background_circles.clear()

    def _create_background_circle(self, initial=False):
        """ Creates a dictionary representing a background circle. """
        size = random.uniform(self.BG_CIRCLE_MIN_SIZE, self.BG_CIRCLE_MAX_SIZE)
        alpha = random.uniform(self.BG_CIRCLE_MIN_ALPHA, self.BG_CIRCLE_MAX_ALPHA)
        # Use a base grey color with random alpha
        color = [0.8, 0.8, 0.8, alpha] 
        speed = random.uniform(self.BG_CIRCLE_MIN_SPEED, self.BG_CIRCLE_MAX_SPEED)
        angle = random.uniform(0, 360)
        velocity = [speed * math.cos(math.radians(angle)), speed * math.sin(math.radians(angle))]
        
        # Start circles off-screen or near edges
        start_side = random.randint(0, 3) # 0:left, 1:right, 2:bottom, 3:top
        pos = [0, 0]
        w, h = Window.size
        if start_side == 0: # Left
            pos = [-size, random.uniform(0, h)]
        elif start_side == 1: # Right
            pos = [w, random.uniform(0, h)]
        elif start_side == 2: # Bottom
            pos = [random.uniform(0, w), -size]
        else: # Top
            pos = [random.uniform(0, w), h]
            
        # If initial setup, distribute positions more randomly across screen
        if initial:
             pos = [random.uniform(-size, w), random.uniform(-size, h)]

        return {'pos': pos, 'size': size, 'color': color, 'velocity': velocity}

    def update_background_animation(self, dt):
        """ Updates and redraws the background circles with softer edges. """
        self.background_animation_layer.canvas.clear()
        w, h = Window.size

        with self.background_animation_layer.canvas:
            for circle in self.background_circles:
                # Update position
                circle['pos'][0] += circle['velocity'][0] * dt
                circle['pos'][1] += circle['velocity'][1] * dt
                
                # Check boundaries and reset if needed
                size = circle['size']
                reset = False
                if circle['velocity'][0] > 0 and circle['pos'][0] > w:
                    circle['pos'][0] = -size # Reset to left
                    circle['pos'][1] = random.uniform(0, h)
                    reset = True
                elif circle['velocity'][0] < 0 and circle['pos'][0] < -size:
                    circle['pos'][0] = w # Reset to right
                    circle['pos'][1] = random.uniform(0, h)
                    reset = True
                    
                if circle['velocity'][1] > 0 and circle['pos'][1] > h:
                    circle['pos'][1] = -size # Reset to bottom
                    circle['pos'][0] = random.uniform(0, w)
                    reset = True
                elif circle['velocity'][1] < 0 and circle['pos'][1] < -size:
                    circle['pos'][1] = h # Reset to top
                    circle['pos'][0] = random.uniform(0, w)
                    reset = True
                    
                # Optional: Randomize velocity slightly on reset
                # if reset:
                #    speed = random.uniform(self.BG_CIRCLE_MIN_SPEED, self.BG_CIRCLE_MAX_SPEED)
                #    angle = random.uniform(0, 360)
                #    circle['velocity'] = [speed * math.cos(math.radians(angle)), speed * math.sin(math.radians(angle))] 

                # Draw softer circle
                pos = circle['pos']
                base_color_rgba = circle['color']

                # 1. Draw a larger, very faint outer ellipse
                outer_size_factor = 1.2 # How much larger the outer faint part is
                outer_alpha_factor = 0.4 # How much fainter the outer part is
                outer_size = size * outer_size_factor
                # Calculate position offset to keep it centered
                outer_pos_offset = (outer_size - size) / 2.0 
                outer_pos = (pos[0] - outer_pos_offset, pos[1] - outer_pos_offset)
                outer_color = base_color_rgba[:3] + [base_color_rgba[3] * outer_alpha_factor]
                
                Color(rgba=outer_color)
                Ellipse(pos=outer_pos, size=(outer_size, outer_size))

                # 2. Draw the main, slightly smaller inner ellipse (original logic)
                Color(rgba=base_color_rgba)
                Ellipse(pos=pos, size=(size, size))