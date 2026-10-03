#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .events import EventBus
from .states import Working, Drinking, Sleeping

__all__ = ["Entity", "MyCharacter", "Working", "Drinking", "Sleeping"]


class Entity:
    """Base Entity to live in the World.

    Need to implement the `update` method which will be called by the World
    at every timestep.
    """

    TOO_THIRSTY = 2
    TOO_TIRED = 5

    def __init__(self, name):
        self.tiredness = 0
        self.thirst = 0
        self.name = name

    def update(self):
        raise NotImplementedError


class MyCharacter(Entity):

    def __init__(self, name, events=None):
        super().__init__(name)
        self.events = events if events is not None else EventBus()
        self.state = Working()

    def change_state(self, new_state):
        """Switch to `new_state`, rolling back safely on failure.

        If entering the new state raises, the entity keeps its previous
        state and the previous state's plot (`enter`) is NOT triggered
        again: a rollback must not replay story events.
        """
        previous_state = self.state
        previous_state.exit(self)
        try:
            new_state.enter(self)
        except Exception:
            self.state = previous_state
            raise
        self.state = new_state

    def update(self):
        self.state.update(self)
