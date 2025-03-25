"""
Tests for the card module functionality.
"""
import unittest
from scoundrelc.game.card import Card, Suit, CardType, Deck, Weapon


class TestCard(unittest.TestCase):
    """Test cases for the Card class."""
    
    def test_card_type(self):
        """Test that card types are correctly determined based on suit."""
        # Test monsters (clubs and spades)
        club_card = Card(Suit.CLUBS, 10)
        spade_card = Card(Suit.SPADES, 5)
        self.assertEqual(club_card.type, CardType.MONSTER)
        self.assertEqual(spade_card.type, CardType.MONSTER)
        
        # Test weapons (diamonds)
        diamond_card = Card(Suit.DIAMONDS, 8)
        self.assertEqual(diamond_card.type, CardType.WEAPON)
        
        # Test potions (hearts)
        heart_card = Card(Suit.HEARTS, 3)
        self.assertEqual(heart_card.type, CardType.POTION)
    
    def test_card_name(self):
        """Test that card names are correctly formatted."""
        # Test number cards
        number_card = Card(Suit.CLUBS, 7)
        self.assertEqual(number_card.name, "7♣")
        
        # Test face cards
        jack = Card(Suit.SPADES, 11)
        queen = Card(Suit.HEARTS, 12)
        king = Card(Suit.DIAMONDS, 13)
        ace = Card(Suit.CLUBS, 14)
        
        self.assertEqual(jack.name, "J♠")
        self.assertEqual(queen.name, "Q♥")
        self.assertEqual(king.name, "K♦")
        self.assertEqual(ace.name, "A♣")
    
    def test_card_string_representation(self):
        """Test that card string representation is correct."""
        card = Card(Suit.DIAMONDS, 10)
        self.assertEqual(str(card), "10♦")


class TestDeck(unittest.TestCase):
    """Test cases for the Deck class."""
    
    def test_deck_size(self):
        """Test that the deck has the correct number of cards."""
        deck = Deck()
        # The Scoundrel deck should have 44 cards
        self.assertEqual(len(deck.cards), 44)
    
    def test_deck_composition(self):
        """Test that the deck has the correct composition of cards."""
        deck = Deck()
        
        # Count cards by suit
        clubs = sum(1 for card in deck.cards if card.suit == Suit.CLUBS)
        spades = sum(1 for card in deck.cards if card.suit == Suit.SPADES)
        diamonds = sum(1 for card in deck.cards if card.suit == Suit.DIAMONDS)
        hearts = sum(1 for card in deck.cards if card.suit == Suit.HEARTS)
        
        # There should be 13 of each clubs and spades (2-A)
        self.assertEqual(clubs, 13)
        self.assertEqual(spades, 13)
        
        # There should be 9 of each diamonds and hearts (2-10)
        self.assertEqual(diamonds, 9)
        self.assertEqual(hearts, 9)
        
        # Verify no face cards in diamonds and hearts
        for card in deck.cards:
            if card.suit in [Suit.DIAMONDS, Suit.HEARTS]:
                self.assertTrue(2 <= card.value <= 10, 
                                f"Card {card} has invalid value for diamonds/hearts")


class TestWeapon(unittest.TestCase):
    """Test cases for the Weapon class."""
    
    def test_weapon_can_defeat_first_use(self):
        """Test that a weapon can defeat any monster on first use."""
        weapon_card = Card(Suit.DIAMONDS, 5)
        weapon = Weapon(weapon_card)
        
        # Weapon should be able to defeat any monster on first use
        weak_monster = Card(Suit.CLUBS, 3)
        strong_monster = Card(Suit.SPADES, 10)
        very_strong_monster = Card(Suit.CLUBS, 14)  # Ace
        
        self.assertTrue(weapon.can_defeat(weak_monster))
        self.assertTrue(weapon.can_defeat(strong_monster))
        self.assertTrue(weapon.can_defeat(very_strong_monster))
    
    def test_weapon_can_defeat_subsequent_use(self):
        """Test that a weapon can only defeat weaker monsters after first use."""
        weapon_card = Card(Suit.DIAMONDS, 8)
        weapon = Weapon(weapon_card)
        
        # First defeat a monster
        medium_monster = Card(Suit.CLUBS, 10)
        weapon.last_monster_defeated = medium_monster
        
        # Now the weapon should only be able to defeat monsters weaker than value 10
        weak_monster = Card(Suit.SPADES, 9)
        equal_monster = Card(Suit.CLUBS, 10)
        strong_monster = Card(Suit.SPADES, 11)
        
        self.assertTrue(weapon.can_defeat(weak_monster))
        self.assertFalse(weapon.can_defeat(equal_monster))
        self.assertFalse(weapon.can_defeat(strong_monster))


if __name__ == '__main__':
    unittest.main()