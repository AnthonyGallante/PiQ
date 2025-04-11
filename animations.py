from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.clock import Clock
from kivy.metrics import dp
import random
import math

def shake_animation(widget, intensity=10, duration=0.2, type='correct'):
    """ Applies a shake animation to a widget. """
    print(f"Placeholder: Shake animation ({type}) triggered on {widget}")
    # Basic shake implementation (can be refined)
    original_pos = widget.pos[:]
    anim = (Animation(x=widget.x + random.uniform(-intensity, intensity),
                      y=widget.y + random.uniform(-intensity, intensity), duration=duration/4) +
            Animation(x=widget.x + random.uniform(-intensity, intensity),
                      y=widget.y + random.uniform(-intensity, intensity), duration=duration/4) +
            Animation(x=widget.x + random.uniform(-intensity, intensity),
                      y=widget.y + random.uniform(-intensity, intensity), duration=duration/4) +
            Animation(pos=original_pos, duration=duration/4))
    anim.start(widget)

def particle_effect(pos, parent_widget, type='correct', combo=1, count=10, duration=0.5):
    """ Creates a simple particle burst effect. """
    print(f"Placeholder: Particle effect ({type}, combo {combo}) triggered at {pos}")
    
    # Example: Create a few simple particles (dots)
    for _ in range(count):
        particle = Widget(size_hint=(None, None), size=(dp(5), dp(5)))
        particle.pos = pos
        
        # Determine color based on type
        if type == 'correct':
            base_color = [0.1, 0.8, 0.1, 1] # Green
            # Make color brighter/more intense with combo
            intensity_factor = min(1 + combo * 0.1, 2.0) # Cap intensity
            particle_color = [min(c * intensity_factor, 1.0) for c in base_color[:3]] + [1]
        else: # incorrect
            particle_color = [0.8, 0.1, 0.1, 1] # Red
        
        with particle.canvas:
            Color(rgba=particle_color)
            Ellipse(pos=particle.pos, size=particle.size)
        
        parent_widget.add_widget(particle)

        # Animate particle
        angle = random.uniform(0, 360)
        distance = random.uniform(dp(20), dp(50 + combo * 5)) # Use dp, fly further with combo
        end_x = pos[0] + distance * math.cos(math.radians(angle))
        end_y = pos[1] + distance * math.sin(math.radians(angle))
        
        anim = Animation(pos=(end_x, end_y), opacity=0, duration=duration * random.uniform(0.8, 1.2))
        anim.bind(on_complete=lambda a, w: parent_widget.remove_widget(w))
        anim.start(particle)

# Math import is now at the top 