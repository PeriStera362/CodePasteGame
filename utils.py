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

def draw_status_bars(screen, pigeon):
    """Draw status bars at the top of the screen."""
    colors = {
        'hygiene': (0, 255, 255),    # Cyan
        'hunger': (50, 205, 50),     # Green
        'happiness': (255, 215, 0)    # Gold
    }

    bar_width = 200
    bar_height = 20
    bar_spacing = 50
    total_width = (bar_width * 3) + (bar_spacing * 2)
    start_x = (screen.get_width() - total_width) // 2
    start_y = 20  # Fixed position at top

    # Calculate hygiene based on mess
    total_mess = len(pigeon.dander) + len(pigeon.droppings)
    hygiene = max(0, 100 - (total_mess * 2))  # Each mess reduces hygiene by 2%

    values = {
        'hygiene': hygiene,
        'hunger': 100 - pigeon.hunger,  # Invert hunger so full bar means not hungry
        'happiness': pigeon.happiness
    }

    for i, (stat_name, color) in enumerate(colors.items()):
        x = start_x + (bar_width + bar_spacing) * i
        # Draw background (gray) bar
        pygame.draw.rect(screen, (128, 128, 128), 
                        (x, start_y, bar_width, bar_height))
        # Draw filled portion
        fill_width = int(bar_width * (values[stat_name] / 100))
        pygame.draw.rect(screen, color,
                        (x, start_y, fill_width, bar_height))
        # Draw border
        pygame.draw.rect(screen, BLACK, 
                        (x, start_y, bar_width, bar_height), 2)
        # Draw label
        font = pygame.font.Font(None, 24)
        text = font.render(stat_name.capitalize(), True, BLACK)
        text_rect = text.get_rect(centerx=x + bar_width//2, top=start_y - 25)
        screen.blit(text, text_rect)

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

def draw_room(surface, width, height, wall_thickness, room_top):
    """Draw the game room with floor and walls."""
    # Draw walls
    pygame.draw.rect(surface, WALL_COLOR, (0, room_top, width, wall_thickness))  # Top wall
    pygame.draw.rect(surface, WALL_COLOR, (0, room_top, wall_thickness, height))  # Left wall
    pygame.draw.rect(surface, WALL_COLOR, (0, room_top + height - wall_thickness, width, wall_thickness))  # Bottom wall
    pygame.draw.rect(surface, WALL_COLOR, (width - wall_thickness, room_top, wall_thickness, height))  # Right wall

def display_messages(screen, messages, max_messages=5):
    """Display game messages on screen."""
    font = pygame.font.Font(None, 24)
    for i, message in enumerate(messages[-max_messages:]):
        text = font.render(message, True, (255, 255, 255))
        screen.blit(text, (10, 500 + i * 20))

def update_combo(last_clean_time, current_time, combo_multiplier):
    """Update cleaning combo multiplier based on timing."""
    COMBO_TIMEOUT = 2000
    if current_time - last_clean_time > COMBO_TIMEOUT:
        combo_multiplier = 1
    return combo_multiplier