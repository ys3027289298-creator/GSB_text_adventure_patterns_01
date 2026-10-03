#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Command chain (Chain of Responsibility) and command factory.

Raw player input travels along a chain of handlers. The first handler
that recognises the input executes it and the chain stops there
(short-circuit): no downstream handler may fire for the same input.

Command objects are created by the `CommandFactory`, which maps a
normalised command name to exactly one command class. Unknown names
always produce an `UnknownCommand`, never a look-alike command.
"""

from .events import EventBus
from .player_input import parse_input


class GameContext:
    "Shared state commands act upon."

    def __init__(self, bus=None, location=None):
        self.bus = bus if bus is not None else EventBus()
        self.location = location


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

class Command:
    "Base command. Subclasses implement `execute`."

    name = ""

    def __init__(self, *args):
        self.args = args

    def execute(self, context):
        raise NotImplementedError


class MoveToCommand(Command):
    name = "move_to"

    def execute(self, context):
        destination = self.args[0] if self.args else ""
        context.bus.publish("command.move_to", destination=destination)
        if destination:
            context.location = destination
            context.bus.publish("player_moved", destination=destination)
        return destination


class LookCommand(Command):
    name = "look"

    def execute(self, context):
        context.bus.publish("command.look")
        context.bus.publish("location_described", location=context.location)
        return context.location


class QuitCommand(Command):
    name = "quit"

    def execute(self, context):
        context.bus.publish("command.quit")
        context.bus.publish("game_over")
        return True


class UnknownCommand(Command):
    name = "unknown"

    def __init__(self, unknown_name="", *args):
        super().__init__(*args)
        self.unknown_name = unknown_name

    def execute(self, context):
        context.bus.publish("command.unknown", command=self.unknown_name)
        return None


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

class CommandFactory:
    """Create the right command object for a command name.

    The lookup is an exact match on the normalised (stripped, lowercased)
    name: partial or substring matches must never produce a command the
    player did not ask for.
    """

    def __init__(self):
        self._registry = {}
        for command_class in (MoveToCommand, LookCommand, QuitCommand):
            self.register(command_class.name, command_class)
        # "exit" is an alias for quitting the game.
        self.register("exit", QuitCommand)

    def register(self, name, command_class):
        self._registry[self.normalize(name)] = command_class

    @staticmethod
    def normalize(name):
        return name.strip().lower()

    def create(self, name, *args):
        command_class = self._registry.get(self.normalize(name))
        if command_class is None:
            return UnknownCommand(name, *args)
        return command_class(*args)


# ---------------------------------------------------------------------------
# Chain of responsibility
# ---------------------------------------------------------------------------

class CommandHandler:
    """Base handler of the command chain.

    `handle` short-circuits: as soon as one handler matches, the request
    is executed and never forwarded down the chain.
    """

    def __init__(self, successor=None, factory=None):
        self.successor = successor
        self.factory = factory if factory is not None else CommandFactory()

    def handle(self, line, context):
        if self.matches(line):
            return self.execute(line, context)
        if self.successor is not None:
            return self.successor.handle(line, context)
        return None

    def matches(self, line):
        raise NotImplementedError

    def execute(self, line, context):
        command_name, *args = parse_input(line)
        command = self.factory.create(command_name, *args)
        return command.execute(context)


class MoveToHandler(CommandHandler):
    def matches(self, line):
        return parse_input(line)[0] == "move_to"


class LookHandler(CommandHandler):
    def matches(self, line):
        return parse_input(line)[0] == "look"


class QuitHandler(CommandHandler):
    def matches(self, line):
        return parse_input(line)[0] in ("quit", "exit")


class UnknownHandler(CommandHandler):
    "Terminal handler: matches everything, so the chain never falls off."

    def matches(self, line):
        return True


def build_command_chain(factory=None):
    "Build the default command chain: move_to -> look -> quit -> unknown."
    factory = factory if factory is not None else CommandFactory()
    unknown = UnknownHandler(factory=factory)
    quit_ = QuitHandler(successor=unknown, factory=factory)
    look = LookHandler(successor=quit_, factory=factory)
    move_to = MoveToHandler(successor=look, factory=factory)
    return move_to
