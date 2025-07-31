class CommandResult:
    def __init__(self, handled, abort=False, message=None):
        self.handled = handled
        self.abort = abort
        self.message = message

def handle_cancel(orchestrator):
    orchestrator.reset()
    return CommandResult(handled=True, abort=True, message="SAM: Current task and follow-ups have been cancelled.")

def handle_shutdown():
    print("SAM: Shutting down. Goodbye!")
    exit(0)

def handle_increase_volume():
    # Placeholder for actual volume logic
    return CommandResult(handled=True, abort=False, message="SAM: I have increased the volume to 7.")

def handle_decrease_volume():
    # Placeholder for actual volume logic
    return CommandResult(handled=True, abort=False, message="SAM: I have decreased the volume to 3.") 