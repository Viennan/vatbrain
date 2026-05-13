# Python 实现状态

状态：v0.3 已完成，v0.4 待规划
日期：2026-05-05
最近更新：2026-05-13

## 当前基线

Python 是 `vatbrain` 的参考实现语言。当前实现已完成 v0.3 core 抽象稳定阶段，后续重点转向新增 provider adapter，首先是 Volcengine。

核心文档：

- [design/high-level-design.CN.md](design/high-level-design.CN.md)
- [design/provider-capability-integration.CN.md](design/provider-capability-integration.CN.md)
- [design/provider-native-replay.CN.md](design/provider-native-replay.CN.md)
- [impls/python/evolution-plan.CN.md](impls/python/evolution-plan.CN.md)
- [impls/python/v0.2-responses-contract-hardening.CN.md](impls/python/v0.2-responses-contract-hardening.CN.md)
- [impls/python/v0.3-core-api-family-expansion.CN.md](impls/python/v0.3-core-api-family-expansion.CN.md)
- [impls/python/pydantic-structured-output.CN.md](impls/python/pydantic-structured-output.CN.md)

## 已实现

### 包与基础设施

- Python 包脚手架与 `pyproject.toml`。
- 通用 client 初始化配置：`ClientConfig`。
- OpenAI API key 环境变量：`ENV_VATBRAIN_OPENAI_API_KEY`。
- 默认单元测试不依赖真实 provider API。

### Core

- `core.items`：
  - `MessageItem`、`TextPart`、`ImagePart`、`AudioPart`、`VideoPart`、`FilePart`。
  - `FunctionCallItem`、`FunctionResultItem`。
  - `ReasoningItem`。
  - `AssistantMessagePhase`。
  - `ProviderItemSnapshot` 与 lookup helper。
- `core.generation`：
  - `GenerationRequest`、`GenerationResponse`、`GenerationConfig`。
  - `ResponseFormat`，仅支持 JSON Schema structured output。
  - `ReasoningConfig`。
  - `RemoteContextHint(previous_response_id, covered_item_count, store)`。
  - `ReplayPolicy`、`ReplayMode`、`RemoteContextInvalidBehavior`。
  - `GenerationStreamEvent` 与 `GenerationStreamAccumulator`。
- `core.embeddings`：
  - `EmbeddingInput`、`EmbeddingRequest`、`EmbeddingResponse`。
  - `EmbeddingVector.dense/sparse` 与兼容字段 `embedding`。
  - `SparseEmbedding`。
- `core.resources`：
  - `FileUploadRequest`、`FileResource`、`FileStatus`、`FilePurpose`、`FilePreprocessConfig`。
- `core.media`：
  - `MediaArtifact`、`ImageGenerationRequest`、`ImageGenerationResponse`、`ImageGenerationStreamEvent`、`MediaGenerationTask`。
- `core.tools`：
  - `FunctionToolSpec` / `ToolSpec`。
  - `FunctionToolType(function | custom)`。
  - `ToolChoice` 与 `ToolExecutionOwner(user)`。
- `core.capabilities`：
  - API family capability。
  - `CapabilityValue` 来源与可靠性。
  - adapter/model capability。
  - provider/model supported reasoning efforts 字段。
- `core.errors` 与 `core.usage`：
  - provider request/response mapping error 诊断字段。
  - normalized usage 与 raw usage。

### OpenAI Adapter

- Responses API generation。
- Responses API streaming。
- Async generation / streaming。
- OpenAI Responses API 合约加固：
  - 不生成未验证的 `stream_options.include_usage`。
  - structured output 映射为 `text.format` JSON Schema。
  - 不兼容 JSON mode / `json_object`。
  - 覆盖 response、content part、text、function/custom tool、reasoning、incomplete、failed/error 与 unknown passthrough stream event。
  - `GenerationStreamAccumulator` 支持文本与 function/custom tool call 重建。
  - provider request / response mapping error 诊断字段。
