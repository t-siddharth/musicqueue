import pytest
from hello_world import greet


def test_greet_default():
    """Test greet function with default name."""
    assert greet() == "Hello, World!"


def test_greet_with_name():
    """Test greet function with custom name."""
    assert greet("Alice") == "Hello, Alice!"


def test_greet_empty_string():
    """Test greet function with empty string."""
    assert greet("") == "Hello, !"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
