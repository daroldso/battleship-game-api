"""utils.py - File for collecting general utility functions."""

import logging
from google.appengine.ext import ndb
import endpoints
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
     GameForms


class GameLogic():
    """Game Logic object"""

    ships = [
        {
            'name': 'aircraft_carrier',
            'size': 5
        },
        {
            'name': 'battleship',
            'size': 4
        },
        {
            'name': 'submarine',
            'size': 3
        },
        {
            'name': 'destroyer',
            'size': 3
        },
        {
            'name': 'patrol_boat',
            'size': 2
        }
    ]

    @classmethod
    def create_default_grid(self):
        return [['~' for _ in range(10)] for _ in range(10)]

    @classmethod
    def place_ship_on_grid(self, request, player):
        grid = self.create_default_grid()

        for ship in self.ships:
            start_row = getattr(request, 'player%s_%s_start_row' % (player, ship['name']) )
            start_col = getattr(request, 'player%s_%s_start_col' % (player, ship['name']) ) - 1
            is_horizontal = getattr(request, 'player%s_%s_is_horizontal' % (player, ship['name']) )
            start_row_dict = start_row.to_dict()
            start_row = start_row_dict[str(start_row)]

            if start_col <= 0 or start_col >= 10:
                raise endpoints.BadRequestException(
                    'start_col must be between 1 to 10')

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

                grid[row][col] = str(ship['size'])

        return grid

    @classmethod
    def is_correct_player(self, game, is_player1_move):
        if is_player1_move:
            return game.current_player == game.player1
        else:
            return game.current_player == game.player2

    @classmethod
    def set_new_ships_locations(self, game, move, is_player1_move):
        if is_player1_move:
            new_location = [
                coord for coord in game.player2_ships_location if move != coord
            ]
            game.player2_ships_location = new_location
        else:
            new_location = [
                coord for coord in game.player1_ships_location if move != coord
            ]
            game.player1_ships_location = new_location

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
