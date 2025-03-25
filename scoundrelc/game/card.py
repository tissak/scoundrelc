"""
Card implementation for Scoundrel.
"""
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional


class Suit(Enum):
    CLUBS = "♣"    # Monsters
    SPADES = "♠"   # Monsters
    DIAMONDS = "♦" # Weapons
    HEARTS = "♥"   # Health potions


class CardType(Enum):
    MONSTER = "Monster"
    WEAPON = "Weapon"
    POTION = "Potion"


@dataclass
class Card:
    suit: Suit
    value: int
    
    @property
    def type(self) -> CardType:
        if self.suit in [Suit.CLUBS, Suit.SPADES]:
            return CardType.MONSTER
        elif self.suit == Suit.DIAMONDS:
            return CardType.WEAPON
        else:  # Hearts
            return CardType.POTION
    
    @property
    def name(self) -> str:
        # Convert number to face card name if applicable
        if self.value <= 10:
            card_name = str(self.value)
        elif self.value == 11:
            card_name = "J"
        elif self.value == 12:
            card_name = "Q"
        elif self.value == 13:
            card_name = "K"
        else:  # value == 14
            card_name = "A"
        
        return f"{card_name}{self.suit.value}"
    
    def __str__(self) -> str:
        return self.name


class Deck:
    def __init__(self):
        """Initialize a standard modified deck for Scoundrel."""
        self.cards: List[Card] = []
        self._build_deck()
    
    def _build_deck(self):
        """Build the Scoundrel deck (44 cards):
        - Complete set of clubs and spades (A-K)
        - Diamonds 2-10
        - Hearts 2-10
        """
        # Add clubs and spades (including face cards and aces)
        for suit in [Suit.CLUBS, Suit.SPADES]:
            for value in range(2, 15):  # 2-14 (Ace is 14)
                self.cards.append(Card(suit, value))
        
        # Add diamonds and hearts (2-10 only)
        for suit in [Suit.DIAMONDS, Suit.HEARTS]:
            for value in range(2, 11):  # 2-10
                self.cards.append(Card(suit, value))


@dataclass
class Weapon:
    """Represents an equipped weapon."""
    card: Card
    last_monster_defeated: Optional[Card] = None
    
    @property
    def value(self) -> int:
        return self.card.value
    
    def can_defeat(self, monster: Card) -> bool:
        """Check if this weapon can defeat the given monster."""
        if self.last_monster_defeated is None:
            # First use: can defeat any monster
            return True
        
        # Subsequent use: can only defeat monsters with value lower than last monster
        return monster.value < self.last_monster_defeated.value