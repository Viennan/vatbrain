# Python 用户指南

状态：v0.2  
日期：2026-05-05
最近更新：2026-05-06

## 编程模型

Python 版本的 `vatbrain` 提供 provider 级 client。用户先初始化某个厂商的 client，然后在每次调用时显式传入 model、上下文 items 和调用配置。

`vatbrain` 不会自动选择 provider，不会自动选择 model，不会 fallback，也不会自动执行工具或运行 agent loop。用户代码始终掌控调用顺序、工具执行和上下文回填。

当前第一阶段实现了 OpenAI adapter：

```python
from whero.vatbrain.providers.openai import OpenAIClient

client = OpenAIClient()
```

OpenAI API key 可以通过 `ENV_VATBRAIN_OPENAI_API_KEY` 环境变量提供：

```bash
export ENV_VATBRAIN_OPENAI_API_KEY="..."
```

也可以在初始化时显式传入通用 client 参数：

```python
client = OpenAIClient(
    api_key="...",
    base_url="...",
    timeout=30.0,
    max_retries=2,
)
```

显式参数优先于环境变量。少量 provider SDK 专有初始化参数仍可作为额外关键字参数传入。

## 安装与测试

在仓库内使用 Python 虚拟环境：

```bash
cd python
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[test]"
.venv/bin/python -m pytest
```

所有 Python 开发与测试命令都应使用 `python/.venv`。

## 内容生成

最小文本生成：

```python
from whero.vatbrain import MessageItem
from whero.vatbrain.providers.openai import OpenAIClient

client = OpenAIClient()

response = client.generate(
    model="gpt-5.1",
    items=[
        MessageItem.system("You are a concise assistant."),
        MessageItem.user("Hello"),
    ],
)

for item in response.output_items:
    print(item)
```

`items` 是完整上下文序列。每次调用都应传入本轮推理所需的全部上下文，而不是依赖 provider 侧隐式状态。

常用 generation 配置：

```python
from whero.vatbrain import GenerationConfig, ReasoningConfig, ToolCallConfig

response = client.generate(
    model="gpt-5.1",
    items=[MessageItem.user("Explain vatbrain in one paragraph.")],
    generation_config=GenerationConfig(
        temperature=0.2,
        max_output_tokens=300,
    ),
    reasoning=ReasoningConfig(
        effort="low",
    ),
    tool_call_config=ToolCallConfig(
        parallel_tool_calls=False,
    ),
)
```

`reasoning` 和 `parallel_tool_calls` 是通用 generation 配置，不是 OpenAI 专有选项。不同 provider/model 可能只支持其中一部分字段。

## 流式生成

流式调用返回标准化事件。v0.2 起，文本增量事件使用更明确的 `text.delta` 类型；为了兼容旧代码，OpenAI 文本增量事件仍会在 metadata 中标记旧语义。

```python
from whero.vatbrain import MessageItem

for event in client.stream_generate(
    model="gpt-5.1",
    items=[MessageItem.user("Write a short haiku.")],
):
    if event.type == "text.delta":
        print(event.delta, end="")
```

事件中会保留 `raw_event`，用于访问尚未被 `vatbrain` 标准化的 provider 原始事件。OpenAI Responses API 的最终 usage 通常随 `response.completed` 或 `response.incomplete` 中的完整 response 返回；`StreamOptions(include_usage=True)` 不会被映射为 OpenAI `stream_options.include_usage`。

如果需要从流式事件重建最终响应，可以使用 accumulator：

```python
from whero.vatbrain import GenerationStreamAccumulator, MessageItem

accumulator = GenerationStreamAccumulator(provider="openai")

for event in client.stream_generate(
    model="gpt-5.1",
    items=[MessageItem.user("Write a short haiku.")],
):
    accumulator.add(event)
    if event.type == "text.delta":
        print(event.delta, end="")

response = accumulator.to_response()
```

异步流式调用：

```python
async for event in client.astream_generate(
    model="gpt-5.1",
    items=[MessageItem.user("Write a short haiku.")],
):
    ...
```

## Structured Output

OpenAI adapter 使用 Responses API 的 `text.format` 表达 JSON mode 与 JSON schema structured output。

JSON object：

