#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity
from google.appengine.ext import ndb
from api import BattleshipApi

from models import User


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User who has not moved 12 hours after
        their opponents moved in every dormant game. Checked every hour using
        a cron job"""
        app_id = app_identity.get_application_id()
        dormant_games = BattleshipApi._get_dormant_games()

        for dormant_game in dormant_games:
            if dormant_game.current_player is not None:
                user = dormant_game.current_player.get()
                if dormant_game.player1.get().name == user.name:
                    if dormant_game.player2 is not None:
                        another_user_name = dormant_game.player2.get().name
                    else:
                        another_user_name = 'Computer'
                else:
                    another_user_name = user.name
                subject = 'This is a reminder!'
                body = 'Hey {}, you have not made a move for a long time, {} is falling asleep!'.format(user.name, another_user_name)
                mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                               user.email,
                               subject,
                               body)


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
    ('/tasks/send_notification_to_opponent', SendNoticationEmailToOpponent),
], debug=True)
