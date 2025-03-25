"""
Terminal UI implementation for Scoundrel using Textual.
"""
from typing import List, Dict, Any
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Static, Label, Footer, Header, OptionList
from textual.reactive import reactive
from textual.binding import Binding
from textual import events
from textual.widgets.option_list import Option
from rich.text import Text
from rich.console import RenderableType
from rich.panel import Panel

from ..game.game import GameState
from ..game.card import Card, CardType


class CardWidget(Button):
    """A widget that displays a card."""
    
    def __init__(self, card: Card, index: int, **kwargs):
        self.card = card
        self.index = index
        
        # Set card classes based on card type
        if card.type == CardType.MONSTER:
            if card.suit.value == "♣":  # Clubs
                style = "card monster"
            else:  # Spades
                style = "card monster"
        elif card.type == CardType.WEAPON:
            style = "card weapon"
        else:  # Potion
            style = "card potion"
        
        super().__init__(str(card), id=f"card_{index}", classes=style, **kwargs)


class RoomDisplay(Container):
    """A widget that displays the current room."""
    
    def __init__(self, game_state: GameState, **kwargs):
        super().__init__(**kwargs)
        self.game_state = game_state
    
    def compose(self) -> ComposeResult:
        """Compose the card widgets."""
        with Horizontal(id="room_cards"):
            for i, card in enumerate(self.game_state.current_room):
                yield CardWidget(card, i)


class StatusDisplay(Container):
    """A widget that displays the player's status."""
    
    def __init__(self, game_state: GameState, **kwargs):
        super().__init__(**kwargs)
        self.game_state = game_state
    
    def compose(self) -> ComposeResult:
        """Compose the status display."""
        yield Label(id="health_display", classes="status_item")
        yield Label(id="weapon_display", classes="status_item")
        yield Label(id="room_status", classes="status_item")
        yield Label(id="monsters_left", classes="status_item")
    
    def update_status(self):
        """Update all status displays."""
        # Update health display
        health_text = f"Health: {self.game_state.player_health}/{self.game_state.max_health}"
        self.query_one("#health_display", Label).update(health_text)
        
        # Update weapon display
        if self.game_state.equipped_weapon:
            weapon = self.game_state.equipped_weapon
            if weapon.last_monster_defeated:
                weapon_text = f"Weapon: {weapon.card} (can only defeat monsters < {weapon.last_monster_defeated.value})"
            else:
                weapon_text = f"Weapon: {weapon.card} (can defeat any monster)"
        else:
            weapon_text = "Weapon: None"
        self.query_one("#weapon_display", Label).update(weapon_text)
        
        # Update room status display
        status_items = []
        if self.game_state.ran_last_room:
            status_items.append("Cannot Run")
        if self.game_state.potion_used_this_room:
            status_items.append("Potion Used")
        
        status_text = f"Status: {', '.join(status_items) if status_items else 'None'}"
        self.query_one("#room_status", Label).update(status_text)
        
        # Update monsters left display
        monsters_left = self.game_state.get_remaining_monster_count()
        monsters_text = f"Monsters Left: {monsters_left}"
        self.query_one("#monsters_left", Label).update(monsters_text)


