# vatbrain 知识库索引

状态：持续维护  
最近更新：2026-05-12

## Design

- [design/draft.CN.md](design/draft.CN.md)：项目冷启动草稿，记录 `vatbrain` 的初始目标和早期设计构想。
- [design/high-level-design.CN.md](design/high-level-design.CN.md)：高层次设计方案，定义设计哲学、模块职责、核心抽象、capability 来源与可靠性、非目标、演进路线和 FAQ。
- [design/provider-capability-integration.CN.md](design/provider-capability-integration.CN.md)：Provider 能力整合设计，基于火山方舟资料完善 provider-side state、文件资源、多模态 embedding、media generation 和异步任务等跨厂商抽象；provider-hosted/remote tools 暂缓进入通用 core。
- [design/provider-native-replay.CN.md](design/provider-native-replay.CN.md)：Provider 原生重放设计，规划 provider item snapshot、显式 replay policy、强制 replay、remote context 覆盖范围、OpenAI 差分传输、OpenAI `phase` 语义评估与跨 provider replay 长期 TODO。

## Third-party References

- [3rds/INDEX.md](3rds/INDEX.md)：第三方资料总索引，说明外部厂商资料在知识库中的定位。
- [3rds/volengine/INDEX.md](3rds/volengine/INDEX.md)：火山方舟资料索引，归纳 Responses、Chat、Files、多模态 embedding、图片/视频理解、图片/视频生成、结构化输出、函数调用、reasoning 与 streaming。

## Impls

- [impls/python/openai-adapter.CN.md](impls/python/openai-adapter.CN.md)：Python OpenAI adapter 实现方案，描述首个 provider adapter 的范围、核心模型、OpenAI 映射、测试策略与实现步骤。
- [impls/python/evolution-plan.CN.md](impls/python/evolution-plan.CN.md)：Python 版本演进方案，定义 v0.2 OpenAI 合约加固、v0.3 core API family 扩展、v0.4 Volcengine adapter MVP、v0.5 hosted tools/media generation 和 v0.6 稳定化路线。
- [impls/python/v0.2-responses-contract-hardening.CN.md](impls/python/v0.2-responses-contract-hardening.CN.md)：Python v0.2 Responses Contract Hardening 设计方案，细化 OpenAI Responses API 参数映射、structured output、streaming event、stream accumulator、错误映射与验收测试。
- [impls/python/v0.3-core-api-family-expansion.CN.md](impls/python/v0.3-core-api-family-expansion.CN.md)：Python v0.3 Core API Family Expansion 实现方案，规划 items、generation、embedding、resources、media、function/custom tools、capabilities 的 core 模型扩展、兼容策略、测试方案与实施步骤。
- [impls/python/pydantic-structured-output.CN.md](impls/python/pydantic-structured-output.CN.md)：Python Pydantic Structured Output 便捷层方案与实现记录，说明可选 Pydantic v2 helper、strict schema 生成、最终响应解析、client convenience 与测试策略。
- [impls/python/STATUS.md](impls/python/STATUS.md)：Python 实现状态，记录当前完成内容、计划实现项和暂不实现项。

## User Docs

- [user/python/quickstart.CN.md](user/python/quickstart.CN.md)：Python 用户指南，说明第一阶段编程模型、OpenAI client、generation、remote context 覆盖范围、streaming、function/custom 工具调用、embedding 和 capability 用法。
- [user/python/pydantic-structured-output.CN.md](user/python/pydantic-structured-output.CN.md)：Python Pydantic Structured Output 编程模型，说明 Pydantic helper、client convenience、strict schema、错误处理与流式限制。
- [user/python/STATUS.md](user/python/STATUS.md)：Python 用户文档状态，记录已完成内容与待完善项。
