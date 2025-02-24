import pygame

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