- Function tool 映射。
- Custom tool 映射：
  - `ToolSpec(type="custom")` -> OpenAI custom tool。
  - `custom_tool_call` -> `FunctionCallItem(type="custom", input=...)`。
  - `FunctionResultItem(tool_type="custom")` -> `custom_tool_call_output`。
  - streaming 复用 tool call event，并用 `metadata["tool_type"]` 标记 custom。
- Provider-native replay：
  - response item 映射时保存 provider 原始 snapshot。
  - 同 provider/API family 重放时默认优先使用 snapshot。
  - 支持 `ReplayPolicy(mode="normalized_only")`。
  - 支持 `ReplayPolicy(mode="require_provider_native")`。
  - 支持 `ReplayPolicy(on_remote_context_invalid="replay_without_remote_context")`。
  - OpenAI assistant message `phase` 与通用 `AssistantMessagePhase` 互相映射。
- Remote context 差分传输：
  - 用户仍传完整 `items`。
  - `RemoteContextHint.covered_item_count` 表达 previous response 覆盖的历史前缀。
  - optimized attempt 发送 suffix。
  - previous response 失效 fallback 重新构造完整 input。
- OpenAI text embeddings。
- Adapter/model capability 查询与用户覆写。

### Pydantic Structured Output

- Optional helper：`whero-vatbrain[pydantic]`。
- `pydantic_output()` 从 Pydantic v2 type 生成 `ResponseFormat`。
- `PydanticOutputSpec.parse_text()` 与 `parse_response()`。
- `ParsedGenerationResponse.output_parsed`。
- `StructuredOutputParseError`。
- OpenAI client `generate_parsed()` / `agenerate_parsed()`。
- 默认 schema name 来自 type 名称，description 来自 type docstring，strict 为 `True`。

## 暂不实现

- 自动 provider routing。
- 自动模型选择或 fallback。
- 自动工具执行。
- 内建 ReAct/agent loop。
- 内部权威模型能力表。
- 对同时支持 Responses API 与 Chat Completions API 的 provider 维护双 generation 调用面。
- 隐式本地文件自动上传。
- Provider-hosted tool、remote tool、MCP tool 的通用 core 抽象。
- Provider conversation 持久化上下文抽象。
- JSON mode / `json_object` structured output 兼容。
- 跨 provider replay。

## 待规划

### v0.4 Volcengine Adapter MVP

- 新增 `impls/python/volcengine-adapter.CN.md`。
- 明确 SDK surface：
  - Responses generation/streaming。
  - Files API。
  - Multimodal embedding。
- 实现 Volcengine provider identity、client 初始化、capability。
- 建立 mapper/stream/files/embeddings fixture tests。
- 保持 generation 不退回 Chat Completions API。
- 根据 OpenAI replay 实现经验决定 Volcengine replay 最小支持面。

### 后续阶段

- Media generation provider implementation。
- Provider-hosted tools 专门设计。
- Provider capability matrix。
- 可选真实 API integration tests。
- API reference 与 migration notes 持续完善。

## 注意事项

- 所有 Python 命令必须使用 `python/.venv`。
- Capability 中无法可靠获取的 model 字段应表达为 unknown。
- Reasoning 与 parallel tool calls 是通用 generation 配置，不应作为 OpenAI 专有参数处理。
- 不同 provider 的 reasoning effort 取值不同，应通过 capability 字段声明支持集合。
- 同时支持 Responses API 与 Chat Completions API 的 provider，Python generation adapter 仅使用 Responses API。
- Provider-side state/cache/previous response 只能作为优化 hint，不改变 Full-context First。
- `RemoteContextHint` 暂只表达 previous response 覆盖范围与本轮 store hint，不包含 cache policy 或远端过期时间。
- `RemoteContextHint.store=None` 依赖 provider 默认存储策略；使用 `previous_response_id` 时，关键是被引用 response 生成时已开启存储。
- Full-context First 要求用户传入完整 `items`，但 provider 请求层可以在覆盖边界明确时只传追加 suffix。
- Response id 失效后的 fallback/replay 必须由用户显式启用；强制 replay 缺少 provider-native snapshot 时应失败而不是静默降级。

## 验证

```bash
cd python
./.venv/bin/python -m pytest
```

当前 v0.3 基线：`96 passed`。
