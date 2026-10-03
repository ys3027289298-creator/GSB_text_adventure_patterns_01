#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""State pattern: the states a character can be in.

Each state knows how to `enter`, `exit` and `update` the entity it
belongs to. States also publish ``state.entered`` / ``state.exited``
events on the entity's event bus so observers can follow transitions
without the states knowing who listens.
"""


class Working:
    def enter(self, entity):
        print("Let's get some work done!")
        entity.events.publish("state.entered", state="working")

    def exit(self, entity):
        print("Leaving the office.")
        entity.events.publish("state.exited", state="working")

    def update(self, entity):
        entity.tiredness += 1
        entity.thirst += 1

        print("Working my ass off.")

        if entity.thirst > entity.TOO_THIRSTY:
            print("I'm too thirsty. Heading off to the bar!")
            entity.change_state(Drinking())
        elif entity.tiredness > entity.TOO_TIRED:
            print("I'm too tired to keep on working. I'll go back home get"
                  " some sleep.")
            entity.change_state(Sleeping())


class Drinking:
    def enter(self, entity):
        print("Let's checkout this bar. They seem to have tap beers.")
        entity.events.publish("state.entered", state="drinking")

    def exit(self, entity):
        print("Let's leave a tip before leaving the bar.")
        entity.events.publish("state.exited", state="drinking")

    def update(self, entity):
        entity.tiredness += 1

        print("Drinking a nice beer")
        entity.thirst = 0

        if entity.tiredness > entity.TOO_TIRED:
            print("Drinking made me tired. I'll go back home get"
                  " some sleep.")
            entity.change_state(Sleeping())
        else:
            print("Now I can go back to work.")
            entity.change_state(Working())


class Sleeping:
    def enter(self, entity):
        print("Home, sweet home.")
        entity.events.publish("state.entered", state="sleeping")

    def exit(self, entity):
        print("Let's lock the front door before leaving home.")
        entity.events.publish("state.exited", state="sleeping")

    def update(self, entity):
        entity.tiredness += 1

        print("Zzzz")
        entity.tiredness -= 3
        if entity.tiredness <= 0:
            entity.tiredness = 0
            print("I had enough sleep. I'll go to work.")
            entity.change_state(Working())
