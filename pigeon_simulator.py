import pygame
import random
import math

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pet Pigeon Simulator")
clock = pygame.time.Clock()

# Define Colors
FLOOR_COLOR = (210, 180, 140)   # Tan floor color
WALL_COLOR = (169, 169, 169)    # Dark grey walls
WALL_THICKNESS = 20             # Thickness for walls
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DANDER_COLOR = (240, 230, 140)   # Light yellowish dander
DROPPING_COLOR = (139, 69, 19)    # Brown droppings
SPARKLE_COLOR = (255, 255, 200)   # Light yellow sparkles
VACUUM_COLOR = (100, 100, 100)    # Dark gray for vacuum head

# Define Font
font = pygame.font.SysFont(None, 24)
score_font = pygame.font.SysFont(None, 36)

# Define UI Button Rectangles
vacuum_button = pygame.Rect(50, 500, 100, 50)
cloth_button = pygame.Rect(200, 500, 100, 50)
feed_button = pygame.Rect(350, 500, 100, 50)

# Global lists to store dander, droppings, and cleaning effects
dander = []
droppings = []
sparkles = []
cleaning_score = 0
combo_multiplier = 1
last_clean_time = 0
COMBO_TIMEOUT = 2000  # 2 seconds to maintain combo

class Sparkle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = 1.0  # Starts full, fades to 0
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

def add_sparkles(x, y):
    """Add cleaning sparkle effects at the given position."""
    for _ in range(5):
        sparkles.append(Sparkle(x, y))

def draw_progress_bar(surface, x, y, width, height, progress, color):
    """Draw a progress bar with the given parameters."""
    border = pygame.Rect(x, y, width, height)
    inner = pygame.Rect(x, y, int(width * progress), height)
    pygame.draw.rect(surface, BLACK, border, 2)
    pygame.draw.rect(surface, color, inner)

def update_combo():
    """Update the combo multiplier based on timing."""
    global combo_multiplier, last_clean_time
    current_time = pygame.time.get_ticks()
    if current_time - last_clean_time > COMBO_TIMEOUT:
        combo_multiplier = 1
    return combo_multiplier

def draw_room(surface):
    """Draws a top-down view of a room with a floor and surrounding walls."""
    # Draw floor
    surface.fill(FLOOR_COLOR)
    # Draw top wall
    pygame.draw.rect(surface, WALL_COLOR, (0, 0, WIDTH, WALL_THICKNESS))
    # Draw left wall
    pygame.draw.rect(surface, WALL_COLOR, (0, 0, WALL_THICKNESS, HEIGHT))
    # Draw bottom wall
    pygame.draw.rect(surface, WALL_COLOR, (0, HEIGHT - WALL_THICKNESS, WIDTH, WALL_THICKNESS))
    # Draw right wall
    pygame.draw.rect(surface, WALL_COLOR, (WIDTH - WALL_THICKNESS, 0, WALL_THICKNESS, HEIGHT))

def add_dander(pigeon_x, pigeon_y):
    """Add a burst of dander particles near the pigeon's current position."""
    for _ in range(10):  # add 10 particles
        x = pigeon_x + random.randint(-30, 30)
        y = pigeon_y + random.randint(-30, 30)
        dander.append((x, y))

def add_dropping(pigeon_x, pigeon_y):
    """Add a dropping particle near the pigeon's current position."""
    x = pigeon_x + random.randint(-20, 20)
    y = pigeon_y + random.randint(20, 40)
    droppings.append((x, y))

