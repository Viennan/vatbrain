# Python 版本演进方案

状态：演进计划  
日期：2026-05-06  
最近更新：2026-05-10

## 背景

Python 是 `vatbrain` 的参考实现语言。第一阶段已经完成基础包结构、core 基础模型、OpenAI provider client、OpenAI Responses API generation/streaming、function tool 映射、text embedding、usage 和 capability 基础表达。

后续演进需要吸收高层设计和 provider 能力整合设计中的新边界：

- generation、embedding、resource/file、media generation 是独立 API 家族。
- 对同时支持 Responses API 与 Chat Completions API 的 provider，generation adapter 仅使用 Responses API。
- provider-side state/cache/previous response 只作为优化 hint，不改变 Full-context First。
- v0.3 先只抽象 user-executed function tools；provider-hosted tools、remote tools、MCP tools 后续再设计。
- reasoning 既是配置，也是可能出现的输出 item。
- 文件资源具有独立生命周期。
- embedding 需要支持多模态输入、instructions、dense/sparse vectors。

参考设计：

- [design/high-level-design.CN.md](design/high-level-design.CN.md)
- [design/provider-capability-integration.CN.md](design/provider-capability-integration.CN.md)
- [impls/python/openai-adapter.CN.md](impls/python/openai-adapter.CN.md)
- [3rds/volengine/INDEX.md](3rds/volengine/INDEX.md)

## 当前实现阶段

当前 Python 实现可定义为 `v0.1 alpha`：

- 包结构：已建立。
- core：已包含 item、generation、embedding、tools、usage、capability、errors。
- OpenAI adapter：已基于 Responses API 实现 generation 与 streaming。
- Tools：已支持 function tool 声明、function call 输出、function result 回填。
- Embedding：已支持 OpenAI text embedding。
- 测试：已有不依赖真实 API 的单元测试。

当前主要缺口：

- OpenAI Responses API 事件覆盖仍不完整。
- OpenAI SDK 合约测试仍偏少。
- `Item` 只覆盖文本、图片、function call/result，尚未覆盖 file/audio/video/reasoning。
- `EmbeddingRequest` 尚不支持 instructions、sparse embedding 和真正多模态输出。
- capability 仍是第一阶段扁平布尔字段，尚未按 API family 系统表达。
- resource/file、media generation、task/operation 还没有 core 模型。
- 还没有 Volcengine provider adapter。

## 演进原则

### 先稳定 core，再扩 provider

新增 provider 前，应先让 core 模型能表达目标 provider 的必要语义。避免在 provider adapter 内堆积 provider-specific 临时结构，导致后续无法跨 provider 复用。

### Responses-only for dual API providers

OpenAI、火山方舟等同时支持 Responses API 与 Chat Completions API 的 provider，Python adapter 的 generation 实现只使用 Responses API。Chat Completions API 不作为兼容 fallback 或平行实现路径。

如果未来某个 provider 不提供 Responses 风格 API，才允许将 Chat/Completions 风格 API 映射到 `vatbrain` generation 模型。

### 保持 Full-context First

即使 provider 支持 `previous_response_id`、stored response、context cache 或 conversation，Python API 的推荐编程模型仍是用户传入完整语义上下文。

provider-side state 通过 `RemoteContextHint` 或 `provider_options` 的明确字段表达，仅作为优化提示。v0.3 的 `RemoteContextHint` 暂不表达 provider conversation 持久化上下文。

当使用 `previous_response_id` 优化请求时，用户仍传入完整 `items`。如果 provider response 已覆盖其中的历史前缀，应通过 `RemoteContextHint.covered_item_count` 显式说明覆盖范围；adapter 才能在 provider 请求层只发送追加 suffix。覆盖范围缺失时不得猜测 history/append 边界。

当 `previous_response_id` 或 provider-side context 失效时，Python client 不应默认静默重试。后续版本应提供显式 replay policy：用户可以选择仅抛错、移除失效 remote context 后用完整 `items` 重放，或要求强制 provider-native replay。完整设计见 [design/provider-native-replay.CN.md](design/provider-native-replay.CN.md)。

### 小步发布，测试闭环

每个阶段都应具备单元测试和 mapping fixture 测试。真实 API integration test 可以作为可选测试层，不进入默认 CI。

### 文档与行为同步

任何 public API、用户可见行为或编程模型变化，都需要同步更新 `docs/user/python` 与 `docs/impls/python/STATUS.md`。

## 版本路线

### v0.2：Responses contract hardening

目标：巩固 OpenAI adapter，稳定第一阶段 public API，避免在 core 扩展前留下 provider 合约债务。

#### 范围

