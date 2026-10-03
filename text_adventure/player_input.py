#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Parsing of the player input into (command, *args) tuples."""


def parse_input(line):
    """Parse a raw input line into a ``(command, *args)`` tuple.

    The command word is case-insensitive; arguments keep their original
    case. Unknown input yields "unknown" as the command and no args.
    """
    words = line.split()
    if not words:
        return ("unknown",)
    if len(words) >= 2 and words[0].lower() == "move" \
            and words[1].lower() == "to":
        parts = line.split(None, 2)
        location = parts[2] if len(parts) > 2 else ""
        if location:
            return ("move_to", location)
        return ("move_to",)
    command = words[0].lower()
    if command in ("move_to", "look", "quit", "exit"):
        return (command,)
    return ("unknown",)


def read_input():
    "Read one line of player input and parse it."
    return parse_input(input("> "))
