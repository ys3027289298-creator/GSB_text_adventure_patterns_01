#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Insert `text_adventure` package to the sys.path so we don't need to
# install the package for testing.
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest

from text_adventure.commands import (
    CommandFactory,
    MoveToCommand,
    LookCommand,
    QuitCommand,
    UnknownCommand,
)


@pytest.fixture
def factory():
    return CommandFactory()


def test_factory_creates_the_requested_command(factory):
    assert isinstance(factory.create("move_to", "bar"), MoveToCommand)
    assert isinstance(factory.create("look"), LookCommand)
    assert isinstance(factory.create("quit"), QuitCommand)
    assert isinstance(factory.create("exit"), QuitCommand)


def test_factory_is_case_insensitive(factory):
    assert isinstance(factory.create("MOVE_TO", "bar"), MoveToCommand)
    assert isinstance(factory.create("Look"), LookCommand)
    assert isinstance(factory.create(" QUIT "), QuitCommand)


def test_factory_never_confuses_similar_names(factory):
    # A prefix or extension of a known command must NOT create that command.
    for name in ("move", "move_to_nowhere", "lookout", "quitter",
                 "qui", "", "move to"):
        command = factory.create(name)
        assert isinstance(command, UnknownCommand), name
        assert not isinstance(command, (MoveToCommand, LookCommand,
                                       QuitCommand)), name


def test_factory_passes_args_through(factory):
    command = factory.create("move_to", "the bar")
    assert command.args == ("the bar",)


def test_unknown_command_remembers_its_name(factory):
    command = factory.create("dance")
    assert command.unknown_name == "dance"
