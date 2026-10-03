#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Insert `text_adventure` package to the sys.path so we don't need to
# install the package for testing.
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest

from text_adventure.events import EventBus


def test_same_listener_subscribed_twice_notified_once():
    bus = EventBus()
    calls = []
    bus.subscribe("ping", lambda event_type, **payload: calls.append(event_type))
    bus.subscribe("ping", lambda event_type, **payload: calls.append("other"))
    # Subscribing the very same listener again must be a no-op.
    listener = lambda event_type, **payload: calls.append("dup")
    bus.subscribe("ping", listener)
    bus.subscribe("ping", listener)

    bus.publish("ping")

    assert calls.count("dup") == 1
    assert len(calls) == 3


def test_duplicate_event_id_produces_no_side_effects():
    bus = EventBus()
    side_effects = []
    bus.subscribe("player_moved",
                  lambda event_type, **payload: side_effects.append(payload))

    assert bus.publish("player_moved", event_id="move-1", destination="bar")
    assert not bus.publish("player_moved", event_id="move-1", destination="bar")

    # The duplicate notification was dropped: only one side effect happened.
    assert side_effects == [{"destination": "bar"}]
    assert bus.log == ["player_moved"]


def test_different_event_ids_are_both_delivered():
    bus = EventBus()
    bus.publish("ping", event_id="a")
    bus.publish("ping", event_id="b")
    assert bus.log == ["ping", "ping"]


def test_unsubscribe_stops_notifications():
    bus = EventBus()
    calls = []
    listener = lambda event_type, **payload: calls.append(event_type)
    bus.subscribe("ping", listener)
    bus.unsubscribe("ping", listener)
    bus.publish("ping")
    assert calls == []
