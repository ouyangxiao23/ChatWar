from dataclasses import dataclass
from typing import List, Dict, Tuple
import random

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
        self.initialize_game()

    def initialize_game(self):
        # 初始化双方单位
        unit_types = ['T', 'I', 'A', 'G']
        commander_names = ['Alpha', 'Beta', 'Gamma', 'Delta']
        
        # 玩家1的单位（左侧）
        for i, (unit_type, commander) in enumerate(zip(unit_types, commander_names)):
            pos = (random.randint(0, 2), random.randint(0, 5))
            unit_id = f'p1_{i}'
            self.units[unit_id] = Unit(unit_type, commander, 100, pos, 'player1')
            self.commander_to_id[commander.lower()] = unit_id
            # Add to player-specific mapping
            self.player_commanders['player1'][commander.lower()] = unit_id

        # 玩家2的单位（右侧）
        for i, (unit_type, commander) in enumerate(zip(unit_types, commander_names)):
            pos = (random.randint(3, 5), random.randint(0, 5))
            unit_id = f'p2_{i}'
            self.units[unit_id] = Unit(unit_type, commander, 100, pos, 'player2')
            self.commander_to_id[commander.lower()] = unit_id
            # Add to player-specific mapping
            self.player_commanders['player2'][commander.lower()] = unit_id

        # 初始化城市
        self.initialize_cities()

    def initialize_cities(self):
        # 在地图上随机放置几个城市
        num_cities = 4
        while len(self.cities) < num_cities:
            pos = (random.randint(0, 5), random.randint(0, 5))
            if pos not in self.cities:
                self.cities.add(pos)

    def is_valid_position(self, pos: Tuple[int, int]) -> bool:
        x, y = pos
        return 0 <= x < self.grid_size and 0 <= y < self.grid_size

    def move_unit(self, unit_id: str, new_pos: Tuple[int, int]) -> Dict:
        if unit_id not in self.units:
            print(f"Invalid unit ID: {unit_id}")
            return {'success': False, 'message': 'Invalid unit ID'}

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

        unit = self.units[unit_id]
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

        if target.hp <= 0:
            print(f"Unit eliminated - {target.commander} was destroyed")
            del self.units[target_id]
            return {
                'success': True,
                'message': f'{attacker.commander} destroyed {target.commander}',
                'eliminated': target_id
            }

        return {
            'success': True,
            'message': f'{attacker.commander} dealt {damage} damage to {target.commander}',
            'damage': damage,
            'target': target_id,
            'target_hp': target.hp
        }

    def get_game_state(self) -> Dict:
        return {
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