class MessageLog(Static):
    """A widget that displays game messages."""
    
    messages: reactive[List[str]] = reactive([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.messages = []
    
    def add_message(self, message: str):
        """Add a message to the log."""
        self.messages.append(message)
        # Keep only the last 5 messages
        if len(self.messages) > 5:
            self.messages = self.messages[-5:]
    
    def render(self) -> RenderableType:
        """Render the message log."""
        message_text = "\n".join(self.messages)
        return Panel(message_text, title="Message Log", border_style="blue")


class ScoundrelApp(App):
    """The main Scoundrel application."""
    
    CSS = """
    Screen {
        background: #1e1e2e;
        color: #cdd6f4;
    }
    
    #game_container {
        width: 100%;
        height: 100%;
        padding: 1;
    }
    
    #room_display {
        height: 10;
        margin-bottom: 1;
    }
    
    #room_cards {
        align: center middle;
        height: 100%;
    }
    
    .card {
        width: 10;
        height: 6;
        margin: 0 1;
        border: tall;
        text-align: center;
        content-align: center middle;
        padding: 0;
    }
    
    .monster {
        border: double green;
    }
    
    .weapon {
        border: dashed yellow;
    }
    
    .potion {
        border: solid red;
    }
    
    #status_display {
        height: 4;
        margin-bottom: 1;
    }
    
    .status_item {
        margin-right: 2;
        height: 1;
    }
    
    #message_log {
        height: 6;
        margin-bottom: 1;
    }
    
    #controls {
        height: 3;
    }
    
    Button {
        margin: 0 1;
    }
    
    Button.run {
        background: #f38ba8;
        color: #1e1e2e;
    }
    
    Button.game_over {
        background: #cba6f7;
        color: #1e1e2e;
    }
    
    /* Combat dialog styling */
    .dialog {
        width: 60%;
        height: auto;
        border: solid white;
        background: #313244;
        margin: 2 2;
        padding: 1;
        align: center top;
        dock: top;
        offset-y: 25%; /* Position dialog at 25% from top of screen */
        layer: overlay; /* Make dialog appear above other content */
    }
    
    #combat_title {
        text-align: center;
        margin-bottom: 1;
    }
    
    #combat_options {
        width: 100%;
        height: auto;
        padding: 1;
    }
    """
    
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit"),
        Binding(key="r", action="run", description="Run"),
        Binding(key="n", action="new_game", description="New Game"),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_state = GameState()
    
    def compose(self) -> ComposeResult:
        """Compose the application UI."""
        yield Header(show_clock=True)
        
        with Container(id="game_container"):
            # Room display - create an empty container for the room
            yield Container(id="room_display")
            
            # Status display
            yield StatusDisplay(self.game_state, id="status_display")
            
            # Message log
            yield MessageLog(id="message_log")
            
            # Controls
            with Horizontal(id="controls"):
                yield Button("Run", id="run_button", classes="run")
                yield Button("New Game", id="new_game_button")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Event handler called when the app is mounted."""
        self.update_ui()
    
    def update_ui(self):
        """Update all UI elements."""
        # Re-render the room - clear and create a new room display with a dynamic ID
        room_container = self.query_one("#room_display")
        room_container.remove_children()  # Clear any existing children first
        
        # Create a unique ID for the room display using timestamp
        import time
        unique_id = f"room_{int(time.time() * 1000)}"
        room_container.mount(RoomDisplay(self.game_state, id=unique_id))
        
        # Update status display
        self.query_one(StatusDisplay).update_status()
        
        # Update run button state
        run_button = self.query_one("#run_button", Button)
        if self.game_state.ran_last_room or self.game_state.cards_played_this_room > 0:
            run_button.disabled = True
        else:
            run_button.disabled = False
        
        # Check for game over
        if self.game_state.game_over:
            self.show_game_over()
    
    def show_game_over(self):
        """Display the game over screen."""
        # Clear the room
        room_container = self.query_one("#room_display")
        room_container.remove_children()
        
        # Display game over message
        message = "Victory! You've defeated all monsters!" if self.game_state.victory else "Game Over! You were defeated!"
        
        # Use a unique ID for the game over message
        import time
        unique_id = f"game_over_message_{int(time.time() * 1000)}"
        room_container.mount(Label(message, id=unique_id))
        
        # Disable run button
        self.query_one("#run_button", Button).disabled = True
            
    def show_combat_options(self, card_index: int) -> None:
        """Show a combat options dialog for fighting a monster."""
        # First, remove any existing combat dialog
        try:
            existing_dialog = self.query_one("#combat_dialog")
            if existing_dialog:
                existing_dialog.remove()
        except Exception:
            pass  # No dialog exists yet
        
        # Store the card index for later use
        self._combat_card_index = card_index
        monster = self.game_state.current_room[card_index]
        weapon = self.game_state.equipped_weapon
        
        # Calculate potential damages
        monster_value = monster.value
        weapon_value = weapon.value if weapon else 0
        weapon_damage = max(0, monster_value - weapon_value)
        barehanded_damage = monster_value
        
        # Check if weapon can defeat the monster
        can_use_weapon = False
        if weapon:
            can_use_weapon = weapon.can_defeat(monster)
        
        # Generate a unique ID using timestamp to avoid conflicts
        import time
        unique_id = f"combat_dialog_{int(time.time() * 1000)}"
        
        # First mount the container to the app - mount to main container for proper positioning
        with self.batch_update():
            # Create and mount the dialog container with unique ID
            combat_dialog = Container(id=unique_id, classes="dialog")
            
            # Mount to game_container instead of the app root to ensure proper positioning
            game_container = self.query_one("#game_container")
            game_container.mount(combat_dialog)
            
            # Now we can add widgets to the mounted container
            # Add a title to the dialog
            combat_title = Label(f"Combat Options - {monster}", id=f"combat_title_{unique_id}")
            combat_dialog.mount(combat_title)
            
            # Create options list with options already in it
            options = OptionList(id=f"combat_options_{unique_id}")
            combat_dialog.mount(options)
            
            # Create a list to hold our options
            combat_options = []
            
            # Only add weapon option if the weapon can defeat the monster
            if can_use_weapon:
                use_weapon_option = Option(f"Use Weapon ({weapon.card}) - Take {weapon_damage} damage", id="use_weapon")
                combat_options.append(use_weapon_option)
            elif weapon:
                # If we have a weapon but can't use it, show it as disabled
                disabled_text = f"Cannot use Weapon ({weapon.card}) - Already defeated stronger monster"
                disabled_option = Option(disabled_text, id="weapon_disabled", disabled=True)
                combat_options.append(disabled_option)
            
            # Always add barehanded option
            barehanded_option = Option(f"Fight Barehanded - Take {barehanded_damage} damage", id="barehanded")
            combat_options.append(barehanded_option)
            
            # Add cancel option
            cancel_option = Option("Cancel", id="cancel")
            combat_options.append(cancel_option)
            
            # Add options after the list is mounted
            options.add_options(combat_options)
            
            # Save the dialog ID for later reference
            self._current_dialog_id = unique_id
            
            # Register handler for option selection
            options.focus()
    
    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle option selection for combat dialog."""
        option_id = event.option.id
        
        # Remove the dialog using the saved unique ID
        try:
            # Use the stored dialog ID from show_combat_options
            if hasattr(self, '_current_dialog_id'):
                dialog_id = self._current_dialog_id
                # Find dialog within game_container
                game_container = self.query_one("#game_container")
                dialog = game_container.query_one(f"#{dialog_id}")
                if dialog:
                    dialog.remove()
        except Exception:
            pass
        
        # Process the selected option
        if option_id == "use_weapon":
            self.play_card(self._combat_card_index, use_weapon=True)
        elif option_id == "barehanded":
            self.play_card(self._combat_card_index, use_weapon=False)
        elif option_id == "cancel":
            # Do nothing, just close the dialog
            message_log = self.query_one(MessageLog)
            message_log.add_message("Combat canceled.")
        # Ignore weapon_disabled option as it's just informational
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        button_id = event.button.id
        
        if button_id == "run_button":
            self.action_run()
        elif button_id == "new_game_button":
            self.action_new_game()
        elif button_id and button_id.startswith("card_"):
            # Extract the card index from the button id
            card_index = int(button_id.split("_")[1])
            
            # If this is a monster card, ask if they want to use weapon
            card = self.game_state.current_room[card_index]
            from ..game.card import CardType
            
            if card.type == CardType.MONSTER and self.game_state.equipped_weapon:
                # Show combat options dialog
                self.show_combat_options(card_index)
            else:
                # Play card normally
                self.play_card(card_index)
    
    def action_run(self) -> None:
        """Run action handler."""
        if not self.game_state.game_over:
            success = self.game_state.run_from_room()
            if success:
                message_log = self.query_one(MessageLog)
                message_log.add_message("You ran away from the room!")
                self.update_ui()
            else:
                message_log = self.query_one(MessageLog)
                message_log.add_message("You cannot run at this time!")
    
    def action_new_game(self) -> None:
        """New game action handler."""
        self.game_state = GameState()
        message_log = self.query_one(MessageLog)
        message_log.messages = []
        message_log.add_message("New game started!")
        self.update_ui()
    
    def play_card(self, card_index: int, use_weapon: bool = True) -> None:
        """
        Play a card from the room.
        
        Args:
            card_index: Index of the card to play
            use_weapon: Whether to use weapon when fighting a monster
        """
        if not self.game_state.game_over:
            message, success = self.game_state.play_card(card_index, use_weapon)
            if success:
                message_log = self.query_one(MessageLog)
                message_log.add_message(message)
                self.update_ui()