class Pigeon:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = 2  # initial horizontal speed
        self.dy = 0  # initial vertical speed
        self.action = "idle"
        self.action_message = "Just chilling..."
        self.last_action_time = pygame.time.get_ticks()
        self.leg_phase = 0  # for leg animation

    def move(self):
        """Update the pigeon's position and bounce off walls (taking wall thickness into account)."""
        self.x += self.dx
        self.y += self.dy
        # Bounce off walls (accounting for wall thickness)
        if self.x - 50 <= WALL_THICKNESS or self.x + 50 >= WIDTH - WALL_THICKNESS:
            self.dx = -self.dx
        if self.y - 50 <= WALL_THICKNESS or self.y + 50 >= HEIGHT - 100:  # Keep above buttons
            self.dy = -self.dy

    def update(self):
        now = pygame.time.get_ticks()
        if self.dx != 0 or self.dy != 0:
            self.leg_phase += 0.2  # advance leg animation
        if now - self.last_action_time > 3000:
            self.choose_action()
            self.last_action_time = now
        if self.dx != 0 or self.dy != 0:
            self.move()

    def choose_action(self):
        """Randomly choose an action and adjust movement accordingly."""
        actions = ["drop", "frolic", "coo", "loaf", "eat", "hop"]
        self.action = random.choice(actions)
        if self.action == "drop":
            self.action_message = "Oops, a dropping!"
            add_dropping(self.x, self.y)
            self.dx = random.choice([-1, 1]) * random.randint(1, 3)
            self.dy = random.choice([-1, 1]) * random.randint(1, 2)
        elif self.action == "frolic":
            self.action_message = "Fluffing feathers!"
            add_dander(self.x, self.y)
            self.dx = random.choice([-1, 1]) * random.randint(2, 4)
            self.dy = random.choice([-1, 1]) * random.randint(1, 3)
        elif self.action == "coo":
            self.action_message = "Cooing softly..."
            self.dx = random.choice([-1, 1]) * random.randint(1, 2)
            self.dy = 0  # Stays at same height while cooing
        elif self.action == "loaf":
            self.action_message = "Just loafing around."
            self.dx = 0  # stops moving
            self.dy = 0
        elif self.action == "eat":
            self.action_message = "Munching on seeds."
            self.dx = random.choice([-1, 1])  # slow movement while eating
            self.dy = 0
        elif self.action == "hop":
            self.action_message = "Hop hop!"
            self.dx = random.choice([-1, 1]) * 2
            self.dy = -4  # Quick upward hop
        print("Pigeon action:", self.action)

    def draw(self, surface):
        """Draw the pigeon with its body, face, and animated legs if moving."""
        # Draw pigeon body
        pygame.draw.circle(surface, (150, 150, 150), (int(self.x), int(self.y)), 50)
        # Draw eyes
        pygame.draw.circle(surface, BLACK, (int(self.x) - 15, int(self.y) - 10), 5)
        pygame.draw.circle(surface, BLACK, (int(self.x) + 15, int(self.y) - 10), 5)
        # Draw beak
        pygame.draw.polygon(surface, (255, 200, 0),
                            [(int(self.x), int(self.y)),
                             (int(self.x) + 30, int(self.y) + 10),
                             (int(self.x), int(self.y) + 20)])
        # Draw legs if moving
        if self.dx != 0 or self.dy != 0:
            offset = int(10 * math.sin(self.leg_phase))
            # Left leg
            left_start = (int(self.x) - 15, int(self.y) + 50)
            left_end = (int(self.x) - 15 + offset, int(self.y) + 70)
            pygame.draw.line(surface, BLACK, left_start, left_end, 3)
            # Right leg (swinging oppositely)
            right_start = (int(self.x) + 15, int(self.y) + 50)
            right_end = (int(self.x) + 15 - offset, int(self.y) + 70)
            pygame.draw.line(surface, BLACK, right_start, right_end, 3)
        # Display action message above the pigeon
        text = font.render(self.action_message, True, BLACK)
        surface.blit(text, (int(self.x) - text.get_width() // 2, int(self.y) - 70))

# Create a pigeon instance centered in the room
pigeon = Pigeon(WIDTH // 2, HEIGHT // 2)

# Cleaning mode variables
cloth_mode = False
vacuum_mode = False  # New variable for vacuum mode

def draw_cloth(surface, pos, cleaning):
    """Draws the cloth cursor at the given position."""
    cloth_size = 40
    rect = pygame.Rect(pos[0] - cloth_size // 2, pos[1] - cloth_size // 2, cloth_size, cloth_size)
    if cleaning:
        pygame.draw.rect(surface, (255, 0, 0), rect, 3)
        s = pygame.Surface((cloth_size, cloth_size), pygame.SRCALPHA)
        s.fill((255, 0, 0, 100))
        surface.blit(s, rect.topleft)
        add_sparkles(pos[0], pos[1])
    else:
        pygame.draw.rect(surface, (173, 216, 230), rect)

def draw_vacuum(surface, pos, cleaning):
    """Draws the vacuum head cursor at the given position."""
    vacuum_size = 50
    # Draw vacuum head (circle with angled line for suction)
    if cleaning:
        # Active vacuum animation
        pygame.draw.circle(surface, (200, 0, 0), pos, vacuum_size // 2, 3)
        # Suction effect (semi-transparent circle)
        s = pygame.Surface((vacuum_size, vacuum_size), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 0, 0, 100), (vacuum_size // 2, vacuum_size // 2), vacuum_size // 2)
        surface.blit(s, (pos[0] - vacuum_size // 2, pos[1] - vacuum_size // 2))
        # Add sparkles for visual feedback
        add_sparkles(pos[0], pos[1])
    else:
        # Inactive vacuum head
        pygame.draw.circle(surface, VACUUM_COLOR, pos, vacuum_size // 2, 3)
    # Draw handle
    handle_start = (pos[0], pos[1])
    handle_end = (pos[0] + 30, pos[1] + 30)
    pygame.draw.line(surface, VACUUM_COLOR, handle_start, handle_end, 4)


# Main Game Loop
running = True
while running:
    clock.tick(60)  # 60 FPS

    # Initialize mouse position and cleaning state variables
    mouse_pos = pygame.mouse.get_pos()
    cleaning_active = pygame.mouse.get_pressed()[0]

    # Handle cleaning modes cursor visibility
    if cloth_mode or vacuum_mode:
        pygame.mouse.set_visible(False)
        if cleaning_active:
            if cloth_mode:
                # Existing cloth cleaning logic
                cloth_rect = pygame.Rect(mouse_pos[0] - 20, mouse_pos[1] - 20, 40, 40)
                original_count = len(droppings)
                droppings = [drop for drop in droppings if not cloth_rect.collidepoint(drop)]
                cleaned_count = original_count - len(droppings)
                if cleaned_count > 0:
                    current_time = pygame.time.get_ticks()
                    if current_time - last_clean_time <= COMBO_TIMEOUT:
                        combo_multiplier = min(combo_multiplier + 0.5, 4.0)
                    else:
                        combo_multiplier = 1.0
                    last_clean_time = current_time
                    cleaning_score += int(10 * combo_multiplier * cleaned_count)
                    add_sparkles(mouse_pos[0], mouse_pos[1])
            elif vacuum_mode:
                # Vacuum cleaning logic
                vacuum_radius = 25  # Size of vacuum effect
                original_count = len(dander)
                dander = [d for d in dander if (d[0] - mouse_pos[0])**2 + (d[1] - mouse_pos[1])**2 > vacuum_radius**2]
                cleaned_count = original_count - len(dander)
                if cleaned_count > 0:
                    current_time = pygame.time.get_ticks()
                    if current_time - last_clean_time <= COMBO_TIMEOUT:
                        combo_multiplier = min(combo_multiplier + 0.5, 4.0)
                    else:
                        combo_multiplier = 1.0
                    last_clean_time = current_time
                    cleaning_score += int(5 * combo_multiplier * cleaned_count)
                    add_sparkles(mouse_pos[0], mouse_pos[1])
    else:
        pygame.mouse.set_visible(True)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if vacuum_button.collidepoint(pos):
                # Toggle vacuum mode, disable cloth mode
                vacuum_mode = not vacuum_mode
                cloth_mode = False
                print("Vacuum mode:", vacuum_mode)
            elif cloth_button.collidepoint(pos):
                # Toggle cloth mode, disable vacuum mode
                cloth_mode = not cloth_mode
                vacuum_mode = False
                print("Cloth mode:", cloth_mode)
            elif feed_button.collidepoint(pos):
                pigeon.action_message = "Yum, seeds!"
                print("Fed the pigeon!")
            elif not (cloth_mode or vacuum_mode):
                dx = pos[0] - pigeon.x
                dy = pos[1] - pigeon.y
                if dx * dx + dy * dy <= 50 * 50:
                    pigeon.action_message = "Coo! Thanks for the pet!"
                    print("Petted the pigeon!")

    # Update game state
    pigeon.update()
    sparkles = [spark for spark in sparkles if spark.update()]

    # Draw everything
    draw_room(screen)
    for pos in dander:
        pygame.draw.circle(screen, DANDER_COLOR, (int(pos[0]), int(pos[1])), 3)
    for pos in droppings:
        pygame.draw.circle(screen, DROPPING_COLOR, (int(pos[0]), int(pos[1])), 5)
    for spark in sparkles:
        spark.draw(screen)
    pigeon.draw(screen)

    # Draw UI elements
    pygame.draw.rect(screen, GRAY, vacuum_button)
    pygame.draw.rect(screen, GRAY, cloth_button)
    pygame.draw.rect(screen, GRAY, feed_button)

    # Draw button labels
    vacuum_text = font.render("Vacuum", True, BLACK)
    cloth_text = font.render("Cloth", True, BLACK)
    feed_text = font.render("Feed", True, BLACK)
    screen.blit(vacuum_text, (vacuum_button.x + 10, vacuum_button.y + 15))
    screen.blit(cloth_text, (cloth_button.x + 10, cloth_button.y + 15))
    screen.blit(feed_text, (feed_button.x + 10, feed_button.y + 15))

    # Draw score and combo
    score_text = score_font.render(f"Score: {cleaning_score}", True, BLACK)
    combo_text = font.render(f"Combo: x{combo_multiplier:.1f}", True, BLACK)
    screen.blit(score_text, (WIDTH - 200, 20))
    screen.blit(combo_text, (WIDTH - 200, 60))

    # Draw cleaning progress bar
    total_mess = len(dander) + len(droppings)
    if total_mess > 0:
        cleanliness = 1 - (total_mess / 50)  # Assume 50 is max mess
        draw_progress_bar(screen, 50, 20, 200, 20, cleanliness, (0, 255, 0))

    # Draw cleaning tool cursors
    if cloth_mode:
        draw_cloth(screen, mouse_pos, cleaning_active)
    elif vacuum_mode:
        draw_vacuum(screen, mouse_pos, cleaning_active)

    pygame.display.flip()

pygame.quit()