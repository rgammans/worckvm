""" Drivers are referenced by name in the YAML config file
but have to instatinated by code loaded with --drivers.

This file manages the binding between name ans instance
"""

def _reset():
    global _registry
    _registry = {}

def register(instance, name):
    if name in _registry:
        raise ValueError(f"A driver named {name} already exists")
    _registry[name] = instance

no_default = object()

def get(name, default=no_default):
    value = _registry.get(name, default)
    if value is no_default:
        raise KeyError(name)
    return value

_reset()
