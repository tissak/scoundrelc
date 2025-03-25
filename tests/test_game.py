"""
Tests for the game module functionality.
"""
import unittest
from unittest.mock import patch, MagicMock
from scoundrelc.game.game import GameState
from scoundrelc.game.card import Card, Suit, CardType, Weapon


class TestGameState(unittest.TestCase):
    """Test cases for the GameState class."""

    def test_init(self):
        """Test that the game state is initialized correctly."""
        game = GameState()
        
        # Check initial player state
        self.assertEqual(game.player_health, 20)
        self.assertEqual(game.max_health, 20)
        self.assertIsNone(game.equipped_weapon)
        
        # Check room setup
        self.assertEqual(len(game.current_room), 4)
        
        # Check flags
        self.assertFalse(game.ran_last_room)
        self.assertFalse(game.potion_used_this_room)
        self.assertFalse(game.game_over)
        self.assertFalse(game.victory)
        self.assertEqual(game.cards_played_this_room, 0)

    @patch('random.shuffle')
    def test_setup_dungeon(self, mock_shuffle):
        """Test that the dungeon is set up correctly."""
        game = GameState()
        
        # The dungeon should have 40 cards (44 total - 4 in the room)
        self.assertEqual(len(game.dungeon), 40)
        
        # Verify random.shuffle was called
        mock_shuffle.assert_called_once()

    def test_deal_room(self):
        """Test dealing a new room."""
        game = GameState()
        
        # Clear the current room and dungeon
        game.current_room = []
        game.dungeon = [
            Card(Suit.CLUBS, 2), Card(Suit.SPADES, 3), 
            Card(Suit.DIAMONDS, 4), Card(Suit.HEARTS, 5)
        ]
        
        # Deal a new room
        game.deal_room()
        
        # The room should have 4 cards
        self.assertEqual(len(game.current_room), 4)
        
        # The dungeon should be empty
        self.assertEqual(len(game.dungeon), 0)
        
        # Room flags should be reset
        self.assertFalse(game.potion_used_this_room)
        self.assertEqual(game.cards_played_this_room, 0)

    def test_deal_room_with_kept_card(self):
        """Test dealing a new room while keeping one card."""
        game = GameState()
        
        # Set up a current room with one card
        kept_card = Card(Suit.DIAMONDS, 10)
        game.current_room = [kept_card]
        
        # Set up the dungeon with 3 cards
        game.dungeon = [
            Card(Suit.CLUBS, 2), Card(Suit.SPADES, 3), Card(Suit.HEARTS, 5)
        ]
        
        # Deal a new room
        game.deal_room()
        
        # The room should have 4 cards
        self.assertEqual(len(game.current_room), 4)
        
        # The first card should be the kept card
        self.assertEqual(game.current_room[0], kept_card)
        
        # The dungeon should be empty
        self.assertEqual(len(game.dungeon), 0)

    def test_run_from_room(self):
        """Test running from a room."""
        game = GameState()
        original_room = game.current_room.copy()
        
        # Run from the room
        success = game.run_from_room()
        
        # Running should succeed
        self.assertTrue(success)
        
        # The ran_last_room flag should be set
        self.assertTrue(game.ran_last_room)
        
        # The original room cards should be at the end of the dungeon
        for card in original_room:
            self.assertIn(card, game.dungeon)
        
        # A new room should be dealt
        self.assertEqual(len(game.current_room), 4)

    def test_run_from_room_not_allowed(self):
        """Test running from a room when not allowed."""
        game = GameState()
        
        # Set up conditions where running is not allowed
        game.ran_last_room = True
        original_room = game.current_room.copy()
        
        # Try to run from the room
        success = game.run_from_room()
        
        # Running should fail
        self.assertFalse(success)
        
        # The room should remain unchanged
        self.assertEqual(game.current_room, original_room)
        
        # Test when cards have been played
        game.ran_last_room = False
        game.cards_played_this_room = 1
        
        # Try to run from the room
        success = game.run_from_room()
        
        # Running should fail
        self.assertFalse(success)

    def test_handle_monster_barehanded(self):
        """Test handling a monster encounter with no weapon."""
        game = GameState()
        
        # Create a monster card
        monster = Card(Suit.CLUBS, 5)
        
        # Handle the monster barehanded
        message = game._handle_monster(monster, use_weapon=False)
        
        # Player should take full damage
        self.assertEqual(game.player_health, 15)
        
        # Message should mention fighting barehanded
        self.assertIn("barehanded", message)
        self.assertIn("5 damage", message)

    def test_handle_monster_with_weapon(self):
        """Test handling a monster encounter with a weapon."""
        game = GameState()
        
        # Equip a weapon
        weapon_card = Card(Suit.DIAMONDS, 3)
        game.equipped_weapon = Weapon(weapon_card)
        
        # Create a monster card
        monster = Card(Suit.SPADES, 5)
        
        # Handle the monster with weapon
        message = game._handle_monster(monster)
        
        # Player should take reduced damage (5-3=2)
        self.assertEqual(game.player_health, 18)
        
        # Weapon should record last monster defeated
        self.assertEqual(game.equipped_weapon.last_monster_defeated, monster)
        
        # Message should mention the weapon
        self.assertIn("3♦", message)
        self.assertIn("2 damage", message)

    def test_handle_monster_game_over(self):
        """Test handling a monster encounter that leads to game over."""
        game = GameState()
        
        # Set player health low
        game.player_health = 5
        
        # Create a deadly monster
        monster = Card(Suit.CLUBS, 7)
        
        # Handle the monster barehanded
        message = game._handle_monster(monster)
        
        # Player should be defeated
        self.assertEqual(game.player_health, -2)
        self.assertTrue(game.game_over)
        self.assertFalse(game.victory)
        
        # Message should mention defeat
        self.assertIn("defeated", message)

    def test_handle_weapon(self):
        """Test handling a weapon card."""
        game = GameState()
        
        # Create a weapon card
        weapon_card = Card(Suit.DIAMONDS, 8)
        
        # Handle the weapon
        message = game._handle_weapon(weapon_card)
        
        # Weapon should be equipped
        self.assertIsNotNone(game.equipped_weapon)
        self.assertEqual(game.equipped_weapon.card, weapon_card)
        
        # Message should mention equipping
        self.assertIn("equipped", message)
        self.assertIn("8♦", message)

    def test_handle_potion(self):
        """Test handling a potion card."""
        game = GameState()
        
        # Set player health below max
        game.player_health = 15
        
        # Create a potion card
        potion_card = Card(Suit.HEARTS, 4)
        
        # Handle the potion
        message = game._handle_potion(potion_card)
        
        # Player should heal
        self.assertEqual(game.player_health, 19)
        
        # Potion used flag should be set
        self.assertTrue(game.potion_used_this_room)
        
        # Message should mention healing
        self.assertIn("healed 4", message)

    def test_handle_potion_at_max_health(self):
        """Test handling a potion card at max health."""
        game = GameState()
        
        # Player starts at max health (20)
        
        # Create a potion card
        potion_card = Card(Suit.HEARTS, 5)
        
        # Handle the potion
        message = game._handle_potion(potion_card)
        
        # Player should still be at max health
        self.assertEqual(game.player_health, 20)
        
        # Message should mention actual healing (0)
        self.assertIn("healed 0", message)

    def test_handle_potion_already_used(self):
        """Test handling a potion card when already used this room."""
        game = GameState()
        
        # Set player health below max
        game.player_health = 15
        
        # Set potion used flag
        game.potion_used_this_room = True
        
        # Create a potion card
        potion_card = Card(Suit.HEARTS, 3)
        
        # Handle the potion
        message = game._handle_potion(potion_card)
        
        # Player health should not change
        self.assertEqual(game.player_health, 15)
        
        # Message should mention no effect
        self.assertIn("no effect", message)

    def test_play_card(self):
        """Test playing a card from the room."""
        game = GameState()
        
        # Set up a controlled room
        monster_card = Card(Suit.CLUBS, 3)
        weapon_card = Card(Suit.DIAMONDS, 5)
        potion_card = Card(Suit.HEARTS, 4)
        game.current_room = [monster_card, weapon_card, potion_card, Card(Suit.SPADES, 2)]
        
        # Play the weapon card
        message, success = game.play_card(1)
        
        # Should succeed
        self.assertTrue(success)
        
        # Weapon should be equipped
        self.assertIsNotNone(game.equipped_weapon)
        self.assertEqual(game.equipped_weapon.card, weapon_card)
        
        # Room should have one less card
        self.assertEqual(len(game.current_room), 3)
        
        # Cards played counter should increment
        self.assertEqual(game.cards_played_this_room, 1)

    def test_check_victory(self):
        """Test the victory condition check."""
        game = GameState()
        
        # Set up a state with no monster cards left
        game.dungeon = [
            Card(Suit.DIAMONDS, 2), Card(Suit.DIAMONDS, 3), 
            Card(Suit.HEARTS, 4), Card(Suit.HEARTS, 5)
        ]
        game.current_room = [
            Card(Suit.DIAMONDS, 6), Card(Suit.DIAMONDS, 7), 
            Card(Suit.HEARTS, 8), Card(Suit.HEARTS, 9)
        ]
        
        # Check for victory
        game._check_victory()
        
        # Game should be over with victory
        self.assertTrue(game.game_over)
        self.assertTrue(game.victory)

    def test_get_remaining_monster_count(self):
        """Test counting remaining monsters."""
        game = GameState()
        
        # Set up a controlled state
        game.dungeon = [
            Card(Suit.CLUBS, 2), Card(Suit.SPADES, 3), 
            Card(Suit.DIAMONDS, 4), Card(Suit.HEARTS, 5)
        ]
        game.current_room = [
            Card(Suit.CLUBS, 6), Card(Suit.DIAMONDS, 7), 
            Card(Suit.HEARTS, 8), Card(Suit.SPADES, 9)
        ]
        
        # Count monsters
        count = game.get_remaining_monster_count()
        
        # Should be 4 monsters (2 in dungeon, 2 in room)
        self.assertEqual(count, 4)


if __name__ == '__main__':
    unittest.main()