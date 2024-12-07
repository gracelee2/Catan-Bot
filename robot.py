from player import Player
import random

class Robot(Player):
    def __init__(self, name, color):
        super().__init__(name, color)

    def make_decision(self, game):
        """
        Executes all available actions in random order before ending the turn.
        """
        # Retrieve all available actions
        available_actions = self.get_available_actions(game)

        # Shuffle the actions for random execution order
        random.shuffle(available_actions)

        # Execute each action in the shuffled list
        for action in available_actions:
            self.execute_action(game, action)

        #game.end_turn()
        # End the turn after completing all actions

    def get_available_actions(self, game):
        """
        Checks all available actions for the robot.
        """
        available_actions = []

            # Check settlements
        for i, row in enumerate(game.moves['settlements']):
            for j, can_build in enumerate(row):
                if can_build:
                    available_actions.append(('build_settlement', i, j))

        # Check cities
        # for i, row in enumerate(game.moves['cities']):
        #    for j, can_build in enumerate(row):
        #        if can_build:
        #            available_actions.append(('build_city', i, j))

        # Check for road purchase
        for road in game.moves['roads']:
            available_actions.append(('buy_road', road))

        # Check for development card purchase
        if game.moves['dev_card']:
            available_actions.append(('buy_dev_card', None))

        # Check for knight, monopoly, road builder, and year of plenty
        if game.moves.get('kinght', 0) > 0:
            available_actions.append(('play_knight', None))
        if game.moves.get('monopoly', 0) > 0:
            available_actions.append(('play_monopoly', None))
        if game.moves.get('road_builder', 0) > 0:
            available_actions.append(('play_road_builder', None))
        if game.moves.get('year_of_plenty', 0) > 0:
            available_actions.append(('play_year_of_plenty', None))

        return available_actions

    def execute_action(self, game, action):
        """
        Executes the chosen action.
        """
        action_type, params = action
        if action_type == 'buy_settlement':
            game.buySettlement(self.name, params)
        elif action_type == 'buy_city':
            game.buyCity(self.name, params)
        elif action_type == 'buy_road':
            game.buyRoad(self.name, params)
        elif action_type == 'buy_dev_card':
            game.buyDev()
        elif action_type == 'play_knight':
            game.playedKnight()
        elif action_type == 'play_monopoly':
            # Implement monopoly logic if applicable
            pass
        elif action_type == 'play_road_builder':
            # Implement road builder logic if applicable
            pass
        elif action_type == 'play_year_of_plenty':
            # Implement year of plenty logic if applicable
            pass

        if hasattr(game, 'visualize'):
            game.visualize.update_gui_after_robot_move()
