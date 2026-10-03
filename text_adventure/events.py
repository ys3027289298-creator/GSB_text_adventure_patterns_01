#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Observer pattern: a small synchronous event bus.

Listeners subscribe to event types and get notified when an event of that
type is published. The bus protects against two edge cases:

* Subscribing the same listener twice must not notify it twice.
* Publishing the same event (identified by ``event_id``) twice must not
  trigger side effects twice.
"""


class EventBus:
    """Synchronous observer hub with duplicate-notification guards."""

    def __init__(self):
        self._listeners = {}
        self._seen_event_ids = set()
        # Ordered log of every event type that was actually delivered.
        # Useful to assert on event sequences in tests.
        self.log = []

    def subscribe(self, event_type, listener):
        "Register `listener` for `event_type` (idempotent)."
        listeners = self._listeners.setdefault(event_type, [])
        if listener not in listeners:
            listeners.append(listener)

    def unsubscribe(self, event_type, listener):
        "Remove `listener` from `event_type` if present."
        listeners = self._listeners.get(event_type, [])
        while listener in listeners:
            listeners.remove(listener)

    def publish(self, event_type, event_id=None, **payload):
        """Notify all listeners of `event_type`.

        Returns True when the event was delivered, False when it was
        dropped as a duplicate (same `event_id` already published).
        """
        if event_id is not None:
            if event_id in self._seen_event_ids:
                # Duplicate notification: no side effects.
                return False
            self._seen_event_ids.add(event_id)
        self.log.append(event_type)
        for listener in list(self._listeners.get(event_type, [])):
            listener(event_type, **payload)
        return True
