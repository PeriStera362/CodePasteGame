import random

class EventManager:
    def __init__(self):
        self.events = {
            'find_coin': {'chance': 0.05, 'message': 'Your pigeon found a shiny coin!'},
            'get_spooked': {'chance': 0.1, 'message': 'A loud noise spooked your pigeon!'},
            'make_friend': {'chance': 0.03, 'message': 'Your pigeon made a friend!'},
            'take_nap': {'chance': 0.08, 'message': 'Your pigeon took a quick nap!'}
        }
        
    def check_events(self, pigeon):
        triggered_events = []
        for event_name, event_data in self.events.items():
            if random.random() < event_data['chance']:
                self.handle_event(event_name, pigeon)
                triggered_events.append(event_data['message'])
        return triggered_events
    
    def handle_event(self, event_name, pigeon):
        if event_name == 'find_coin':
            pigeon.happiness = min(100, pigeon.happiness + 15)
        elif event_name == 'get_spooked':
            pigeon.happiness = max(0, pigeon.happiness - 10)
            pigeon.velocity[0] = random.randint(-5, 5)
            pigeon.velocity[1] = random.randint(-5, 5)
        elif event_name == 'make_friend':
            pigeon.happiness = min(100, pigeon.happiness + 20)
        elif event_name == 'take_nap':
            pigeon.energy = min(100, pigeon.energy + 30)
