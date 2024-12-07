from player import Player
from board import Board
from dev_cards import DevelopmentCards
import random
#from handler import getState

from handler import processActions, getState, selectAction, dropCards

class Robot:
    count = 0

    def __init__(self):
        self.name = f"Bot_{Robot.count}"
        Robot.count += 1

    # Evaluate the game state for the AI.
    def evaluate_state(self, game, depth):
        player_score = game.current_player.points
        opponent_scores = [p.points for p in game.players if p != game.current_player]
        resource_count = sum(game.current_player.hand.values())
        return player_score - max(opponent_scores) + resource_count * 0.1

    # Perform Alpha-Beta Pruning to find the best move.
    def alpha_beta_move(self, game, depth, alpha, beta, maximizing_player):
        if depth == 0 or game.current_player.points >= 10:
            return self.evaluate_state(game, depth), None

        new_states, actions = processActions(game, getState(game))

        if maximizing_player:
            max_eval = float('-inf')
            best_action = None
            for state, action in zip(new_states, actions):
                game_copy = Game()  # Simulate game
                selectAction(game_copy, [state], [action])
                eval, _ = self.alpha_beta_move(game_copy, depth - 1, alpha, beta, False)
                if eval > max_eval:
                    max_eval = eval
                    best_action = action
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_action
        else:
            min_eval = float('inf')
            best_action = None
            for state, action in zip(new_states, actions):
                game_copy = Game()  # Simulate game
                selectAction(game_copy, [state], [action])
                eval, _ = self.alpha_beta_move(game_copy, depth - 1, alpha, beta, True)
                if eval < min_eval:
                    min_eval = eval
                    best_action = action
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_action

    # Decide and execute the best move.
    def move(self, game):
        depth = 3
        _, best_action = self.alpha_beta_move(game, depth, float('-inf'), float('inf'), True)
        if best_action:
            selectAction(game, [None], [best_action])

