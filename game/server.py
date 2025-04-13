"""
Server Module for ChatWar
Handles web interface and socket.io communication
"""
import logging
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from .game_manager import GameManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("server")


class GameServer:
    """
    Game server that manages the web interface and Socket.IO connections
    """
    
    def __init__(self, debug_mode: bool = True):
        """Initialize the game server"""
        # Create the Flask app
        self.app = Flask(__name__, template_folder='../templates')
        self.app.config['SECRET_KEY'] = 'chatwar-secret!'
        
        # Create the Socket.IO server
        self.socketio = SocketIO(self.app)
        
        # Create the game manager
        self.game_manager = GameManager(debug_mode)
        
        # Set up routes and event handlers
        self._setup_routes()
        self._setup_socket_handlers()
        
        # Debug mode
        self.debug_mode = True
        
        logger.info("Game server initialized")
        if debug_mode:
            logger.info("Debug mode enabled")
    
    def debug_log(self, message: str) -> None:
        """Log a debug message with formatted output"""
        if self.debug_mode:
            logger.info(f"┌─────────── GAME SERVER ────────────┐")
            for line in message.split('\n'):
                logger.info(f"│ {line.ljust(35)} │")
            logger.info(f"└───────────────────────────────────┘")
    
    def _setup_routes(self):
        """Set up HTTP routes"""
        
        @self.app.route('/')
        def index():
            """Render the main game page"""
            self.debug_log("Serving index page")
            return render_template('index.html')
        
        @self.app.route('/reset')
        def reset():
            """Reset the game"""
            self.debug_log("Resetting game via HTTP request")
            self.game_manager.reset_game()
            return {"status": "Game reset"}
            
        @self.app.route('/languages')
        def get_languages():
            """Get available languages"""
            self.debug_log("Fetching available languages")
            languages = self.game_manager.get_available_languages()
            return jsonify(languages)
            
        @self.app.route('/player_language/<player>')
        def get_player_language(player):
            """Get language for a specific player"""
            self.debug_log(f"Fetching language for player: {player}")
            language = self.game_manager.get_player_language(player)
            return jsonify({"player": player, "language": language})
            
        @self.app.route('/dictionary')
        def dictionary():
            """Render the language dictionary page"""
            self.debug_log("Serving language dictionary page")
            return render_template('dictionary.html')
    
    def _setup_socket_handlers(self):
        """Set up Socket.IO event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            self.debug_log("Client connected")
            
            # Send initial game state
            emit('connected', {'data': 'Connected'})
            emit('game_update', self.game_manager.get_game_state())
        
        @self.socketio.on('move')
        def handle_move(data):
            """Handle move command"""
            self.debug_log(f"Received move command: {data}")
            
            # First send the command as a message to the channel
            channel = 'allied' if data['player'] == 'player1' else 'enemy'
            emit('channel_message', {
                'channel': channel,
                'message': data['command'],
                'is_command': True
            }, broadcast=True)
            
            # Process the command and get the result
            result = self.game_manager.process_command(data['command'], data['player'])
            
            # Broadcast the result to all clients
            emit('game_update', result, broadcast=True)
            
            # Also send the command result as a message
            status = "SUCCESS" if result.get('success') else "FAILED"
            result_message = f"> {data['command']} - {status}: {result.get('message', '')}"
            emit('channel_message', {
                'channel': channel,
                'message': result_message,
                'is_command': True,
                'is_result': True,
                'success': result.get('success', False)
            }, broadcast=True)
        
        @self.socketio.on('attack')
        def handle_attack(data):
            """Handle attack command"""
            self.debug_log(f"Received attack command: {data}")
            
            # First send the command as a message to the channel
            channel = 'allied' if data['player'] == 'player1' else 'enemy'
            emit('channel_message', {
                'channel': channel,
                'message': data['command'],
                'is_command': True
            }, broadcast=True)
            
            # Process the command and get the result
            result = self.game_manager.process_command(data['command'], data['player'])
            
            # Broadcast the result to all clients
            emit('game_update', result, broadcast=True)
            
            # Also send the command result as a message
            status = "SUCCESS" if result.get('success') else "FAILED"
            result_message = f"> {data['command']} - {status}: {result.get('message', '')}"
            emit('channel_message', {
                'channel': channel,
                'message': result_message,
                'is_command': True,
                'is_result': True,
                'success': result.get('success', False)
            }, broadcast=True)
        
        @self.socketio.on('message')
        def handle_message(data):
            """Handle chat message"""
            self.debug_log(f"Received message: {data}")
            
            # Attempt to parse the command if it's potentially a command
            parsed_data = data.copy()
            if not data.get('is_command', False) and data.get('message') and data.get('channel'):
                player = 'player1' if data['channel'] == 'allied' else 'player2'
                command_text = data['message']
                
                # Parse the command but don't execute it
                parsed_result = self.game_manager.parse_military_command(command_text, player)
                if parsed_result and parsed_result.get('orders'):
                    parsed_data['parsed_command'] = parsed_result
                    self.debug_log(f"Parsed message as command: {parsed_result}")
            
            # Broadcast the message to all clients
            emit('channel_message', {
                'channel': data['channel'],
                'message': data['message'],
                'is_command': data.get('is_command', False),
                'parsed_command': parsed_data.get('parsed_command', None)
            }, broadcast=True)
        
        @self.socketio.on('command')
        def handle_command(data):
            """Handle a general command"""
            self.debug_log(f"Received command: {data}")
            
            # First send the command as a message to the channel
            channel = 'allied' if data['player'] == 'player1' else 'enemy'
            emit('channel_message', {
                'channel': channel,
                'message': data['command'],
                'is_command': True
            }, broadcast=True)
            
            # Process the command
            result = self.game_manager.process_command(data['command'], data['player'])
            
            # Broadcast the result to all clients
            emit('game_update', result, broadcast=True)
            
            # Also send the command result and its interpretation
            status = "SUCCESS" if result.get('success') else "FAILED"
            result_message = f"> {data['command']} - {status}: {result.get('message', '')}"
            emit('channel_message', {
                'channel': channel,
                'message': result_message,
                'is_command': True,
                'is_result': True,
                'success': result.get('success', False),
                'parsed_command': result.get('parsed_command')
            }, broadcast=True)
        
        @self.socketio.on('reset_game')
        def handle_reset():
            """Handle game reset request"""
            self.debug_log("Resetting game via socket request")
            
            # Reset the game
            self.game_manager.reset_game()
            
            # Broadcast the new state
            emit('game_update', self.game_manager.get_game_state(), broadcast=True)
            emit('channel_message', {
                'channel': 'system',
                'message': 'Game has been reset',
                'is_command': False
            }, broadcast=True)
        
        @self.socketio.on('get_unit_info')
        def handle_get_unit_info(data):
            """Handle unit info request"""
            unit_id = data.get('unit_id', '')
            self.debug_log(f"Getting unit info for: {unit_id}")
            
            # Get the unit info
            unit_info = self.game_manager.get_unit_info(unit_id)
            
            # Send the response
            emit('unit_info', unit_info)
            
        @self.socketio.on('set_language')
        def handle_set_language(data):
            """Handle language change request"""
            player = data.get('player')
            language = data.get('language')
            
            if not player or not language:
                self.debug_log(f"Invalid set_language request: {data}")
                return
                
            self.debug_log(f"Setting language for {player} to {language}")
            self.game_manager.set_player_language(player, language)
            
            # Broadcast updated game state with new language info
            emit('game_update', self.game_manager.get_game_state(), broadcast=True)
            emit('channel_message', {
                'channel': 'system',
                'message': f'Player {player} language set to {language}',
                'is_command': False
            }, broadcast=True)
    
    def run(self, host='0.0.0.0', port=5000, debug=None):
        """Run the game server"""
        if debug is not None:
            self.debug_mode = debug
            self.game_manager.set_debug(debug)
        
        logger.info(f"Starting game server on {host}:{port}")
        self.socketio.run(self.app, host=host, port=port, debug=self.debug_mode)


def create_server(debug_mode: bool = True) -> GameServer:
    """Create and return a game server instance"""
    return GameServer(debug_mode) 