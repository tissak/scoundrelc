# Scoundrel - Terminal Card Game

A terminal-based implementation of the Scoundrel card game, a single-player roguelike dungeon crawl card game designed by Zach Gage and Kurt Bieg.

## Installation

```bash
# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install from the current directory (optional)
pip install -e .
```

## Running the Game

```bash
# Run as a module
python -m scoundrelc

# Or use the installed script (if installed with pip install -e .)
scoundrelc
```

## Testing

Run the tests with:

```bash
# Run all tests
pytest tests/

# Run specific test files
pytest tests/test_card.py
pytest tests/test_game.py
pytest tests/test_weapon_mechanics.py
```

## How to Play

Scoundrel is played with a modified deck of 44 cards:
- Complete set of clubs and spades (including face cards and aces)
- Diamonds 2-10
- Hearts 2-10

### Card Types
- **Clubs (♣) and Spades (♠)**: Monsters - fighting these cards will cause damage
- **Diamonds (♦)**: Weapons - equip these to reduce damage from monsters
- **Hearts (♥)**: Health potions - restore health equal to the card's value

### Game Rules
1. You start with 20 health points and no weapon
2. Each room contains 4 cards
3. You must play 3 cards from each room (in any order)
4. The remaining card is kept and 3 new cards are dealt to form the next room
5. You can run from a room before playing any cards, but you can't run from two consecutive rooms
6. Combat:
   - Barehanded: You take damage equal to the monster's value
   - With weapon: You take damage equal to (monster's value - weapon's value), minimum 0
   - Weapons can only be used against monsters with value LOWER than the last monster defeated
7. Health potions: Only the first potion used in each room has an effect

### Victory Condition
- Defeat all monster cards (clubs and spades) in the dungeon

### Controls
- Click on cards to play them
- Click the "Run" button to run from a room
- Click "New Game" to start a new game
- Press 'q' to quit
- Press 'r' to run
- Press 'n' for a new game

## Credits

- Original game design by Zach Gage and Kurt Bieg (2011)
- Terminal implementation by Claude