class Game:

    def __init__(self, player_names = ['Adam','Rachel'], bot_names =['bot1'],
                 colors = ['Orange','Pink','Blue'], standard_setup=True):

        all_names = player_names + bot_names
        all_colors = colors[:len(all_names)]

        if len(all_names) != len(all_colors):
            raise ValueError("The number of players and bots must match the number of colors.")
        if not (3 <= len(all_names) <= 4):
            raise ValueError("The total number of players (humans + bots) must be between 3 and 4.")

        self.players = []
        for name, color in zip(player_names, colors[:len(player_names)]):
            self.players.append(Player(name, color))  # Add human players
        for bot_name, color in zip(bot_names, colors[len(player_names):]):
            bot = Robot()
            bot.name = bot_name  # Set bot's name
            self.players.append(bot)  # Add bots
        
        # Create player dictionary for quick lookup
        self.player_dic = {player.name: player for player in self.players}
        
        self.board = Board()
        self.devcards = DevelopmentCards()

        self.order = player_names
        random.shuffle(self.order)

        self.turn = 0 #counts the turn number, does not reset between rounds
        self.round = 0 #counts revolutions around the board

        self.lastHouse = [] #used for set up phase
        self.moves = {}

        self.current_player = self.player_dic[self.order[self.turn]]
        self.availableMoves()

        self.dieRoll = ''
        self.playedDev = False
        self.building_roads = 0
        self.longest_holder = ''
        self.largest_holder = ''


    def rollDice(self):

        d1 = random.randint(1,6)
        d2 = random.randint(1,6)

        self.dieRoll = d1 + d2

        if self.round == 2:

            while self.dieRoll == 7:
                self.dieRoll = random.randint(1,6) + random.randint(1,6)

        for spot in self.board.rollDic.keys():

            if self.board.rollDic[spot] == self.dieRoll and \
                    not self.board.spots[spot].blocked:
                for vertex in self.board.spots[spot].vertices:
                    if self.board.vertices[vertex[0]][vertex[1]].owner:
                        self.board.vertices[vertex[0]][vertex[1]]\
                            .owner.hand[self.board.spots[spot]\
                                        .resource.lower()] +=\
                        self.board.vertices[vertex[0]][vertex[1]].val



    def playerUpdate(self):
        self.playedDev = False
        if self.round == 1:
                self.current_player =\
                    self.player_dic[self.order[::-1]\
                                [self.turn % len(self.players)]]

        else:
                self.current_player =\
                    self.player_dic[self.order[self.turn % len(self.players)]]
                self.availableMoves()

    def availableMoves(self):
        settlements = [[]]
        cities = []
        roads = []

        #set up rounds
        if self.round < 2:

            if len(self.current_player.settlements) ==\
                    len(self.current_player.roads)\
                    and len(self.current_player.settlements) <= self.round:
                #then we buy a house
                settlements = self.board.availableVertices

            elif len(self.current_player.roads) <= self.round:
                #then we buy a road
                for road in self.board.availableEdges:
                    if tuple(self.lastHouse) in road:
                        roads.append(road)

                settlements = [[None]*11 for i in range(6)]


            self.moves = {'roads':roads,
                    'settlements':settlements}


        else:

            self.moves ={'settlements':self.buyableHomes(),
                         'roads':self.buyableRoads(),
                         'cities':self.buyableCities(),
                         'kinght':self.current_player.knight,
                         'year_of_plenty':self.current_player.year_of_plenty,
                         'monopoly':self.current_player.monopoly,
                         'road_builder':self.current_player.road_builder,
                         'dev_card':self.buyableDevCard()}



        self.current_player.updateScore()

    def buyableCities(self):

        cities = []
        for i in range(6):
            row = []
            for q in range(11):
                row.append(self.board.vertices[i][q]!=None\
                    and self.board.vertices[i][q].owner == self.current_player\
                           and self.board.vertices[i][q].val == 1\
                           and self.current_player.hand['wheat'] > 1\
                           and self.current_player.hand['ore']>2) \
                           and len(self.current_player.cities) < 4

            cities.append(row)


        return cities




    def buyableHomes(self):

        homes = []
        for i in range(6):
            row = []
            for q in range(11):
                row.append(False)

            homes.append(row)

        if self.current_player.hand['wheat'] > 0 and\
           self.current_player.hand['sheep'] > 0 and\
           self.current_player.hand['brick'] > 0 and\
           self.current_player.hand['wood'] > 0 and\
           len(self.current_player.settlements) < 5:

            for road in self.current_player.roads:

                spot1, spot2 = road

                if self.board.availableVertices[spot1[0]][spot1[1]]:
                    homes[spot1[0]][spot1[1]] = True

                if self.board.availableVertices[spot2[0]][spot2[1]]:
                    homes[spot2[0]][spot2[1]] = True

        return homes

    def buyableRoads(self):

        roads = []

        if ((self.current_player.hand['wood'] > 0 and\
           self.current_player.hand['brick'] > 0) or self.building_roads!=0) and\
           len(self.current_player.roads) < 15:

            for road in self.current_player.roads:


                for edge in self.board.availableEdges:

                    intersect = set(road).intersection(set(edge))
                    if len(intersect) > 0:

                        intersect = list(intersect)[0]

                        verts = self.board.vertices

                        if verts[intersect[0]][intersect[1]].owner == None or \
                           verts[intersect[0]][intersect[1]].owner == \
                           self.current_player:
                            roads.append(edge)


        return roads

    def buyableDevCard(self):
        if len(self.devcards.cards) > 0 and \
           self.current_player.hand['wheat'] > 0 and \
           self.current_player.hand['ore'] > 0 and \
           self.current_player.hand['sheep'] > 0:

            return True

        else:
            return False


    def buySettlement(self, player, coordinates):
        self.player_dic[player].settlements.append(coordinates)
        self.board.availableVertices[coordinates[0]][coordinates[1]] = False
        self.board.propogateVertexPurchase(tuple(coordinates))
        self.lastHouse = coordinates
        self.board.vertices[coordinates[0]][coordinates[1]].owner = \
            self.current_player
        self.board.vertices[coordinates[0]][coordinates[1]].val = 1

        port = self.board.vertices[coordinates[0]][coordinates[1]].port

        if port:
            self.current_player.ports[port] = True

        if self.round > 1:
            self.current_player.hand['wheat'] -= 1
            self.current_player.hand['sheep'] -= 1
            self.current_player.hand['brick'] -= 1
            self.current_player.hand['wood'] -= 1

        if self.round == 1:
            for tile in self.board.spots.values():
                if list(coordinates) in tile.vertices and tile.resource !=\
                        'Desert':
                    self.current_player.hand[tile.resource.lower()] += 1

        self.checkLongest()

    def buyCity(self, player, coordinates):
        self.board.vertices[coordinates[0]][coordinates[1]].city = True
        self.current_player.hand['wheat'] -= 2
        self.current_player.hand['ore'] -= 3
        self.board.vertices[coordinates[0]][coordinates[1]].val = 2
        self.current_player.cities.append(coordinates)


    def buyRoad(self, player, road):
        self.player_dic[player].roads.append(road)
        self.board.availableEdges.remove(road)
        self.board.edges[road].owner = self.current_player
        if self.round > 1 and self.building_roads == 0:
            self.current_player.hand['wood'] -= 1
            self.current_player.hand['brick'] -= 1

        elif self.building_roads > 0:
            self.building_roads -= 1

        self.checkLongest()

    def buyDev(self):
        card = self.devcards.cards.pop()

        if card == 'Knight':
            self.current_player.knight += 1

        elif card == 'Year of Plenty':
            self.current_player.year_of_plenty += 1

        elif card == 'Monoploy':
            self.current_player.monopoly += 1

        elif card == 'Road Builder':
            self.current_player.road_builder += 1

        else:
            self.current_player.point_cards += 1

        self.current_player.hand['ore'] -= 1
        self.current_player.hand['sheep'] -= 1
        self.current_player.hand['wheat'] -= 1


    def checkLongest(self):
        mx = 0
        p = []
        for player in self.players:
            length = self.calcLongest(player)
            if length > mx:
                mx = length
                p = [player]

            elif length == mx:
                p.append(player)

        if len(p)>1:
            p = self.longest_holder

        else:
            p = p[0]


        if mx > 4:
            for player in self.players:
                if player == p:
                    player.longest_road = True
                else:
                    player.longest_road = False

            self.longest_holder = p

    def calcLongest(self, player):

        roads = player.roads
        seen = set()

        def recurse(last_vertex):

            nonlocal roads

            if self.board.vertices[last_vertex[0]][last_vertex[1]].owner and \
               self.board.vertices[last_vertex[0]][last_vertex[1]].owner != player:
                return 0

            ans = [0]
            for road in roads:
                if last_vertex in road and road not in seen:
                    seen.add(road)
                    l_v = set(road) - set([last_vertex])
                    ans.append(1 + recurse(list(l_v)[0]))


            return max(ans)

        lengths = [1]

        for road in roads:

            if road not in seen:
                seen.add(road)
                lengths.append(1 + recurse(road[0]) + recurse(road[1]))

        return max(lengths)

    def playedKnight(self):

        self.current_player.played_knights += 1
        mx = 0
        p = []
        for player in self.players:
            size = player.played_knights
            if size > mx:
                mx = size
                p = [player]

            elif size == mx:
                p.append(player)

        if len(p)>1:
            p = self.largest_holder

        else:
            p = p[0]


        if mx > 2:
            for player in self.players:
                if player == p:
                    player.largest_army = True
                else:
                    player.largest_army = False

            self.largest_holder = p

