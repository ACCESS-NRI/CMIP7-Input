"""Tests for the registration/fallback mechanics of GeneratorRegistry.

These are independent of any real model, so it's easy to convince
yourself the mechanics are right without wading through real
processing code.
"""

import pytest

from cmip7_inputs.core.registry import GeneratorRegistry


def test_resolve_returns_exact_experiment_match() -> None:
    registry = GeneratorRegistry()

    @registry.register(model="m", input_name="n", experiments=["e1"])
    def generator_e1(request):
        return "e1"

    @registry.register(model="m", input_name="n", experiments=["e2"])
    def generator_e2(request):
        return "e2"

    assert (
        registry.resolve(model="m", input_name="n", experiment="e1")
        is generator_e1
    )
    assert (
        registry.resolve(model="m", input_name="n", experiment="e2")
        is generator_e2
    )


def test_resolve_falls_back_to_default() -> None:
    registry = GeneratorRegistry()

    @registry.register(model="m", input_name="n", experiments=None)
    def default_generator(request):
        return "default"

    resolved = registry.resolve(
        model="m", input_name="n", experiment="anything"
    )
    assert resolved is default_generator


def test_resolve_prefers_exact_match_over_default() -> None:
    registry = GeneratorRegistry()

    @registry.register(model="m", input_name="n", experiments=None)
    def default_generator(request):
        return "default"

    @registry.register(model="m", input_name="n", experiments=["e1"])
    def specific_generator(request):
        return "specific"

    assert (
        registry.resolve(model="m", input_name="n", experiment="e1")
        is specific_generator
    )
    assert (
        registry.resolve(model="m", input_name="n", experiment="other")
        is default_generator
    )


def test_resolve_raises_when_nothing_registered() -> None:
    registry = GeneratorRegistry()

    with pytest.raises(KeyError):
        registry.resolve(model="m", input_name="n", experiment="e1")


def test_register_shared_across_multiple_experiments() -> None:
    registry = GeneratorRegistry()

    @registry.register(
        model="m", input_name="n", experiments=["e1", "e2"]
    )
    def shared_generator(request):
        return "shared"

    assert (
        registry.resolve(model="m", input_name="n", experiment="e1")
        is shared_generator
    )
    assert (
        registry.resolve(model="m", input_name="n", experiment="e2")
        is shared_generator
    )
