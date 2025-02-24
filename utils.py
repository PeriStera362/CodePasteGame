import pygame
import random
import math

def draw_stat_bars(screen, pigeon):
    # Colors for the stat bars
    COLORS = {
        'health': (255, 0, 0),      # Red
        'happiness': (255, 255, 0),  # Yellow
        'hunger': (0, 255, 0),      # Green
        'cleanliness': (0, 255, 255),# Cyan
        'energy': (255, 165, 0)      # Orange
    }
    
    # Draw stat bars
    bar_height = 20
    bar_spacing = 25
    for i, (stat_name, color) in enumerate(COLORS.items()):
        # Get the stat value
        stat_value = getattr(pigeon, stat_name)
        if stat_name == 'hunger':
            stat_value = 100 - stat_value  # Invert hunger so full bar means not hungry
            
        # Draw the background (gray) bar
        pygame.draw.rect(screen, (128, 128, 128), 
                        (10, 10 + i * bar_spacing, 100, bar_height))
        
        # Draw the colored stat bar
        pygame.draw.rect(screen, color,
                        (10, 10 + i * bar_spacing, stat_value, bar_height))
        
        # Draw the stat name
        font = pygame.font.Font(None, 24)
        text = font.render(stat_name.capitalize(), True, (255, 255, 255))
        screen.blit(text, (120, 10 + i * bar_spacing))

def display_messages(screen, messages, max_messages=5):
    font = pygame.font.Font(None, 24)
    for i, message in enumerate(messages[-max_messages:]):
        text = font.render(message, True, (255, 255, 255))
        screen.blit(text, (10, 500 + i * 20))

FLOOR_COLOR = (210, 180, 140)
WALL_COLOR = (169, 169, 169)
BLACK = (0, 0, 0)
SPARKLE_COLOR = (255, 255, 200)
SEED_COLOR = (218, 165, 32)

class Sparkle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = 1.0
        self.speed = random.uniform(1, 3)
        self.angle = random.uniform(0, 2 * math.pi)

    def update(self):
        self.life -= 0.05
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        return self.life > 0

    def draw(self, surface):
        alpha = int(255 * self.life)
        color = (*SPARKLE_COLOR, alpha)
        s = pygame.Surface((5, 5), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (2, 2), 2)
        surface.blit(s, (int(self.x), int(self.y)))

class SeedParticle:
    def __init__(self, x, y, target_y):
        self.x = x
        self.y = y
        self.target_y = target_y
        self.fall_speed = random.uniform(2, 4)
        self.falling = True
        self.rotation = random.uniform(0, 360)
        self.spin_speed = random.uniform(-5, 5)
        self.scale = random.uniform(0.8, 1.2)

    def update(self):
        if self.falling:
            self.y += self.fall_speed
            self.rotation += self.spin_speed
            if self.y >= self.target_y:
                self.y = self.target_y
                self.falling = False

    def draw(self, surface):
        seed_size = 3 * self.scale
        points = [
            (self.x + math.cos(math.radians(self.rotation)) * seed_size,
             self.y + math.sin(math.radians(self.rotation)) * seed_size),
            (self.x + math.cos(math.radians(self.rotation + 120)) * seed_size,
             self.y + math.sin(math.radians(self.rotation + 120)) * seed_size),
            (self.x + math.cos(math.radians(self.rotation + 240)) * seed_size,
             self.y + math.sin(math.radians(self.rotation + 240)) * seed_size)
        ]
        pygame.draw.polygon(surface, SEED_COLOR, points)

def draw_progress_bar(surface, x, y, width, height, progress, color):
    border = pygame.Rect(x, y, width, height)
    inner = pygame.Rect(x, y, int(width * progress), height)
    pygame.draw.rect(surface, BLACK, border, 2)
    pygame.draw.rect(surface, color, inner)

def draw_room(surface, width, height, wall_thickness):
    surface.fill(FLOOR_COLOR)
    pygame.draw.rect(surface, WALL_COLOR, (0, 0, width, wall_thickness))
    pygame.draw.rect(surface, WALL_COLOR, (0, 0, wall_thickness, height))
    pygame.draw.rect(surface, WALL_COLOR, (0, height - wall_thickness, width, wall_thickness))
    pygame.draw.rect(surface, WALL_COLOR, (width - wall_thickness, 0, wall_thickness, height))