from importlib import import_module


def test_package_is_importable() -> None:
    package = import_module("embedded_ai_platform")

    assert package.__name__ == "embedded_ai_platform"
