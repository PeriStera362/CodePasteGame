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
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DANDER_COLOR = (240, 230, 140)   # light yellowish dander
DROPPING_COLOR = (139, 69, 19)    # brown droppings

# Define Fonts
font = pygame.font.SysFont(None, 24)

# Define UI Button Rectangles
vacuum_button = pygame.Rect(50, 500, 100, 50)
cloth_button = pygame.Rect(200, 500, 100, 50)
feed_button = pygame.Rect(350, 500, 100, 50)

# Global lists to store dander and droppings positions
dander = []
droppings = []

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
        self.action = "idle"
        self.action_message = "Just chilling..."
        self.last_action_time = pygame.time.get_ticks()
        self.leg_phase = 0  # for leg animation

    def move(self):
        """Update the pigeon's position and bounce off screen edges."""
        self.x += self.dx
        # Bounce off left and right edges (assuming pigeon radius of 50)
        if self.x - 50 <= 0 or self.x + 50 >= WIDTH:
            self.dx = -self.dx

    def update(self):
        """Update movement and actions. Every few seconds, choose a new random action."""
        now = pygame.time.get_ticks()
        # If pigeon is moving, update leg animation
        if self.dx != 0:
            self.leg_phase += 0.2  # Adjust for desired swing speed
        # Choose new action every 3 seconds
        if now - self.last_action_time > 3000:
            self.choose_action()
            self.last_action_time = now
        # Only move if not loafing (loafing = stopped)
        if self.dx != 0:
            self.move()

    def choose_action(self):
        """Randomly choose an action and trigger side effects relative to the pigeon's current position."""
        actions = ["drop", "frolic", "coo", "loaf", "eat"]
        self.action = random.choice(actions)
        if self.action == "drop":
            self.action_message = "Oops, a dropping!"
            add_dropping(self.x, self.y)
            # Moving action: random speed and direction
            self.dx = random.choice([-1, 1]) * random.randint(1, 4)
        elif self.action == "frolic":
            self.action_message = "Fluffing feathers!"
            add_dander(self.x, self.y)
            self.dx = random.choice([-1, 1]) * random.randint(1, 4)
        elif self.action == "coo":
            self.action_message = "Cooing softly..."
            self.dx = random.choice([-1, 1]) * random.randint(1, 4)
        elif self.action == "loaf":
            self.action_message = "Just loafing around."
            self.dx = 0  # stop moving; legs won't animate
        elif self.action == "eat":
            self.action_message = "Munching on seeds."
            self.dx = random.choice([-1, 1]) * random.randint(1, 4)
        print("Pigeon action:", self.action)

    def draw(self, surface):
        """Draw the pigeon, its legs (if moving), and its current action message."""
        # Draw pigeon body (a simple circle)
        pygame.draw.circle(surface, (150, 150, 150), (int(self.x), int(self.y)), 50)
        # Draw eyes
        pygame.draw.circle(surface, BLACK, (int(self.x) - 15, int(self.y) - 10), 5)
        pygame.draw.circle(surface, BLACK, (int(self.x) + 15, int(self.y) - 10), 5)
        # Draw beak (a triangle)
        pygame.draw.polygon(surface, (255, 200, 0),
                            [(int(self.x), int(self.y)),
                             (int(self.x) + 30, int(self.y) + 10),
                             (int(self.x), int(self.y) + 20)])
        # Draw legs if pigeon is moving (dx != 0)
        if self.dx != 0:
            # Calculate leg swing offset using sine wave for simple animation
            offset = int(10 * math.sin(self.leg_phase))
            # Left leg: starting at bottom left of circle
            left_start = (int(self.x) - 15, int(self.y) + 50)
            left_end = (int(self.x) - 15 + offset, int(self.y) + 70)
            pygame.draw.line(surface, BLACK, left_start, left_end, 3)
            # Right leg: starting at bottom right of circle; opposite swing phase
            right_start = (int(self.x) + 15, int(self.y) + 50)
            right_end = (int(self.x) + 15 - offset, int(self.y) + 70)
            pygame.draw.line(surface, BLACK, right_start, right_end, 3)
        # Display the action message above the pigeon
        text = font.render(self.action_message, True, BLACK)
        surface.blit(text, (int(self.x) - text.get_width() // 2, int(self.y) - 70))

# Create a pigeon instance centered on the screen
pigeon = Pigeon(WIDTH // 2, HEIGHT // 2)

# Main Game Loop
running = True
while running:
    clock.tick(60)  # run at 60 frames per second
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle mouse clicks for UI buttons and petting the pigeon
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if vacuum_button.collidepoint(pos):
                dander.clear()
                print("Dander vacuumed!")
            elif cloth_button.collidepoint(pos):
                droppings.clear()
                print("Droppings cleaned!")
            elif feed_button.collidepoint(pos):
                pigeon.action_message = "Yum, seeds!"
                print("Fed the pigeon!")
            else:
                # Check if the pigeon was clicked (within its circular area)
                dx = pos[0] - pigeon.x
                dy = pos[1] - pigeon.y
                if dx * dx + dy * dy <= 50 * 50:
                    pigeon.action_message = "Coo! Thanks for the pet!"
                    print("Petted the pigeon!")

    # Update game state
    pigeon.update()

    # Clear the screen
    screen.fill(WHITE)

    # Draw dander particles
    for pos in dander:
        pygame.draw.circle(screen, DANDER_COLOR, (int(pos[0]), int(pos[1])), 3)

    # Draw droppings
    for pos in droppings:
        pygame.draw.circle(screen, DROPPING_COLOR, (int(pos[0]), int(pos[1])), 5)

    # Draw the pigeon
    pigeon.draw(screen)

    # Draw UI Buttons
    pygame.draw.rect(screen, GRAY, vacuum_button)
    pygame.draw.rect(screen, GRAY, cloth_button)
    pygame.draw.rect(screen, GRAY, feed_button)
    # Render button labels
    vacuum_text = font.render("Vacuum", True, BLACK)
    cloth_text = font.render("Cloth", True, BLACK)
    feed_text = font.render("Feed", True, BLACK)
    screen.blit(vacuum_text, (vacuum_button.x + 10, vacuum_button.y + 15))
    screen.blit(cloth_text, (cloth_button.x + 10, cloth_button.y + 15))
    screen.blit(feed_text, (feed_button.x + 10, feed_button.y + 15))

    # Update the display
    pygame.display.flip()

pygame.quit()