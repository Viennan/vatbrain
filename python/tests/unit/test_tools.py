from __future__ import annotations

import pytest

from whero.vatbrain import (
    FunctionToolSpec,
    ToolExecutionOwner,
    ToolSpec,
)


def test_tool_spec_is_function_tool_compatible_alias() -> None:
    tool = ToolSpec(name="lookup", parameters_schema={"type": "object"})

    assert isinstance(tool, FunctionToolSpec)
    assert tool.type == "function"
    assert tool.execution_owner == ToolExecutionOwner.USER


def test_function_tool_requires_name() -> None:
    with pytest.raises(ValueError):
        FunctionToolSpec(name="")
