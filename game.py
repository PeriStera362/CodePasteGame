import pygame
import random
from classes import Pigeon, Sparkle, SeedParticle
from utils import (
    draw_stat_bars, display_messages, draw_room, draw_cloth,
    draw_vacuum, draw_feed_cursor, draw_progress_bar, update_combo,
    FLOOR_COLOR, WALL_COLOR, BLACK, GRAY, DANDER_COLOR, DROPPING_COLOR
)

# Game Constants
WIDTH = 800
HEIGHT = 600
WALL_THICKNESS = 20

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pigeon Simulator")
        self.clock = pygame.time.Clock()

        # Game objects
        self.pigeon = Pigeon(WIDTH // 2, HEIGHT // 2)
        self.messages = []
        self.sparkles = []
        self.seeds = []
        self.cleaning_score = 0
        self.combo_multiplier = 1
        self.last_clean_time = 0

        # UI elements
        self.setup_ui()

        # Game modes
        self.cloth_mode = False
        self.vacuum_mode = False
        self.feed_mode = False

        self.running = True

    def setup_ui(self):
        """Initialize UI elements."""
        self.font = pygame.font.SysFont(None, 24)
        self.score_font = pygame.font.SysFont(None, 36)
        self.vacuum_button = pygame.Rect(50, 500, 100, 50)
        self.cloth_button = pygame.Rect(200, 500, 100, 50)
        self.feed_button = pygame.Rect(350, 500, 100, 50)

    def handle_input(self):
        """Process user input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_click(pygame.mouse.get_pos())

    def handle_click(self, pos):
        """Handle mouse click events."""
        if self.feed_button.collidepoint(pos):
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
            self.pigeon.action_message = "Coo! Thanks for the pet!"

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
                        self.pigeon.start_eating((seed.x, seed.y))
                        seed.being_eaten = True
                        self.pigeon.eat_seed((seed.x, seed.y))
                # If seed is visible and not too far, move towards it
                elif distance < 200 * 200 and not self.pigeon.is_eating:
                    self.pigeon.move_towards_seed((seed.x, seed.y))

    def draw(self):
        """Render game state."""
        # Draw background
        draw_room(self.screen, WIDTH, HEIGHT, WALL_THICKNESS)

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
        self.pigeon.draw_satiety_meter(self.screen)
        self.pigeon.draw_feeding_effects(self.screen)

    def draw_ui(self):
        """Draw UI elements."""
        # Draw buttons
        for button, label in [
            (self.vacuum_button, "Vacuum"),
            (self.cloth_button, "Cloth"),
            (self.feed_button, "Feed")
        ]:
            pygame.draw.rect(self.screen, GRAY, button)
            text = self.font.render(label, True, BLACK)
            self.screen.blit(text, (button.x + 10, button.y + 15))

        # Draw score and combo
        score_text = self.score_font.render(f"Score: {self.cleaning_score}", True, BLACK)
        combo_text = self.font.render(f"Combo: x{self.combo_multiplier:.1f}", True, BLACK)
        self.screen.blit(score_text, (WIDTH - 200, 20))
        self.screen.blit(combo_text, (WIDTH - 200, 60))

        # Draw cleanliness bar
        total_mess = len(self.pigeon.dander) + len(self.pigeon.droppings)
        if total_mess > 0:
            cleanliness = 1 - (total_mess / 50)
            draw_progress_bar(self.screen, 50, 20, 200, 20, cleanliness, (0, 255, 0))

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