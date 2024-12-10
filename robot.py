from player import Player
import random
import math

class Robot(Player):
    def __init__(self, name="Bot"):
        super().__init__(name, "Purple")
        self.is_bot = True  # Additional flag to identify a bot player

    def take_action(self, game):
        """
        Use Alpha-Beta Pruning to decide the best action during the bot's turn.
        """
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

        # If no actions are available
        if not actions:
            return ('no_action', None)

        # Perform Alpha-Beta Pruning to choose the best action
        best_action, _ = self.alpha_beta(game, depth=3, alpha=-math.inf, beta=math.inf, maximizing_player=True, valid_actions=actions)

        # Execute the chosen action
        if best_action[0] == 'settlement':
            print("The Bot Built a Settlement!")
        elif best_action[0] == 'road':
            print("The Bot Built a Road!")
        elif best_action[0] == 'city':
            print("The Bot Built a City!")
        elif best_action[0] == 'dev_card':
            game.buyDev()
            print("The Bot Built a Dev Card!")

        return best_action

    def alpha_beta(self, game, depth, alpha, beta, maximizing_player, valid_actions):
        """
        Alpha-Beta Pruning algorithm to evaluate the best action.
        """
        if depth == 0 or not valid_actions:
            return None, self.evaluate_game_state(game)

        best_action = None

        if maximizing_player:
            max_eval = -math.inf
            for action in valid_actions:
                # Simulate the action
                new_game = self.simulate_action(game, action)
                _, eval = self.alpha_beta(new_game, depth - 1, alpha, beta, False, self.get_valid_actions(new_game))

                # Update max evaluation and best action
                if eval > max_eval:
                    max_eval = eval
                    best_action = action

                # Update alpha
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cut-off

            return best_action, max_eval
        else:
            min_eval = math.inf
            for action in valid_actions:
                # Simulate the action
                new_game = self.simulate_action(game, action)
                _, eval = self.alpha_beta(new_game, depth - 1, alpha, beta, True, self.get_valid_actions(new_game))

                # Update min evaluation and best action
                if eval < min_eval:
                    min_eval = eval
                    best_action = action

                # Update beta
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha cut-off

            return best_action, min_eval

    def evaluate_game_state(self, game):
        """
        Evaluate the current game state and return a score.
        """
        # A simple heuristic based on points and resources
        return self.points + sum(self.hand.values()) * 0.1

    def simulate_action(self, game, action):
        """
        Simulate a game state resulting from the given action.
        """
        import copy
        new_game = copy.deepcopy(game)

        try:
            if action[0] == 'settlement':
                if action[1] in new_game.moves['settlements']:
                    new_game.buySettlement(self.name, action[1])
            elif action[0] == 'road':
                if action[1] in new_game.moves['roads']:
                    new_game.buyRoad(self.name, action[1])
            elif action[0] == 'city':
                if action[1] in new_game.moves['cities']:
                    new_game.buyCity(self.name, action[1])
            elif action[0] == 'dev_card' and new_game.moves.get('dev_card', False):
                new_game.buyDev()
        except KeyError as e:
            print(f"Simulation error: {e} - Action {action} might not be valid anymore.")
        except Exception as e:
            print(f"Unexpected error during simulation: {e}")
        return new_game

    def get_valid_actions(self, game):
        """
        Generate valid actions for the current game state.
        """
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
    # def first_Turn(self, game):
    #     """
    #     Perform the robot's first turn by placing a settlement and a road.
    #     """
    #     # Get valid settlement and road actions
    #     actions = self.get_valid_actions(game)
    #     settlement_actions = [action for action in actions if action[0] == 'settlement']
    #     road_actions = [action for action in actions if action[0] == 'road']

    #     # Place settlement
    #     if settlement_actions:
    #         settlement_action = settlement_actions[0]  # Choose the first valid settlement action
    #         game.buySettlement(self.name, settlement_action[1])
    #         print(f"{self.name} placed a settlement at {settlement_action[1]}.")

    #     # Place road
    #     if road_actions:
    #         road_action = road_actions[0]  # Choose the first valid road action
    #         game.buyRoad(self.name, road_action[1])
    #         print(f"{self.name} placed a road at {road_action[1]}.")
