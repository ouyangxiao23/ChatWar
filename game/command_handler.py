"""
Command Handler Module for ChatWar
Responsible for processing and executing game commands
"""
from typing import Dict, Tuple, Optional, Any
import logging
from .game_state import GameState

# Configure logging with custom formatter
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("command_handler")

class CommandResult:
    """Standardized result object for command execution"""
    def __init__(self, 
                 success: bool = False, 
                 message: str = "", 
                 command_type: str = "", 
                 data: Dict[str, Any] = None):
        self.success = success
        self.message = message
        self.command_type = command_type
        self.data = data or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization"""
        result = {
            'success': self.success,
            'message': self.message,
            'type': self.command_type,
        }
        # Add any additional data
        if self.data:
            result.update(self.data)
        return result


class CommandHandler:
    """Handles parsing and execution of game commands"""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.debug_mode = True
    
    def set_debug(self, debug: bool) -> None:
        """Enable or disable debug mode"""
        self.debug_mode = debug
    
    def debug_log(self, message: str) -> None:
        """Log debug information if debug mode is enabled"""
        if self.debug_mode:
            logger.info(f"┌───────────────────────────────┐")
            for line in message.split('\n'):
                logger.info(f"│ {line.ljust(29)} │")
            logger.info(f"└───────────────────────────────┘")
    
    def parse_position(self, x_str: str, y_str: str) -> Optional[Tuple[int, int]]:
        """Parse position coordinates safely, handling numerical words"""
        # Define numerical word mappings for different languages
        number_mappings = {
            # English
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            # Hindi
            'shunya': 0, 'ek': 1, 'do': 2, 'teen': 3, 'char': 4, 'panch': 5,
            # Swahili
            'sifuri': 0, 'moja': 1, 'mbili': 2, 'tatu': 3, 'nne': 4, 'tano': 5
        }
        
        # Try to convert numerical words to numbers
        x = x_str.lower()
        y = y_str.lower()
        
        # Replace with numeric values if they're numerical words
        if x in number_mappings:
            x = str(number_mappings[x])
        if y in number_mappings:
            y = str(number_mappings[y])
            
        try:
            x_val = int(x)
            y_val = int(y)
            return (x_val, y_val)
        except ValueError:
            self.debug_log(f"Failed to parse position: {x_str}, {y_str}")
            return None
    
    def resolve_unit_id(self, unit_identifier: str, player: str) -> Optional[str]:
        """Resolve a unit identifier to a unit ID"""
        unit_identifier = unit_identifier.lower()
        
        # First try player-specific commander lookup
        unit_id = self.game_state.get_player_unit_id(unit_identifier, player)
        
        # If not found, try looking up in global commander_to_id mapping
        if not unit_id:
            unit_id = self.game_state.commander_to_id.get(unit_identifier)
        
        # If still not found, treat the identifier as a direct unit ID
        if not unit_id:
            unit_id = unit_identifier
        
        # Verify the unit exists and belongs to the player
        if unit_id not in self.game_state.units:
            self.debug_log(f"Invalid unit ID: {unit_id}")
            return None
        
        if self.game_state.units[unit_id].side != player:
            self.debug_log(f"Unit {unit_id} does not belong to player {player}")
            return None
            
        return unit_id
    
    def handle_move(self, unit_identifier: str, x_str: str, y_str: str, player: str) -> CommandResult:
        """Handle move command"""
        self.debug_log(f"Processing move command: {unit_identifier} to ({x_str}, {y_str}) by {player}")
        
        # Parse position
        position = self.parse_position(x_str, y_str)
        if not position:
            return CommandResult(False, "Invalid position format", "move")
        
        # Resolve unit ID
        unit_id = self.resolve_unit_id(unit_identifier, player)
        if not unit_id:
            return CommandResult(False, "Invalid unit or not your unit", "move")
        
        # Execute move
        result = self.game_state.move_unit(unit_id, position)
        
        # Create result object
        if result['success']:
            return CommandResult(
                True, 
                result['message'], 
                "move",
                {
                    'unit': unit_id, 
                    'position': position
                }
            )
        else:
            return CommandResult(False, result['message'], "move")
    
    def handle_attack(self, unit_identifier: str, x_str: str, y_str: str, player: str) -> CommandResult:
        """Handle attack command"""
        self.debug_log(f"Processing attack command: {unit_identifier} attacking ({x_str}, {y_str}) by {player}")
        
        # Parse position
        target_pos = self.parse_position(x_str, y_str)
        if not target_pos:
            return CommandResult(False, "Invalid position format", "attack")
            
        # Resolve unit ID
        unit_id = self.resolve_unit_id(unit_identifier, player)
        if not unit_id:
            return CommandResult(False, "Invalid unit or not your unit", "attack")
        
        # Execute attack
        result = self.game_state.attack(unit_id, target_pos)
        
        # Create result object
        if result['success']:
            data = {
                'unit': unit_id,
                'target_position': target_pos
            }
            # Add additional attack result data
            if 'damage' in result:
                data['damage'] = result['damage']
            if 'target' in result:
                data['target'] = result['target']
            if 'target_hp' in result:
                data['target_hp'] = result['target_hp']
            if 'eliminated' in result:
                data['eliminated'] = result['eliminated']
                
            return CommandResult(True, result['message'], "attack", data)
        else:
            return CommandResult(False, result['message'], "attack")
    
    def process_command(self, command: str, player: str) -> CommandResult:
        """Process a raw command string"""
        self.debug_log(f"Processing raw command: '{command}' from player {player}")
        
        # Split and normalize command
        parts = command.lower().strip().split()
        if not parts:
            return CommandResult(False, "Empty command", "unknown")
        
        # Identify command type and process
        action = parts[0]
        
        if action == 'move' and len(parts) == 4:
            return self.handle_move(parts[1], parts[2], parts[3], player)
            
        elif action == 'attack' and len(parts) == 4:
            return self.handle_attack(parts[1], parts[2], parts[3], player)
            
        else:
            self.debug_log(f"Unrecognized command format: {parts}")
            return CommandResult(False, "Invalid command format", "unknown") 