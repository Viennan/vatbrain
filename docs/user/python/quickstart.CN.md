# Python 用户指南

状态：v0.3  
日期：2026-05-05
最近更新：2026-05-06

## 编程模型

Python 版本的 `vatbrain` 提供 provider 级 client。用户先初始化某个厂商的 client，然后在每次调用时显式传入 model、上下文 items 和调用配置。

`vatbrain` 不会自动选择 provider，不会自动选择 model，不会 fallback，也不会自动执行工具或运行 agent loop。用户代码始终掌控调用顺序、工具执行和上下文回填。

当前实现了 OpenAI adapter：

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

v0.3 新增 `RemoteContextHint`，用于显式表达 provider 侧 previous response 与 store hint。这只是优化提示，不改变 Full-context First，也不表示 `vatbrain` 使用 provider conversation 持久化上下文：

```python
from whero.vatbrain import MessageItem, RemoteContextHint

first_items = [MessageItem.user("Summarize the contract.")]

first_response = client.generate(
    model="gpt-5.1",
    items=first_items,
    remote_context=RemoteContextHint(store=True),
)

history_items = [*first_items, *first_response.output_items]
items = [*history_items, MessageItem.user("Now extract the termination clause.")]

response = client.generate(
    model="gpt-5.1",
    items=items,
    remote_context=RemoteContextHint(
        previous_response_id=first_response.id,
        covered_item_count=len(history_items),
    ),
)
```

OpenAI adapter 会映射 `previous_response_id` 与 `store`；provider conversation 这类持久化上下文能力暂不进入 core。

`store=None` 表示不由 `vatbrain` 显式指定存储策略，而是交给 provider 默认行为。本轮是否设置 `store=True` 只影响“本轮 response 是否便于未来作为 `previous_response_id` 被引用”；使用某个 `previous_response_id` 时，需要确保那个 id 对应 response 在生成时已开启存储，例如当时使用了 `RemoteContextHint(store=True)`，或用户明确依赖该 provider 的默认存储行为。

上例中，`first_response.id` 对应的 provider response 覆盖了第一轮输入 `first_items` 与第一轮输出 `first_response.output_items`，所以第二轮完整上下文的 history 前缀是 `history_items`，`covered_item_count` 应为 `len(history_items)`。`items[len(history_items):]` 才是本轮追加的新输入。

用户侧仍应传入完整 `items`。如果 `previous_response_id` 对应的 provider response 已覆盖完整上下文中的历史前缀，可以用 `covered_item_count` 显式说明覆盖范围；adapter 才能在 provider 请求层只发送追加 items：

```python
from whero.vatbrain import MessageItem, RemoteContextHint

items = [
    MessageItem.system("Answer with concise reasoning."),
    MessageItem.user("Summarize the contract."),
    MessageItem.assistant("The contract defines payment terms."),
    MessageItem.user("Now extract the termination clause."),
]

response = client.generate(
    model="gpt-5.1",
    items=items,
    remote_context=RemoteContextHint(
        previous_response_id="resp_previous",
        covered_item_count=3,
    ),
)
```

上例中，`items[:3]` 仍是本次调用的语义上下文；OpenAI provider 请求只需要传输 `items[3:]`。如果传入 `previous_response_id` 但没有 `covered_item_count`，OpenAI adapter 不应猜测哪些 item 是历史、哪些 item 是新增输入，应提示用户补充覆盖范围或移除 `previous_response_id`。

Provider response 映射出的 `Item` 会在 `provider_snapshots` 字段保留同 provider/API family 的原始 item payload。再次调用同一 provider 时，OpenAI adapter 默认会优先使用该 snapshot 重放历史 item，从而保留 OpenAI assistant message 的 `phase` 等原生字段：

```python
from whero.vatbrain import AssistantMessagePhase, MessageItem, ReplayPolicy

history = [
    MessageItem.assistant(
        "Let me inspect that.",
        assistant_phase=AssistantMessagePhase.COMMENTARY,
    ),
    MessageItem.user("Continue."),
]

response = client.generate(model="gpt-5.1", items=history)
```

