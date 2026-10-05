"""Tests de agent."""

import pytest


def test_create_agent():
    from api.agent import create_agent
    agent = create_agent()
    assert agent is not None


def test_get_agent():
    from api.agent import get_agent
    agent = get_agent()
    assert agent is not None
