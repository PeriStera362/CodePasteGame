import pygame
import random
from pigeon import Pigeon
from utils import (
    draw_stat_bars, display_messages, draw_room, draw_cloth,
    draw_vacuum, draw_feed_cursor, draw_progress_bar,
    Sparkle, SeedParticle
)

# Constants
WIDTH = 800
HEIGHT = 600
WALL_THICKNESS = 20
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
FLOOR_COLOR = (210, 180, 140)
WALL_COLOR = (169, 169, 169)
DANDER_COLOR = (240, 230, 140)
DROPPING_COLOR = (139, 69, 19)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pigeon Simulator")
        self.clock = pygame.time.Clock()

        # Initialize game objects
        self.pigeon = Pigeon(WIDTH // 2, HEIGHT // 2)
        self.messages = []

        # Game state
        self.dander = []
        self.droppings = []
        self.sparkles = []
        self.seeds = []
        self.cleaning_score = 0
        self.combo_multiplier = 1
        self.last_clean_time = 0

        # UI elements
        self.font = pygame.font.SysFont(None, 24)
        self.score_font = pygame.font.SysFont(None, 36)
        self.vacuum_button = pygame.Rect(50, 500, 100, 50)
        self.cloth_button = pygame.Rect(200, 500, 100, 50)
        self.feed_button = pygame.Rect(350, 500, 100, 50)

        # Modes
        self.cloth_mode = False
        self.vacuum_mode = False
        self.feed_mode = False

        self.running = True

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_click(pygame.mouse.get_pos())

    def handle_click(self, pos):
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
        num_seeds = random.randint(8, 12)
        scatter_radius = 20
        for _ in range(num_seeds):
            seed_x = pos[0] + random.uniform(-scatter_radius, scatter_radius)
            seed_y = pos[1] - random.uniform(20, 40)
            target_y = pos[1] + random.uniform(-5, 5)
            self.seeds.append(SeedParticle(seed_x, seed_y, target_y))
        self.feed_mode = False

    def handle_pet(self, pos):
        dx = pos[0] - self.pigeon.x
        dy = pos[1] - self.pigeon.y
        if dx * dx + dy * dy <= 50 * 50:
            self.pigeon.action_message = "Coo! Thanks for the pet!"

    def update(self):
        # Update pigeon and effects
        self.pigeon.update()
        self.sparkles = [spark for spark in self.sparkles if spark.update()]

        # Update seeds and check for eating
        for seed in self.seeds[:]:
            seed.update()
            if not seed.falling:
                dx = seed.x - self.pigeon.x
                dy = seed.y - self.pigeon.y
                if dx * dx + dy * dy < 50 * 50:
                    self.pigeon.eat_seed((seed.x, seed.y))
                    self.seeds.remove(seed)

        # Handle cleaning modes
        mouse_pos = pygame.mouse.get_pos()
        cleaning_active = pygame.mouse.get_pressed()[0]

        if cleaning_active:
            if self.cloth_mode:
                self.handle_cloth_cleaning(mouse_pos)
            elif self.vacuum_mode:
                self.handle_vacuum_cleaning(mouse_pos)

    def handle_cloth_cleaning(self, pos):
        cloth_rect = pygame.Rect(pos[0] - 20, pos[1] - 20, 40, 40)
        original_count = len(self.droppings)
        self.droppings = [drop for drop in self.droppings if not cloth_rect.collidepoint(drop)]
        cleaned_count = original_count - len(self.droppings)
        if cleaned_count > 0:
            self.update_cleaning_score(cleaned_count * 10)
            self.sparkles.append(Sparkle(pos[0], pos[1]))

    def handle_vacuum_cleaning(self, pos):
        vacuum_radius = 25
        original_count = len(self.dander)
        self.dander = [d for d in self.dander if (d[0] - pos[0])**2 + (d[1] - pos[1])**2 > vacuum_radius**2]
        cleaned_count = original_count - len(self.dander)
        if cleaned_count > 0:
            self.update_cleaning_score(cleaned_count * 5)
            self.sparkles.append(Sparkle(pos[0], pos[1]))

    def update_cleaning_score(self, points):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_clean_time <= 2000:
            self.combo_multiplier = min(self.combo_multiplier + 0.5, 4.0)
        else:
            self.combo_multiplier = 1.0
        self.last_clean_time = current_time
        self.cleaning_score += int(points * self.combo_multiplier)

    def draw(self):
        # Draw background and room
        draw_room(self.screen, WIDTH, HEIGHT, WALL_THICKNESS)

        # Draw game objects
        for pos in self.dander:
            pygame.draw.circle(self.screen, DANDER_COLOR, (int(pos[0]), int(pos[1])), 3)
        for pos in self.droppings:
            pygame.draw.circle(self.screen, DROPPING_COLOR, (int(pos[0]), int(pos[1])), 5)
        for spark in self.sparkles:
            spark.draw(self.screen)
        for seed in self.seeds:
            seed.draw(self.screen)

        # Draw pigeon
        self.pigeon.draw(self.screen)
        self.pigeon.draw_satiety_meter(self.screen)
        self.pigeon.draw_feeding_effects(self.screen)

        # Draw UI
        self.draw_ui()

        # Update display
        pygame.display.flip()

    def draw_ui(self):
        # Draw buttons
        pygame.draw.rect(self.screen, GRAY, self.vacuum_button)
        pygame.draw.rect(self.screen, GRAY, self.cloth_button)
        pygame.draw.rect(self.screen, GRAY, self.feed_button)

        # Draw button labels
        vacuum_text = self.font.render("Vacuum", True, BLACK)
        cloth_text = self.font.render("Cloth", True, BLACK)
        feed_text = self.font.render("Feed", True, BLACK)
        self.screen.blit(vacuum_text, (self.vacuum_button.x + 10, self.vacuum_button.y + 15))
        self.screen.blit(cloth_text, (self.cloth_button.x + 10, self.cloth_button.y + 15))
        self.screen.blit(feed_text, (self.feed_button.x + 10, self.feed_button.y + 15))

        # Draw score and combo
        score_text = self.score_font.render(f"Score: {self.cleaning_score}", True, BLACK)
        combo_text = self.font.render(f"Combo: x{self.combo_multiplier:.1f}", True, BLACK)
        self.screen.blit(score_text, (WIDTH - 200, 20))
        self.screen.blit(combo_text, (WIDTH - 200, 60))

        # Draw cursor based on mode
        mouse_pos = pygame.mouse.get_pos()
        cleaning_active = pygame.mouse.get_pressed()[0]

        if self.cloth_mode:
            draw_cloth(self.screen, mouse_pos, cleaning_active)
        elif self.vacuum_mode:
            draw_vacuum(self.screen, mouse_pos, cleaning_active)
        elif self.feed_mode:
            draw_feed_cursor(self.screen, mouse_pos)

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.handle_input()
            self.update()
            self.draw()

        pygame.quit()