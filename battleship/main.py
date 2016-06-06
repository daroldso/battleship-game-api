#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity
from google.appengine.ext import ndb
from api import BattleshipApi

from models import User, Game
from datetime import datetime


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User with an email about games.
        Called every hour using a cron job"""
        app_id = app_identity.get_application_id()
        users = []
        games = Game.query(ndb.AND(Game.game_over == False,
                                   Game.cancelled == False))
        inactive_games = []
        for game in games:
            elapsedTime = datetime.now() - game.last_move
            elaspedHours, elaspedSeconds = divmod(elapsedTime.days * 86400 + elapsedTime.seconds, 3600)
            if elaspedHours >= 12:
                inactive_games.append(game)
        for inactive_game in inactive_games:
            if inactive_game.current_player != None:
                user = inactive_game.current_player.get()
                if game.player1.get().name == user.name:
                    another_user_name = game.player2.get().name
                else:
                    another_user_name = user.name
                subject = 'This is a reminder!'
                body = 'Hey {}, you have not made a move for a long time, {} is falling asleep!'.format(user.name, another_user_name)
                mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                               user.email,
                               subject,
                               body)


class UpdateAverageMovesRemaining(webapp2.RequestHandler):
    def post(self):
        """Update game listing announcement in memcache."""
        # BattleshipApi._cache_average_attempts()
        self.response.set_status(204)


class SendNoticationEmailToOpponent(webapp2.RequestHandler):
    def post(self):
        """Send Notication Email To Opponent"""
        app_id = app_identity.get_application_id()
        player_to_move = self.request.get('player_to_move')
        user = User.query(User.name == player_to_move).get()
        subject = 'This is a reminder!'
        body = 'Hey {}, it\'s your turn!'.format(user.name)
        mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                       user.email,
                       subject,
                       body)
        

app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
    ('/tasks/cache_average_attempts', UpdateAverageMovesRemaining),
    ('/tasks/send_notification_to_opponent', SendNoticationEmailToOpponent),
], debug=True)
