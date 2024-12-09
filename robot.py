from player import Player
import random

class Robot(Player):
    def __init__(self, name="Bot"):
        super().__init__(name, "Purple")
        self.is_bot = True  # Additional flag to identify a bot player

    def take_action(self, game):
        """Perform a random valid action during the robot's turn and return it."""
        moves = game.moves
        actions = []

        if 'settlements' in moves:
            actions += [('settlement', (i, q)) for i, row in enumerate(moves['settlements']) for q, valid in enumerate(row) if valid]
        if 'roads' in moves:
            actions += [('road', road) for road in moves['roads']]
        if 'cities' in moves:
            actions += [('city', (i, q)) for i, row in enumerate(moves['cities']) for q, valid in enumerate(row) if valid]
        if moves.get('dev_card', False):
            actions.append(('dev_card', None))

        # Randomly choose an action
        if actions:
            action = random.choice(actions)
            if action[0] == 'settlement':
                print("The Bot Built a Settlement!")
            elif action[0] == 'road':
                print("The Bot Built a Road!")
            elif action[0] == 'city':
                print("The Bot Built a City!")
            elif action[0] == 'dev_card':
                print("The Bot Built a Dev Card!")
            return action

        # Return a "no-action" signal if no valid moves
        return ('no_action', None)
