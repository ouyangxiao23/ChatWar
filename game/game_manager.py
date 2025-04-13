"""
Game Manager Module for ChatWar
Acts as the central coordinator for all game activities
"""
import logging
import sys
import os
from typing import Dict, Any, List
from .game_state import GameState
from .command_handler import CommandHandler, CommandResult

# Add path to language directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the military instruction parser
from language.interpreter import MilitaryInstructionParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("game_manager")


class GameManager:
    """
    Central manager for game operations
    
    Provides a high-level API for all game operations, including:
    - Initializing and resetting games
    - Processing player commands
    - Getting game state updates
    - Handling events and notifications
    - Language processing for command interpretation
    """
    
    def __init__(self, debug_mode: bool = True):
        """Initialize the game manager"""
        # Create the game state
        self.game_state = GameState()
        
        # Create command handler
        self.command_handler = CommandHandler(self.game_state)
        
        # Set debug mode
        self.debug_mode = debug_mode
        self.command_handler.set_debug(debug_mode)
        
        # Event tracking
        self.event_history = []

        # Initialize language parsers for both players
        self.player_languages = {
            'player1': 'english',
            'player2': 'swahili'
        }
        self.language_parsers = {
            'player1': MilitaryInstructionParser(self.player_languages['player1']),
            'player2': MilitaryInstructionParser(self.player_languages['player2'])
        }
        
        logger.info("Game manager initialized")
        logger.info(f"Player1 language: {self.player_languages['player1']}, Player2 language: {self.player_languages['player2']}")
        if debug_mode:
            logger.info("Debug mode enabled")
    
    def set_debug(self, debug_mode: bool) -> None:
        """Enable or disable debug mode"""
        self.debug_mode = debug_mode
        self.command_handler.set_debug(debug_mode)
        logger.info(f"Debug mode {'enabled' if debug_mode else 'disabled'}")
    
    def debug_log(self, message: str) -> None:
        """Log a debug message with formatted output"""
        if self.debug_mode:
            logger.info(f"┌─────────── GAME MANAGER ───────────┐")
            for line in message.split('\n'):
                logger.info(f"│ {line.ljust(35)} │")
            logger.info(f"└───────────────────────────────────┘")

    def set_player_language(self, player: str, language: str) -> None:
        """Set the language for a player"""
        if player not in ['player1', 'player2']:
            logger.error(f"Invalid player: {player}")
            return
            
        self.debug_log(f"Setting {player} language to {language}")
        self.player_languages[player] = language
        self.language_parsers[player] = MilitaryInstructionParser(language)
    
    def get_available_languages(self) -> List[str]:
        """Get list of available languages"""
        return ['english', 'swahili', 'hindi']
    
    def get_player_language(self, player: str) -> str:
        """Get the current language for a player"""
        if player not in ['player1', 'player2']:
            return 'unknown'
        return self.player_languages[player]
    
    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        self.debug_log("Retrieving current game state")
        game_state = self.game_state.get_game_state()
        
        # Add language information to game state
        game_state['languages'] = {
            'player1': self.player_languages['player1'],
            'player2': self.player_languages['player2'],
            'available': self.get_available_languages()
        }
        
        return game_state
    
    def reset_game(self) -> None:
        """Reset the game to initial state"""
        self.debug_log("Resetting game")
        self.game_state = GameState()
        self.command_handler = CommandHandler(self.game_state)
        self.command_handler.set_debug(self.debug_mode)
        self.event_history = []
    
    def process_move_command(self, unit: str, x: int, y: int, player: str) -> CommandResult:
        """
        Process a move command
        Direct method to move a unit without parsing a command string
        """
        self.debug_log(f"Direct move command: {unit} to ({x},{y}) by {player}")
        return self.command_handler.handle_move(unit, str(x), str(y), player)
    
    def process_attack_command(self, unit: str, x: int, y: int, player: str) -> CommandResult:
        """
        Process an attack command
        Direct method to attack without parsing a command string
        """
        self.debug_log(f"Direct attack command: {unit} attacking ({x},{y}) by {player}")
        return self.command_handler.handle_attack(unit, str(x), str(y), player)
    
    def parse_military_command(self, command_text: str, player: str) -> Dict[str, Any]:
        """
        Parse a military command in the player's language
        Returns parsed command data or empty result if parsing failed
        """
        if player not in self.language_parsers:
            self.debug_log(f"No language parser for player: {player}")
            return {"text": command_text, "orders": []}
            
        parser = self.language_parsers[player]
        self.debug_log(f"Parsing command '{command_text}' using {self.player_languages[player]} parser")
        
        result = parser.process_single(command_text)
        self.debug_log(f"Parser result: {result}")
        return result
    
    def process_command(self, command: str, player: str) -> Dict[str, Any]:
        """
        Process a command string from a player
        Now integrates with language parser to interpret natural language commands
        Returns a dictionary with the command result and updated game state
        """
        self.debug_log(f"Processing command: '{command}' from {player}")
        
        # First parse the command using the language parser
        parsed_result = self.parse_military_command(command, player)
        
        # Track the parsed command event
        parse_event = {
            'type': 'parse',
            'player': player,
            'command': command,
            'parsed': parsed_result
        }
        self.event_history.append(parse_event)
        
        # Initialize results
        results = []
        
        # Process each order in the parsed result
        if parsed_result and parsed_result.get('orders'):
            for order in parsed_result.get('orders', []):
                # Extract unit, action and parameters
                unit = order.get('unit')
                action = order.get('action')
                parameters = order.get('parameters', {})
                
                # Skip if missing required fields
                if not unit or not action:
                    self.debug_log(f"Skipping order with missing fields: {order}")
                    continue
                
                result = None
                if action == 'move' and parameters:
                    # Handle move command
                    x = parameters.get('x', parameters[0] if isinstance(parameters, list) else None)
                    y = parameters.get('y', parameters[1] if isinstance(parameters, list) else None)
                    
                    if x is not None and y is not None:
                        self.debug_log(f"Executing move: {unit} to ({x},{y})")
                        result = self.command_handler.handle_move(unit, x, y, player)
                    else:
                        self.debug_log(f"Invalid move parameters: {parameters}")
                        
                elif action == 'attack' and parameters:
                    # Handle attack command
                    x = parameters.get('x', parameters[0] if isinstance(parameters, list) else None)
                    y = parameters.get('y', parameters[1] if isinstance(parameters, list) else None)
                    
                    if x is not None and y is not None:
                        self.debug_log(f"Executing attack: {unit} attacking ({x},{y})")
                        result = self.command_handler.handle_attack(unit, x, y, player)
                    else:
                        self.debug_log(f"Invalid attack parameters: {parameters}")
                
                if result:
                    results.append(result)
                    self.debug_log(f"Execution result: {result.to_dict()}")
        
        # If no orders were processed, try direct command processing as fallback
        if not results:
            self.debug_log(f"No orders extracted, trying direct command parsing")
            direct_result = self.command_handler.process_command(command, player)
            if direct_result.success:
                results.append(direct_result)
                self.debug_log(f"Direct processing result: {direct_result.to_dict()}")
        
        # Determine the final result to return
        if not results:
            # No command was successfully processed
            result = CommandResult(
                False, 
                "Command could not be parsed or executed", 
                "unknown"
            )
        else:
            # Use the first successful result, or the last result if none succeeded
            successful_results = [r for r in results if r.success]
            result = successful_results[0] if successful_results else results[-1]
        
        # Track the command execution event
        command_event = {
            'type': 'command',
            'player': player,
            'command': command,
            'result': result.to_dict()
        }
        self.event_history.append(command_event)
        
        # Return combined result with game state
        response = self.get_game_state()
        response.update(result.to_dict())
        response['original_command'] = command
        response['parsed_command'] = parsed_result
        
        return response
    
    def get_unit_info(self, unit_id_or_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific unit"""
        self.debug_log(f"Getting unit info for: {unit_id_or_name}")
        
        # Try to find by ID first
        if unit_id_or_name in self.game_state.units:
            unit = self.game_state.units[unit_id_or_name]
            return {
                'id': unit_id_or_name,
                'type': unit.unit_type,
                'commander': unit.commander,
                'hp': unit.hp,
                'position': unit.position,
                'side': unit.side
            }
        
        # Try to find by commander name
        unit_id = self.game_state.commander_to_id.get(unit_id_or_name.lower())
        if unit_id:
            unit = self.game_state.units[unit_id]
            return {
                'id': unit_id,
                'type': unit.unit_type,
                'commander': unit.commander,
                'hp': unit.hp,
                'position': unit.position,
                'side': unit.side
            }
        
        return {'error': 'Unit not found'}
    
    def get_event_history(self) -> list:
        """Get the history of game events"""
        return self.event_history 