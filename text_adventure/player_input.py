#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Parsing of the player input into (command, *args) tuples."""


def parse_input(line):
    """Parse a raw input line into a ``(command, *args)`` tuple.

    The command word is case-insensitive; arguments keep their original
    case. Unknown input yields the first word as command and no args.
    """
    words = line.split()
    if not words:
        return ("",)
    if len(words) >= 2 and words[0].lower() == "move" \
            and words[1].lower() == "to":
        parts = line.split(None, 2)
        location = parts[2] if len(parts) > 2 else ""
        return ("move_to", location)
    return (words[0].lower(),)


def read_input():
    "Read one line of player input and parse it."
    return parse_input(input("> "))