```python
from whero.vatbrain import MessageItem, ResponseFormat

response = client.generate(
    model="gpt-5.1",
    items=[MessageItem.user("Return a JSON object with a short title.")],
    response_format=ResponseFormat(type="json_object"),
)
```

JSON schema：

```python
from whero.vatbrain import MessageItem, ResponseFormat

response = client.generate(
    model="gpt-5.1",
    items=[MessageItem.user("Extract a contact.")],
    response_format=ResponseFormat(
        type="json_schema",
        json_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
            },
            "required": ["name", "email"],
            "additionalProperties": False,
        },
        json_schema_name="contact",
        json_schema_strict=True,
    ),
)
```

## 工具调用

`vatbrain` 只定义工具协议，不执行工具。用户需要读取模型输出中的 `FunctionCallItem`，自行执行工具，然后把结果作为 `FunctionResultItem` 加入下一轮上下文。

```python
from whero.vatbrain import FunctionCallItem, FunctionResultItem, MessageItem, ToolSpec

tools = [
    ToolSpec(
        name="get_weather",
        description="Get weather by city.",
        parameters_schema={
            "type": "object",
            "properties": {
                "city": {"type": "string"},
            },
            "required": ["city"],
        },
        strict=True,
    )
]

items = [
    MessageItem.user("What is the weather in Shanghai?"),
]

response = client.generate(
    model="gpt-5.1",
    items=items,
    tools=tools,
)

for output_item in response.output_items:
    if isinstance(output_item, FunctionCallItem):
        tool_output = '{"city":"Shanghai","temperature_c":22}'
        items.append(output_item)
        items.append(
            FunctionResultItem(
                call_id=output_item.call_id,
                output=tool_output,
            )
        )

followup = client.generate(
    model="gpt-5.1",
    items=items,
    tools=tools,
)
```

这段流程由用户代码驱动；`vatbrain` 不会自动调用 `get_weather`，也不会自动发起 follow-up 请求。

## Embedding

embedding 是独立入口，不并入 generation request。

```python
embedding = client.embed(
    model="text-embedding-3-small",
    inputs=[
        "first document",
        "second document",
    ],
)

for vector in embedding.vectors:
    print(vector.index, vector.embedding)
```

第一阶段 OpenAI adapter 只支持 text embedding。多模态 embedding 属于设计目标，但不在当前 OpenAI adapter 第一阶段范围内。

## Capability

adapter capability 描述当前 adapter 自身实现了什么：

```python
capability = client.get_adapter_capability()
print(capability.supports_generation)
print(capability.supports_text_embedding)
```

model capability 是对某个 model 的能力描述，但不保证权威。对于上下文窗口、embedding 维度等易变字段，默认可能是 unknown：

```python
model_capability = client.get_model_capability("gpt-5.1")
print(model_capability.max_context_tokens.value)  # None means unknown.
```

用户可以显式提供覆盖信息：

```python
client = OpenAIClient(
    model_capability_overrides={
        "gpt-5.1": {
            "supports_streaming": True,
        }
    }
)
```

用户提供的 capability 覆盖会被标记为 `user_config` / `user_supplied`。

## Provider Options

`provider_options` 用于传递暂未被 `vatbrain` 归一化的厂商专有参数：

```python
response = client.generate(
    model="gpt-5.1",
    items=[MessageItem.user("Hello")],
    provider_options={
        "metadata": {"trace_id": "example"},
    },
)
```

如果某个参数表达的是通用 generation 语义，应优先使用 `GenerationConfig`、`ReasoningConfig`、`ToolCallConfig` 或其他 core 模型，而不是放入 `provider_options`。

## 当前限制

第一阶段存在以下限制：

- 仅实现 OpenAI provider。
- generation 使用 OpenAI Responses API。
- embedding 仅支持文本输入。
- streaming event 已覆盖 OpenAI Responses API 的主要 lifecycle、text、function call、reasoning summary/text 与错误事件；未知事件会 raw passthrough。
- capability 不维护内部权威模型能力表。
- 不提供 routing、fallback、自动模型选择、自动工具执行或 agent loop。

## 参考

- [design/high-level-design.CN.md](design/high-level-design.CN.md)
- [impls/python/openai-adapter.CN.md](impls/python/openai-adapter.CN.md)
- [impls/python/STATUS.md](impls/python/STATUS.md)