- 修正 OpenAI Responses API 参数映射，特别是 streaming options 与当前 SDK 类型的契合度。
- 扩充 OpenAI streaming event 映射：
  - response lifecycle。
  - output item lifecycle。
  - content part lifecycle。
  - text delta/done。
  - function call arguments delta/done。
  - reasoning/summary 事件的 raw passthrough 或初步 normalized event。
  - failed/incomplete/error。
- 增加 stream accumulator helper，用于从事件流重建 `GenerationResponse`。
- 增强 structured output 映射，明确 `ResponseFormat` 的 JSON schema 结构。
- 增强 provider error mapping，至少区分 request error、response mapping error、unsupported capability。
- 调整 `openai` 依赖下限到实际验证过的 Responses API SDK 范围。

#### 非范围

- 不新增 Volcengine adapter。
- 不实现 media generation。
- 不改变 `OpenAIClient.generate()` 的基本调用方式。

#### 主要文件

```text
python/whero/vatbrain/core/generation.py
python/whero/vatbrain/core/errors.py
python/whero/vatbrain/providers/openai/mapper.py
python/whero/vatbrain/providers/openai/stream.py
python/whero/vatbrain/providers/openai/client.py
python/tests/unit/test_openai_*.py
```

#### 验证

- `python/.venv/bin/python -m pytest`
- 新增 OpenAI Responses create params fixture tests。
- 新增 OpenAI stream event fixture tests。

### v0.3：Core API family expansion

目标：让 Python core 能表达 provider 能力整合设计中的核心语义，为 Volcengine adapter 做准备。

#### 范围

##### Items

扩展 `core.items`：

```text
PartKind
- text
- image
- audio
- video
- file

ItemKind
- message
- function_call
- function_result
- reasoning
```

新增：

- `AudioPart`
- `VideoPart`
- `FilePart`
- `ReasoningItem`
- 可选 `ArtifactPart`，若 media generation 在同阶段进入 core。

`FilePart` 应支持：

- provider file id。
- URL。
- base64/data URL。
- local path metadata。
- MIME type。
- media type。
- provider 标识。

本阶段只定义模型，不默认执行本地文件上传。

##### Generation

扩展 `core.generation`：

- `RemoteContextHint`
- `ReplayPolicy` 与 provider-native replay 策略
- `ReasoningConfig.mode`
- 更明确的 `ReasoningConfig.effort`
- `ResponseFormat` 的 JSON schema name/description/schema/strict
- stream event metadata 字段增强

##### Embeddings

扩展 `core.embeddings`：

- `EmbeddingRequest.instructions`
- `SparseEmbedding`
- `EmbeddingVector.dense`
- `EmbeddingVector.sparse`
- modality-aware usage metadata

保持现有 text embedding 用法兼容：

```python
client.embed(model="text-embedding-3-small", inputs=["hello"])
```

##### Resources

新增 `core.resources`：

```text
FileUploadRequest
FileResource
FileStatus
FilePurpose
FilePreprocessConfig
```

##### Media

新增 `core.media` 的最小模型：

```text
MediaArtifact
ImageGenerationRequest
ImageGenerationResponse
ImageGenerationStreamEvent
MediaGenerationTask
TaskStatus
```

本阶段可以只定义模型和测试，不接入 provider。

##### Tools

扩展 `core.tools`：

- `ToolExecutionOwner`: user/provider/remote。
- `FunctionToolSpec`，保留现有 `ToolSpec` 的兼容别名。
- 暂不新增 `HostedToolSpec`、`RemoteToolSpec` 或 `MCPToolSpec`。

##### Capabilities

将 capability 从扁平字段逐步演进到 API family 结构：

```text
GenerationCapability
EmbeddingCapability
ResourceCapability
MediaGenerationCapability
ToolCapability
AdapterCapability
ModelCapability
```

`GenerationCapability` 应包含 provider/adapter 支持的 reasoning effort 字符串集合；`ModelCapability.supported_reasoning_efforts` 用于表达具体 model 的更窄集合或用户覆写。

保留第一阶段字段的兼容属性或迁移说明，避免立即破坏 OpenAI adapter。

#### 非范围

- 不要求 OpenAI adapter 立刻支持所有新增 part。
- 不实现 Volcengine API 调用。
- 不实现自动工具执行。
- 不实现 response id 失效后的自动 retry/fallback；provider-native replay 基础能力先服务 OpenAI 同 provider 重放。

#### 主要文件

```text
python/whero/vatbrain/core/items.py
python/whero/vatbrain/core/generation.py
python/whero/vatbrain/core/embeddings.py
python/whero/vatbrain/core/resources.py
python/whero/vatbrain/core/media.py
python/whero/vatbrain/core/tools.py
python/whero/vatbrain/core/capabilities.py
python/whero/vatbrain/__init__.py
python/tests/unit/test_*.py
```

#### 验证

- core dataclass construction tests。
- backward compatibility tests for existing OpenAI usage。
- embedding dense/sparse shape tests。
- capability unknown/source/reliability tests。

