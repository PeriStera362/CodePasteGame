import pygame
import sys
from pigeon import Pigeon
from events import EventManager
from utils import draw_stat_bars, display_messages

class Game:
    def __init__(self):
        pygame.init()
        self.WIDTH = 800
        self.HEIGHT = 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Pigeon Simulator")
        
        self.pigeon = Pigeon()
        self.event_manager = EventManager()
        self.clock = pygame.time.Clock()
        self.messages = []
        
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:  # Feed the pigeon
                    if self.pigeon.feed():
                        self.messages.append("You fed your pigeon!")
                elif event.key == pygame.K_c:  # Clean the pigeon
                    self.pigeon.clean()
                    self.messages.append("You cleaned your pigeon!")
                elif event.key == pygame.K_p:  # Pet the pigeon
                    self.pigeon.pet()
                    self.messages.append("You pet your pigeon!")
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Move pigeon toward click location
                mouse_x, mouse_y = pygame.mouse.get_pos()
                dx = (mouse_x - self.pigeon.position[0]) * 0.1
                dy = (mouse_y - self.pigeon.position[1]) * 0.1
                self.pigeon.velocity = [dx, dy]
        
        return True
    
    def update(self):
        self.pigeon.update()
        
        # Check for random events
        new_events = self.event_manager.check_events(self.pigeon)
        self.messages.extend(new_events)
        
        # Keep only the last 5 messages
        self.messages = self.messages[-5:]
    
    def draw(self):
        self.screen.fill((50, 50, 50))  # Dark gray background
        
        # Draw the pigeon (simple circle for now)
        pygame.draw.circle(self.screen, (200, 200, 200), 
                         [int(self.pigeon.position[0]), int(self.pigeon.position[1])], 20)
        
        # Draw stats and messages
        draw_stat_bars(self.screen, self.pigeon)
        display_messages(self.screen, self.messages)
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()
