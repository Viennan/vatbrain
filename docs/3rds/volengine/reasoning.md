深度思考指模型在回答前，对问题进行分析及多步骤规划，再尝试解决问题。擅长处理编程、科学推理、智能体工作流等复杂及抽象场景。启用深度思考后，会在指定字段返回思维链内容，可基此观察和使用模型推导内容。
说明
方舟平台的新用户？获取 API Key 及 开通模型等准备工作，请参见 快速入门。
快速开始

输入

思维链

回答

Plain
复制
我要研究深度思考模型与非深度思考模型区别的课题，怎么体现我的专业性

Plain
复制
用户现在要做深度思考模型和非深度思考模型区别的课题，需要体现专业性。首先得明确，专业性体现在哪里？
...
要在“深度思考模型与非深度思考模型区别”的课题中体现专业性，核心在于**严谨的概念界定、系统的对比框架、科学的方法论支撑、以及深度的理论与实践结合**。以下是具体的实施路径，从研究框架到细节落地，帮你构建专业的研究体系：

Plain
复制
### **一、第一步：明确概念边界——避免泛化，精准定义**
专业性的起点是**清晰的概念界定**，避免将“深度模型”等同于“深度思考模型”，也避免将“非深度模型”简化为“传统模型”。需基于学术共识和研究目标给出操作性定义：
...
通过以上路径，你的课题将从“表面对比”升级为“本质穿透”，充分体现专业性与研究深度。祝你研究顺利！

示例代码

Curl
Python
Go
Java
OpenAI SDK
curl https://ark.cn-beijing.volces.com/api/v3/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seed-2-0-lite-260215",
    "messages": [
        {
            "role": "user",
            "content": "我要研究深度思考模型与非深度思考模型区别的课题，怎么体现我的专业性"
        }
    ]
  }'

您可按需替换 Model ID。Model ID 查询见 模型列表。
package main

import (
    "context"
    "fmt"
    "os"
    "time"
    "github.com/volcengine/volcengine-go-sdk/service/arkruntime"
    "github.com/volcengine/volcengine-go-sdk/service/arkruntime/model"
    "github.com/volcengine/volcengine-go-sdk/volcengine"
)

func main() {
    client := arkruntime.NewClientWithApiKey(
        // Get API Key：https://console.volcengine.com/ark/region:ark+cn-beijing/apikey
        os.Getenv("ARK_API_KEY"),
        // The base URL for model invocation
        arkruntime.WithBaseUrl("https://ark.cn-beijing.volces.com/api/v3"),
        // Deep thinking takes longer; set a larger timeout, with 1,800 seconds or more recommended
        arkruntime.WithTimeout(30*time.Minute),
    )
    ctx := context.Background()
    req := model.CreateChatCompletionRequest{
        // Replace with Model ID
       Model: "doubao-seed-2-0-lite-260215",
        Messages: []*model.ChatCompletionMessage{
            {
                Role: model.ChatMessageRoleUser,
                Content: &model.ChatCompletionMessageContent{
                    StringValue: volcengine.String("我要研究深度思考模型与非深度思考模型区别的课题，怎么体现我的专业性"),
                },
            },
        },
    }

resp, err := client.CreateChatCompletion(ctx, req)
    if err != nil {
        fmt.Printf("standard chat error: %v\n", err)
        return
    }
    // When deep thinking is triggered, print the chain-of-thought content
    if resp.Choices[0].Message.ReasoningContent != nil {
        fmt.Println(*resp.Choices[0].Message.ReasoningContent)
    }
    fmt.Println(*resp.Choices[0].Message.Content.StringValue)
}

package com.ark.sample;

import com.volcengine.ark.runtime.model.completion.chat.ChatCompletionContentPart;
import com.volcengine.ark.runtime.model.completion.chat.ChatCompletionRequest;
import com.volcengine.ark.runtime.model.completion.chat.ChatMessage;
import com.volcengine.ark.runtime.model.completion.chat.ChatMessageRole;
import com.volcengine.ark.runtime.service.ArkService;
import java.util.*;
import java.util.concurrent.TimeUnit;
import java.time.Duration;

