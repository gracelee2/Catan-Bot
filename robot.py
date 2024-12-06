from handler import processActions, getState, selectAction, dropCards
from game import Game


class Robot:
    count = 0

    def __init__(self):
        self.name = f"Bot_{Robot.count}"
        Robot.count += 1

    #Evaluate the game state for the AI.
    def evaluate_state(self, game, depth):
        player_score = game.current_player.points
        opponent_scores = [p.points for p in game.players if p != game.current_player]
        resource_count = sum(game.current_player.hand.values())
        return player_score - max(opponent_scores) + resource_count * 0.1

    #Perform Alpha-Beta Pruning to find the best move.
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

    #Decide and execute the best move.
    def move(self, game):
        depth = 3
        _, best_action = self.alpha_beta_move(game, depth, float('-inf'), float('inf'), True)
        if best_action:
            selectAction(game, [None], [best_action])

#Bot game
def threeBot():
    bots = [Robot() for _ in range(3)]
    game = Game(player_names=[bot.name for bot in bots])

    print("Starting a game with three AI players...")
    print(f"Players: {[bot.name for bot in bots]}")

    for i in range(500):
        if game.dieRoll == 7:
            dropCards(game)

        state = getState(game)
        new_states, actions = processActions(game, state)
        if selectAction(game, new_states, actions):
            print(f"Game ended after {i + 1} turns.")
            print(f"Winner: {game.current_player.name} with {game.current_player.points} points!")
            break

        # Print progress every 10 turns
        if i % 10 == 0:
            print(f"Turn {i + 1}: Current player is {game.current_player.name}.")

    print("Game finished.")