### v0.4：Volcengine adapter MVP

目标：实现第二个 provider adapter，用火山方舟验证 Python core 的跨厂商表达能力。

#### Provider identity

- provider id：`volcengine`
- client：`VolcengineClient`
- API key 环境变量：`ENV_VATBRAIN_VOLCENGINE_API_KEY`
- 默认 base URL：`https://ark.cn-beijing.volces.com/api/v3`

#### 调用面原则

- generation 仅使用 Responses API。
- 不引入 Chat Completions API 调用路径。
- Chat API 资料只作为参数语义和迁移对照。

#### 范围

##### Generation

支持：

- text input。
- image input。
- video input by URL/base64/file id。
- `ReasoningConfig.mode` -> `thinking.type`。
- `ReasoningConfig.effort` -> `reasoning.effort`。
- function tools。
- function call output。
- `RemoteContextHint.previous_response_id`。
- `RemoteContextHint.cache_policy` -> `caching`。
- `RemoteContextHint.store` -> `store`。
- structured output via `text.format`。
- usage mapping。

##### Streaming

支持 Responses API streaming：

- text delta/done。
- reasoning summary delta/done。
- output item added/done。
- function call arguments delta/done。
- response completed/failed。
- unknown event raw passthrough。

##### Files

支持：

- `upload_file`
- `retrieve_file`
- `list_files`
- `delete_file`
- 可选 `wait_for_file_processing`

文件预处理配置支持 video fps 与 raw provider_options。

##### Embedding

支持火山多模态 embedding：

- text。
- image URL/data URL。
- video URL/data URL。
- instructions。
- dimensions。
- encoding_format。
- sparse embedding。
- usage mapping。

##### Capabilities

声明 adapter capability：

- generation。
- stream generation。
- function tools。
- provider-side state/cache hints。
- file resources。
- multimodal embedding。
- sparse embedding。
- usage mapping。

model capability 仍默认 unknown，允许用户 overrides。

##### Replay

Provider-native replay 基础能力已优先在 OpenAI adapter 上实现；v0.4 可根据 OpenAI 实现经验决定 Volcengine 是否同步支持：

- 已新增 `ProviderItemSnapshot`，保存同 provider/API family 的原始 item payload。
- 已新增 `ReplayPolicy`，支持 `normalized_only`、`prefer_provider_native`、`require_provider_native`。
- 已支持 `require_provider_native` 作为强制 replay 选项，缺少可重放 snapshot 时抛错。
- 已支持 `on_remote_context_invalid="replay_without_remote_context"`；默认 `raise`，只有用户显式启用时才清除失效 `previous_response_id` 并用完整 `items` 重试一次。
- OpenAI Responses assistant message 的 `phase` 已通过 snapshot 保真，并已通过 `AssistantMessagePhase(commentary | final_answer)` 进入通用 `MessageItem`。
- 跨 provider replay 暂不支持，记录为长期 TODO。

待补充：

- `RemoteContextHint.covered_item_count`，用于表达 `previous_response_id` 覆盖完整 `items` 的前缀长度。
- OpenAI provider 差分传输：存在 `previous_response_id` 且覆盖边界明确时发送 suffix，失效 fallback 重新构造完整 input。

#### 非范围

- 不支持 Chat Completions API。
- 不支持跨 provider replay。
- 不自动执行 function tools。
- 不自动 provider routing。
- 不自动上传本地文件，除非用户显式调用 file API。
- 不支持 image/video generation；留给 v0.5。
- 不支持 hosted tools 的高级封装；可通过 provider_options 临时透传。

#### 目录结构

```text
python/whero/vatbrain/providers/volcengine/
  __init__.py
  capabilities.py
  client.py
  mapper.py
  stream.py
  files.py
  embeddings.py
```

测试：

```text
python/tests/unit/test_volcengine_client.py
python/tests/unit/test_volcengine_generation_mapper.py
python/tests/unit/test_volcengine_stream_mapper.py
python/tests/unit/test_volcengine_files.py
python/tests/unit/test_volcengine_embeddings.py
```

#### SDK 选择

优先策略：

- generation/files 可优先使用 OpenAI-compatible SDK surface，前提是 Responses/Files 参数能完整表达。
- multimodal embeddings 与 content generation task 若 OpenAI SDK surface 不覆盖，则使用 `volcenginesdkarkruntime` 或直接 HTTP adapter。

依赖策略：

- 将 Volcengine SDK 作为 optional dependency，例如 `.[volcengine]`。
- core 和 OpenAI adapter 不依赖 Volcengine SDK。

### v0.5：Hosted tools and media generation

目标：覆盖火山方舟 provider-hosted tools、图片生成和视频生成，完善 media API family。

#### 范围

##### Hosted tools

支持声明映射：

- web search。
- image process。
- knowledge search。
- MCP。