public class ChatCompletionsExample {
    public static void main(String[] args) {
        // Get API Key：https://console.volcengine.com/ark/region:ark+cn-beijing/apikey
        String apiKey = System.getenv("ARK_API_KEY");
        ArkService arkService = ArkService.builder()
                .apiKey(apiKey)
                .timeout(Duration.ofMinutes(30))// Deep thinking takes longer; set a larger timeout, with 1,800 seconds or more recommended
                .baseUrl("https://ark.cn-beijing.volces.com/api/v3")// The base URL for model invocation
                .build();
        List<ChatMessage> chatMessages = new ArrayList<>();
        ChatMessage userMessage = ChatMessage.builder()
                .role(ChatMessageRole.USER)
                .content("我要研究深度思考模型与非深度思考模型区别的课题，怎么体现我的专业性")
                .build();
        chatMessages.add(userMessage);
        ChatCompletionRequest chatCompletionRequest = ChatCompletionRequest.builder()
                .model("doubao-seed-2-0-lite-260215")//Replace with Model ID
                .messages(chatMessages)
                .build();
        try {
            arkService.createChatCompletion(chatCompletionRequest)
                    .getChoices()
                    .forEach(choice -> {                    
                        if (choice.getMessage().getReasoningContent() != null) {
                            System.out.println(choice.getMessage().getReasoningContent());
                        }
                        System.out.println(choice.getMessage().getContent());
                    });
        } catch (Exception e) {
            System.out.println(e.getMessage());
        } finally {
            // Shut down the service executor
            arkService.shutdownExecutor();
        }
    }
}

import os
from openai import OpenAI

client = OpenAI(
    # Get API Key：https://console.volcengine.com/ark/region:ark+cn-beijing/apikey
    api_key=os.environ.get("ARK_API_KEY"), 
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    # Deep thinking takes longer; set a larger timeout, with 1,800 seconds or more recommended
    timeout=1800,
    )
completion = client.chat.completions.create(
    # Replace with Model ID
    model = "doubao-seed-2-0-lite-260215",
    messages=[
        {"role": "user", "content": "我要研究深度思考模型与非深度思考模型区别的课题，怎么体现我的专业性"}
    ]
)
# When deep thinking is triggered, print the chain-of-thought content
if hasattr(completion.choices[0].message, 'reasoning_content'):
    print(completion.choices[0].message.reasoning_content)
print(completion.choices[0].message.content)

Python
复制
import os
# Install SDK:  pip install 'volcengine-python-sdk[ark]'
from volcenginesdkarkruntime import Ark 

client = Ark(
    # The base URL for model invocation
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    # Get API Key：https://console.volcengine.com/ark/region:ark+cn-beijing/apikey
    api_key=os.getenv('ARK_API_KEY'), 
    # Deep thinking takes longer; set a larger timeout, with 1,800 seconds or more recommended
    timeout=1800,
)

completion = client.chat.completions.create(
    # Replace with Model ID
    model = "doubao-seed-2-0-lite-260215",
    messages=[
        {"role": "user", "content": "我要研究深度思考模型与非深度思考模型区别的课题，怎么体现我的专业性"}
    ]
)
# When deep thinking is triggered, print the chain-of-thought content
if hasattr(completion.choices[0].message, 'reasoning_content'):
    print(completion.choices[0].message.reasoning_content)
print(completion.choices[0].message.content)

模型及API
支持的模型：深度思考能力。
支持的API ：
Responses API：新推出的 API，简洁上下文管理，增强工具调用能力，缓存能力降低成本，新业务及用户推荐。
Chat API：使用广泛的 API，存量业务迁移成本低。
基础使用
多轮对话
组合使用系统消息、模型消息以及用户消息，可以实现多轮对话。当需要持续在一个主题内对话，可以将历史轮次的对话记录输入给模型。

