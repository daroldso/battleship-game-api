"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages, message_types
from google.appengine.ext import ndb

DEFAULT_SHIPS = 5


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()


class Game(ndb.Model):
    """Game object"""
    player1 = ndb.KeyProperty(required=True, kind='User')
    player2 = ndb.KeyProperty(kind='User')
    player1_ships_remaining = ndb.IntegerProperty(required=True,
                                                  default=DEFAULT_SHIPS)
    player2_ships_remaining = ndb.IntegerProperty(required=True,
                                                  default=DEFAULT_SHIPS)
    player1_primary_grid = ndb.PickleProperty(repeated=True)
    player2_primary_grid = ndb.PickleProperty(repeated=True)
    player1_tracking_grid = ndb.PickleProperty(repeated=True)
    player2_tracking_grid = ndb.PickleProperty(repeated=True)
    player1_aircraft_carrier_remaining = ndb.IntegerProperty(required=True, default=5)
    player1_battleship_remaining = ndb.IntegerProperty(required=True, default=4)
    player1_submarine_remaining = ndb.IntegerProperty(required=True, default=3)
    player1_destroyer_remaining = ndb.IntegerProperty(required=True, default=3)
    player1_patrol_boat_remaining = ndb.IntegerProperty(required=True, default=2)
    player2_aircraft_carrier_remaining = ndb.IntegerProperty(required=True, default=5)
    player2_battleship_remaining = ndb.IntegerProperty(required=True, default=4)
    player2_submarine_remaining = ndb.IntegerProperty(required=True, default=3)
    player2_destroyer_remaining = ndb.IntegerProperty(required=True, default=3)
    player2_patrol_boat_remaining = ndb.IntegerProperty(required=True, default=2)
    current_player = ndb.KeyProperty(kind='User')
    game_over = ndb.BooleanProperty(required=True, default=False)
    cancelled = ndb.BooleanProperty(required=True, default=False)
    history = ndb.PickleProperty(repeated=True)
    last_move = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def new_game(cls, user1, user2,
                 player1_primary_grid, player2_primary_grid,
                 player1_tracking_grid, player2_tracking_grid):
        """Creates and returns a new game"""
        # Ship location is entered arbitrarily in API interface.
        # This API expect the validation of ship location in frontend.
        # So that ships are not overlapped.
        game = Game(player1=user1,
                    player2=user2,
                    player1_ships_remaining=DEFAULT_SHIPS,
                    player2_ships_remaining=DEFAULT_SHIPS,
                    player1_primary_grid=player1_primary_grid,
                    player2_primary_grid=player2_primary_grid,
                    player1_tracking_grid=player1_tracking_grid,
                    player2_tracking_grid=player2_tracking_grid,
                    current_player=user1,
                    game_over=False,
                    cancelled=False,
                    history=[])
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.player1_name = self.player1.get().name
        if(self.player2):
            form.player2_name = self.player2.get().name
        else:
            form.player2_name = 'Computer'

        if(self.current_player):
            form.current_player = self.current_player.get().name
        else:
            form.current_player = 'Computer'

        form.player1_primary_grid = self.to_grid_form(self.player1_primary_grid)
        form.player2_primary_grid = self.to_grid_form(self.player2_primary_grid)
        form.player1_tracking_grid = self.to_grid_form(self.player1_tracking_grid)
        form.player2_tracking_grid = self.to_grid_form(self.player2_tracking_grid)
        
        form.player1_aircraft_carrier_remaining = self.player1_aircraft_carrier_remaining
        form.player1_battleship_remaining = self.player1_battleship_remaining
        form.player1_submarine_remaining = self.player1_submarine_remaining
        form.player1_destroyer_remaining = self.player1_destroyer_remaining
        form.player1_patrol_boat_remaining = self.player1_patrol_boat_remaining
        form.player2_aircraft_carrier_remaining = self.player2_aircraft_carrier_remaining
        form.player2_battleship_remaining = self.player2_battleship_remaining
        form.player2_submarine_remaining = self.player2_submarine_remaining
        form.player2_destroyer_remaining = self.player2_destroyer_remaining
        form.player2_patrol_boat_remaining = self.player2_patrol_boat_remaining
        form.player1_ships_remaining = self.player1_ships_remaining
        form.player2_ships_remaining = self.player2_ships_remaining
        form.game_over = self.game_over
        form.cancelled = self.cancelled
        form.last_move = self.last_move
        form.message = message
        return form

    def to_grid_form(self, grids):
        return GridForm(
                    A=grids[0],
                    B=grids[1],
                    C=grids[2],
                    D=grids[3],
                    E=grids[4],
                    F=grids[5],
                    G=grids[6],
                    H=grids[7],
                    I=grids[8],
                    J=grids[9]
               )

    def end_game(self, winner=False):
        """Ends the game - winner will be either player 1 or 2,
        # or will be False if AI wins"""
        self.game_over = True
        self.put()
        # Add the game to the score 'board' if a player wins
        if(winner):
            if(winner == self.player1):
                ships_remaining = self.player1_ships_remaining
            else:
                ships_remaining = self.player2_ships_remaining
            score = Score(winner=winner,
                          date=date.today(),
                          ships_remaining=ships_remaining)
            score.put()


