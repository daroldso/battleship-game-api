"""utils.py - File for collecting general utility functions."""

import logging
from google.appengine.ext import ndb
import endpoints
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
     GameForms


class GameLogic():
    """Game Logic object"""

    ships = {
        'ac': {
            'name': 'aircraft_carrier',
            'size': 5
        },
        'bs': {
            'name': 'battleship',
            'size': 4
        },
        'sm': {
            'name': 'submarine',
            'size': 3
        },
        'dt': {
            'name': 'destroyer',
            'size': 3
        },
        'pb': {
            'name': 'patrol_boat',
            'size': 2
        }
    }

    @classmethod
    def create_default_grid(self):
        return [['~' for _ in range(10)] for _ in range(10)]

    @classmethod
    def place_ship_on_grid(self, request, player):
        grid = self.create_default_grid()

        for shipcode, ship in self.ships.iteritems():
            start_row = getattr(request, 'player%s_%s_start_row' % (player, ship['name']) )
            start_col = getattr(request, 'player%s_%s_start_col' % (player, ship['name']) ) - 1
            is_horizontal = getattr(request, 'player%s_%s_is_horizontal' % (player, ship['name']) )
            start_row_dict = start_row.to_dict()
            start_row = start_row_dict[str(start_row)]

            if start_col < 0 or start_col >= 10:
                raise endpoints.BadRequestException(
                    'Player %s %s start_col must be between 1 to 10' % (player, ship['name']) )

            if is_horizontal and start_col + ship['size'] > 10:
                raise endpoints.BadRequestException(
                    'The %s of player %s is too long' % (ship['name'], player))

            if is_horizontal == False and start_row + ship['size'] > 10:
                raise endpoints.BadRequestException(
                    'The %s of player %s is too tall' % (ship['name'], player))

            for i in range(ship['size']):
                col = start_col
                row = start_row
                if is_horizontal:
                    col = start_col + i
                else:
                    row = start_row + i
                if grid[row][col] != '~':
                    raise endpoints.BadRequestException(
                        'The %s of player %s is overlapping with another ship' % (ship['name'], player))

                grid[row][col] = str(shipcode)

        return grid

    @classmethod
    def make_move(self, request, game):
        move_row = getattr(request, 'move_row')
        move_col = getattr(request, 'move_col')
        is_player1_move = getattr(request, 'is_player1_move')

        player_move = str(move_row) + str(move_col)

        move_col = move_col - 1
        move_row_dict = move_row.to_dict()
        move_row = move_row_dict[str(move_row)]

        if move_col < 0 or move_col >= 10:
            raise endpoints.BadRequestException(
                'move_col must be between 1 to 10')

        if request.is_player1_move:
            player = '1'
            opponent = '2'
        else:
            player = '2'
            opponent = '1'

        is_ship_hit = False
        is_ship_destroyed = False
        ship_being_hit = ''
        target_grid = getattr(game, 'player%s_primary_grid' % opponent)
        tracking_grid = getattr(game, 'player%s_tracking_grid' % player)
        hit_target = target_grid[move_row][move_col]

        if hit_target == 'x':
            raise endpoints.BadRequestException(
                'You have hit this square already!')

        if hit_target != '~':
            is_ship_hit = True
            ship_being_hit = self.ships[hit_target]['name']
            tracking_grid[move_row][move_col] = hit_target
        else:
            tracking_grid[move_row][move_col] = 'x'
        
        target_grid[move_row][move_col] = 'x'

        if is_ship_hit == True:
            for shipcode, ship in self.ships.iteritems():
                if hit_target == shipcode:
                    hit_target_remaining = getattr(game,
                        'player%s_%s_remaining' % (opponent, ship['name']))
                    if hit_target_remaining == 1:
                        hit_target_remaining = 0
                        setattr(game,
                                'player%s_%s_remaining' % (opponent, ship['name']),
                                hit_target_remaining)
                        is_ship_destroyed = True
                    else:
                        hit_target_remaining -= 1
                        setattr(game,
                                'player%s_%s_remaining' % (opponent, ship['name']),
                                hit_target_remaining)

        return player_move, is_ship_hit, ship_being_hit, is_ship_destroyed


    @classmethod
    def is_correct_player(self, game, is_player1_move):
        if is_player1_move:
            return game.current_player == game.player1
        else:
            return game.current_player == game.player2

    @classmethod
    def set_new_ships_remaining(self,
                                 game,
                                 is_ship_destroyed,
                                 is_player1_move):
        if is_ship_destroyed:
            if is_player1_move:
                game.player2_ships_remaining -= 1
            else:
                game.player1_ships_remaining -= 1
