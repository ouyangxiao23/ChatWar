"""
ChatWar - A strategic game of combat and communication
Main application entry point
"""
import argparse
import logging
from game.server import create_server

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("chatwar")

def main():
    """Main entry point for the ChatWar game"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='ChatWar Game Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind the server to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind the server to')
    parser.add_argument('--no-debug', action='store_true', help='Disable debug mode')
    parser.add_argument('--language', type=str, default='swahili', help='Language for in-game communications')
    args = parser.parse_args()
    
    # Debug mode is on by default
    debug_mode = not args.no_debug
    
    # Create and run the game server
    logger.info(f"Starting ChatWar game server on {args.host}:{args.port}")
    server = create_server(debug_mode=debug_mode)
    
    # Language dictionary for military communications - displayed as white scrollable box
    language_dictionaries = {
        "swahili": {
            "title": "KAMUSI YA KIJESHI / MILITARY DICTIONARY",
            "move": ["nenda", "ziende", "sogeza", "hamisha", "tembea", "peleka"],
            "attack": ["shambulia", "vamia", "piga", "rukia", "dhuru", "pambana"],
            "units": ["Alpha", "Beta", "Gamma", "Delta", "Kikosi", "Jeshi", "Wapiganaji"],
            "numbers": ["sifuri/0", "moja/1", "mbili/2", "tatu/3", "nne/4", "tano/5"],
            "directions": ["kaskazini", "kusini", "mashariki", "magharibi"]
        },
        "hindi": {
            "title": "सैन्य शब्दकोश / MILITARY DICTIONARY",
            "move": ["जाओ", "बढ़ो", "चलो", "आगे बढ़ो", "स्थानांतरित करो", "प्रस्थान करो"],
            "attack": ["हमला करो", "आक्रमण करो", "प्रहार करो", "वार करो", "धावा बोलो", "मार करो"],
            "units": ["अल्फा", "बीटा", "गामा", "डेल्टा", "यूनिट", "दस्ता", "टुकड़ी"],
            "numbers": ["शून्य/0", "एक/1", "दो/2", "तीन/3", "चार/4", "पांच/5"],
            "directions": ["उत्तर", "दक्षिण", "पूर्व", "पश्चिम"]
        },
        "english": {
            "title": "MILITARY DICTIONARY",
            "move": ["move", "advance", "proceed", "go", "march", "relocate", "shift"],
            "attack": ["attack", "strike", "hit", "assault", "engage", "charge", "raid"],
            "units": ["Alpha", "Beta", "Gamma", "Delta", "Squad", "Team", "Unit"],
            "numbers": ["zero/0", "one/1", "two/2", "three/3", "four/4", "five/5"],
            "directions": ["north", "south", "east", "west"]
        }
    }
    
    # Print dictionary for selected language
    logger.info("Language dictionary loaded: " + args.language)
    
    # Print startup message
    logger.info("Debug mode enabled - additional logging will be displayed")
    
    logger.info("======================================================")
    logger.info("               CHATWAR SERVER STARTED                ")
    logger.info("======================================================")
    logger.info(f"Server URL: http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{args.port}")
    logger.info("Press Ctrl+C to stop the server")
    
    # Run the server
    server.run(host=args.host, port=args.port)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        logger.info("Goodbye!")