`assistant_phase` 是通用抽象，只对 assistant message 有意义。OpenAI adapter 会将其映射为原生 `phase`。如果需要禁用 snapshot replay 或强制所有重放 item 都带 provider 原始快照，可以使用 `ReplayPolicy(mode="normalized_only")` 或 `ReplayPolicy(mode="require_provider_native")`。

当 `previous_response_id` 失效时，OpenAI adapter 默认抛出 provider request error。只有显式设置 `ReplayPolicy(on_remote_context_invalid="replay_without_remote_context")` 时，client 才会移除失效的 `previous_response_id`，用完整 `items` 自动重试一次：

```python
response = client.generate(
    model="gpt-5.1",
    items=history,
    remote_context=RemoteContextHint(previous_response_id="resp_previous"),
    replay_policy=ReplayPolicy(on_remote_context_invalid="replay_without_remote_context"),
)
```

如果第一次请求使用 OpenAI previous response 差分传输，失效 fallback 仍会回到完整 `items`。因此不要只把“新增输入”传给 `items`；`items` 永远应是完整语义上下文。

跨 provider replay 暂不支持；provider snapshot 只用于原 provider 的高保真重放。

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

OpenAI adapter 使用 Responses API 的 `text.format` 表达 JSON Schema structured output。`vatbrain` 不兼容已淘汰的 JSON mode / `json_object` 调用方式。

```python
from whero.vatbrain import MessageItem, ResponseFormat

response = client.generate(
    model="gpt-5.1",
    items=[MessageItem.user("Extract a contact.")],
    response_format=ResponseFormat(
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

当前 OpenAI adapter 只支持 text embedding。多模态 embedding 属于 core 表达目标，但不在当前 OpenAI adapter 支持范围内。

v0.3 的 core 已能表达多模态 embedding、instructions 和 sparse vectors：

```python
from whero.vatbrain import EmbeddingInput, ImagePart

sample = EmbeddingInput(
    [
        ImagePart(url="https://example.test/image.png"),
    ],
    modality="image",
)
```

这只是 core 表达能力；OpenAI adapter 目前仍只接受文本 embedding input。

## Core Models

v0.3 新增音频、视频、文件、reasoning、resource/file 和 media artifact/task 的 core 模型。这些模型用于在不同 provider adapter 之间表达语义，不代表当前 OpenAI adapter 已全部支持。

```python
from whero.vatbrain import FilePart, MessageItem, VideoPart

items = [
    MessageItem.user(
        [
            VideoPart(url="https://example.test/demo.mp4", mime_type="video/mp4"),
            FilePart(file_id="file_provider_123", provider="example"),
        ]
    )
]
```

`FilePart.local_path`、`AudioPart.local_path` 和 `VideoPart.local_path` 只是路径 metadata，不会自动读取文件或上传文件。需要上传文件时，未来 provider adapter 会提供显式 file/resource API。

工具抽象当前只覆盖用户代码执行的 function tool。provider-hosted tool、remote tool 和 MCP tool 暂不暴露为通用 core 抽象。

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

不同 provider 对 `ReasoningConfig.effort` 的取值和含义可能不同。adapter capability 会在可声明时列出 provider 支持的 effort；具体 model 也可以通过 model capability 或用户覆写给出更窄集合：

```python
adapter_capability = client.get_adapter_capability()
print(adapter_capability.generation.supported_reasoning_efforts.value)

model_capability = client.get_model_capability("gpt-5.1")
print(model_capability.supported_reasoning_efforts.value)
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

当前存在以下限制：

- 仅实现 OpenAI provider。
- generation 使用 OpenAI Responses API。
- embedding 仅支持文本输入。
- v0.3 新增的 audio/video/file/reasoning/resource/media 模型主要是 core 表达层，OpenAI adapter 未全部映射。
- streaming event 已覆盖 OpenAI Responses API 的主要 lifecycle、text、function call、reasoning summary/text 与错误事件；未知事件会 raw passthrough。
- capability 不维护内部权威模型能力表。
- 不提供 routing、fallback、自动模型选择、自动工具执行或 agent loop。

## 参考

- [design/high-level-design.CN.md](design/high-level-design.CN.md)
- [impls/python/openai-adapter.CN.md](impls/python/openai-adapter.CN.md)
- [impls/python/STATUS.md](impls/python/STATUS.md)