传入方式

手动管理上下文

通过ID管理上下文

使用示例

JSON
复制
...
    "model": "doubao-seed-2-0-lite-260215",
    "messages":[
        {"role": "user", "content": "Hi, tell a joke."},
        {"role": "assistant", "content": "Why did the math book look sad? Because it had too many problems! 😄"},
        {"role": "user", "content": "What's the punchline of this joke?"}
    ]
...

JSON
复制
...
    "model": "doubao-seed-2-0-lite-260215",
    "previous_response_id":"<id>",
    "input": "What is the punchline of this joke?"
...

API

Chat API

Responses API

在构建多轮对话的上下文时：
模型版本在251228之前：剔除历史对话的 reasoning_content 字段，仅保留 role 和 content。方舟会尝试忽略该字段，但显式剔除能确保请求结构的正确性。
doubao-seed-1.8及后续模型：保留历史对话的 reasoning_content 字段，由模型自行判断是否将该字段加入到推理输入中。
更多说明及完整示例请参见 上下文管理。
流式输出
随着大模型输出，动态输出内容，无需等待模型推理完毕，即可看到中间输出过程内容。

预览

优势

改善等待体验：无需等待完整内容生成完毕，可立即处理过程内容。
实时过程反馈：多轮交互场景，实时了解任务当前的处理阶段。
更高的容错性：中途出错，也能获取到已生成内容，避免非流式输出失败无返回的情况。
简化超时管理：保持客户端与服务端的连接状态，避免复杂任务耗时过长而连接超时。

通过配置 stream 为 true，来启用流式输出。

JSON
复制
...
    "model": "doubao-seed-2-0-lite-260215",
    "messages": [
        {"role": "user", "content": "深度思考模型与非深度思考模型区别"}
    ],
    "stream": true
 ...

完整示例及更多说明请参见 流式输出。
开启/关闭深度思考
提供 thinking 字段控制是否关闭深度思考能力，实现“复杂任务深度推理，简单任务高效响应”的精细控制，获得成本、效率收益。
取值说明：
enabled：强制开启，强制开启深度思考能力。
disabled：强制关闭深度思考能力。
auto：模型自行判断是否进行深度思考。
示例代码：

Curl
Python
Go
Java
OpenAI SDK
import os
# Install SDK:  pip install 'volcengine-python-sdk[ark]'
from volcenginesdkarkruntime import Ark 

client = Ark(
    # The base URL for model invocation
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    # Get API Key：https://console.volcengine.com/ark/region:ark+cn-beijing/apikey
    api_key=os.getenv('ARK_API_KEY'), 
    # Deep thinking takes longer; set a larger timeout, with 1,800 seconds or more recommended
    timeout=1800,
)

# 创建一个对话请求
completion = client.chat.completions.create(
    # Replace with Model ID
    model = "doubao-seed-2-0-lite-260215",
    messages=[
        {"role": "user", "content": "我要研究深度思考模型与非深度思考模型区别的课题，体现出我的专业性"}
    ],
     thinking={
         "type": "disabled", # 不使用深度思考能力
         # "type": "enabled", # 使用深度思考能力
         # "type": "auto", # 模型自行判断是否使用深度思考能力
     },
)

print(completion)

package main

import (
    "context"
    "fmt"
    "os"
    "time"
    "github.com/volcengine/volcengine-go-sdk/service/arkruntime"
    "github.com/volcengine/volcengine-go-sdk/service/arkruntime/model"
    "github.com/volcengine/volcengine-go-sdk/volcengine"
)

