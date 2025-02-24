import pygame

# Colors
FLOOR_COLOR = (210, 180, 140)
WALL_COLOR = (169, 169, 169)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DANDER_COLOR = (240, 230, 140)
DROPPING_COLOR = (139, 69, 19)
SEED_COLOR = (218, 165, 32)
VACUUM_COLOR = (100, 100, 100)

def draw_stat_bars(screen, pigeon):
    """Draw status bars for pigeon's attributes."""
    colors = {
        'health': (255, 0, 0),      # Red
        'happiness': (255, 255, 0),  # Yellow
        'hunger': (0, 255, 0),      # Green
        'cleanliness': (0, 255, 255),# Cyan
        'energy': (255, 165, 0)      # Orange
    }

    bar_height = 20
    bar_spacing = 25
    for i, (stat_name, color) in enumerate(colors.items()):
        stat_value = getattr(pigeon, stat_name)
        if stat_name == 'hunger':
            stat_value = 100 - stat_value  # Invert hunger so full bar means not hungry

        pygame.draw.rect(screen, (128, 128, 128), 
                        (10, 10 + i * bar_spacing, 100, bar_height))
        pygame.draw.rect(screen, color,
                        (10, 10 + i * bar_spacing, stat_value, bar_height))

        font = pygame.font.Font(None, 24)
        text = font.render(stat_name.capitalize(), True, (255, 255, 255))
        screen.blit(text, (120, 10 + i * bar_spacing))

def display_messages(screen, messages, max_messages=5):
    """Display game messages on screen."""
    font = pygame.font.Font(None, 24)
    for i, message in enumerate(messages[-max_messages:]):
        text = font.render(message, True, (255, 255, 255))
        screen.blit(text, (10, 500 + i * 20))

def draw_cloth(surface, pos, cleaning):
    """Draw cloth cleaning cursor."""
    cloth_size = 40
    rect = pygame.Rect(pos[0] - cloth_size // 2, pos[1] - cloth_size // 2, cloth_size, cloth_size)
    if cleaning:
        pygame.draw.rect(surface, (255, 0, 0), rect, 3)
        s = pygame.Surface((cloth_size, cloth_size), pygame.SRCALPHA)
        s.fill((255, 0, 0, 100))
        surface.blit(s, rect.topleft)
    else:
        pygame.draw.rect(surface, (173, 216, 230), rect)

def draw_vacuum(surface, pos, cleaning):
    """Draw vacuum cleaning cursor."""
    vacuum_size = 50
    if cleaning:
        pygame.draw.circle(surface, (200, 0, 0), pos, vacuum_size // 2, 3)
        s = pygame.Surface((vacuum_size, vacuum_size), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 0, 0, 100), (vacuum_size // 2, vacuum_size // 2), vacuum_size // 2)
        surface.blit(s, (pos[0] - vacuum_size // 2, pos[1] - vacuum_size // 2))
    else:
        pygame.draw.circle(surface, VACUUM_COLOR, pos, vacuum_size // 2, 3)
    handle_start = (pos[0], pos[1])
    handle_end = (pos[0] + 30, pos[1] + 30)
    pygame.draw.line(surface, VACUUM_COLOR, handle_start, handle_end, 4)

def draw_feed_cursor(surface, pos):
    """Draw seed spreading cursor."""
    cursor_radius = 3
    seed_positions = [
        (-5, -5), (0, -5), (5, -5),
        (-5, 0), (0, 0), (5, 0),
        (-5, 5), (0, 5), (5, 5)
    ]
    for dx, dy in seed_positions:
        pygame.draw.circle(surface, SEED_COLOR,
                        (pos[0] + dx, pos[1] + dy), cursor_radius)

def draw_progress_bar(surface, x, y, width, height, progress, color):
    """Draw a generic progress bar."""
    border = pygame.Rect(x, y, width, height)
    inner = pygame.Rect(x, y, int(width * progress), height)
    pygame.draw.rect(surface, BLACK, border, 2)
    pygame.draw.rect(surface, color, inner)

def draw_room(surface, width, height, wall_thickness):
    """Draw the game room with floor and walls."""
    surface.fill(FLOOR_COLOR)
    pygame.draw.rect(surface, WALL_COLOR, (0, 0, width, wall_thickness))
    pygame.draw.rect(surface, WALL_COLOR, (0, 0, wall_thickness, height))
    pygame.draw.rect(surface, WALL_COLOR, (0, height - wall_thickness, width, wall_thickness))
    pygame.draw.rect(surface, WALL_COLOR, (width - wall_thickness, 0, wall_thickness, height))

def update_combo(last_clean_time, current_time, combo_multiplier):
    """Update cleaning combo multiplier based on timing."""
    COMBO_TIMEOUT = 2000
    if current_time - last_clean_time > COMBO_TIMEOUT:
        combo_multiplier = 1
    return combo_multiplier