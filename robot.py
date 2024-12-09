from player import Player
import random

class Robot(Player):
    def __init__(self, name="Bot"):
        super().__init__(name, "Purple")
        self.is_bot = True

    def evaluate_state(self, game):
        """Heuristic evaluation of the game state."""
        score = self.points * 10
        score += sum(self.hand.values())  # Additional resources add flexibility
        return score
    
    def take_action(self, game):
        """Use Alpha-Beta pruning to decide and take an action."""
        depth = 2  # Adjust search depth as needed
        _, best_action = self.alpha_beta_search(game, depth, float('-inf'), float('inf'), True)
        if best_action:
            if game.is_action_valid(self, best_action):  # Final check for validity
                self.apply_actions(game, best_action)
                print(f"{self.name} executed action: {best_action}")
            else:
                print(f"Invalid action attempted: {best_action}")

    def get_available_actions(self,game):
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

        return actions
    def apply_actions(self,game,action):
        """
        Apply the chosen action to the game.
        """
        action_type, details = self.get_available_actions()

        if action_type == 'settlement':
            game.buySettlement(self.name, details)
            print(f"{self.name} built a settlement at {details}.")
        
        elif action_type == 'road':
            game.buyRoad(self.name, details)
            print(f"{self.name} built a road at {details}.")
        
        elif action_type == 'city':
            game.buyCity(self.name, details)
            print(f"{self.name} upgraded a settlement to a city at {details}.")
        
        elif action_type == 'dev_card':
            game.buyDev()
            print(f"{self.name} purchased a development card.")

        else:
            print(f"Unknown action type: {action_type}")

    def alpha_beta_search(self, game, depth, alpha, beta, maximizing_player):
        """Perform Alpha-Beta pruning with action validation."""
        if depth == 0:
        #or game.is_game_over():
            return self.evaluate_state(game), None

        actions = self.get_available_actions(game)
        if not actions:
            return self.evaluate_state(game), None

        best_action = None
        if maximizing_player:
            max_eval = float('-inf')
            for action in actions:
                if not game.is_action_valid(self, action):
                    continue
                game_copy = game.clone()
                game_copy.apply_action(self, action)
                eval, _ = self.alpha_beta_search(game_copy, depth - 1, alpha, beta, False)
                if eval > max_eval:
                    max_eval = eval
                    best_action = action
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_action
        else:
            min_eval = float('inf')
            for action in actions:
                if not game.is_action_valid(self, action):
                    continue
                game_copy = game.clone()
                game_copy.apply_action(self, action)
                eval, _ = self.alpha_beta_search(game_copy, depth - 1, alpha, beta, True)
                if eval < min_eval:
                    min_eval = eval
                    best_action = action
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_action

    