func main() {
    client := arkruntime.NewClientWithApiKey(
        // Get API Key：https://console.volcengine.com/ark/region:ark+cn-beijing/apikey
        os.Getenv("ARK_API_KEY"),
        // The base URL for model invocation
        arkruntime.WithBaseUrl("https://ark.cn-beijing.volces.com/api/v3"),
        //深度思考耗时更长，请设置更大的超时限制，推荐为30分钟及以上
        arkruntime.WithTimeout(30*time.Minute),
    )
    // 创建一个上下文，通常用于传递请求的上下文信息，如超时、取消等
    ctx := context.Background()
    // 构建聊天完成请求，设置请求的模型和消息内容
    req := model.CreateChatCompletionRequest{
        // Replace with Model ID
       Model: "doubao-seed-2-0-lite-260215",
       Messages: []*model.ChatCompletionMessage{
            {
                // 消息的角色为用户
                Role: model.ChatMessageRoleUser,
                Content: &model.ChatCompletionMessageContent{
                    StringValue: volcengine.String("我要研究深度思考模型与非深度思考模型区别的课题，怎么体现我的专业性"),
                },
            },
        },
        Thinking: &model.Thinking{
            Type: model.ThinkingTypeDisabled, // 关闭深度思考能力
            // Type: model.ThinkingTypeEnabled, //开启深度思考能力
            // Type: model.ThinkingTypeAuto, //模型自行判断是否使用深度思考能力
        },
    }

// 发送聊天完成请求，并将结果存储在 resp 中，将可能出现的错误存储在 err 中
    resp, err := client.CreateChatCompletion(ctx, req)
    if err != nil {
        // 若出现错误，打印错误信息并终止程序
        fmt.Printf("standard chat error: %v\n", err)
        return
    }
    // 检查是否触发深度思考，触发则打印思维链内容
    if resp.Choices[0].Message.ReasoningContent != nil {
        fmt.Println(*resp.Choices[0].Message.ReasoningContent)
    }
    // 打印聊天完成请求的响应结果
    fmt.Println(*resp.Choices[0].Message.Content.StringValue)
}

package com.ark.sample;

import com.volcengine.ark.runtime.model.completion.chat.*;
import com.volcengine.ark.runtime.service.ArkService;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;

/**
 * 这是一个示例类，展示了如何使用ArkService来完成聊天功能。
 */
public class ChatCompletionsExample {
    public static void main(String[] args) {
        // 从环境变量中获取API密钥
        String apiKey = System.getenv("ARK_API_KEY");
        // 创建ArkService实例
        ArkService arkService = ArkService.builder()
                .apiKey(apiKey)
                .timeout(Duration.ofMinutes(30))// 深度思考耗时更长，请设置更大的超时限制，推荐为30分钟及以上
                // The base URL for model invocation
                .baseUrl("https://ark.cn-beijing.volces.com/api/v3")
                .build();
        // 初始化消息列表
        List<ChatMessage> chatMessages = new ArrayList<>();
        // 创建用户消息
        ChatMessage userMessage = ChatMessage.builder()
                .role(ChatMessageRole.USER) // 设置消息角色为用户
                .content("我要研究深度思考模型与非深度思考模型区别的课题，怎么体现我的专业性") // 设置消息内容
                .build();
        // 将用户消息添加到消息列表
        chatMessages.add(userMessage);
        ChatCompletionRequest chatCompletionRequest = ChatCompletionRequest.builder()
                .model("doubao-seed-2-0-lite-260215")//Replace with Model ID
                .messages(chatMessages) // 设置消息列表
                .thinking(new ChatCompletionRequest.ChatCompletionRequestThinking("disabled"))
                .build();
        // 发送聊天完成请求并打印响应
        try {
            // 获取响应并打印每个选择的消息内容
            arkService.createChatCompletion(chatCompletionRequest)
                    .getChoices()
                    .forEach(choice -> {                    
                        // 校验是否触发了深度思考，打印思维链内容
                        if (choice.getMessage().getReasoningContent() != null) {
                            System.out.println("推理内容: " + choice.getMessage().getReasoningContent());
                        } else {
                            System.out.println("推理内容为空");
                        }
                        // 打印消息内容
                        System.out.println("消息内容: " + choice.getMessage().getContent());
                    });
        } catch (Exception e) {
            System.out.println("请求失败: " + e.getMessage());
        } finally {
            // 关闭服务执行器
            arkService.shutdownExecutor();
        }
    }
}

