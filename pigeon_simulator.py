# pigeon.py
import pygame
import random
import math

FLOOR_COLOR = (210, 180, 140)
WALL_COLOR = (169, 169, 169)
WALL_THICKNESS = 20
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DANDER_COLOR = (240, 230, 140)
DROPPING_COLOR = (139, 69, 19)
SPARKLE_COLOR = (255, 255, 200)
VACUUM_COLOR = (100, 100, 100)
SEED_COLOR = (218, 165, 32)
SATIETY_COLOR = (50, 205, 50)

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

class FeedingEffect:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = 1.0
        self.particles = []
        for _ in range(5):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            self.particles.append({
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'size': random.uniform(2, 4)
            })

    def update(self):
        self.life -= 0.05
        return self.life > 0

    def draw(self, surface):
        for particle in self.particles:
            x = self.x + particle['dx'] * (1 - self.life) * 20
            y = self.y + particle['dy'] * (1 - self.life) * 20
            alpha = int(255 * self.life)
            s = pygame.Surface((int(particle['size'] * 2), int(particle['size'] * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*SEED_COLOR, alpha),
                               (int(particle['size']), int(particle['size'])),
                               int(particle['size']))
            surface.blit(s, (int(x - particle['size']), int(y - particle['size'])))

class Pigeon:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = 2
        self.dy = 0
        self.action = "idle"
        self.action_message = "Just chilling..."
        self.last_action_time = pygame.time.get_ticks()
        self.leg_phase = 0
        self.satiety = 50
        self.feeding_effects = []

    def move(self):
        self.x += self.dx
        self.y += self.dy
        if self.x - 50 <= WALL_THICKNESS or self.x + 50 >= 800 - WALL_THICKNESS:
            self.dx = -self.dx
        if self.y - 50 <= WALL_THICKNESS or self.y + 50 >= 600 - 100:
            self.dy = -self.dy

    def update(self):
        now = pygame.time.get_ticks()
        self.satiety = max(0, self.satiety - 0.02)
        self.update_feeding_effects()
        if self.dx != 0 or self.dy != 0:
            self.leg_phase += 0.2
        if now - self.last_action_time > 3000:
            self.choose_action()
            self.last_action_time = now
        if self.dx != 0 or self.dy != 0:
            self.move()

    def choose_action(self):
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
            self.dy = 0
        elif self.action == "loaf":
            self.action_message = "Just loafing around."
            self.dx = 0
            self.dy = 0
        elif self.action == "eat":
            self.action_message = "Munching on seeds."
            self.dx = random.choice([-1, 1])
            self.dy = 0
        elif self.action == "hop":
            self.action_message = "Hop hop!"
            self.dx = random.choice([-1, 1]) * 2
            self.dy = -4

    def draw(self, surface):
        pygame.draw.circle(surface, (150, 150, 150), (int(self.x), int(self.y)), 50)
        pygame.draw.circle(surface, BLACK, (int(self.x) - 15, int(self.y) - 10), 5)
        pygame.draw.circle(surface, BLACK, (int(self.x) + 15, int(self.y) - 10), 5)
        pygame.draw.polygon(surface, (255, 200, 0),
                            [(int(self.x), int(self.y)),
                             (int(self.x) + 30, int(self.y) + 10),
                             (int(self.x), int(self.y) + 20)])
        if self.dx != 0 or self.dy != 0:
            offset = int(10 * math.sin(self.leg_phase))
            left_start = (int(self.x) - 15, int(self.y) + 50)
            left_end = (int(self.x) - 15 + offset, int(self.y) + 70)
            pygame.draw.line(surface, BLACK, left_start, left_end, 3)
            right_start = (int(self.x) + 15, int(self.y) + 50)
            right_end = (int(self.x) + 15 - offset, int(self.y) + 70)
            pygame.draw.line(surface, BLACK, right_start, right_end, 3)
        text = pygame.font.SysFont(None, 24).render(self.action_message, True, BLACK)
        surface.blit(text, (int(self.x) - text.get_width() // 2, int(self.y) - 70))

    def draw_satiety_meter(self, surface):
        meter_width = 60
        meter_height = 8
        x = self.x - meter_width // 2
        y = self.y - 80
        pygame.draw.rect(surface, BLACK, (x - 1, y - 1, meter_width + 2, meter_height + 2), 1)
        fill_width = int(meter_width * (self.satiety / 100))
        pygame.draw.rect(surface, SATIETY_COLOR, (x, y, fill_width, meter_height))

    def eat_seed(self, seed_pos):
        self.satiety = min(self.satiety + 5, 100)
        self.feeding_effects.append(FeedingEffect(seed_pos[0], seed_pos[1]))

    def update_feeding_effects(self):
        self.feeding_effects = [effect for effect in self.feeding_effects if effect.update()]

    def draw_feeding_effects(self, surface):
        for effect in self.feeding_effects:
            effect.draw(surface)


def add_sparkles(x, y):
    for _ in range(5):
        sparkles.append(Sparkle(x, y))

def add_dander(pigeon_x, pigeon_y):
    for _ in range(10):
        x = pigeon_x + random.randint(-30, 30)
        y = pigeon_y + random.randint(-30, 30)
        dander.append((x, y))

def add_dropping(pigeon_x, pigeon_y):
    x = pigeon_x + random.randint(-20, 20)
    y = pigeon_y + random.randint(20, 40)
    droppings.append((x, y))

def draw_progress_bar(surface, x, y, width, height, progress, color):
    border = pygame.Rect(x, y, width, height)
    inner = pygame.Rect(x, y, int(width * progress), height)
    pygame.draw.rect(surface, BLACK, border, 2)
    pygame.draw.rect(surface, color, inner)

# utils.py
import pygame
import random
import math

def update_combo(last_clean_time, current_time, combo_multiplier):
    COMBO_TIMEOUT = 2000
    if current_time - last_clean_time > COMBO_TIMEOUT:
        combo_multiplier = 1
    return combo_multiplier

def draw_room(surface, WIDTH, HEIGHT, WALL_THICKNESS, FLOOR_COLOR, WALL_COLOR):
    surface.fill(FLOOR_COLOR)
    pygame.draw.rect(surface, WALL_COLOR, (0, 0, WIDTH, WALL_THICKNESS))
    pygame.draw.rect(surface, WALL_COLOR, (0, 0, WALL_THICKNESS, HEIGHT))
    pygame.draw.rect(surface, WALL_COLOR, (0, HEIGHT - WALL_THICKNESS, WIDTH, WALL_THICKNESS))
    pygame.draw.rect(surface, WALL_COLOR, (WIDTH - WALL_THICKNESS, 0, WALL_THICKNESS, HEIGHT))


def draw_cloth(surface, pos, cleaning):
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
    vacuum_size = 50
    if cleaning:
        pygame.draw.circle(surface, (200, 0, 0), pos, vacuum_size // 2, 3)
        s = pygame.Surface((vacuum_size, vacuum_size), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 0, 0, 100), (vacuum_size // 2, vacuum_size // 2), vacuum_size // 2)
        surface.blit(s, (pos[0] - vacuum_size // 2, pos[1] - vacuum_size // 2))
        add_sparkles(pos[0], pos[1])
    else:
        pygame.draw.circle(surface, VACUUM_COLOR, pos, vacuum_size // 2, 3)
    handle_start = (pos[0], pos[1])
    handle_end = (pos[0] + 30, pos[1] + 30)
    pygame.draw.line(surface, VACUUM_COLOR, handle_start, handle_end, 4)

def draw_feed_cursor(surface, pos):
    cursor_radius = 3
    seed_positions = [
        (-5, -5), (0, -5), (5, -5),
        (-5, 0), (0, 0), (5, 0),
        (-5, 5), (0, 5), (5, 5)
    ]
    for dx, dy in seed_positions:
        pygame.draw.circle(surface, SEED_COLOR,
                           (pos[0] + dx, pos[1] + dy), cursor_radius)

# events.py
import pygame

def handle_events(game):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            game.handle_click(pos)

# game.py
import pygame
import random
from pigeon import Pigeon, add_sparkles, add_dander, add_dropping, draw_progress_bar, Sparkle, SeedParticle, FeedingEffect
from utils import update_combo, draw_room, draw_cloth, draw_vacuum, draw_feed_cursor
from events import handle_events

WIDTH, HEIGHT = 800, 600
FLOOR_COLOR = (210, 180, 140)
WALL_COLOR = (169, 169, 169)
WALL_THICKNESS = 20
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DANDER_COLOR = (240, 230, 140)
DROPPING_COLOR = (139, 69, 19)
SPARKLE_COLOR = (255, 255, 200)
VACUUM_COLOR = (100, 100, 100)
SEED_COLOR = (218, 165, 32)
SATIETY_COLOR = (50, 205, 50)
font = pygame.font.SysFont(None, 24)
score_font = pygame.font.SysFont(None, 36)
vacuum_button = pygame.Rect(50, 500, 100, 50)
cloth_button = pygame.Rect(200, 500, 100, 50)
feed_button = pygame.Rect(350, 500, 100, 50)
dander = []
droppings = []
sparkles = []
seeds = []
cleaning_score = 0
combo_multiplier = 1
last_clean_time = 0
MAX_SATIETY = 100
SEED_POINTS = 5

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pet Pigeon Simulator")
        self.clock = pygame.time.Clock()
        self.pigeon = Pigeon(WIDTH // 2, HEIGHT // 2)
        self.cloth_mode = False
        self.vacuum_mode = False
        self.feed_mode = False
        self.running = True

    def run(self):
        while self.running:
            self.clock.tick(60)
            mouse_pos = pygame.mouse.get_pos()
            cleaning_active = pygame.mouse.get_pressed()[0]

            if self.cloth_mode or self.vacuum_mode or self.feed_mode:
                pygame.mouse.set_visible(False)
                if cleaning_active:
                    if self.cloth_mode:
                        cloth_rect = pygame.Rect(mouse_pos[0] - 20, mouse_pos[1] - 20, 40, 40)
                        original_count = len(droppings)
                        droppings = [drop for drop in droppings if not cloth_rect.collidepoint(drop)]
                        cleaned_count = original_count - len(droppings)
                        if cleaned_count > 0:
                            current_time = pygame.time.get_ticks()
                            combo_multiplier = update_combo(self.last_clean_time, current_time, combo_multiplier)
                            self.last_clean_time = current_time
                            cleaning_score += int(10 * combo_multiplier * cleaned_count)
                            add_sparkles(mouse_pos[0], mouse_pos[1])
                    elif self.vacuum_mode:
                        vacuum_radius = 25
                        original_count = len(dander)
                        dander = [d for d in dander if (d[0] - mouse_pos[0])**2 + (d[1] - mouse_pos[1])**2 > vacuum_radius**2]
                        cleaned_count = original_count - len(dander)
                        if cleaned_count > 0:
                            current_time = pygame.time.get_ticks()
                            combo_multiplier = update_combo(self.last_clean_time, current_time, combo_multiplier)
                            self.last_clean_time = current_time
                            cleaning_score += int(5 * combo_multiplier * cleaned_count)
                            add_sparkles(mouse_pos[0], mouse_pos[1])
            else:
                pygame.mouse.set_visible(True)

            handle_events(self)
            self.pigeon.update()
            sparkles = [spark for spark in sparkles if spark.update()]

            for seed in seeds[:]:
                seed.update()
                if not seed.falling:
                    dx = seed.x - self.pigeon.x
                    dy = seed.y - self.pigeon.y
                    if dx * dx + dy * dy < 50 * 50:
                        self.pigeon.eat_seed((seed.x, seed.y))
                        seeds.remove(seed)

            draw_room(self.screen, WIDTH, HEIGHT, WALL_THICKNESS, FLOOR_COLOR, WALL_COLOR)
            for pos in dander:
                pygame.draw.circle(self.screen, DANDER_COLOR, (int(pos[0]), int(pos[1])), 3)
            for pos in droppings:
                pygame.draw.circle(self.screen, DROPPING_COLOR, (int(pos[0]), int(pos[1])), 5)
            for spark in sparkles:
                spark.draw(self.screen)
            for seed in seeds:
                seed.draw(self.screen)
            self.pigeon.draw(self.screen)
            self.pigeon.draw_satiety_meter(self.screen)
            self.pigeon.draw_feeding_effects(self.screen)

            pygame.draw.rect(self.screen, GRAY, vacuum_button)
            pygame.draw.rect(self.screen, GRAY, cloth_button)
            pygame.draw.rect(self.screen, GRAY, feed_button)

            vacuum_text = font.render("Vacuum", True, BLACK)
            cloth_text = font.render("Cloth", True, BLACK)
            feed_text = font.render("Feed", True, BLACK)
            self.screen.blit(vacuum_text, (vacuum_button.x + 10, vacuum_button.y + 15))
            self.screen.blit(cloth_text, (cloth_button.x + 10, cloth_button.y + 15))
            self.screen.blit(feed_text, (feed_button.x + 10, feed_button.y + 15))

            score_text = score_font.render(f"Score: {cleaning_score}", True, BLACK)
            combo_text = font.render(f"Combo: x{combo_multiplier:.1f}", True, BLACK)
            self.screen.blit(score_text, (WIDTH - 200, 20))
            self.screen.blit(combo_text, (WIDTH - 200, 60))

            total_mess = len(dander) + len(droppings)
            if total_mess > 0:
                cleanliness = 1 - (total_mess / 50)
                draw_progress_bar(self.screen, 50, 20, 200, 20, cleanliness, (0, 255, 0))

            if self.cloth_mode:
                draw_cloth(self.screen, mouse_pos, cleaning_active)
            elif self.vacuum_mode:
                draw_vacuum(self.screen, mouse_pos, cleaning_active)
            elif self.feed_mode:
                draw_feed_cursor(self.screen, mouse_pos)

            pygame.display.flip()

    def handle_click(self, pos):
        if feed_button.collidepoint(pos):
            self.feed_mode = True
            self.cloth_mode = False
            self.vacuum_mode = False
        elif cloth_button.collidepoint(pos):
            self.cloth_mode = not self.cloth_mode
            self.feed_mode = False
            self.vacuum_mode = False
        elif vacuum_button.collidepoint(pos):
            self.vacuum_mode = not self.vacuum_mode
            self.cloth_mode = False
            self.feed_mode = False
        elif self.feed_mode:
            num_seeds = random.randint(8, 12)
            scatter_radius = 20
            for _ in range(num_seeds):
                seed_x = pos[0] + random.uniform(-scatter_radius, scatter_radius)
                seed_y = pos[1] - random.uniform(20, 40)
                target_y = pos[1] + random.uniform(-5, 5)
                seeds.append(SeedParticle(seed_x, seed_y, target_y))
            self.feed_mode = False
        elif not any([self.cloth_mode, self.vacuum_mode, self.feed_mode]):
            dx = pos[0] - self.pigeon.x
            dy = pos[1] - self.pigeon.y
            if dx * dx + dy * dy <= 50 * 50:
                self.pigeon.action_message = "Coo! Thanks for the pet!"


import pygame
from game import Game

if __name__ == "__main__":
    game = Game()
    game.run()
pygame.quit()