class Score(ndb.Model):
    """Score object. For Single player game,
    only those who beat AI player will be stored"""
    winner = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    ships_remaining = ndb.IntegerProperty(required=True)

    def to_form(self):
        return ScoreForm(winner=self.winner.get().name,
                         date=str(self.date),
                         ships_remaining=self.ships_remaining)


class GameStepForm(messages.Message):
    """GameStepForm for outbound game history"""
    player = messages.StringField(1, required=True)
    move = messages.StringField(2, required=True)
    is_ship_destroyed = messages.BooleanField(3, required=True)


class GameStepForms(messages.Message):
    """Return multiple GameStepForms"""
    items = messages.MessageField(GameStepForm, 1, repeated=True)


class GridForm(messages.Message):
    """GameStepForm for outbound game history"""
    A = messages.StringField(1, repeated=True)
    B = messages.StringField(2, repeated=True)
    C = messages.StringField(3, repeated=True)
    D = messages.StringField(4, repeated=True)
    E = messages.StringField(5, repeated=True)
    F = messages.StringField(6, repeated=True)
    G = messages.StringField(7, repeated=True)
    H = messages.StringField(8, repeated=True)
    I = messages.StringField(9, repeated=True)
    J = messages.StringField(10, repeated=True)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    player1_ships_remaining = messages.IntegerField(2, required=True)
    player2_ships_remaining = messages.IntegerField(3)
    player1_primary_grid = messages.MessageField(GridForm, 4)
    player2_primary_grid = messages.MessageField(GridForm, 5)
    player1_tracking_grid = messages.MessageField(GridForm, 6)
    player2_tracking_grid = messages.MessageField(GridForm, 7)
    player1_name = messages.StringField(8, required=True)
    player2_name = messages.StringField(9)
    current_player = messages.StringField(10)
    cancelled = messages.BooleanField(11)
    history = messages.MessageField(GameStepForm, 12, repeated=True)
    last_move = message_types.DateTimeField(13)
    game_over = messages.BooleanField(14, required=True)
    message = messages.StringField(15, required=True)

    player1_aircraft_carrier_remaining = messages.IntegerField(16, required=True)
    player1_battleship_remaining = messages.IntegerField(17, required=True)
    player1_submarine_remaining = messages.IntegerField(18, required=True)
    player1_destroyer_remaining = messages.IntegerField(19, required=True)
    player1_patrol_boat_remaining = messages.IntegerField(20, required=True)
    player2_aircraft_carrier_remaining = messages.IntegerField(21, required=True)
    player2_battleship_remaining = messages.IntegerField(22, required=True)
    player2_submarine_remaining = messages.IntegerField(23, required=True)
    player2_destroyer_remaining = messages.IntegerField(24, required=True)
    player2_patrol_boat_remaining = messages.IntegerField(25, required=True)
    player1_ships_remaining = messages.IntegerField(26, required=True)
    player2_ships_remaining = messages.IntegerField(27, required=True)


