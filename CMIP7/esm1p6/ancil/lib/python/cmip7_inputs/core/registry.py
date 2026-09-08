"""Registry mapping (model, input_name, experiment) to generators."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from cmip7_inputs.core.context import GenerationRequest

Generator = Callable[[GenerationRequest], Any]


class GeneratorRegistry:
    """A registry of generator functions.

    Generator modules populate this purely as an import side effect,
    using the :meth:`register` decorator -- nothing needs to be
    registered by hand in a central place.
    """

    def __init__(self) -> None:
        self._generators: dict[tuple[str, str, str], Generator] = {}
        self._defaults: dict[tuple[str, str], Generator] = {}

    def register(
        self,
        *,
        model: str,
        input_name: str,
        experiments: Iterable[str] | None,
    ) -> Callable[[Generator], Generator]:
        """Register a generator for a model and input name.

        If ``experiments`` is ``None``, the generator is registered as
        the default for any experiment that doesn't have a more
        specific registration. Otherwise it is registered for each
        experiment id in ``experiments`` (several experiments can
        share the exact same generator).
        """

        def decorator(func: Generator) -> Generator:
            if experiments is None:
                self._defaults[(model, input_name)] = func
            else:
                for experiment in experiments:
                    key = (model, input_name, experiment)
                    self._generators[key] = func
            return func

        return decorator

    def resolve(
        self, *, model: str, input_name: str, experiment: str
    ) -> Generator:
        """Return the generator for a model/input_name/experiment.

        An exact ``(model, input_name, experiment)`` match always
        wins; otherwise falls back to the ``(model, input_name)``
        default, if any. Raises ``KeyError`` if nothing matches.
        """
        key = (model, input_name, experiment)
        if key in self._generators:
            return self._generators[key]

        default_key = (model, input_name)
        if default_key in self._defaults:
            return self._defaults[default_key]

        raise KeyError(
            "No generator registered for "
            f"model={model!r}, input_name={input_name!r}, "
            f"experiment={experiment!r}"
        )


registry = GeneratorRegistry()
