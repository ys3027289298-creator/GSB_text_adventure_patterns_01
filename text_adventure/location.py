#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Locations of the text adventure world."""


class Location:
    "A place the player can move to."

    def __init__(self, id, description, neighbours=None):
        self.id = id
        self.description = description
        self.neighbours = set(neighbours) if neighbours else set()