要求：

- 另行设计 provider-hosted/remote tool 的执行责任模型，不预设 v0.3 core 中存在 `ToolExecutionOwner.PROVIDER` 或 `REMOTE`。
- 不自动执行 user function tools。
- provider beta headers 或 provider-specific flags 明确放入 adapter/provider options。

##### Image generation

支持：

- text-to-image。
- image-to-image/reference image。
- output format。
- response format。
- size/resolution。
- stream events。
- partial image/artifact events。
- usage mapping。

##### Video generation

支持：

- create task。
- retrieve task。
- poll helper。
- task status mapping。
- artifact mapping。
- error mapping。

#### 非范围

- 不做图像/视频编辑的所有 provider 专有高级参数标准化。
- 不内置媒体文件下载、保存或转码。
- 不自动调用 web search 或 MCP；只映射 provider-hosted tool 声明。

### v0.6：Stabilization and compatibility

目标：稳定 public API，完善文档和测试策略。

范围：

- API reference。
- migration notes。
- provider capability matrix。
- optional integration tests。
- error hierarchy refinement。
- type-check/lint 可选引入。
- deprecation policy。

## 测试策略

### Unit tests

默认测试层，不调用真实 provider：

- core model construction。
- request mapper。
- response mapper。
- stream event mapper。
- error wrapping。
- capability unknown/source/reliability。

### Fixture tests

使用本地 JSON/dict fixture 模拟 provider 响应：

- OpenAI Responses events。
- Volcengine Responses events。
- Volcengine Files responses。
- Volcengine multimodal embeddings responses。
- media generation task responses。

### Optional integration tests

真实 API 测试必须默认关闭，通过环境变量显式启用：

```text
ENV_VATBRAIN_RUN_INTEGRATION_TESTS=1
ENV_VATBRAIN_OPENAI_API_KEY=...
ENV_VATBRAIN_VOLCENGINE_API_KEY=...
```

integration tests 不应影响默认 `pytest`。

## 文档同步计划

每个阶段完成时同步更新：

- [impls/python/STATUS.md](impls/python/STATUS.md)
- [user/python/quickstart.CN.md](user/python/quickstart.CN.md)
- [user/python/STATUS.md](user/python/STATUS.md)
- [INDEX.md](INDEX.md)

新增 Volcengine adapter 时，应新增：

```text
docs/impls/python/volcengine-adapter.CN.md
docs/user/python/volcengine-quickstart.CN.md
```

## 风险与决策点

### Core 兼容风险

`Item`、`EmbeddingVector`、`AdapterCapability` 扩展可能影响现有 OpenAI adapter。应保留兼容构造方式和旧字段读取方式，至少维持 v0.1 用户示例可运行。

### SDK 表面差异

火山方舟存在 OpenAI-compatible SDK surface 与 Ark SDK surface。实现前需要针对每个 API family 决定 SDK 选择，并用 fixture test 锁定映射。generation 不应退回 Chat Completions API。

### Provider-specific 参数边界

如 image process、knowledge search、MCP、video generation 高级参数，短期可以通过 provider-specific model 或 provider_options 表达。只有具备跨 provider 语义时才进入 core 通用字段。

### Provider-native replay 与通用抽象边界

OpenAI assistant message `phase` 暴露了一个重要边界：部分 provider 原生 item 字段会影响同 provider follow-up/replay 行为，但不应该为每个字段都扩展 provider-specific mapper 分支。后续实现应优先保存 provider-native snapshot，用 replay policy 决定是否使用原始 payload。具备跨 provider 潜力的字段，例如 assistant output phase，可以再提升为通用抽象。

跨 provider replay 暂不支持。长期 TODO 是提供 replay compatibility report，而不是直接把 provider-native payload 转换给另一个 provider。

### 自动上传本地文件

火山方舟 SDK 支持部分本地路径便捷上传，但 `vatbrain` 不应默认隐式上传。若实现便捷 API，必须是显式方法或显式 `auto_upload=True`。

### AI 协助下的实施成本

在 AI 协助下，core dataclass、mapper、fixture test 和文档同步的单位成本较低，适合小步快跑。真正需要谨慎投入的是 provider SDK 合约验证、真实 API 行为差异、streaming event 完整性和 public API 稳定性。

## 建议近期任务

1. 先做 v0.2，修正和加固 OpenAI Responses 合约。
2. 再做 v0.3 的 core 模型扩展，保持 OpenAI adapter 兼容。
3. 为 v0.4 新增 `volcengine-adapter.CN.md`，明确 SDK surface 后再编码。
4. Volcengine MVP 优先覆盖 Responses generation、Files API 和 multimodal embedding。
5. 根据 Volcengine adapter 实现经验评估 provider-native replay 在第二 provider 上的最小支持面。
6. hosted tools、image generation、video generation 放入 v0.5。
