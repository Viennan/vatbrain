# Python 实现状态

状态：第一阶段已实现  
日期：2026-05-05

## 当前范围

Python 是 `vatbrain` 的参考实现语言。第一阶段目标是建立基础包结构，并实现 OpenAI SDK adapter。

## 已完成

- 高层设计文档已建立：[design/high-level-design.CN.md](design/high-level-design.CN.md)。
- Python OpenAI adapter 实现方案已建立：[impls/python/openai-adapter.CN.md](impls/python/openai-adapter.CN.md)。
- Python 包脚手架与 `pyproject.toml`。
- core 模型：
  - item。
  - generation request/response/event。
  - embedding request/response。
  - tools。
  - usage。
  - capability。
  - errors。
- OpenAI provider client。
- OpenAI Responses API generation。
- OpenAI Responses API streaming。
- OpenAI function tool 协议映射。
- OpenAI text embeddings。
- 通用 client 初始化参数：`api_key`、`base_url`、`timeout`、`max_retries`。
- OpenAI API key 环境变量：`ENV_VATBRAIN_OPENAI_API_KEY`。
- 单元测试。

## 待完善

- 更完整的 OpenAI Responses API 事件类型覆盖。
- 更细粒度的 provider error 映射。
- 多模态 generation 输入的真实 SDK 集成验证。
- 用户文档与示例。

## 暂不实现

- 非 OpenAI provider。
- 自动 provider routing。
- 自动模型选择或 fallback。
- 自动工具执行。
- 内建 ReAct/agent loop。
- 内部权威模型能力表。
- 多模态 embedding。

## 注意事项

- 所有 Python 命令必须使用 `python/.venv`。
- capability 中无法可靠获取的 model 字段应表达为 unknown。
- reasoning 与 parallel tool calls 是通用 generation 配置，不应作为 OpenAI 专有参数处理。

## 验证

- `python/.venv/bin/python -m pytest`：通过。
