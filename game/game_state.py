from dataclasses import dataclass
from typing import List, Dict, Tuple
import random
import logging

logger = logging.getLogger("game_state")

@dataclass
class Unit:
    unit_type: str  # T: Tank, I: Infantry, A: Artillery, G: Garrison
    commander: str
    hp: int
    position: Tuple[int, int]
    side: str  # 'player1' or 'player2'

class GameState:
    def __init__(self):
        self.grid_size = 6
        self.units: Dict[str, Unit] = {}
        self.cities = set()  # 存储城市位置
        self.commander_to_id = {}
        # Add separate mappings per player
        self.player_commanders = {
            'player1': {},
            'player2': {}
        }
        self.game_over = False
        self.winner = None
        self.initialize_game()

    def initialize_game(self):
        # 初始化双方单位
        unit_types = ['T', 'I', 'A', 'G']
        commander_names = ['Alpha', 'Beta', 'Gamma', 'Delta']
        
        # Track occupied positions
        occupied_positions = set()
        
        # 玩家1的单位（左侧）
        for i, (unit_type, commander) in enumerate(zip(unit_types, commander_names)):
            # Ensure positions don't overlap
            while True:
                pos = (random.randint(0, 2), random.randint(0, 5))
                if pos not in occupied_positions:
                    occupied_positions.add(pos)
                    break
                    
            unit_id = f'p1_{i}'
            self.units[unit_id] = Unit(unit_type, commander, 100, pos, 'player1')
            self.commander_to_id[commander.lower()] = unit_id
            # Add to player-specific mapping
            self.player_commanders['player1'][commander.lower()] = unit_id

        # 玩家2的单位（右侧）
        for i, (unit_type, commander) in enumerate(zip(unit_types, commander_names)):
            # Ensure positions don't overlap
            while True:
                pos = (random.randint(3, 5), random.randint(0, 5))
                if pos not in occupied_positions:
                    occupied_positions.add(pos)
                    break
                    
            unit_id = f'p2_{i}'
            self.units[unit_id] = Unit(unit_type, commander, 100, pos, 'player2')
            self.commander_to_id[commander.lower()] = unit_id
            # Add to player-specific mapping
            self.player_commanders['player2'][commander.lower()] = unit_id

        # 初始化城市
        self.initialize_cities(occupied_positions)

    def initialize_cities(self, occupied_positions):
        # 在地图上随机放置几个城市，避免与单位重叠
        num_cities = 4
        while len(self.cities) < num_cities:
            pos = (random.randint(0, 5), random.randint(0, 5))
            if pos not in occupied_positions and pos not in self.cities:
                self.cities.add(pos)
                occupied_positions.add(pos)

    def is_valid_position(self, pos: Tuple[int, int]) -> bool:
        x, y = pos
        return 0 <= x < self.grid_size and 0 <= y < self.grid_size

    def move_unit(self, unit_id: str, new_pos: Tuple[int, int]) -> Dict:
        if unit_id not in self.units:
            print(f"Invalid unit ID: {unit_id}")
            return {'success': False, 'message': 'Invalid unit ID'}

        unit = self.units[unit_id]
        
        # Check if unit is a Garrison (non-movable)
        if unit.unit_type == 'G':
            print(f"Unit {unit_id} is a Garrison and cannot move")
            return {'success': False, 'message': 'Garrison units cannot move'}

        if not self.is_valid_position(new_pos):
            print(f"Invalid position: {new_pos}")
            return {'success': False, 'message': 'Invalid position'}
        
        # Check if new position is occupied by another unit
        for other_id, other_unit in self.units.items():
            if other_unit.position == new_pos:
                print(f"Position {new_pos} is occupied by unit {other_id}")
                return {'success': False, 'message': 'Position is already occupied'}

        # Check if new position contains a city
        if new_pos in self.cities:
            print(f"Position {new_pos} contains a city")
            return {'success': False, 'message': 'Cannot move onto a city'}

        old_pos = unit.position
        unit.position = new_pos
        print(f"Unit {unit_id} moved from {old_pos} to {new_pos}")
        return {'success': True, 'message': f'{unit.commander} moved to {new_pos}'}

    def attack(self, attacker_id: str, target_pos: Tuple[int, int]) -> Dict:
        print(f"Attack initiated - Attacker ID: {attacker_id}, Target Position: {target_pos}")
        
        if attacker_id not in self.units:
            print(f"Attack failed - Invalid attacker ID: {attacker_id}")
            return {'success': False, 'message': 'Invalid attacker'}

        attacker = self.units[attacker_id]
        print(f"Attacker found - Commander: {attacker.commander}, Position: {attacker.position}")
        
        # Check attack range based on unit type
        attack_range = self.get_attack_range(attacker.unit_type)
        if not self.is_in_range(attacker.position, target_pos, attack_range):
            print(f"Attack failed - Target out of range for {attacker.unit_type}")
            return {'success': False, 'message': f'Target out of range (max range: {attack_range})'}
        
        # Find target unit at position
        target = None
        target_id = None
        for uid, unit in self.units.items():
            if unit.position == target_pos:
                target = unit
                target_id = uid
                break

        if not target:
            print(f"Attack failed - No target found at position {target_pos}")
            return {'success': False, 'message': 'No target at position'}

        print(f"Target found - Commander: {target.commander}, Current HP: {target.hp}")
        
        # Combat system
        damage = random.randint(20, 40)
        target.hp -= damage
        print(f"Combat result - Damage dealt: {damage}, Target's remaining HP: {target.hp}")

        result = {
            'success': True,
            'message': f'{attacker.commander} dealt {damage} damage to {target.commander}',
            'damage': damage,
            'target': target_id,
            'target_hp': target.hp
        }

        if target.hp <= 0:
            print(f"Unit eliminated - {target.commander} was destroyed")
            # Remove the unit
            del self.units[target_id]
            result['message'] = f'{attacker.commander} destroyed {target.commander}'
            result['eliminated'] = target_id
            
            # Check for victory condition
            self.check_victory_condition()
            if self.game_over:
                result['game_over'] = True
                result['winner'] = self.winner
                result['message'] += f". {self.winner} has won the game!"

        return result

    def get_attack_range(self, unit_type: str) -> int:
        """Get the attack range for a given unit type"""
        attack_ranges = {
            'G': 1,  # Garrison has range 1
            'I': 1,  # Infantry has range 1
            'T': 2,  # Tank has range 2
            'A': 4   # Artillery has range 4
        }
        return attack_ranges.get(unit_type, 1)  # Default to 1 if unit type not recognized
        
    def is_in_range(self, source_pos: Tuple[int, int], target_pos: Tuple[int, int], max_range: int) -> bool:
        """Check if target position is within the specified range from source position"""
        x1, y1 = source_pos
        x2, y2 = target_pos
        
        # Calculate Manhattan distance
        distance = abs(x2 - x1) + abs(y2 - y1)
        return distance <= max_range
        
    def get_cells_in_range(self, position: Tuple[int, int], range_value: int) -> List[Tuple[int, int]]:
        """Get all valid grid cells within the specified range of a position"""
        x, y = position
        cells = []
        
        for dx in range(-range_value, range_value + 1):
            for dy in range(-range_value, range_value + 1):
                # Skip if manhattan distance exceeds range
                if abs(dx) + abs(dy) > range_value:
                    continue
                    
                new_x, new_y = x + dx, y + dy
                
                # Check if the position is valid
                if self.is_valid_position((new_x, new_y)):
                    cells.append((new_x, new_y))
        
        return cells

    def check_victory_condition(self):
        """Check if one side has lost all their units"""
        player1_units = sum(1 for unit in self.units.values() if unit.side == 'player1')
        player2_units = sum(1 for unit in self.units.values() if unit.side == 'player2')
        
        if player1_units == 0:
            self.game_over = True
            self.winner = 'Player 2'
            logger.info("Player 2 has won the game by eliminating all enemy units!")
        elif player2_units == 0:
            self.game_over = True
            self.winner = 'Player 1'
            logger.info("Player 1 has won the game by eliminating all enemy units!")
        
        return self.game_over

    def get_game_state(self) -> Dict:
        state = {
            'units': {
                uid: {
                    'type': unit.unit_type,
                    'commander': unit.commander,
                    'hp': unit.hp,
                    'position': unit.position,
                    'side': unit.side
                } for uid, unit in self.units.items()
            },
            'cities': list(self.cities)
        }
        
        # Add game over status if applicable
        if self.game_over:
            state['game_over'] = True
            state['winner'] = self.winner
            state['message'] = f"{self.winner} has won the game!"
        
        return state

    def get_player_unit_id(self, commander_name: str, player: str) -> str:
        """Get unit ID for a player-specific commander name"""
        if player not in self.player_commanders:
            return None
            
        return self.player_commanders[player].get(commander_name.lower())

    def process_command(self, command: str, player: str) -> Dict:
        print(f"Processing command: {command} from {player}")
        parts = command.lower().split()
        
        if not parts:
            return {'success': False, 'message': 'Empty command'}

        action = parts[0]
        if action == 'move' and len(parts) == 4:
            unit_identifier = parts[1].lower()
            try:
                new_pos = (int(parts[2]), int(parts[3]))
                # Check if using commander name or unit ID
                unit_id = self.get_player_unit_id(unit_identifier, player) or self.commander_to_id.get(unit_identifier, unit_identifier)
                
                # Verify unit exists and belongs to the player
                if unit_id not in self.units or self.units[unit_id].side != player:
                    print(f"Unit {unit_identifier} does not belong to {player}")
                    return {'success': False, 'message': 'Not your unit'}
                
                result = self.move_unit(unit_id, new_pos)
                if result['success']:
                    return {'success': True, 'type': 'move', 'unit': unit_id, 'position': new_pos, 'message': result['message']}
                return result
            except ValueError:
                print(f"Invalid position format in command: {command}")
                return {'success': False, 'message': 'Invalid position format'}

        elif action == 'attack' and len(parts) == 4:
            unit_identifier = parts[1].lower()
            try:
                target_pos = (int(parts[2]), int(parts[3]))
                # Check if using commander name or unit ID, use player-specific lookup
                unit_id = self.get_player_unit_id(unit_identifier, player) or self.commander_to_id.get(unit_identifier, unit_identifier)
                return self.attack(unit_id, target_pos)
            except ValueError:
                pass

        return {'success': False, 'message': 'Invalid command'}