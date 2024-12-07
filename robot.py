from player import Player
import random

class Robot(Player):
    def get_available_actions(self, game):
        actions = []
        if game.moves.get('settlements'):
            actions.append('build_settlement')
        if game.moves.get('cities'):
            actions.append('build_city')
        if game.moves.get('roads'):
            actions.append('build_road')
        if game.moves.get('dev_card'):
            actions.append('buy_dev_card')
        if game.moves.get('trade'):
            actions.append('trade')
        return actions

    def take_action(self, game, action):
        if action == 'build_settlement' and game.moves.get('settlements'):
            game.buySettlement(self.name, random.choice(game.moves['settlements']))
        elif action == 'build_city' and game.moves.get('cities'):
            game.buyCity(self.name, random.choice(game.moves['cities']))
        elif action == 'build_road' and game.moves.get('roads'):
            game.buyRoad(self.name, random.choice(game.moves['roads']))
        elif action == 'buy_dev_card' and game.moves.get('dev_card'):
            game.buyDev()
        elif action == 'trade' and game.moves.get('trade'):
            # Implement a simple trade logic here if needed
            pass

