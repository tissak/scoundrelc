"""
Game implementation for Scoundrel.
"""
import random
from typing import List, Optional, Tuple

from .card import Card, CardType, Deck, Weapon


class GameState:
    """Represents the current state of a Scoundrel game."""
    
    def __init__(self):
        self.player_health: int = 20
        self.max_health: int = 20
        self.equipped_weapon: Optional[Weapon] = None
        self.current_room: List[Card] = []
        self.dungeon: List[Card] = []
        self.discard: List[Card] = []
        self.ran_last_room: bool = False
        self.potion_used_this_room: bool = False
        self.game_over: bool = False
        self.victory: bool = False
        self.cards_played_this_room: int = 0
        
        # Initialize the dungeon
        self._setup_dungeon()
        
        # Deal the first room
        self.deal_room()
    
    def _setup_dungeon(self):
        """Set up the dungeon deck by creating and shuffling the cards."""
        deck = Deck()
        self.dungeon = deck.cards.copy()
        random.shuffle(self.dungeon)
    
    def deal_room(self):
        """Deal 4 cards to form a new room. Keep one card from previous room if available."""
        # Reset room state
        self.potion_used_this_room = False
        self.cards_played_this_room = 0
        
        # If this is not the first room, keep one card
        kept_card = None
        if self.current_room:
            kept_card = self.current_room[0]
            self.current_room = []
        
        # Add the kept card if there was one
        if kept_card:
            self.current_room.append(kept_card)
        
        # Deal cards until we have 4 in the room
        cards_to_deal = 4 - len(self.current_room)
        if cards_to_deal > len(self.dungeon):
            # Not enough cards left in the dungeon
            self.current_room.extend(self.dungeon)
            self.dungeon = []
            self._check_victory()
        else:
            for _ in range(cards_to_deal):
                self.current_room.append(self.dungeon.pop(0))
    
    def run_from_room(self) -> bool:
        """Handle running mechanic. Return False if running is not allowed."""
        if self.ran_last_room:
            return False
        
        if self.cards_played_this_room > 0:
            return False
        
        # Put current room cards at the bottom of the dungeon
        self.dungeon.extend(self.current_room)
        self.current_room = []
        
        # Set ran_last_room flag
        self.ran_last_room = True
        
        # Deal a new room
        self.deal_room()
        
        return True
    
    def play_card(self, card_index: int, use_weapon: bool = True) -> Tuple[str, bool]:
        """
        Play a card from the room.
        
        Args:
            card_index: The index of the card to play
            use_weapon: Whether to use the equipped weapon when fighting a monster
        
        Returns:
        - A message describing the result
        - A boolean indicating whether the action was successful
        """
        if card_index < 0 or card_index >= len(self.current_room):
            return "Invalid card index.", False
        
        card = self.current_room[card_index]
        message = ""
        
        # Process the card based on its type
        if card.type == CardType.MONSTER:
            message = self._handle_monster(card, use_weapon)
        elif card.type == CardType.WEAPON:
            message = self._handle_weapon(card)
        elif card.type == CardType.POTION:
            message = self._handle_potion(card)
        
        # Remove the card from the room and add to discard
        self.current_room.pop(card_index)
        self.discard.append(card)
        
        # Increment cards played this room
        self.cards_played_this_room += 1
        
        # Check if we need to deal a new room
        if self.cards_played_this_room >= 3 and len(self.current_room) == 1:
            self.ran_last_room = False  # Reset the ran_last_room flag
            self.deal_room()
            message += " You enter a new room."
        
        return message, True
    
    def _handle_monster(self, monster: Card, use_weapon: bool = True) -> str:
        """
        Handle interaction with a monster card.
        
        Args:
            monster: The monster card to handle
            use_weapon: Whether to use the equipped weapon (if available)
        
        Returns a message describing the result.
        """
        weapon_value = 0
        can_use_weapon = False
        
        # Check if we have a weapon and can use it
        if self.equipped_weapon and use_weapon:
            weapon_value = self.equipped_weapon.value
            can_use_weapon = self.equipped_weapon.can_defeat(monster)
        
        # Calculate damage
        damage = monster.value
        weapon_used = False
        
        if can_use_weapon:
            damage = max(0, monster.value - weapon_value)
            weapon_used = True
            # Update the last monster defeated with this weapon
            self.equipped_weapon.last_monster_defeated = monster
        
        # Apply damage
        self.player_health -= damage
        
        # Check for game over
        if self.player_health <= 0:
            self.game_over = True
            self.victory = False
            
            if weapon_used:
                return f"You fought {monster} with your {self.equipped_weapon.card}. " \
                       f"You took {damage} damage and were defeated!"
            else:
                return f"You fought {monster} barehanded. " \
                       f"You took {damage} damage and were defeated!"
        
        if weapon_used:
            return f"You fought {monster} with your {self.equipped_weapon.card}. " \
                   f"You took {damage} damage."
        else:
            return f"You fought {monster} barehanded. You took {damage} damage."
    
    def _handle_weapon(self, weapon_card: Card) -> str:
        """
        Handle interaction with a weapon card.
        
        Returns a message describing the result.
        """
        # Equip the weapon
        self.equipped_weapon = Weapon(weapon_card)
        
        return f"You equipped {weapon_card} as your weapon."
    
    def _handle_potion(self, potion: Card) -> str:
        """
        Handle interaction with a potion card.
        
        Returns a message describing the result.
        """
        # Check if a potion has already been used this room
        if self.potion_used_this_room:
            return f"You drank {potion}, but it had no effect since you already used a potion this room."
        
        # Use the potion to heal
        healing = potion.value
        old_health = self.player_health
        self.player_health = min(self.max_health, self.player_health + healing)
        actual_healing = self.player_health - old_health
        
        # Mark that a potion has been used this room
        self.potion_used_this_room = True
        
        return f"You drank {potion} and healed {actual_healing} health."
    
    def _check_victory(self):
        """Check for victory condition (all monster cards defeated)."""
        # Check if any monster cards remain in the dungeon
        for card in self.dungeon:
            if card.type == CardType.MONSTER:
                return
        
        # If no monster cards remain in the dungeon, check the current room
        for card in self.current_room:
            if card.type == CardType.MONSTER:
                return
                
        # No monster cards remain, player wins
        self.game_over = True
        self.victory = True
    
    def get_remaining_monster_count(self) -> int:
        """Get the count of remaining monster cards in the game."""
        count = 0
        
        # Count monsters in the dungeon
        for card in self.dungeon:
            if card.type == CardType.MONSTER:
                count += 1
        
        # Count monsters in the current room
        for card in self.current_room:
            if card.type == CardType.MONSTER:
                count += 1
                
        return count