import os
from openai import OpenAI

client = OpenAI(
    # 从环境变量中读取方舟API Key
    api_key=os.environ.get("ARK_API_KEY"), 
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    # 深度思考耗时更长，避免连接超时导致失败，请设置更大的超时限制，推荐为1800 秒及以上
    timeout=1800,
    )
completion = client.chat.completions.create(
    # Replace with Model ID
    model = "doubao-seed-2-0-lite-260215",
    messages=[
        {
            "role": "user",
            "content": "我要研究深度思考模型与非深度思考模型区别的课题，体现出我的专业性",
        }
    ],
    extra_body={
        "thinking": {
            "type": "disabled",  # 不使用深度思考能力
            # "type": "enabled", # 使用深度思考能力
            # "type": "auto", # 模型自行判断是否使用深度思考能力
        }
    },
)

print(completion)

Bash
复制
curl https://ark.cn-beijing.volces.com/api/v3/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seed-2-0-lite-260215",
     "messages": [
         {
             "role": "user",
             "content": [
                 {
                     "type":"text",
                     "text":"我要研究深度思考模型与非深度思考模型区别的课题，体现出我的专业性"
                 }
             ]
         }
     ],
     "thinking":{
         "type":"disabled"
     }
}'

model：请变更为实际调用的模型。
thinking.type：字段可以取值范围。
disabled：强制关闭深度思考能力，模型不输出思维链内容。
enabled：强制开启深度思考能力，模型强制输出思维链内容。
auto：模型自行判断是否需要进行深度思考。

支持模型：
doubao-seed-2-0-pro-260215：支持 enabled（默认）、disabled。
doubao-seed-2-0-lite-260215：支持 enabled（默认）、disabled。
doubao-seed-2-0-mini-260215：支持 enabled（默认）、disabled。
doubao-seed-2-0-code-preview-260215：支持 enabled（默认）、disabled。
doubao-seed-1-8-251228：支持 enabled（默认）、disabled。
glm-4-7-251222：支持enabled（默认）、disabled。
doubao-seed-code-preview-251028：支持 enabled（默认）、disabled。
doubao-seed-1-6-vision-250815：支持 enabled（默认）、disabled。
doubao-seed-1-6-lite-251015：支持 enabled（默认）、disabled。
doubao-seed-1-6-250615：支持 enabled（默认）、disabled、auto。
doubao-seed-1-6-251015：支持 enabled（默认）、disabled。
doubao-seed-1-6-flash-250828：支持 enabled（默认）、disabled。
doubao-seed-1-6-flash-250615：支持 enabled（默认）、disabled。
deepseek-v3-2-251201：支持 enabled、disabled（默认）。
deepseek-v3-1-terminus：支持 enabled、disabled（默认）。
更多说明
Responses API 使用说明请参见 控制深度思考。
深度思考会影响续写模式，详细信息请参见续写模式。

设置最大输出长度
模型输出内容由思维链（Chain of Thought, COT） 和最终回答（Answer） 两部分组成。合理控制模型输出长度，平衡效果、速度、成本与稳定性。

传入方式

手动管理上下文

通过ID管理上下文

API

Chat API

Responses API

示例

JSON
复制
...
    "model": "doubao-seed-2-0-lite-260215",
    "messages": [
        {"role": "user", "content": "Hi, tell a joke."}
    ],
    "max_completion_tokens": 300
...

