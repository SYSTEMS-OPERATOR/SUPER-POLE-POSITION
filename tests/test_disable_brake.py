import types
import os

import pytest  # noqa: F401

from super_pole_position.agents import keyboard_agent, joystick_agent


class DummyJoystick:
    def __init__(self):
        pass

    def init(self):
        pass

    def get_axis(self, idx):
        return 0.0

    def get_numbuttons(self):
        return 0

    def get_button(self, btn):
        return False


def make_pygame_stub():
    pg = types.SimpleNamespace()
    pg.K_UP = 0
    pg.K_DOWN = 1
    pg.K_LEFT = 2
    pg.K_RIGHT = 3
    pg.K_x = 4
    pg.K_z = 5
    pg.key = types.SimpleNamespace(get_pressed=lambda: [0, 1, 0, 0, 0, 0])
    pg.joystick = types.SimpleNamespace(
        init=lambda: None, get_count=lambda: 1, Joystick=lambda idx: DummyJoystick()
    )
    pg.event = types.SimpleNamespace(pump=lambda: None)
    return pg


def test_disable_brake(monkeypatch):
    pg = make_pygame_stub()
    monkeypatch.setattr(keyboard_agent, "pygame", pg)
    monkeypatch.setattr(joystick_agent, "pygame", pg)
    monkeypatch.setenv("DISABLE_BRAKE", "1")

    kb = keyboard_agent.KeyboardAgent()
    kb_action = kb.act(None)
    assert kb_action["brake"] == 0

    js = joystick_agent.JoystickAgent()
    js_action = js.act(None)
    assert js_action["brake"] == 0
