#!/usr/bin/env python3
"""
ChatWar - A strategic game of combat and communication

Quick start script for the game server.
Run this script to start the ChatWar game server.
"""
import sys
import os

if __name__ == "__main__":
    # Print welcome message
    print("\n" + "=" * 60)
    print(" ChatWar - A strategic game of combat and communication")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 6):
        print("\nError: ChatWar requires Python 3.6 or higher")
        print(f"Current Python version: {sys.version}")
        print("Please upgrade your Python installation\n")
        sys.exit(1)
    
    # Check if requirements are installed
    try:
        import flask
        import flask_socketio
    except ImportError:
        print("\nMissing dependencies. Installing required packages...")
        os.system(f"{sys.executable} -m pip install -r requirements.txt")
        print("Dependencies installed.\n")
    
    # Execute the app module
    from app import main
    main() 