JSON
复制
...
    "model": "doubao-seed-2-0-lite-260215",
    "previous_response_id":"<id>",
     "input": "Hi, tell a joke.",
     "max_output_tokens": 300
...

完整示例及更多说明请参见 控制输出（回答+思维链）长度。
调节思考长度
提供字段 reasoning_effort（Chat API）、reasoning.effort（Responses API）调节思维链长度，平衡不同场景对效果、时延、成本的需求。取值如下：
minimal：关闭思考，直接回答。
low：轻量思考，侧重快速响应。
medium（默认值）：均衡模式，兼顾速度与深度。
high：深度分析，处理复杂问题。

API

Chat API

Responses API

示例

JSON
复制
...
    "model": "doubao-seed-2-0-lite-260215",
    "messages": [
        {"role": "user","content": "What are some common cruciferous plants?"}
    ],
    "reasoning_effort": "low"
...

JSON
复制
...
    "model": "doubao-seed-2-0-lite-260215",
    "input": [
        {"role": "user","content":"What are some common cruciferous plants?"}
    ],
    "reasoning":{"effort": "low"}
...

支持模型

doubao-seed-2-0-pro-260215
doubao-seed-2-0-lite-260215
doubao-seed-2-0-mini-260215
doubao-seed-2-0-code-preview-260215
doubao-seed-1-8-251228
doubao-seed-1-6-lite-251015
doubao-seed-1-6-251015

doubao-seed-2-0-pro-260215
doubao-seed-2-0-lite-260215
doubao-seed-2-0-mini-260215
doubao-seed-2-0-code-preview-260215
doubao-seed-1-8-251228
doubao-seed-1-6-lite-251015
doubao-seed-1-6-251015

完整示例及说明请参见 控制思维链长度 [ 新增 ]。
工具调用
doubao-seed-1.8 之前的模型在工具调用场景中开启深度思考后，会直接丢弃思维链内容。doubao-seed-1.8 及部分模型为给出更详尽准确的回答，将不会直接丢弃思维链内容，思维链内容可能参与后续轮次推理，输入 tokens 会增加，具体参见工作原理。
说明
推荐在 Responses API 中使用 previous_response_id，平台自动保存历史对话的上下文，并在多轮交互中回传给推理服务。
回传原始思考内容
部分模型开启深度思考后，默认输出模型原始的思考内容。以下是在工具调用场景，回传原始思考内容的示例。

API

Chat API

Responses API

支持模型

doubao-seed-2-0-pro-260215
doubao-seed-2-0-lite-260215
doubao-seed-2-0-mini-260215
doubao-seed-2-0-code-preview-260215
doubao-seed-1-8-251228
deepseek-v3-2-251201

doubao-seed-2-0-pro-260215
doubao-seed-2-0-lite-260215
doubao-seed-2-0-mini-260215
doubao-seed-2-0-code-preview-260215
doubao-seed-1-8-251228
deepseek-v3-2-251201

示例

第一轮请求：触发工具调用

Bash
复制
curl https://ark.cn-beijing.volces.com/api/v3/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seed-2-0-lite-260215",
    "messages": [
        {
            "role": "system",
            "content": "你是人工智能助手。"
        },
        {
            "role": "user",
            "content": "今天北京天气怎么样"
        }
    ],
    "thinking":{"type": "enabled"},
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "天气查询",
                "parameters": {
                    "properties": {
                        "location": {
                            "description": "地点的位置信息，例如北京、上海。",
                            "type": "string"
                        }
                    },
                    "required": [
                        "location"
                    ],
                    "type": "object"
                }
            }
        }
    ]
  }'

第一轮响应：返回工具调用指令
模型会返回reasoning_content、tool_calls等关键字段。

