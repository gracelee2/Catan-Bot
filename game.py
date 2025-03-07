from robot import Robot
from player import Player
from board import Board
from dev_cards import DevelopmentCards
import random


class Game:
    def __init__(self, player_names=['Adam', 'bot', 'Julia'],
                 colors=['Orange', 'Pink', 'Blue'], standard_setup=True):
        assert len(player_names) == len(colors)
        assert 2 < len(player_names) < 5

        # Identify bots and create appropriate player objects
        self.players = [
            Robot(name) if "bot" in name.lower() else Player(name, color)
            for name, color in zip(player_names, colors)
        ]

        self.player_dic = {player.name: player for player in self.players}
        self.board = Board()
        self.devcards = DevelopmentCards()

        self.order = player_names
        random.shuffle(self.order)

        self.turn = 0  # counts the turn number, does not reset between rounds
        self.round = 0  # counts revolutions around the board

        self.lastHouse = []  # used for setup phase
        self.moves = {}

        self.current_player = self.player_dic[self.order[self.turn]]
        self.availableMoves()

        self.dieRoll = ''
        self.rolled = False
        self.playedDev = False
        self.building_roads = 0
        self.longest_holder = ''
        self.largest_holder = ''

    def clone(self):
        """Create a deep copy of the game state."""
        import copy
        return copy.deepcopy(self)

    def is_action_valid(self, player, action):
        """Check if the action is valid in the current game state."""
        if action[0] == 'settlement':
            return self.is_settlement_valid(player, action[1])
        elif action[0] == 'road':
            return self.is_road_valid(player, action[1])
        elif action[0] == 'city':
            return self.is_city_valid(player, action[1])
        elif action[0] == 'dev_card':
            return self.is_dev_card_valid(player)
        return False

    def is_settlement_valid(self, player, coordinates):
        """Check if a settlement can be placed at the given coordinates."""
        # Example logic: Check resources and if the spot is available
        return (
            coordinates in self.board.availableVertices and
            player.hand['wheat'] > 0 and
            player.hand['sheep'] > 0 and
            player.hand['brick'] > 0 and
            player.hand['wood'] > 0
        )

    def is_road_valid(self, player, road):
        """Check if a road can be placed at the given coordinates."""
        return road in self.board.availableEdges and player.hand['wood'] > 0 and player.hand['brick'] > 0

    def is_city_valid(self, player, coordinates):
        """Check if a city can be upgraded at the given coordinates."""
        vertex = self.board.vertices[coordinates[0]][coordinates[1]]
        return vertex.owner == player and vertex.val == 1 and player.hand['wheat'] > 1 and player.hand['ore'] > 2

    def is_dev_card_valid(self, player):
        """Check if a development card can be bought."""
        return len(self.devcards.cards) > 0 and player.hand['wheat'] > 0 and player.hand['ore'] > 0 and player.hand['sheep'] > 0

    def apply_action(self, player, action):
        """Apply an action to the game state if valid."""
        if not self.is_action_valid(player, action):
            print(f"Invalid action attempted: {action}")
            return

        if action[0] == 'settlement':
            self.buySettlement(player.name, action[1])
        elif action[0] == 'road':
            self.buyRoad(player.name, action[1])
        elif action[0] == 'city':
            self.buyCity(player.name, action[1])
        elif action[0] == 'dev_card':
            self.buyDev()

    def playerUpdate(self):
        """Switch to the next player and handle their actions."""
        self.playedDev = False

        if self.round == 1:
            self.current_player = self.player_dic[self.order[::-1][self.turn % len(self.players)]]
        else:
            self.current_player = self.player_dic[self.order[self.turn % len(self.players)]]

        # Check if it's a bot's turn
        if isinstance(self.current_player, Robot):
            # Wait for the dice to be rolled before the bot takes actions
            self.rolled = False  # Reset roll state
        else:
            self.availableMoves()
            self.rolled = False

    def endTurn(self):
        """End the current player's turn."""
        self.turn += 1
        self.round = self.turn // len(self.players)
        self.playerUpdate()
        if self.round > 1:
            self.rollDice()


    def rollDice(self):
        """Roll dice and distribute resources."""
        if not self.rolled:  # Ensure dice can only be rolled once per turn
            d1 = random.randint(1, 6)
            d2 = random.randint(1, 6)
            self.dieRoll = d1 + d2
            self.rolled = True  # Mark dice as rolled

            # Distribute resources
            for spot in self.board.rollDic.keys():
                if self.board.rollDic[spot] == self.dieRoll and not self.board.spots[spot].blocked:
                    for vertex in self.board.spots[spot].vertices:
                        if self.board.vertices[vertex[0]][vertex[1]].owner:
                            owner = self.board.vertices[vertex[0]][vertex[1]].owner
                            owner.hand[self.board.spots[spot].resource.lower()] += self.board.vertices[vertex[0]][vertex[1]].val

          


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


