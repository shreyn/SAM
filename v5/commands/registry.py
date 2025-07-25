from .handlers import handle_cancel, handle_shutdown, handle_increase_volume, handle_decrease_volume

COMMANDS = {
    "sam cancel": {"handler": handle_cancel, "interrupting": True},
    "sam reset": {"handler": handle_cancel, "interrupting": True},
    "sam shut down": {"handler": handle_shutdown, "interrupting": True},
    "sam deactivate": {"handler": handle_shutdown, "interrupting": True},
    "sam increase volume": {"handler": handle_increase_volume, "interrupting": False},
    "sam decrease volume": {"handler": handle_decrease_volume, "interrupting": False},
}

def get_command_handler(user_input):
    normalized = user_input.strip().lower()
    return COMMANDS.get(normalized) 