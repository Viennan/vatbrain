# Python 实现状态

状态：v0.3 已实现，v0.4 规划中  
日期：2026-05-05  
最近更新：2026-05-10

## 当前范围

Python 是 `vatbrain` 的参考实现语言。第一阶段目标是建立基础包结构，并实现 OpenAI SDK adapter。

## 已完成

- 高层设计文档已建立：[design/high-level-design.CN.md](design/high-level-design.CN.md)。
- Provider 能力整合设计已建立：[design/provider-capability-integration.CN.md](design/provider-capability-integration.CN.md)。
- Python OpenAI adapter 实现方案已建立：[impls/python/openai-adapter.CN.md](impls/python/openai-adapter.CN.md)。
- Python 版本演进方案已建立：[impls/python/evolution-plan.CN.md](impls/python/evolution-plan.CN.md)。
- Python v0.3 Core API Family Expansion 实现方案已建立：[impls/python/v0.3-core-api-family-expansion.CN.md](impls/python/v0.3-core-api-family-expansion.CN.md)。
- Python 包脚手架与 `pyproject.toml`。
- core 模型：
  - item。
  - generation request/response/event。
  - embedding request/response。
  - resource/file request/resource/status。
  - media artifact/image generation/task。
  - tools。
  - usage。
  - capability。
  - errors。
- OpenAI provider client。
- OpenAI Responses API generation。
- OpenAI Responses API streaming。
- OpenAI Responses API 合约加固：
  - 修正 Responses streaming options 映射，不再生成未验证的 `stream_options.include_usage`。
  - 增强 structured output 到 `text.format` 的 JSON Schema 映射，不兼容 JSON mode / `json_object`。
  - 扩展 streaming event 覆盖 response、content part、text、function call、reasoning、incomplete、failed/error 与 unknown passthrough。
  - 新增 `GenerationStreamAccumulator` 用于从流式事件重建响应。
  - 增强 provider request / response mapping error 诊断字段。
- Python core API family expansion：
  - 新增 `AudioPart`、`VideoPart`、`FilePart` 与 `ReasoningItem`。
  - 新增 `RemoteContextHint`，并保持 Full-context First。
  - 新增 `ProviderItemSnapshot` 专门字段与 `AssistantMessagePhase` 通用抽象。
  - 新增 `ReplayPolicy`，支持 normalized-only、prefer provider-native 与强制 replay。
  - 扩展 embedding instructions、dense/sparse vector 表达。
  - 新增 `core.resources` 与 `core.media` 模型。
  - 扩展 user-executed function tool spec，并暂缓 provider-hosted/remote tool 抽象。
  - 扩展 API family capability，同时保留 v0.2 兼容字段。
- OpenAI function tool 协议映射。
- OpenAI provider-native replay 基础实现：
  - response item 映射时保存 provider 原始 snapshot。
  - 同 provider/API family 重放时优先使用 snapshot payload。
  - 支持 `ReplayPolicy(mode="normalized_only")` 禁用 snapshot replay。
  - 支持 `ReplayPolicy(mode="require_provider_native")` 强制 provider-native replay。
  - 支持 `ReplayPolicy(on_remote_context_invalid="replay_without_remote_context")` 在 previous response 失效时移除 `previous_response_id` 并重试一次。
  - OpenAI assistant message `phase` 与通用 `AssistantMessagePhase` 互相映射。
- OpenAI text embeddings。
- 通用 client 初始化参数：`api_key`、`base_url`、`timeout`、`max_retries`。
- OpenAI API key 环境变量：`ENV_VATBRAIN_OPENAI_API_KEY`。
- 单元测试。

## 待完善

- Provider-native replay 后续增强：
  - 新增 remote context 覆盖范围模型：`RemoteContextHint.covered_item_count`。
  - OpenAI provider 差分传输：存在 `previous_response_id` 且覆盖边界明确时发送 suffix。
  - OpenAI fallback 行为需重新构造请求：optimized attempt 发送 suffix，失效 fallback 发送完整 `items`。
  - 跨 provider replay 暂不支持，作为长期 TODO。
- 多模态 generation 输入的真实 SDK 集成验证。
- Volcengine adapter MVP：
  - Responses API generation/streaming。
  - Files API。
  - multimodal embedding。
  - 不引入 Chat Completions API 调用路径。
- 用户文档与示例。

## 暂不实现

- 自动 provider routing。
- 自动模型选择或 fallback。
- 自动工具执行。
- 内建 ReAct/agent loop。
- 内部权威模型能力表。
- 对同时支持 Responses API 与 Chat Completions API 的 provider 维护双 generation 调用面。
- 隐式本地文件自动上传。
- provider-hosted tool、remote tool、MCP tool 的通用 core 抽象。
- provider conversation 持久化上下文抽象。

## 注意事项

- 所有 Python 命令必须使用 `python/.venv`。
- capability 中无法可靠获取的 model 字段应表达为 unknown。
- reasoning 与 parallel tool calls 是通用 generation 配置，不应作为 OpenAI 专有参数处理。
- 同时支持 Responses API 与 Chat Completions API 的 provider，Python generation adapter 仅使用 Responses API。
- provider-side state/cache/previous response 只能作为优化 hint，不改变 Full-context First。
- Full-context First 要求用户传入完整 `items`，但 provider 请求层可以在覆盖边界明确时只传追加 suffix。
- response id 失效后的 fallback/replay 必须由用户显式启用；强制 replay 缺少 provider-native snapshot 时应失败而不是静默降级。

## 验证

- `python/.venv/bin/python -m pytest`：通过。
