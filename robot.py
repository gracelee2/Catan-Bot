from player import Player
import math
import random


class Robot(Player):
    def __init__(self, name="Bot"):
        # Determine the bot's color based on its name
        colors = {
            "1": "Purple",
            "2": "Green",
            "3": "Blue",
            "4": "Red"
        }
        assigned_color = "Gray"  # Default color if no match found
        for key, color in colors.items():
            if key in name:
                assigned_color = color
                break
        
        super().__init__(name, assigned_color)
        self.is_bot = True

    def take_action(self, game):
        """
        Decide the best action during the bot's turn using Alpha-Beta Pruning.
        Prefer building roads in segments of 2 extending from settlements.
        """
        actions = self.get_valid_actions(game)

        # If no actions are available
        if not actions:
            return ('no_action', None)
        

        if game.round < 2:  # Assuming round < 1 indicates the setup phase
            # Filter out edge settlement locations
            filtered_actions = [
                action for action in actions
                if action[0] != 'settlement' or not self.is_edge_settlement(action[1], game)
            ]

            # If no non-edge settlement actions are available, fall back to all actions
            if filtered_actions:
                actions = filtered_actions

            # Choose a random action from the filtered list
            chosen_action = random.choice(actions)
            print(f"{self.name} chose random action during setup: {chosen_action}")
            return chosen_action
        
        # Perform Alpha-Beta Pruning to choose the best action
        best_action, _ = self.alpha_beta(
            game, depth=3, alpha=-math.inf, beta=math.inf, maximizing_player=True, valid_actions=actions
        )

        # Log and return the chosen action
        if best_action[0] == 'road':
            print(f"The Bot chose to build a road at: {best_action[1]}")
        elif best_action[0] == 'settlement':
            print(f"The Bot chose to build a settlement at: {best_action[1]}")
        elif best_action[0] == 'city':
            print(f"The Bot chose to build a city at: {best_action[1]}")
        elif best_action[0] == 'dev_card':
            game.buyDev()
            print("The Bot chose to buy a development card.")
        elif best_action[0] == 'use_dev_card':
            print(f"The Bot chose to use a development card: {best_action[1]}")
        elif best_action[0] == 'trade_in':
            print(f"The Bot chose to trade in: {best_action[1]}")
        else:
            print(f"The Bot chose action: {best_action}")

        return best_action

    def alpha_beta(self, game, depth, alpha, beta, maximizing_player, valid_actions):
        """
        Alpha-Beta Pruning to evaluate the best action.
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
        return self.points + sum(self.hand.values()) * 0.1 + len(self.roads) * 0.5

    def simulate_action(self, game, action):
        """
        Simulate a game state resulting from the given action.
        """
        import copy
        new_game = copy.deepcopy(game)

        try:
            if action[0] == 'settlement':
                new_game.buySettlement(self.name, action[1])
            elif action[0] == 'road':
                new_game.buyRoad(self.name, action[1])
            elif action[0] == 'city':
                new_game.buyCity(self.name, action[1])
            elif action[0] == 'dev_card':
                new_game.buyDev()
        except Exception as e:
            print(f"Checking Roads: {e}")
        return new_game

    def get_valid_actions(self, game):
        """
        Generate valid actions for the current game state.
        """
        actions = []

        # Add settlement actions
        if 'settlements' in game.moves:
            actions += [('settlement', (i, q)) for i, row in enumerate(game.moves['settlements']) for q, valid in enumerate(row) if valid]

        # Add road actions with prioritization
        if 'roads' in game.moves:
            actions += [('road', road) for road in self.prioritize_roads(game)]

        # Add city actions
        if 'cities' in game.moves:
            actions += [('city', (i, q)) for i, row in enumerate(game.moves['cities']) for q, valid in enumerate(row) if valid]

        # Add dev card purchase
        if game.moves.get('dev_card', False):
            actions.append(('dev_card', None))

        if self.can_trade_in():
            actions.append(('trade_in', None))

        # Add dev card usage
        actions += self.get_dev_card_usage_actions(game)

        return actions

    def prioritize_roads(self, game):
        """
        Prioritize roads to extend from settlements and form segments of 2.
        """
        prioritized_roads = []

        for road in game.moves.get('roads', []):
            # Check if the road connects to a settlement or extends an existing road segment
            for vertex in road:
                if any(vertex == settlement for settlement in self.settlements) or \
                        any(vertex in edge for edge in self.roads):
                    prioritized_roads.append(road)

        return prioritized_roads
    
    def can_trade_in(self):
        """
        Check if the bot has 4 or more of any resource type to enable a trade-in action.
        """
        return any(count >= 4 for count in self.hand.values())


    def get_dev_card_usage_actions(self, game):
        """
        Generate a list of actions for using dev cards.
        """
        dev_card_actions = []
        if self.knight > 0 and not game.playedDev:
            dev_card_actions.append(('use_dev_card', 'knight'))
        if self.monopoly > 0 and not game.playedDev:
            dev_card_actions.append(('use_dev_card', 'monopoly'))
        if self.road_builder > 0 and not game.playedDev:
            dev_card_actions.append(('use_dev_card', 'road_builder'))
        if self.year_of_plenty > 0 and not game.playedDev:
            dev_card_actions.append(('use_dev_card', 'year_of_plenty'))
        return dev_card_actions
    
    def is_edge_settlement(self, settlement, game):
        """
        Check if a settlement location is on the edge of the board.
        """
        i, j = settlement
        # Check if the settlement is on the edge (top/bottom row or left/right column)
        max_rows = len(game.board.vertices)
        max_cols = len(game.board.vertices[0])

        return i == 0 or i == max_rows - 1 or j == 0 or j == max_cols - 1

