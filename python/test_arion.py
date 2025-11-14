import json
from arion import dumps_arion, loads_arion


def roundtrip(obj):
    text = dumps_arion(obj)
    back = loads_arion(text)
    assert back == obj
    return text, back


def test_simple_object():
    data = {"name": "Joachim", "age": 37, "active": True}
    roundtrip(data)


def test_nested():
    data = {
        "name": "Joachim",
        "profile": {"role": "Developer", "location": "Austria"},
        "skills": ["Python", "Audio", "AI"],
    }
    roundtrip(data)


def test_multiline():
    data = {
        "bio": "Line one\nLine two\nLine three"
    }
    text, back = roundtrip(data)
    assert "Line two" in text
    assert back == data


def test_forced_strings():
    data = {
        "flag": "true",
        "number_as_string": "37",
        "null_as_string": "null",
    }
    text, back = roundtrip(data)
    assert back == data


if __name__ == "__main__":
    # run basic tests
    for func in [test_simple_object, test_nested, test_multiline, test_forced_strings]:
        func()
    print("All tests passed.")