JSON
复制
{
    "choices": [
        {
            "finish_reason": "tool_calls",
            "index": 0,
            "logprobs": null,
            "message": {
                "content": "",
                "reasoning_content": "用户想查询今天北京的天气，这正好符合get_weather工具的功能，需要传入location参数为北京。所以我要调用这个工具来获取天气信息。",
                "role": "assistant",
                "tool_calls": [
                    {
                        "function": {
                            "arguments": " {\"location\": \"北京\"}",
                            "name": "get_weather"
                        },
                        "id": "call_wiezxeyae8jzxl3jx8nhfgb5",
                        "type": "function"
                    }
                ]
            }
        }
    ],
    ...
 }

第二轮请求：回传完整上下文并生成最终响应
在第一轮请求的基础上，还需要回传思维链信息、工具调用结果，模型生成自然语言回答。

Bash
复制
curl https://ark.cn-beijing.volces.com/api/v3/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seed-2-0-lite-260215",
    "messages": [
        {
            "role": "system",
            "content": "你是人工智能助手。"
        },
        {
            "role": "user",
            "content": "今天北京天气怎么样"
        },
        {
            "reasoning_content": "用户想查询今天北京的天气，这正好符合get_weather工具的功能，需要传入location参数为北京。所以我要调用这个工具来获取天气信息。",
            "role": "assistant",
            "tool_calls": [
                {
                    "function": {
                        "arguments": " {\"location\": \"北京\"}",
                        "name": "get_weather"
                    },
                    "id": "call_wiezxeyae8jzxl3jx8nhfgb5",
                    "type": "function"
                }
            ]
        },
        {
            "role": "tool",
            "tool_call_id":"call_wiezxeyae8jzxl3jx8nhfgb5",
            "content": "5度"
        }
    ],
    "thinking":{"type": "enabled"},
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "天气查询",
                "parameters": {
                    "properties": {
                        "location": {
                            "description": "地点的位置信息，例如北京、上海。",
                            "type": "string"
                        }
                    },
                    "required": [
                        "location"
                    ],
                    "type": "object"
                }
            }
        }
    ]
  }'

第一轮请求：触发工具调用

Bash
复制
curl https://ark.cn-beijing.volces.com/api/v3/responses \
    -H "Authorization: Bearer $ARK_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "model": "doubao-seed-2-0-lite-260215",
        "input": [
            {
                "role": "system",
                "content": "你是人工智能助手."
            },
            {
                "role": "user",
                "content": "今天北京天气怎么样"
            }
        ],
        "thinking":{"type": "enabled"},
        "tools": [
            {
                "type": "function",
                "name": "get_weather",
                "description": "天气查询",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "地点的位置信息，例如北京、上海。",
                        }
                    },
                    "required": ["location"]
                }
            }
        ]
    }'

第一轮响应：返回工具调用指令
模型返回信息包含id、call_id、arguments等关键字段。

Bash
复制
{
    "created_at": 1766126702,
    "id": "resp_0217661267019147d8950efa0e2f7c9d9cc7a1cc971272cf4548c",
    "max_output_tokens": 32768,
    "model": "doubao-seed-1-8-251228",
    "object": "response",
    "output": [
        {
            "id": "rs_02176612670248500000000000000000000ffffac154e10754f5c",
            "type": "reasoning",
            "summary": [
                {
                    "type": "summary_text",
                    "text": "用户问今天北京的天气怎么样，我需要调用get_weather工具，参数location是北京。按照格式要求来写函数调用。"
                }
            ],
            "status": "completed"
        },
        {
            "arguments": " {\"location\": \"北京\"}",
            "call_id": "call_t885uulopdd499rn0pioze7l",
            "name": "get_weather",
            "type": "function_call",
            "id": "fc_02176612670345400000000000000000000ffffac154e10a6753e",
            "status": "completed"
        }
    ],
    ....
 }

第二轮请求：回传结果并生成最终响应
传入上一轮 response_id、工具调用结果等信息，模型生成自然语言回答。

