"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb

DEFAULT_NUMBER_OF_SHIPS = 5

class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()


class Game(ndb.Model):
    """Game object"""
    player1 = ndb.KeyProperty(required=True, kind='User')
    player2 = ndb.KeyProperty(kind='User')
    player1_ships_remaining = ndb.IntegerProperty(required=True,
                                                  default=DEFAULT_NUMBER_OF_SHIPS)
    player2_ships_remaining = ndb.IntegerProperty(required=True,
                                                  default=DEFAULT_NUMBER_OF_SHIPS)
    player1_ships_location = ndb.StringProperty(repeated=True)
    player2_ships_location = ndb.StringProperty(repeated=True)
    current_player = ndb.KeyProperty(kind='User')
    game_over = ndb.BooleanProperty(required=True, default=False)

    @classmethod
    def new_game(cls, user1, user2,
                 player1_ships_location, player2_ships_location):
        """Creates and returns a new game"""
        # if user2 is not None:
            # user2 = None
        game = Game(player1=user1,
                    player2=user2,
                    player1_ships_remaining=DEFAULT_NUMBER_OF_SHIPS,
                    player2_ships_remaining=DEFAULT_NUMBER_OF_SHIPS,
                    player1_ships_location=player1_ships_location,
                    player2_ships_location=player2_ships_location,
                    current_player=user1,
                    game_over=False)
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
        form.player1_ships_remaining = self.player1_ships_remaining
        form.player2_ships_remaining = self.player2_ships_remaining
        form.player1_ships_location = self.player1_ships_location
        form.player2_ships_location = self.player2_ships_location
        if(self.current_player):
            form.current_player = self.current_player.get().name
        else:
            form.current_player = 'Computer'
        form.game_over = self.game_over
        form.message = message
        return form

    def end_game(self, winner=False):
        """Ends the game - winner will be either player 1 or 2, or will be False if AI wins"""
        self.game_over = True
        self.put()
        # Add the game to the score 'board' if a player wins
        if(winner):
            if(winner == self.player1):
                ships_remaining = self.player1_ships_remaining
            else:
                ships_remaining = self.player2_ships_remaining
            score = Score(winner=winner, date=date.today(), ships_remaining=ships_remaining)
            score.put()


class Score(ndb.Model):
    """Score object. For Single player game, only those who beat AI player will be stored"""
    winner = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    ships_remaining = ndb.IntegerProperty(required=True)

    def to_form(self):
        return ScoreForm(winner=self.winner.get().name,
                         date=str(self.date), ships_remaining=self.ships_remaining)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    player1_ships_remaining = messages.IntegerField(2, required=True)
    player2_ships_remaining = messages.IntegerField(3)
    player1_ships_location = messages.StringField(4, repeated=True)
    player2_ships_location = messages.StringField(5, repeated=True)
    game_over = messages.BooleanField(6, required=True)
    message = messages.StringField(7, required=True)
    player1_name = messages.StringField(8, required=True)
    player2_name = messages.StringField(9)
    current_player = messages.StringField(10)


class GameForms(messages.Message):
    """Return multiple GameForms"""
    items = messages.MessageField(GameForm, 1, repeated=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    player1_name = messages.StringField(1, required=True)
    player2_name = messages.StringField(2)
    player1_ships_location = messages.StringField(3, repeated=True)
    player2_ships_location = messages.StringField(4, repeated=True)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    is_player1_move = messages.BooleanField(1, required=True)
    move = messages.StringField(2, required=True)
    is_ship_destroyed = messages.BooleanField(3, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    winner = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    ships_remaining = messages.IntegerField(4, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
