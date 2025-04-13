"""
Test Integration between Language Parser and Game System
"""
import logging
import sys
import json
from language.interpreter import MilitaryInstructionParser
from game.game_manager import GameManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("integration_test")

def test_languages():
    """Test parsing commands in different languages"""
    logger.info("Testing command parsing in multiple languages")
    
    test_cases = {
        "english": [
            "Unit Alpha move to 2,2 with support",
            "Team Charlie attack 5,7 before dawn",
            "Tell Gamma to attack position 4,4 immediately"
        ],
        "swahili": [
            "Kikosi Alpha ziende 2,2 kwa msaada",
            "Timu Charlie ishambulie 5,7 kabla ya alfajiri",
            "Amuru Gamma kushambulia nafasi 4,4 sasa"
        ],
        "hindi": [
            "Unit Alpha 2,2 par jaaye",
            "Team Charlie 5,7 par hamla kare subah se pehle",
            "Gamma ko 4,4 par hamla karne ko kaho"
        ]
    }
    
    for language, commands in test_cases.items():
        logger.info(f"\nTesting {language.upper()} language parsing:")
        parser = MilitaryInstructionParser(language)
        
        for command in commands:
            result = parser.process_single(command)
            logger.info(f"  Command: {command}")
            logger.info(f"  Parsed: {json.dumps(result, indent=2)}")
            
            if result.get('orders'):
                logger.info(f"  ✓ Successfully parsed {len(result['orders'])} order(s)")
            else:
                logger.info(f"  ✗ Failed to parse any orders")

def test_game_integration():
    """Test integration between language parser and game system"""
    logger.info("\nTesting integration with game system:")
    
    # Create game manager
    game_manager = GameManager(debug_mode=True)
    
    # Test scenarios - language, player, command
    test_scenarios = [
        # English commands
        ("english", "player1", "Alpha move to 2,2"),
        ("english", "player1", "Tell Beta to attack 4,3"),
        # Swahili commands
        ("swahili", "player2", "Kikosi Alpha ziende 3,3 sasa"),
        ("swahili", "player2", "Beta ishambulie 1,2"),
        # Hindi commands
        ("hindi", "player1", "Gamma ko 2,4 par bhejo"),
        ("hindi", "player2", "Delta 5,5 par hamla kare")
    ]
    
    for language, player, command in test_scenarios:
        # Set the language for the player
        game_manager.set_player_language(player, language)
        
        logger.info(f"\nScenario: {player} using {language}")
        logger.info(f"  Command: {command}")
        
        # Parse and execute the command
        result = game_manager.process_command(command, player)
        
        # Check if we got a parsed result
        if 'parsed_command' in result and result['parsed_command'].get('orders'):
            logger.info(f"  ✓ Command successfully parsed")
            logger.info(f"  Parsed as: {json.dumps(result['parsed_command']['orders'], indent=2)}")
        else:
            logger.info(f"  ✗ Failed to parse command")
            
        # Check if the command was executed
        if result.get('success'):
            logger.info(f"  ✓ Command executed successfully: {result.get('message')}")
        else:
            logger.info(f"  ✗ Command execution failed: {result.get('message')}")

if __name__ == "__main__":
    logger.info("Integration Test for ChatWar Language System")
    logger.info("===========================================")
    
    # Test language parsing
    test_languages()
    
    # Test game integration
    test_game_integration()
    
    logger.info("\nIntegration tests completed.") 