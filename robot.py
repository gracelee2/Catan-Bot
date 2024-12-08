from player import Player
import random


class Robot(Player):

    def evaluate_settlement(self, game):
        best_score = -1
        best_location = None
        for i, row in enumerate(game.moves['settlements']):
            for j, available in enumerate(row):
                if available:
                    score = self.evaluate_vertex(game, (i, j))
                    if score > best_score:
                        best_score = score
                        best_location = (i, j)
        return best_location

    def evaluate_vertex(self, game, coordinates):
        score = 0
        x, y = coordinates
        vertex = game.board.vertices[x][y]

        if vertex.port:
            score += 3
        for tile in game.board.spots.values():
            if (x, y) in tile.vertices and tile.resource != "Desert":
                score += 2

        return score

    def get_available_actions(self, game):
        actions = []
        if game.moves.get('settlements') and any(any(row) for row in game.moves['settlements']):
            actions.append('build_settlement')
        if game.moves.get('cities') and any(any(row) for row in game.moves['cities']):
            actions.append('build_city')
        if game.moves.get('roads'):
            actions.append('build_road')
        if game.moves.get('dev_card'):
            actions.append('buy_dev_card')
        return actions

    def take_action(self, game, action):
        if action == "build_settlement":
            location = self.evaluate_settlement(game)
            if location:
                game.buySettlement(self.name, location)
        elif action == "build_city":
            location = random.choice(game.moves["cities"])
            game.buyCity(self.name, location)
        elif action == "build_road":
            road = random.choice(game.moves["roads"])
            game.buyRoad(self.name, road)
        elif action == "buy_dev_card":
            game.buyDev()
