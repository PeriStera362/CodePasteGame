import pygame
import random
from classes import Pigeon, Sparkle, SeedParticle, Ball
from utils import (
    draw_status_bars, draw_room, draw_cloth,
    draw_vacuum, draw_feed_cursor,
    FLOOR_COLOR, WALL_COLOR, BLACK, GRAY, DANDER_COLOR, DROPPING_COLOR
)

# Game Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700  # Increased to accommodate UI
ROOM_TOP = 80       # Room starts below status bars
ROOM_BOTTOM = 600   # Room ends above buttons
WALL_THICKNESS = 20

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pigeon Simulator")
        self.clock = pygame.time.Clock()

        # Game objects
        self.pigeon = Pigeon(WINDOW_WIDTH // 2, (ROOM_TOP + ROOM_BOTTOM) // 2)
        self.messages = []
        self.sparkles = []
        self.seeds = []
        self.ball = None

        # UI elements
        self.setup_ui()

        # Game modes
        self.cloth_mode = False
        self.vacuum_mode = False
        self.feed_mode = False

        self.running = True
        self.last_clean_time = 0
        self.cleaning_score = 0
        self.combo_multiplier = 1.0

    def setup_ui(self):
        """Initialize UI elements."""
        self.font = pygame.font.SysFont(None, 24)
        button_y = ROOM_BOTTOM + 20  # Place buttons below room
        button_width = 100
        button_spacing = 30
        start_x = (WINDOW_WIDTH - (4 * button_width + 3 * button_spacing)) // 2

        self.vacuum_button = pygame.Rect(start_x, button_y, button_width, 50)
        self.cloth_button = pygame.Rect(start_x + button_width + button_spacing, button_y, button_width, 50)
        self.feed_button = pygame.Rect(start_x + 2 * (button_width + button_spacing), button_y, button_width, 50)
        self.play_button = pygame.Rect(start_x + 3 * (button_width + button_spacing), button_y, button_width, 50)

    def handle_input(self):
        """Process user input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_click(pygame.mouse.get_pos())

    def handle_click(self, pos):
        """Handle mouse click events."""
        if self.play_button.collidepoint(pos):
            if not self.ball or not self.pigeon.playing_with_ball:
                self.ball = Ball(WINDOW_WIDTH // 2, (ROOM_TOP + ROOM_BOTTOM) // 2)
                self.pigeon.start_playing(self.ball)
        elif self.feed_button.collidepoint(pos):
            self.feed_mode = True
            self.cloth_mode = False
            self.vacuum_mode = False
        elif self.cloth_button.collidepoint(pos):
            self.cloth_mode = not self.cloth_mode
            self.feed_mode = False
            self.vacuum_mode = False
        elif self.vacuum_button.collidepoint(pos):
            self.vacuum_mode = not self.vacuum_mode
            self.cloth_mode = False
            self.feed_mode = False
        elif self.feed_mode:
            self.handle_feed(pos)
        elif not any([self.cloth_mode, self.vacuum_mode, self.feed_mode]):
            self.handle_pet(pos)

    def handle_feed(self, pos):
        """Handle feed mode interaction."""
        num_seeds = random.randint(8, 12)
        scatter_radius = 20
        for _ in range(num_seeds):
            seed_x = pos[0] + random.uniform(-scatter_radius, scatter_radius)
            seed_y = pos[1] - random.uniform(20, 40)
            target_y = pos[1] + random.uniform(-5, 5)
            self.seeds.append(SeedParticle(seed_x, seed_y, target_y))
        self.feed_mode = False

    def handle_pet(self, pos):
        """Handle petting interaction."""
        dx = pos[0] - self.pigeon.x
        dy = pos[1] - self.pigeon.y
        if dx * dx + dy * dy <= 50 * 50:
            self.pigeon.start_petting()

    def handle_cleaning(self, pos, cleaning_active):
        """Handle cleaning mode interactions."""
        if cleaning_active:
            if self.cloth_mode:
                self.handle_cloth_cleaning(pos)
            elif self.vacuum_mode:
                self.handle_vacuum_cleaning(pos)

    def handle_cloth_cleaning(self, pos):
        """Handle cloth cleaning interaction."""
        cloth_rect = pygame.Rect(pos[0] - 20, pos[1] - 20, 40, 40)
        original_count = len(self.pigeon.droppings)
        self.pigeon.droppings = [drop for drop in self.pigeon.droppings if not cloth_rect.collidepoint(drop)]
        cleaned_count = original_count - len(self.pigeon.droppings)
        if cleaned_count > 0:
            self.update_cleaning_score(cleaned_count * 10)
            self.sparkles.append(Sparkle(pos[0], pos[1]))

    def handle_vacuum_cleaning(self, pos):
        """Handle vacuum cleaning interaction."""
        vacuum_radius = 25
        original_count = len(self.pigeon.dander)
        self.pigeon.dander = [d for d in self.pigeon.dander if (d[0] - pos[0])**2 + (d[1] - pos[1])**2 > vacuum_radius**2]
        cleaned_count = original_count - len(self.pigeon.dander)
        if cleaned_count > 0:
            self.update_cleaning_score(cleaned_count * 5)
            self.sparkles.append(Sparkle(pos[0], pos[1]))

    def update_cleaning_score(self, points):
        """Update cleaning score and combo."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_clean_time <= 2000:
            self.combo_multiplier = min(self.combo_multiplier + 0.5, 4.0)
        else:
            self.combo_multiplier = 1.0
        self.last_clean_time = current_time
        self.cleaning_score += int(points * self.combo_multiplier)

    def update(self):
        """Update game state."""
        mouse_pos = pygame.mouse.get_pos()
        cleaning_active = pygame.mouse.get_pressed()[0]

        self.handle_cleaning(mouse_pos, cleaning_active)
        self.pigeon.update()
        self.sparkles = [spark for spark in self.sparkles if spark.update()]

        # Update seeds and check for eating
        for seed in self.seeds[:]:
            if not seed.update():  # If seed has completely faded out
                self.seeds.remove(seed)
                continue

            if not seed.falling and not seed.being_eaten:
                dx = seed.x - self.pigeon.x
                dy = seed.y - self.pigeon.y
                distance = dx * dx + dy * dy

                # If pigeon is close enough to eat
                if distance < 50 * 50:
                    if not self.pigeon.is_eating:
                        self.pigeon.eat_seed((seed.x, seed.y), seed)
                # If seed is visible and not too far, move towards it
                elif distance < 200 * 200 and not self.pigeon.is_eating:
                    self.pigeon.move_towards_seed((seed.x, seed.y))

        # Update ball if it exists
        if self.ball:
            self.ball.update(WINDOW_WIDTH, WINDOW_HEIGHT, WALL_THICKNESS)

            # Check if ball should be removed
            edge_margin = 50
            near_edge = (
                self.ball.x <= WALL_THICKNESS + edge_margin or
                self.ball.x >= WINDOW_WIDTH - WALL_THICKNESS - edge_margin or
                self.ball.y <= ROOM_TOP + edge_margin or #Corrected y-coordinate check
                self.ball.y >= ROOM_BOTTOM - WALL_THICKNESS - edge_margin
            )

            # Only remove if ball has been pushed and is near edge
            if not self.ball.being_pushed and near_edge and self.pigeon.playing_with_ball:
                self.ball = None
                self.pigeon.playing_with_ball = False
                self.pigeon.action_message = "That was fun!"

    def draw(self):
        """Render game state."""
        # Fill background
        self.screen.fill((200, 200, 200))  # Light gray background

        # Draw room background
        pygame.draw.rect(self.screen, FLOOR_COLOR, 
                        (0, ROOM_TOP, WINDOW_WIDTH, ROOM_BOTTOM - ROOM_TOP))

        # Draw room walls
        draw_room(self.screen, WINDOW_WIDTH, ROOM_BOTTOM - ROOM_TOP, WALL_THICKNESS, ROOM_TOP)

        # Draw status bars (at the top)
        draw_status_bars(self.screen, self.pigeon)

        # Draw game objects
        self.draw_game_objects()
        self.draw_ui()

        # Update display
        pygame.display.flip()

    def draw_game_objects(self):
        """Draw all game objects."""
        for pos in self.pigeon.dander:
            pygame.draw.circle(self.screen, DANDER_COLOR, (int(pos[0]), int(pos[1])), 3)
        for pos in self.pigeon.droppings:
            pygame.draw.circle(self.screen, DROPPING_COLOR, (int(pos[0]), int(pos[1])), 5)
        for spark in self.sparkles:
            spark.draw(self.screen)
        for seed in self.seeds:
            seed.draw(self.screen)

        self.pigeon.draw(self.screen)
        self.pigeon.draw_feeding_effects(self.screen)

        if self.ball:
            self.ball.draw(self.screen)

    def draw_ui(self):
        """Draw UI elements."""
        # Draw buttons
        for button, label in [
            (self.vacuum_button, "Vacuum"),
            (self.cloth_button, "Cloth"),
            (self.feed_button, "Feed"),
            (self.play_button, "Play")
        ]:
            pygame.draw.rect(self.screen, GRAY, button)
            text = self.font.render(label, True, BLACK)
            text_rect = text.get_rect(center=button.center)
            self.screen.blit(text, text_rect)

        # Draw mode-specific cursors
        mouse_pos = pygame.mouse.get_pos()
        cleaning_active = pygame.mouse.get_pressed()[0]
        pygame.mouse.set_visible(not any([self.cloth_mode, self.vacuum_mode, self.feed_mode]))

        if self.cloth_mode:
            draw_cloth(self.screen, mouse_pos, cleaning_active)
        elif self.vacuum_mode:
            draw_vacuum(self.screen, mouse_pos, cleaning_active)
        elif self.feed_mode:
            draw_feed_cursor(self.screen, mouse_pos)

    def run(self):
        """Main game loop."""
        while self.running:
            self.clock.tick(60)
            self.handle_input()
            self.update()
            self.draw()

        pygame.quit()