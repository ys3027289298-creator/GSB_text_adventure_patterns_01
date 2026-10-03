#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Main game entry point."""

from .world import World
from .entity import MyCharacter
from .events import EventBus
from .commands import GameContext, build_command_chain


def run():
    "Run the game."
    world = World()

    # Instantiate your character here and add it to the world:
    character = MyCharacter("Dan")
    world.add_entity(character)

    # We advance the world 20 timesteps
    for step in range(20):
        world.update()


def game_loop(is_game_over, on_step=None):
    """Run the game loop until `is_game_over()` returns True.

    `on_step` is called once per iteration (after the end check) and
    typically processes one piece of player input.
    """
    while not is_game_over():
        if on_step is not None:
            on_step()


def process_input(line, context, chain=None):
    """Dispatch one raw input line through the command chain."""
    chain = chain if chain is not None else build_command_chain()
    return chain.handle(line, context)


def new_game(bus=None):
    """Build the interactive game context and its command chain."""
    bus = bus if bus is not None else EventBus()
    context = GameContext(bus=bus)
    chain = build_command_chain()
    return context, chain
