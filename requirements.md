# Scoundrel Game - Developer Specifications

## Overview
Scoundrel is a single-player roguelike dungeon crawl card game designed by Zach Gage and Kurt Bieg. This document outlines the specifications for developing a digital implementation of the game.

## 1. Game Components

### 1.1 Card Deck
- **Base**: Standard 52-card playing deck
- **Modifications**: Remove all jokers, red face cards (hearts/diamonds J, Q, K), and red aces (A♥, A♦)
- **Remaining Cards**: 44 cards total (complete set of clubs and spades, diamonds 2-10, hearts 2-10)

### 1.2 Card Values
- **Number Cards**: Face value (2-10)
- **Face Cards**: Jack = 11, Queen = 12, King = 13, Ace = 14
- **Card Types by Suit**:
  - **♣ Clubs**: Monsters
  - **♠ Spades**: Monsters
  - **♦ Diamonds**: Weapons
  - **♥ Hearts**: Health potions

## 2. Game Setup

### 2.1 Initial State
- **Player Health**: Start at 20 points
- **Weapon**: None equipped
- **Dungeon Deck**: Shuffled modified deck as described in 1.1
- **Discard Pile**: Empty
- **First Room**: Deal 4 cards face up from the dungeon deck

## 3. Core Mechanics

### 3.1 Room Navigation
- **Room Structure**: 4 cards dealt face up
- **Room Completion**: Player must play 3 of the 4 cards in any order
- **Room Progression**: After playing 3 cards, the remaining card is retained and 3 new cards are dealt to form the next room
- **Running**: 
  - Player may "run" from a room before playing any cards
  - Running places all 4 current room cards at the bottom of the dungeon deck
  - A new room of 4 cards is immediately dealt
  - Player cannot run from two consecutive rooms
  - The system must track whether the player ran from the previous room

### 3.2 Card Interactions

#### 3.2.1 Monster Cards (♣ Clubs, ♠ Spades)
- **Combat Options**:
  - **Barehanded Combat**: Player takes damage equal to the monster's card value
  - **Weapon Combat**: Player takes damage equal to (monster's value - weapon's value), minimum 0
- **Health Reduction**: Subtract damage taken from player's health
- **Game Over**: If health reaches 0 or below, the game ends in defeat

#### 3.2.2 Weapon Cards (♦ Diamonds)
- **Equipping**: 
  - Only one weapon can be equipped at a time
  - Equipping a new weapon replaces the previous one
- **Combat Usage**:
  - Initial use: Can be used against any monster
  - Subsequent use: Can only be used against monsters with value LOWER than the previously defeated monster
- **Tracking**: 
  - System must track the value of the last monster defeated with the current weapon
  - Visual feedback should indicate which monsters the weapon can be used against

#### 3.2.3 Health Potion Cards (♥ Hearts)
- **Healing Effect**: Restore health equal to the card's value
- **Usage Limit**: Only the first health potion used in a room has effect
- **Additional Potions**: Any subsequent health potions used in the same room are discarded with no effect
- **Room Tracking**: System must track whether a potion has been used in the current room

## 4. Game Flow

### 4.1 Player Turn
1. At the start of a new room, player is presented with 4 cards
2. Player may run from the room (if allowed) or must play 3 cards
3. For each card played, apply its effect:
   - Monster: Take damage according to combat rules
   - Weapon: Equip weapon, replacing any existing one
   - Health Potion: Restore health (if first used in room)
4. After playing 3 cards, the remaining card is kept and 3 new cards are dealt

### 4.2 Game End Conditions
- **Victory**: All monster cards (clubs and spades) have been defeated
- **Defeat**: Player's health reaches 0 or below

## 5. User Interface Requirements

### 5.1 Game Screen Elements
- **Room Display**: Current 4 cards clearly visible with indication of which cards can be played
- **Player Status**:
  - Health indicator (current/maximum)
  - Currently equipped weapon with its value
  - Visual indication of weapon's dulling status (what monster value it can defeat)
- **Game State Indicators**:
  - "Cannot Run" indicator (if player ran from previous room)
  - "Potion Used" indicator (if a potion has already been used in current room)
  - Cards remaining in dungeon deck

### 5.2 Card Interaction
- **Selection Method**: Click/tap or drag-and-drop cards to perform actions
- **Action Buttons**:
  - "Run" button (when applicable)
  - Optional "Fight Barehanded" or "Fight with Weapon" buttons for clarity
- **Visual Feedback**:
  - Card highlighting to show valid actions
  - Animation for card effects (damage, healing, weapon equipping)
  - Clear indication of dulled weapon restrictions

### 5.3 Information Displays
- **Combat Log**: Recent actions and their effects
- **Tutorial/Help**: Rules explanation accessible during gameplay
- **Victory/Defeat Screens**: Clear indication of game outcome

## 6. Optional Enhanced Features

### 6.1 Core Enhancements
- **Save/Load**: Ability to save and resume games
- **Undo**: Option to undo the last card played (limited to current room)
- **Game Statistics**: Track games played, win ratio, average health remaining, etc.
- **Difficulty Settings**: Adjustable starting health, weapon dulling rules, etc.

### 6.2 Presentation Enhancements
- **Visual Themes**: Multiple card and background themes (fantasy, sci-fi, medieval, etc.)
- **Sound Effects**: Card draw/play, combat, healing, victory/defeat
- **Music**: Background soundtrack with options to enable/disable
- **Animations**: Card movement, combat effects, health changes

### 6.3 Extended Gameplay
- **Custom Rules**: Toggleable rule variations
- **Challenge Modes**: Predefined setups with special rules or limitations
- **Achievements**: Milestone rewards for special accomplishments

## 7. Technical Specifications

### 7.1 Data Structures
- **Card**: { suit, value, type }
- **Weapon**: { value, lastMonsterDefeated }
- **Room**: Array of 4 Cards
- **GameState**: { playerHealth, equippedWeapon, currentRoom, dungeon, discard, ranLastRoom, potionUsedThisRoom }

### 7.2 Key Functions
- **dealRoom()**: Deal 4 cards to form a new room
- **playCard(card, action)**: Handle card effect based on chosen action
- **runFromRoom()**: Handle running mechanic
- **checkGameEnd()**: Check for victory or defeat conditions
- **calculateDamage(monsterValue, weaponValue)**: Calculate damage taken from combat

### 7.3 Save Game Format
- JSON structure containing full game state for save/load functionality

## 8. Testing Requirements
- Unit tests for core mechanics (damage calculation, weapon dulling, etc.)
- Game flow tests to ensure proper room progression and win/loss conditions
- Edge case testing (empty deck, running rules, etc.)
- UI responsiveness and interaction testing

## 9. Implementation Timeline
- **Phase 1**: Core game mechanics and basic UI
- **Phase 2**: Enhanced UI, animations, and sound
- **Phase 3**: Optional features, polish, and final testing

## 10. Credits
The implementation should include proper attribution to the original game designers:
- Game design by Zach Gage and Kurt Bieg (2011)
