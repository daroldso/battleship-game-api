# Battleship Game API
This is the Project 3 of Full Stack Web Developer Nanodegree by Udacity
 
## Installation
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this project.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.

##Game Description:
Battle is a guessing game between 2 players. Each game begins with each player having 5 ships in their own arena. Their ships will be placed in the grid either horizontally or vertically. Ships cannot be overlapped. In each move, one of the player will decide a coordinate to hit. It can either hit or miss the ships of the opponents. The ship will be sinked when all the coordinates of the ship was hit. Player who has no ship remaining is lost.
'Moves' are sent to `make_move` endpoint which will reply with the state of the game and who is next to move.
Score is recorded when the game ends with the ships remaining as the actual score of the player of that game.

##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: player1_name, player2_name (optional), player1_ships_location, player2_ships_location
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. player1_name provided must correspond to an
    existing user - will raise a NotFoundException if not. player2_name is optional. If not provided, player 1 will play against the computer. player1_ships_location, player2_ships_location will be the coordinates of the ships, e.g. 'A1', 'A2', 'A3', 'A4', 'A5'
     
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.
    
 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, is_player1_move, is_ship_destroyed, move
    - Returns: GameForm with new game state.
    - Description: Accepts two boolean values is_player1_move and is_ship_destroyed to determine who is moving and any ship is destroyed. Move will be used to determined whether opponent's ship is hit
    
 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).
    
 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms. 
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.
    
 - **get_user_games**
    - Path: 'game/user/{user_name}'
    - Method: GET
    - Parameters: user_name, email (optional)
    - Returns: GameForms
    - Description: Return all the active games of a specific user

 - **cancel_game**
    - Path: 'game'
    - Method: PUT
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Cancel an active game and returns the current state of a game.

 - **get_high_scores**
    - Path: 'scores/highscore'
    - Method: GET
    - Parameters: number_of_results (optional)
    - Returns: ScoreForms
    - Description: Returns all scores sorted by their ships remaining.

 - **get_user_rankings**
    - Path: 'scores/ranking'
    - Method: GET
    - Parameters: None
    - Returns: RankForms
    - Description: Returns the ranking of all users with at least one score.

 - **get_game_history**
    - Path: 'game/{urlsafe_game_key}/history'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameStepForms
    - Description: Return the history of a game in an array of moves.

##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.
    
 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.
    
 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.
    
##Forms Included:
 - **GameStepForm**
    - Representation of a Game's move (player, move, is_ship_destroyed).
 - **GameStepForms**
    - Multiple GameStepForm container.
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, player1_ships_remaining, player2_ships_remaining, player1_ships_location, player2_ships_location, game_over, message, player1_name, player2_name, current_player, cancelled, history, last_move).
 - **GameForms**
    - Multiple GameForm container.
 - **NewGameForm**
    - Used to create a new game (player1_name, player2_name, player1_ships_location, player2_ships_location)
 - **MakeMoveForm**
    - Inbound make move form (is_player1_move, move, is_ship_destroyed).
 - **ScoreForm**
    - Representation of a completed game's Score (winner, date, ships_remaining).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **RankForm**
    - Representation of the total score of a user (user, score).
 - **RankForms**
    - Multiple RankForm container
 - **StringMessage**
    - General purpose String container.
