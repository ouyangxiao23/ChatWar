# ChatWar

**URL: [chatwar.onrender.com](https://chatwar.onrender.com)**

## Overview

ChatWar is a strategic real-time communication game developed as a project for the "Understanding Human Language" course. The game simulates military operations where success depends on the ability to decipher foreign languages under specific contexts. Players command units on a tactical battlefield, issuing commands in various languages while attempting to decode their opponent's communications.

## Game Background

During wartime, two nations communicate openly in their respective languages, believing that the enemy cannot understand them. However, this year, everything is about to change. Each side has deployed a linguist to the front lines, aiming to decode the enemy's language and anticipate their actions. Players must recognize and interpret commands in a foreign language, using context clues to decipher the meaning and respond effectively. This creates a game of reasoning and deception, where understanding the nuances of language is crucial.

## Key Features

- **Multilingual Command System**: Issue commands in English, Hindi, Swahili, and more.
- **Real-time Strategy**: Control units on a tactical battlefield map.
- **Natural Language Processing**: The game interprets commands written in natural language.
- **Complex Command Handling**: Supports multi-command sentences and various unit identifiers.
- **Cross-Cultural Interaction**: Experience the challenges of military communication protocols.

## How to Play

1. **Open the game** at [ChatWar.onrender.com](https://ChatWar.onrender.com).
2. **Choose a language** for your communications.
3. **Command your units** using the military vocabulary provided in the dictionary.
4. **Move units** with commands like "Alpha move to position three four" (or equivalent in other languages).
5. **Attack enemy positions** with commands like "Beta attack position one two" (or equivalent).
6. **Coordinate with teammates** to achieve strategic objectives.

## Game Mechanics

- **Turn-Based Gameplay**: Players take turns issuing commands in their chosen language while trying to decipher the opponent's commands.
- **Unit Management**: Each player starts with a set number of units, each with unique roles and abilities.
- **Command Structure**: Commands follow a specific format, allowing for complex orders to be issued in a single sentence.

## Technical Implementation

### Frontend

- Minimalist UI resembling a 90s DOS online war room.
- A 6x6 grid representing the battlefield with units labeled as letters (T for tank, I for infantry, A for artillery, G for garrison, and C for city).
- Chatboxes for both players to view and send messages.

### Backend

- Built with Python, featuring game state management and real-time multiplayer capabilities.
- Implements Vanilla language control, allowing units to move and attack based on commands issued in the respective languages.

## Academic Context

This project explores several linguistic concepts covered in the "Understanding Human Language" course:

1. **Cross-Cultural Communication Challenges**: Understanding how language affects military operations.
2. **Natural Language Processing**: Using AI to interpret and execute commands in multiple languages.
3. **Command Interpretation**: The importance of deciphering foreign languages in high-stakes environments.


### Prerequisites

- Python 3.6+
- Flask and Flask-SocketIO
- Additional dependencies in requirements.txt

### Local Setup

```bash
git clone https://github.com/yourusername/ChatWar.git
cd ChatWar
pip install -r requirements.txt
python run.py
```

## License

This project was developed for educational purposes as part of the "Understanding Human Language" course curriculum.

---

*"In the fog of war, deciphering the enemy's language is your strongest weapon."*
