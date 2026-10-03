#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Insert `text_adventure` package to the sys.path so we don't need to
# install the package for testing.
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest

from text_adventure.events import EventBus
from text_adventure.entity import MyCharacter
from text_adventure.states import Working, Drinking, Sleeping
from text_adventure.world import World


class FailingState:
    """State whose `enter` always raises (a broken transition)."""

    def enter(self, entity):
        entity.events.publish("state.entered", state="broken")
        raise RuntimeError("cannot enter")

    def exit(self, entity):
        entity.events.publish("state.exited", state="broken")

    def update(self, entity):
        raise RuntimeError("should never update")


def test_failed_transition_rolls_back_to_previous_state():
    character = MyCharacter("Dan")
    previous = character.state
    assert isinstance(previous, Working)

    with pytest.raises(RuntimeError):
        character.change_state(FailingState())

    assert character.state is previous
    assert isinstance(character.state, Working)


def test_rollback_does_not_retrigger_previous_plot():
    bus = EventBus()
    character = MyCharacter("Dan", events=bus)
    entered_working = [
        event for event in bus.log
        if event == "state.entered"
    ]
    # Initial state is assigned directly, no enter plot at construction.
    assert entered_working == []

    with pytest.raises(RuntimeError):
        character.change_state(FailingState())

    events = bus.log
    # The broken enter happened exactly once (and its rollback must not
    # replay the previous state's enter plot).
    assert events.count("state.entered") == 1
    # Working's "enter" plot must not have been re-fired by the rollback.
    assert events == ["state.exited", "state.entered"]
    assert character.state is not None
    assert isinstance(character.state, Working)


def test_rollback_does_not_print_previous_plot_again(capsys):
    character = MyCharacter("Dan")

    with pytest.raises(RuntimeError):
        character.change_state(FailingState())

    printed = capsys.readouterr().out
    # Working's enter line ("Let's get some work done!") is never
    # printed by a rollback; only the exit line appears.
    assert "Let's get some work done!" not in printed
    assert printed.count("Leaving the office.") == 1


def test_successful_transition_fires_enter_once():
    bus = EventBus()
    character = MyCharacter("Dan", events=bus)

    character.change_state(Drinking())

    assert isinstance(character.state, Drinking)
    assert bus.log == ["state.exited", "state.entered"]


def test_full_run_transition_events_never_interleave():
    bus = EventBus()
    world = World()
    character = MyCharacter("Dan", events=bus)
    world.add_entity(character)

    for _ in range(20):
        world.update()

    # Every successful transition is an (exited, entered) pair: no two
    # enters in a row and no two exits in a row, so two inputs/steps
    # can never interleave within one transition.
    for previous, current in zip(bus.log, bus.log[1:]):
        assert previous != current
    assert bus.log[0] == "state.exited"
    assert len(bus.log) % 2 == 0


def test_update_after_rollback_resumes_normally(capsys):
    character = MyCharacter("Dan")

    with pytest.raises(RuntimeError):
        character.change_state(FailingState())

    # The character is back in Working and a normal update still works.
    thirst_before = character.thirst
    character.update()
    assert character.thirst == thirst_before + 1
    assert "Working my ass off." in capsys.readouterr().out
