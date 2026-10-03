#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Insert `text_adventure` package to the sys.path so we don't need to
# install the package for testing.
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest

from text_adventure.events import EventBus
from text_adventure.commands import (
    CommandHandler,
    GameContext,
    build_command_chain,
)


class RecordingHandler(CommandHandler):
    """Spy handler recording whether it was consulted or executed."""

    def __init__(self, successor=None, factory=None, does_match=True):
        super().__init__(successor=successor, factory=factory)
        self.does_match = does_match
        self.consulted = []
        self.executed = []

    def matches(self, line):
        self.consulted.append(line)
        return self.does_match

    def execute(self, line, context):
        self.executed.append(line)
        return "handled"


def make_context():
    bus = EventBus()
    return GameContext(bus=bus), bus


def test_chain_short_circuits_at_first_matching_handler():
    tail = RecordingHandler(does_match=True)
    middle = RecordingHandler(successor=tail, does_match=True)
    head = RecordingHandler(successor=middle, does_match=True)

    result = head.handle("anything", context=None)

    assert result == "handled"
    # Head handled it: downstream handlers were never even consulted.
    assert head.executed == ["anything"]
    assert middle.consulted == []
    assert tail.consulted == []


def test_chain_forwards_until_a_handler_matches():
    tail = RecordingHandler(does_match=True)
    middle = RecordingHandler(successor=tail, does_match=False)
    head = RecordingHandler(successor=middle, does_match=False)

    result = head.handle("anything", context=None)

    assert result == "handled"
    assert head.executed == []
    assert middle.executed == []
    assert tail.executed == ["anything"]


def test_each_command_triggers_only_its_expected_events():
    cases = {
        "move to the bar": ["command.move_to", "player_moved"],
        "look": ["command.look", "location_described"],
        "quit": ["command.quit", "game_over"],
        "exit": ["command.quit", "game_over"],
        "dance": ["command.unknown"],
    }
    for line, expected in cases.items():
        context, bus = make_context()
        chain = build_command_chain()

        chain.handle(line, context)

        assert bus.log == expected, line


def test_short_circuit_prevents_fallthrough_to_unknown():
    context, bus = make_context()
    chain = build_command_chain()

    chain.handle("move to the bar", context)

    # If the chain failed to short-circuit, the terminal UnknownHandler
    # would have appended "command.unknown" to the sequence.
    assert bus.log == ["command.move_to", "player_moved"]
    assert "command.unknown" not in bus.log


def test_event_sequence_shows_no_interleaving_between_inputs():
    context, bus = make_context()
    chain = build_command_chain()
    inputs = ["move to the bar", "look", "dance", "quit"]
    per_input = {
        "move to the bar": ["command.move_to", "player_moved"],
        "look": ["command.look", "location_described"],
        "dance": ["command.unknown"],
        "quit": ["command.quit", "game_over"],
    }

    for line in inputs:
        chain.handle(line, context)

    expected = [event for line in inputs for event in per_input[line]]
    assert bus.log == expected

    # Each input's events form one contiguous block: no event from a
    # later input may appear before the previous input's block ended.
    index = 0
    for line in inputs:
        block = per_input[line]
        assert bus.log[index:index + len(block)] == block
        index += len(block)

    # Inputs share the context but state from one input must not bleed
    # into the next input's event payload in the wrong place: "look"
    # describes exactly the destination chosen by the move before it.
    assert context.location == "the bar"


def test_unknown_command_only_fires_unknown_event():
    context, bus = make_context()
    chain = build_command_chain()

    chain.handle("jump", context)
    chain.handle("sing", context)

    assert bus.log == ["command.unknown", "command.unknown"]