Bash
复制
curl https://ark.cn-beijing.volces.com/api/v3/responses \
    -H "Authorization: Bearer $ARK_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "model": "doubao-seed-2-0-lite-260215",
        "input": [
            {
                "type": "function_call_output",
                "call_id": "call_t885uulopdd499rn0pioze7l",
                "output": "5度"
            }
        ],
        "previous_response_id": "resp_0217661267019147d8950efa0e2f7c9d9cc7a1cc971272cf4548c",
        "thinking":{"type": "enabled"},
        "tools": [
            {
                "type": "function",
                "name": "get_weather",
                "description": "天气查询",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "地点的位置信息，例如北京、上海。"
                        }
                    },
                    "required": ["location"]
                }
            }
        ]
    }'

使用说明
工作原理
多轮对话场景

流程图

说明

在每一轮对话过程中，深度思考模型会输出思维链内容（COT）和最终回答（Answer）。
在下一轮对话中，之前输出的思维链内容不会被拼接到上下文中。
思维链内容展现的是模型处理问题的过程，包括将问题拆分为多个问题进行处理，生成多种回复综合得出更好回答等过程。

工具调用场景（doubao-seed-1.8 及后续模型）
工具调用场景中开启深度思考后，为给出更详尽准确的回答，将不会直接丢弃思维链内容，历史轮次的思维链内容按需（模型自主判断）参与推理。在整个请求过程中，用户回传完整上下文即可，由服务端自行判断，是否保留思维链内容。未输入给模型的思维链内容，不会计算 token 用量。代码示例参见工具调用。

流程图

说明

回答问题 1 时（请求 1.1 - 1.2），模型进行多次思考 + 工具调用后给出答案，方舟会输入完整上下文包括思维链内容给模型处理。
开始回答问题2时（请求 2.1），方舟会自行判断并删除之前上下文中的思维链，输入给模型。

减少请求超时失败
深度思考模型使用思维链输出内容，导致回复篇幅更长、速率更慢，所以极易因超时导致任务失败。尤其在非流式输出模式下，任务未完成时断开连接，未输出内容，又产生 token 用量费用。
可使用流式输出或设置更长超时时间，减少超时失败：
使用流式输出（推荐）：通过分块即时返回生成内容，可有效维持连接活性（避免因长时无响应导致的连接中断），是高效且可靠的输出方式（示例代码及说明参见 流式输出）。若当前应用使用非流式输出，可改造为：通过流式接口获取内容，实时拼接完整结果后再统一输出，从而显著降低请求超时失败风险。
调大超时时间参数：非流式输出场景下，推荐将timeout参数设置为30分钟以上，并根据超时触发概率进一步调整超时时间。另需注意网络链路中的 TCP Keep-Alive 设置（tcp_keepalive_time参数），避免因长时间无数据传输导致连接被系统、防火墙、路由器等中断。
方舟Go SDK特殊说明：无论是否使用流式输出，均需将SDK超时参数设置为30分钟以上。
使用批量推理获得更高吞吐
当您的业务需要处理大量的数据，且对于模型返回及时性要求不高，您可使用批量推理获取最低 10B token/天 的配额以及批量推理的成本降低。批量推理支持任务的方式以及类似 Chat 的接口调用方式，使用批量推理，详细说明请查看批量推理。
提示词优化建议
深度思考模型会自行分析和拆解问题（思维链），与普通模型相比，提示词侧重点有所不同。
提示词除了待解决问题，应该更多补充目标和场景等信息。如使用英语，用Python等语言要求；面向小学生、向领导汇报等阅读对象信息；完成论文写作、完成课题报告、撰写剧本等场景信息；体现我的专业性、获得领导赏识等目标信息。
减少或者避免对问题的拆解描述，如分步骤思考、使用示例等，这样会限制住模型的推理逻辑。
减少使用系统提示词，所有提示词信息直接通过用户提示词（role: user）来提问。
常见问题
并发 RPM 或者 TPM 额度明明有剩余为什么提示限流报错？
