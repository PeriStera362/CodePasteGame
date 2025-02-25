import pygame
import random
import math

# Colors
SEED_COLOR = (218, 165, 32)
BLACK = (0, 0, 0)
SPARKLE_COLOR = (255, 255, 200)

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
        self.being_eaten = False
        self.fade_alpha = 255

    def update(self):
        if self.being_eaten:
            self.fade_alpha = max(0, self.fade_alpha - 15)  # Fade out when being eaten
            return self.fade_alpha > 0
        elif self.falling:
            self.y += self.fall_speed
            self.rotation += self.spin_speed
            if self.y >= self.target_y:
                self.y = self.target_y
                self.falling = False
        return True

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

        if self.being_eaten:
            s = pygame.Surface((seed_size * 4, seed_size * 4), pygame.SRCALPHA)
            pygame.draw.polygon(s, (*SEED_COLOR, self.fade_alpha), [
                (p[0] - self.x + seed_size * 2, p[1] - self.y + seed_size * 2) for p in points
            ])
            surface.blit(s, (self.x - seed_size * 2, self.y - seed_size * 2))
        else:
            pygame.draw.polygon(surface, SEED_COLOR, points)

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = random.uniform(-3, 3)
        self.dy = random.uniform(-3, 3)
        self.radius = 10
        self.color = (255, 0, 0)  # Red ball
        self.being_pushed = False
        self.push_timer = 0
        self.push_duration = 2000  # 2 seconds of pushing
        self.push_decay = 0.95  # Decay rate for push force

    def update(self, width, height, wall_thickness):
        """Update ball position and handle bouncing."""
        # Update position
        self.x += self.dx
        self.y += self.dy

        # Bounce off walls with energy loss
        bounce_damping = 0.8  # Reduce velocity on bounce
        if self.x - self.radius <= wall_thickness:
            self.x = wall_thickness + self.radius
            self.dx = abs(self.dx) * bounce_damping
        elif self.x + self.radius >= width - wall_thickness:
            self.x = width - wall_thickness - self.radius
            self.dx = -abs(self.dx) * bounce_damping

        if self.y - self.radius <= wall_thickness:
            self.y = wall_thickness + self.radius
            self.dy = abs(self.dy) * bounce_damping
        elif self.y + self.radius >= height - wall_thickness:
            self.y = height - wall_thickness - self.radius
            self.dy = -abs(self.dy) * bounce_damping

        # Apply friction
        self.dx *= 0.99
        self.dy *= 0.99

        # Stop very slow movement
        if abs(self.dx) < 0.1: self.dx = 0
        if abs(self.dy) < 0.1: self.dy = 0

        # Check if we should still be in "pushed" state
        if self.being_pushed:
            current_time = pygame.time.get_ticks()
            if current_time - self.push_timer >= self.push_duration:
                self.being_pushed = False

    def draw(self, surface):
        """Draw the ball with shadow effect."""
        # Draw shadow
        shadow_offset = 4
        pygame.draw.circle(surface, (100, 100, 100), 
                         (int(self.x + shadow_offset), int(self.y + shadow_offset)), 
                         self.radius)
        # Draw ball
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        # Draw highlight
        highlight_pos = (int(self.x - self.radius/3), int(self.y - self.radius/3))
        pygame.draw.circle(surface, (255, 200, 200), highlight_pos, 3)


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
        self.satiety = 50
        self.feeding_effects = []
        self.dander = []
        self.droppings = []
        # Eating-related attributes
        self.is_eating = False
        self.eating_time = 0
        self.eating_duration = 800
        self.eating_animation_phase = 0
        self.target_seed = None
        # Petting-related attributes
        self.being_petted = False
        self.pet_time = 0
        self.pet_duration = 1000  # 1 second of happy animation
        self.pet_animation_phase = 0
        self.playing_with_ball = False
        self.play_start_time = 0
        self.play_duration = 5000  # 5 seconds of playing
        self.target_ball = None

    def start_petting(self):
        """Start the petting animation."""
        self.being_petted = True
        self.pet_time = pygame.time.get_ticks()
        self.pet_animation_phase = 0
        self.action_message = "Coo! Thanks for the pet!"
        # Increase happiness when petted
        self.happiness = min(100, self.happiness + 10)

    def update(self):
        now = pygame.time.get_ticks()

        # Handle petting animation
        if self.being_petted:
            self.pet_animation_phase += 0.2
            if now - self.pet_time >= self.pet_duration:
                self.being_petted = False
                self.pet_animation_phase = 0

        # Only update satiety and stats if not eating
        if not self.is_eating:
            self.satiety = max(0, self.satiety - 0.02)
            # Update core stats only when not eating
            self.hunger = min(100, self.hunger + 0.1)
            self.energy = max(0, self.energy - 0.05)
            self.cleanliness = max(0, self.cleanliness - 0.1)
            self.happiness = max(0, self.happiness - 0.05)  # Gradual decrease in happiness
            self.happiness = (self.health + (100 - self.hunger) + self.cleanliness + self.energy) / 4

        self.update_feeding_effects()

        if self.is_eating:
            self.eating_animation_phase += 0.2
            if now - self.eating_time >= self.eating_duration:
                self.finish_eating()
            return  # Don't move while eating

        # Handle playing state
        if self.playing_with_ball:
            if now - self.play_start_time >= self.play_duration:
                self.playing_with_ball = False
                self.target_ball = None
                self.action_message = "That was fun!"
            elif self.target_ball:
                self.chase_ball(self.target_ball)


        if self.dx != 0 or self.dy != 0:
            self.leg_phase += 0.2

        if now - self.last_action_time > 3000:
            self.choose_action()
            self.last_action_time = now

        if self.dx != 0 or self.dy != 0:
            self.move()

    def finish_eating(self):
        """Reset eating state and resume normal behavior."""
        self.is_eating = False
        self.target_seed = None
        self.eating_animation_phase = 0
        self.action_message = "Yum!"
        self.dx = random.choice([-1, 1])  # Resume random movement
        self.dy = 0

    def move_towards_seed(self, seed_pos):
        """Move the pigeon towards a seed."""
        if self.is_eating:
            return  # Don't move if already eating

        dx = seed_pos[0] - self.x
        dy = seed_pos[1] - self.y
        dist = (dx * dx + dy * dy) ** 0.5
        if dist > 0:
            self.dx = dx / dist * 2
            self.dy = dy / dist * 2

    def start_eating(self, seed_pos):
        """Start the eating animation."""
        if self.is_eating:
            return  # Don't start eating if already eating

        self.is_eating = True
        self.eating_time = pygame.time.get_ticks()
        self.dx = 0
        self.dy = 0
        self.action_message = "Nom nom nom..."
        self.target_seed = seed_pos

    def draw(self, surface):
        """Draw the pigeon with its body, face, and animated legs if moving."""
        bob_offset = 0

        if self.is_eating:
            # Eating animation
            bob_offset = math.sin(self.eating_animation_phase) * 5
            pygame.draw.circle(surface, (150, 150, 150), 
                             (int(self.x), int(self.y + bob_offset)), 50)

            # Animate beak during eating
            beak_open = math.sin(self.eating_animation_phase * 2) * 10
            pygame.draw.polygon(surface, (255, 200, 0),
                              [(int(self.x), int(self.y + bob_offset)),
                               (int(self.x) + 30, int(self.y + bob_offset) + 10 - beak_open),
                               (int(self.x), int(self.y + bob_offset) + 20)])
        else:
            # Normal drawing
            pygame.draw.circle(surface, (150, 150, 150), (int(self.x), int(self.y)), 50)
            pygame.draw.polygon(surface, (255, 200, 0),
                              [(int(self.x), int(self.y)),
                               (int(self.x) + 30, int(self.y) + 10),
                               (int(self.x), int(self.y) + 20)])

        # Draw eyes based on state
        if self.being_petted:
            # Happy closed eyes (^ ^)
            eye_y = self.y + bob_offset - 10
            # Left eye
            start_l = (int(self.x) - 20, int(eye_y))
            end_l = (int(self.x) - 10, int(eye_y))
            control_l = (int(self.x) - 15, int(eye_y) - 5)
            # Right eye
            start_r = (int(self.x) + 10, int(eye_y))
            end_r = (int(self.x) + 20, int(eye_y))
            control_r = (int(self.x) + 15, int(eye_y) - 5)

            # Draw curved lines for happy eyes
            for i in range(0, 10):
                t = i / 10
                # Left eye
                x1 = (1-t)**2 * start_l[0] + 2*(1-t)*t*control_l[0] + t**2*end_l[0]
                y1 = (1-t)**2 * start_l[1] + 2*(1-t)*t*control_l[1] + t**2*end_l[1]
                # Right eye
                x2 = (1-t)**2 * start_r[0] + 2*(1-t)*t*control_r[0] + t**2*end_r[0]
                y2 = (1-t)**2 * start_r[1] + 2*(1-t)*t*control_r[1] + t**2*end_r[1]

                pygame.draw.circle(surface, (0, 0, 0), (int(x1), int(y1)), 1)
                pygame.draw.circle(surface, (0, 0, 0), (int(x2), int(y2)), 1)
        else:
            # Normal eyes
            pygame.draw.circle(surface, (0, 0, 0), (int(self.x) - 15, int(self.y + bob_offset) - 10), 5)
            pygame.draw.circle(surface, (0, 0, 0), (int(self.x) + 15, int(self.y + bob_offset) - 10), 5)

        if self.dx != 0 or self.dy != 0:
            offset = int(10 * math.sin(self.leg_phase))
            left_start = (int(self.x) - 15, int(self.y) + 50)
            left_end = (int(self.x) - 15 + offset, int(self.y) + 70)
            pygame.draw.line(surface, (0, 0, 0), left_start, left_end, 3)
            right_start = (int(self.x) + 15, int(self.y) + 50)
            right_end = (int(self.x) + 15 - offset, int(self.y) + 70)
            pygame.draw.line(surface, (0, 0, 0), right_start, right_end, 3)

        # Display action message above the pigeon
        font = pygame.font.Font(None, 24)
        text = font.render(self.action_message, True, (0, 0, 0))
        surface.blit(text, (int(self.x) - text.get_width() // 2, int(self.y) - 70))

    def choose_action(self):
        actions = ["drop", "frolic", "coo", "loaf", "eat", "hop"]
        self.action = random.choice(actions)
        if self.action == "drop":
            self.action_message = "Oops, a dropping!"
            self.add_dropping()
            self.dx = random.choice([-1, 1]) * random.randint(1, 3)
            self.dy = random.choice([-1, 1]) * random.randint(1, 2)
        elif self.action == "frolic":
            self.action_message = "Fluffing feathers!"
            self.add_dander()
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
            self.action_message = "Looking for seeds..." #Changed message
            self.dx = 0
            self.dy = 0
            #Find nearest seed
            #self.start_eating(nearest_seed_pos) #This line needs more info
        elif self.action == "hop":
            self.action_message = "Hop hop!"
            self.dx = random.choice([-1, 1]) * 2
            self.dy = -4

    def add_dander(self):
        """Add a burst of dander particles near the pigeon's current position."""
        for _ in range(10):
            x = self.x + random.randint(-30, 30)
            y = self.y + random.randint(-30, 30)
            self.dander.append((x, y))

    def add_dropping(self):
        """Add a dropping particle near the pigeon's current position."""
        x = self.x + random.randint(-20, 20)
        y = self.y + random.randint(20, 40)
        self.droppings.append((x, y))

    def eat_seed(self, seed_pos, seed_object): #Added seed_object parameter
        self.satiety = min(self.satiety + 5, 100)
        self.feeding_effects.append(FeedingEffect(seed_pos[0], seed_pos[1]))
        self.start_eating(seed_pos)
        seed_object.being_eaten = True #Added line to initiate fade-out

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
        pygame.draw.rect(surface, BLACK, (x - 1, y - 1, meter_width + 2, meter_height + 2), 1)
        fill_width = int(meter_width * (self.satiety / 100))
        pygame.draw.rect(surface, (50, 205, 50), (x, y, fill_width, meter_height))

    def move(self):
        self.x += self.dx
        self.y += self.dy
        if self.x - 50 <= 20 or self.x + 50 >= 780:
            self.dx = -self.dx
        if self.y - 50 <= 20 or self.y + 50 >= 500:
            self.dy = -self.dy

    def start_playing(self, ball):
        """Start playing with a ball."""
        self.playing_with_ball = True
        self.play_start_time = pygame.time.get_ticks()
        self.target_ball = ball
        self.action_message = "Time to play!"

    def chase_ball(self, ball):
        """Chase the ball and push it when close."""
        if not self.playing_with_ball:
            return

        dx = ball.x - self.x
        dy = ball.y - self.y
        dist = (dx * dx + dy * dy) ** 0.5

        if dist > 0:
            # Move towards ball
            speed = 3
            self.dx = (dx / dist) * speed
            self.dy = (dy / dist) * speed

            # If close enough, push the ball
            if dist < 60:
                # Calculate push vector
                push_force = 8
                push_angle = math.atan2(dy, dx)

                # Add some randomness to push direction
                push_angle += random.uniform(-0.5, 0.5)

                # Apply push force to ball
                ball.dx = math.cos(push_angle) * push_force
                ball.dy = math.sin(push_angle) * push_force

                # Apply recoil to pigeon
                recoil = 2
                self.dx = -math.cos(push_angle) * recoil
                self.dy = -math.sin(push_angle) * recoil

                ball.being_pushed = True
                ball.push_timer = pygame.time.get_ticks()

                # Add some "playful" randomness to pigeon's next move
                self.action_message = random.choice([
                    "Boop!", 
                    "Play with me!",
                    "This is fun!",
                    "Chase the ball!"
                ])