class GameForms(messages.Message):
    """Return multiple GameForms"""
    items = messages.MessageField(GameForm, 1, repeated=True)


class GridRowNum(messages.Enum):
    """GridRowNum -- The row number of the grid"""
    A = 0
    B = 1
    C = 2
    D = 3
    E = 4
    F = 5
    G = 6
    H = 7
    I = 8
    J = 9


class NewGameForm(messages.Message):
    """Used to create a new game"""
    player1_name = messages.StringField(1, required=True)
    player2_name = messages.StringField(2)

    player1_aircraft_carrier_is_horizontal = \
        messages.BooleanField(3, required=True)
    player1_aircraft_carrier_start_row = messages.EnumField('GridRowNum', 4, required=True)
    player1_aircraft_carrier_start_col = messages.IntegerField(5, required=True)
    player1_battleship_is_horizontal = messages.BooleanField(6, required=True)
    player1_battleship_start_row = messages.EnumField('GridRowNum', 7, required=True)
    player1_battleship_start_col = messages.IntegerField(8, required=True)
    player1_submarine_is_horizontal = messages.BooleanField(9, required=True)
    player1_submarine_start_row = messages.EnumField('GridRowNum', 10, required=True)
    player1_submarine_start_col = messages.IntegerField(11, required=True)
    player1_destroyer_is_horizontal = messages.BooleanField(12, required=True)
    player1_destroyer_start_row = messages.EnumField('GridRowNum', 13, required=True)
    player1_destroyer_start_col = messages.IntegerField(14, required=True)
    player1_patrol_boat_is_horizontal = messages.BooleanField(15, required=True)
    player1_patrol_boat_start_row = messages.EnumField('GridRowNum', 16, required=True)
    player1_patrol_boat_start_col = messages.IntegerField(17, required=True)

    player2_aircraft_carrier_is_horizontal = \
        messages.BooleanField(18, required=True)
    player2_aircraft_carrier_start_row = messages.EnumField('GridRowNum', 19, required=True)
    player2_aircraft_carrier_start_col = messages.IntegerField(20, required=True)
    player2_battleship_is_horizontal = messages.BooleanField(21, required=True)
    player2_battleship_start_row = messages.EnumField('GridRowNum', 22, required=True)
    player2_battleship_start_col = messages.IntegerField(23, required=True)
    player2_submarine_is_horizontal = messages.BooleanField(24, required=True)
    player2_submarine_start_row = messages.EnumField('GridRowNum', 25, required=True)
    player2_submarine_start_col = messages.IntegerField(26, required=True)
    player2_destroyer_is_horizontal = messages.BooleanField(27, required=True)
    player2_destroyer_start_row = messages.EnumField('GridRowNum', 28, required=True)
    player2_destroyer_start_col = messages.IntegerField(29, required=True)
    player2_patrol_boat_is_horizontal = messages.BooleanField(30, required=True)
    player2_patrol_boat_start_row = messages.EnumField('GridRowNum', 31, required=True)
    player2_patrol_boat_start_col = messages.IntegerField(32, required=True)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    is_player1_move = messages.BooleanField(1, required=True)
    move_row = messages.EnumField('GridRowNum', 2, required=True)
    move_col = messages.IntegerField(3, required=True)
    # move = messages.StringField(2, required=True)
    # is_ship_destroyed = messages.BooleanField(3, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    winner = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    ships_remaining = messages.IntegerField(4, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class RankForm(messages.Message):
    """RankForm for outbound Rank information"""
    user = messages.StringField(1, required=True)
    score = messages.IntegerField(2, required=True)


class RankForms(messages.Message):
    """Return multiple RankForms"""
    items = messages.MessageField(RankForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
