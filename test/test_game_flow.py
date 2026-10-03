#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Insert `text_adventure` package to the sys.path so we don't need to
# install the package for testing.
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest

from text_adventure import game


def test_game_run_output_is_unchanged(capsys):
    """Golden-master test: pattern refactoring must not change the flow."""
    golden_path = os.path.join(os.path.dirname(__file__),
                               "golden_run_output.txt")
    with open(golden_path, encoding="utf-8") as golden_file:
        expected = golden_file.read()

    game.run()

    assert capsys.readouterr().out == expected
