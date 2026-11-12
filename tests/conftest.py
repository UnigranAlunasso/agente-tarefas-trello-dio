"""Permite testar as ferramentas sem instalar o SDK ou usar tokens reais."""
import importlib.util
import sys
import types

try:
    has_adk = importlib.util.find_spec("google.adk") is not None
except ModuleNotFoundError:
    has_adk = False

if not has_adk:
    try:
        import google  # noqa: F401
    except ImportError:
        sys.modules["google"] = types.ModuleType("google")
    sys.modules["google.adk"] = types.ModuleType("google.adk")
    agents = types.ModuleType("google.adk.agents")
    class Agent:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
    agents.Agent = Agent
    sys.modules["google.adk.agents"] = agents
