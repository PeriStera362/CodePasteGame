import pygame
import random
import math

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
            pygame.draw.circle(s, (218, 165, 32, alpha),
                            (int(particle['size']), int(particle['size'])),
                            int(particle['size']))
            surface.blit(s, (int(x - particle['size']), int(y - particle['size'])))

class Pigeon:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = 2
        self.dy = 0
        self.health = 100
        self.happiness = 100
        self.hunger = 0
        self.cleanliness = 100
        self.energy = 100
        self.action = "idle"
        self.action_message = "Just chilling..."
        self.last_action_time = pygame.time.get_ticks()
        self.leg_phase = 0
        self.satiety = 50  # Start with 50% satiety
        self.feeding_effects = []

    def update(self):
        now = pygame.time.get_ticks()
        # Decay satiety over time
        self.satiety = max(0, self.satiety - 0.02)
        self.update_feeding_effects()

        if self.dx != 0 or self.dy != 0:
            self.leg_phase += 0.2  # advance leg animation

        # Update core stats
        self.hunger = min(100, self.hunger + 0.1)
        self.energy = max(0, self.energy - 0.05)
        self.cleanliness = max(0, self.cleanliness - 0.1)
        self.happiness = (self.health + (100 - self.hunger) + self.cleanliness + self.energy) / 4

        if now - self.last_action_time > 3000:
            self.choose_action()
            self.last_action_time = now

        if self.dx != 0 or self.dy != 0:
            self.move()

    def move(self):
        """Update the pigeon's position and bounce off walls."""
        self.x += self.dx
        self.y += self.dy
        # Bounce off walls (accounting for wall thickness)
        if self.x - 50 <= 20 or self.x + 50 >= 780:  # 20px wall thickness
            self.dx = -self.dx
        if self.y - 50 <= 20 or self.y + 50 >= 500:  # Keep above buttons
            self.dy = -self.dy

    def draw(self, surface):
        """Draw the pigeon with its body, face, and animated legs if moving."""
        # Draw pigeon body
        pygame.draw.circle(surface, (150, 150, 150), (int(self.x), int(self.y)), 50)
        # Draw eyes
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x) - 15, int(self.y) - 10), 5)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x) + 15, int(self.y) - 10), 5)
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
            pygame.draw.line(surface, (0, 0, 0), left_start, left_end, 3)
            # Right leg
            right_start = (int(self.x) + 15, int(self.y) + 50)
            right_end = (int(self.x) + 15 - offset, int(self.y) + 70)
            pygame.draw.line(surface, (0, 0, 0), right_start, right_end, 3)

        # Display action message above the pigeon
        font = pygame.font.Font(None, 24)
        text = font.render(self.action_message, True, (0, 0, 0))
        surface.blit(text, (int(self.x) - text.get_width() // 2, int(self.y) - 70))

    def choose_action(self):
        """Randomly choose an action and adjust movement accordingly."""
        actions = ["drop", "frolic", "coo", "loaf", "eat", "hop"]
        self.action = random.choice(actions)
        if self.action == "drop":
            self.action_message = "Oops, a dropping!"
            self.dx = random.choice([-1, 1]) * random.randint(1, 3)
            self.dy = random.choice([-1, 1]) * random.randint(1, 2)
        elif self.action == "frolic":
            self.action_message = "Fluffing feathers!"
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

    def eat_seed(self, seed_pos):
        self.satiety = min(self.satiety + 5, 100)
        self.feeding_effects.append(FeedingEffect(seed_pos[0], seed_pos[1]))

    def update_feeding_effects(self):
        self.feeding_effects = [effect for effect in self.feeding_effects if effect.update()]

    def draw_feeding_effects(self, surface):
        for effect in self.feeding_effects:
            effect.draw(surface)

    def draw_satiety_meter(self, surface):
        meter_width = 60
        meter_height = 8
        x = self.x - meter_width // 2
        y = self.y - 80
        # Draw border
        pygame.draw.rect(surface, (0, 0, 0), (x - 1, y - 1, meter_width + 2, meter_height + 2), 1)
        # Draw fill
        fill_width = int(meter_width * (self.satiety / 100))
        pygame.draw.rect(surface, (50, 205, 50), (x, y, fill_width, meter_height))