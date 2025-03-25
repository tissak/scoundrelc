"""
Special tests for the weapon mechanics.
"""
import unittest
from scoundrelc.game.game import GameState
from scoundrelc.game.card import Card, Suit, CardType, Weapon


class TestWeaponMechanics(unittest.TestCase):
    """Test cases specifically for weapon mechanics."""

    def test_weapon_first_use_any_monster(self):
        """Test that a weapon on first use can defeat any monster, regardless of value."""
        game = GameState()
        
        # Equip a weak weapon (2)
        weapon_card = Card(Suit.DIAMONDS, 2)
        game.equipped_weapon = Weapon(weapon_card)
        
        # Create a powerful monster (Ace = 14)
        monster = Card(Suit.CLUBS, 14)
        
        # Weapon should be able to defeat the monster (first use)
        self.assertTrue(game.equipped_weapon.can_defeat(monster))
        
        # Player should take reduced damage (14-2=12)
        initial_health = game.player_health
        game._handle_monster(monster)
        self.assertEqual(game.player_health, initial_health - 12)
        
        # Weapon should now have a "last monster defeated" value of 14 (Ace)
        self.assertEqual(game.equipped_weapon.last_monster_defeated, monster)

    def test_weapon_subsequent_restriction(self):
        """Test that a weapon can only defeat weaker monsters after first use."""
        game = GameState()
        
        # Equip a weapon (7)
        weapon_card = Card(Suit.DIAMONDS, 7)
        game.equipped_weapon = Weapon(weapon_card)
        
        # First defeat a monster of value 10
        first_monster = Card(Suit.CLUBS, 10)
        game.equipped_weapon.last_monster_defeated = first_monster
        
        # Now try to defeat a stronger monster (J=11)
        stronger_monster = Card(Suit.SPADES, 11)
        
        # Weapon should not be able to defeat the stronger monster
        self.assertFalse(game.equipped_weapon.can_defeat(stronger_monster))
        
        # Player should take full damage if fighting anyway
        initial_health = game.player_health
        game._handle_monster(stronger_monster, use_weapon=True)  # Try to use weapon
        self.assertEqual(game.player_health, initial_health - 11)  # Should take full 11 damage
        
        # Weapon's last monster defeated should still be the original monster (10)
        self.assertEqual(game.equipped_weapon.last_monster_defeated, first_monster)

    def test_weapon_subsequent_success(self):
        """Test that a weapon can defeat a weaker monster after first use."""
        game = GameState()
        
        # Equip a weapon (9)
        weapon_card = Card(Suit.DIAMONDS, 9)
        game.equipped_weapon = Weapon(weapon_card)
        
        # First defeat a monster of value 10
        first_monster = Card(Suit.CLUBS, 10)
        game.equipped_weapon.last_monster_defeated = first_monster
        
        # Now try to defeat a weaker monster (8)
        weaker_monster = Card(Suit.SPADES, 8)
        
        # Weapon should be able to defeat the weaker monster
        self.assertTrue(game.equipped_weapon.can_defeat(weaker_monster))
        
        # Player should take reduced damage (8-9=0)
        initial_health = game.player_health
        game._handle_monster(weaker_monster, use_weapon=True)
        self.assertEqual(game.player_health, initial_health)  # Should take 0 damage
        
        # Weapon's last monster defeated should now be the weaker monster (8)
        self.assertEqual(game.equipped_weapon.last_monster_defeated, weaker_monster)

    def test_weapon_equal_value_monster(self):
        """Test that a weapon cannot defeat a monster of equal value after first use."""
        game = GameState()
        
        # Equip a weapon (7)
        weapon_card = Card(Suit.DIAMONDS, 7)
        game.equipped_weapon = Weapon(weapon_card)
        
        # First defeat a monster of value 7
        first_monster = Card(Suit.CLUBS, 7)
        game.equipped_weapon.last_monster_defeated = first_monster
        
        # Now try to defeat another monster of value 7
        equal_monster = Card(Suit.SPADES, 7)
        
        # Weapon should not be able to defeat the equal value monster
        self.assertFalse(game.equipped_weapon.can_defeat(equal_monster))
        
        # Player should take full damage if fighting anyway
        initial_health = game.player_health
        game._handle_monster(equal_monster, use_weapon=True)  # Try to use weapon
        self.assertEqual(game.player_health, initial_health - 7)  # Should take full 7 damage

    def test_barehanded_option_preserves_weapon(self):
        """Test that fighting barehanded preserves weapon effectiveness."""
        game = GameState()
        
        # Equip a weapon (8)
        weapon_card = Card(Suit.DIAMONDS, 8)
        game.equipped_weapon = Weapon(weapon_card)
        
        # First defeat a monster of value 5 with the weapon
        first_monster = Card(Suit.CLUBS, 5)
        game._handle_monster(first_monster, use_weapon=True)
        
        # Weapon's last monster defeated should be value 5
        self.assertEqual(game.equipped_weapon.last_monster_defeated, first_monster)
        
        # Now fight another monster barehanded
        second_monster = Card(Suit.SPADES, 7)
        game._handle_monster(second_monster, use_weapon=False)
        
        # Weapon's last monster defeated should still be the first monster (5)
        self.assertEqual(game.equipped_weapon.last_monster_defeated, first_monster)
        
        # Now try to defeat a stronger monster (6) with the weapon
        stronger_monster = Card(Suit.CLUBS, 6)
        
        # Weapon should NOT be able to defeat the stronger monster
        self.assertFalse(game.equipped_weapon.can_defeat(stronger_monster))
        
        # Try to defeat a weaker monster (4) with the weapon
        weaker_monster = Card(Suit.SPADES, 4)
        
        # Weapon should be able to defeat the weaker monster
        self.assertTrue(game.equipped_weapon.can_defeat(weaker_monster))


if __name__ == '__main__':
    unittest.main()