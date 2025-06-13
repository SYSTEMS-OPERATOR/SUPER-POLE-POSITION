from super_pole_position.agents.openai_agent import parse_action


def test_parse_action_valid():
    data = parse_action('{"throttle":1,"brake":0,"steer":0.5}')
    assert data == {"throttle": 1, "brake": 0, "steer": 0.5}


def test_parse_action_invalid():
    data = parse_action('not json')
    assert data == {"throttle": 0, "brake": 0, "steer": 0.0}
