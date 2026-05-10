# Python 用户文档状态

状态：v0.3 已更新  
日期：2026-05-05
最近更新：2026-05-10

## 已完成

- Python 快速开始与编程模型：[user/python/quickstart.CN.md](user/python/quickstart.CN.md)。
- OpenAI provider client 的基本使用方式。
- generation、streaming、stream accumulator、JSON Schema-only structured output、工具调用、embedding、capability 的基础示例。
- 说明 OpenAI Responses API 下 `StreamOptions(include_usage=True)` 不映射为 `stream_options.include_usage`。
- 说明 provider-native snapshot、ReplayPolicy、OpenAI `phase` 保真、`AssistantMessagePhase` 基础用法和 response id 失效 fallback。
- 说明 v0.3 新增 core models、RemoteContextHint、多模态 embedding 表达，以及这些模型与当前 OpenAI adapter 支持范围的边界。
- 说明 `previous_response_id` 优化下仍需传入完整 `items`，并用 `RemoteContextHint.covered_item_count` 表达远端已覆盖的历史前缀。
- 说明 `RemoteContextHint.store=None` 依赖 provider 默认存储策略；引用 `previous_response_id` 时，需要确保被引用 response 生成时已开启存储。
- 说明 provider-hosted tool、remote tool、MCP tool 和 provider conversation 持久化上下文暂不作为通用 core 抽象暴露。

## 待完善

- 更完整的 API reference。
- 真实 OpenAI 调用示例。
- 常见错误处理指南。
- 多模态输入示例。
- 与未来 provider adapter 对齐后的跨厂商用法说明。
