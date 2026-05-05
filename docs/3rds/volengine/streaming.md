默认情况下，方舟 API 会在生成全部内容后，再通过单次 HTTP 响应返回结果。如果输出长内容，等待时间会较长。流式响应模式下，模型会持续发送已生成的数据片段，你可实时看到中间输出过程内容，方便立即开始处理或展示部分结果。
效果与优势

预览

优势

改善等待体验：无需等待完整内容生成完毕，可立即处理过程内容。
实时过程反馈：多轮交互场景，实时了解任务当前的处理阶段。
更高的容错性：中途出错，也能获取到已生成内容，避免非流式输出失败无返回的情况。
简化超时管理：保持客户端与服务端的连接状态，避免复杂任务耗时过长而连接超时。

使用说明
启用流式
通过配置 stream 为 true，来启用流式输出。
示例代码
Chat API 示例代码：

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
)

completion = client.chat.completions.create(
    # Replace with Model ID
    model = "doubao-seed-2-0-lite-260215",
    messages=[
        {"role": "user", "content": "常见的十字花科植物有哪些？"},
    ],
    stream=True,
)

# Ensure the connection is closed automatically to prevent connection leaks.
with completion:
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")

说明
with completion：当 with 代码块内出现异常时，会自动调用对象的 exit() 方法进行清理工作。当设置了max_tokens 等中断条件时，可避免socket层数据载满最终程序卡住。
package main

import (
    "context"
    "fmt"
    "os"
    "github.com/volcengine/volcengine-go-sdk/service/arkruntime"
    "github.com/volcengine/volcengine-go-sdk/service/arkruntime/model"
    "github.com/volcengine/volcengine-go-sdk/volcengine"
)

func main() {
    client := arkruntime.NewClientWithApiKey(
        os.Getenv("ARK_API_KEY"),
        // The base URL for model invocation
        arkruntime.WithBaseUrl("https://ark.cn-beijing.volces.com/api/v3"),
    )

ctx := context.Background()

fmt.Println("----- standard request -----")
    req := model.CreateChatCompletionRequest{
        // Replace with Model ID
       Model: "doubao-seed-2-0-lite-260215",
        Messages: []*model.ChatCompletionMessage{
            {
                Role: model.ChatMessageRoleUser,
                Content: &model.ChatCompletionMessageContent{
                    StringValue: volcengine.String("常见的十字花科植物有哪些？"),
                },
            },
        },
        Stream: volcengine.Bool(true),
    }

// 调用 CreateChatCompletionStream 方法，而不要使用非流式调用的 CreateChatCompletion 方法，否则将无法获取流式响应。
    resp, err := client.CreateChatCompletionStream(ctx, req)
    if err != nil {
        fmt.Printf("standard chat error: %\v", err)
        return
    }

defer resp.Close()
    for {
        chunk, err := resp.Recv()
        if err != nil {
            fmt.Printf("stream error: %v", err)
            break
        }
        fmt.Print(chunk.Choices[0].Delta.Content)
    }
    fmt.Println()
}

package com.volcengine.ark.runtime;

import com.volcengine.ark.runtime.model.completion.chat.ChatCompletionRequest;
import com.volcengine.ark.runtime.model.completion.chat.ChatMessage;
import com.volcengine.ark.runtime.model.completion.chat.ChatMessageRole;
import com.volcengine.ark.runtime.service.ArkService;
import java.util.ArrayList;
import java.util.List;

public class ChatCompletionsExample {
    public static void main(String[] args) {
        String apiKey = System.getenv("ARK_API_KEY");
        // The base URL for model invocation
        ArkService service = ArkService.builder().apiKey(apiKey).baseUrl("https://ark.cn-beijing.volces.com/api/v3").build();
        final List<ChatMessage> messages = new ArrayList<>();
        final ChatMessage userMessage = ChatMessage.builder().role(ChatMessageRole.USER).content("常见的十字花科植物有哪些？").build();
        messages.add(userMessage);

ChatCompletionRequest chatCompletionRequest = ChatCompletionRequest.builder()
               .model("doubao-seed-2-0-lite-260215")//Replace with Model ID
               .messages(messages)
               .stream(true)
               .thinking(new ChatCompletionRequest.ChatCompletionRequestThinking("disabled"))
               .build();
        service.streamChatCompletion(chatCompletionRequest)
               .doOnError(Throwable::printStackTrace) // 处理错误
               .blockingForEach(response -> {
                    if (response.getChoices() != null && !response.getChoices().isEmpty()) {
                        String content = String.valueOf(response.getChoices().get(0).getMessage().getContent());
                        if (content != null) {
                            System.out.print(content); // 注意用print而非println，保持内容连续
                        }
                    }
                });
        // shutdown service
        service.shutdownExecutor();
    }
}

import os
from openai import OpenAI

client = OpenAI(
    # Get API Key：https://console.volcengine.com/ark/region:ark+cn-beijing/apikey
    api_key=os.environ.get("ARK_API_KEY"), 
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    )

completion = client.chat.completions.create(
    # Replace with Model ID
    model = "doubao-seed-2-0-lite-260215",
    messages=[
        {"role": "user", "content": "常见的十字花科植物有哪些？"},
    ],
    stream=True,
)

# Ensure the connection is closed automatically to prevent connection leaks.
with completion: 
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")

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
            "content": "常见的十字花科植物有哪些？"
        }
    ],
    "stream": true
  }'

Responses API 示例代码：

Curl
Python
Go
Java
OpenAI SDK
import os
from volcenginesdkarkruntime import Ark
from volcenginesdkarkruntime.types.responses.response_completed_event import ResponseCompletedEvent
from volcenginesdkarkruntime.types.responses.response_reasoning_summary_text_delta_event import ResponseReasoningSummaryTextDeltaEvent
from volcenginesdkarkruntime.types.responses.response_output_item_added_event import ResponseOutputItemAddedEvent
from volcenginesdkarkruntime.types.responses.response_text_delta_event import ResponseTextDeltaEvent
from volcenginesdkarkruntime.types.responses.response_text_done_event import ResponseTextDoneEvent

# Get API Key：https://console.volcengine.com/ark/region:ark+cn-beijing/apikey
api_key = os.getenv('ARK_API_KEY')

client = Ark(
    base_url='https://ark.cn-beijing.volces.com/api/v3',
    api_key=api_key,
)

# Create a request
response = client.responses.create(
    model="doubao-seed-2-0-lite-260215",
    input="常见的十字花科植物有哪些？",
    stream=True
)

for event in response:
    if isinstance(event, ResponseReasoningSummaryTextDeltaEvent):
        print(event.delta, end="")
    if isinstance(event, ResponseOutputItemAddedEvent):
        print("\noutPutItem " + event.type + " start:")
    if isinstance(event, ResponseTextDeltaEvent):
        print(event.delta,end="")
    if isinstance(event, ResponseTextDoneEvent):
        print("\noutPutTextDone.")
    if isinstance(event, ResponseCompletedEvent):
        print("Response Completed. Usage = " + event.response.usage.model_dump_json())

package main

import (
    "context"
    "fmt"
    "os"

"github.com/volcengine/volcengine-go-sdk/service/arkruntime"
    "github.com/volcengine/volcengine-go-sdk/service/arkruntime/model/responses"
)

func main() {
    client := arkruntime.NewClientWithApiKey(
        // Get API Key：https://console.volcengine.com/ark/region:ark+cn-beijing/apikey
        os.Getenv("ARK_API_KEY"),
        arkruntime.WithBaseUrl("https://ark.cn-beijing.volces.com/api/v3"),
    )
    ctx := context.Background()

resp, err := client.CreateResponsesStream(ctx, &responses.ResponsesRequest{
        Model:    "doubao-seed-2-0-lite-260215",
        Input:    &responses.ResponsesInput{Union: &responses.ResponsesInput_StringValue{StringValue: "常见的十字花科植物有哪些？"}},
    })
    if err != nil {
        fmt.Printf("stream error: %v", err)
        return
    }
    for {
        event, err := resp.Recv()
        if err == io.EOF {
            break
        }
        if err != nil {
            fmt.Printf("stream error: %v", err)
            return
        }
        handleEvent(event)
    }
}
func handleEvent(event *responses.Event) {
    switch event.GetEventType() {
    case responses.EventType_response_reasoning_summary_text_delta.String():
        print(event.GetReasoningText().GetDelta())
    case responses.EventType_response_reasoning_summary_text_done.String(): // aggregated reasoning text
        fmt.Printf("\nAggregated reasoning text: %s\n", event.GetReasoningTextDone().GetText())
    case responses.EventType_response_output_text_delta.String():
        print(event.GetText().GetDelta())
    case responses.EventType_response_output_text_done.String(): // aggregated output text
        fmt.Printf("\nAggregated output text: %s\n", event.GetTextDone().GetText())
    default:
        return
    }
}

package com.ark.example;
import com.volcengine.ark.runtime.service.ArkService;
import com.volcengine.ark.runtime.model.responses.request.*;
import com.volcengine.ark.runtime.model.responses.response.ResponseObject;
import com.volcengine.ark.runtime.model.responses.constant.ResponsesConstants;
import com.volcengine.ark.runtime.model.responses.common.ResponsesThinking;
import com.volcengine.ark.runtime.model.responses.event.functioncall.FunctionCallArgumentsDoneEvent;
import com.volcengine.ark.runtime.model.responses.event.outputitem.OutputItemAddedEvent;
import com.volcengine.ark.runtime.model.responses.event.outputitem.OutputItemDoneEvent;
import com.volcengine.ark.runtime.model.responses.event.outputtext.OutputTextDeltaEvent;
import com.volcengine.ark.runtime.model.responses.event.outputtext.OutputTextDoneEvent;
import com.volcengine.ark.runtime.model.responses.event.reasoningsummary.ReasoningSummaryTextDeltaEvent;
import com.volcengine.ark.runtime.model.responses.event.response.ResponseCompletedEvent;

public class demo {
    public static void main(String[] args) {
        String apiKey = System.getenv("ARK_API_KEY");
        // The base URL for model invocation
        ArkService arkService = ArkService.builder().apiKey(apiKey).baseUrl("https://ark.cn-beijing.volces.com/api/v3").build();

CreateResponsesRequest request = CreateResponsesRequest.builder()
                .model("doubao-seed-2-0-lite-260215")
                .stream(true)
                .input(ResponsesInput.builder().stringValue("常见的十字花科植物有哪些？").build())
                .build();
        arkService.streamResponse(request)
            .doOnError(Throwable::printStackTrace)
            .blockingForEach(event -> {
                if (event instanceof ReasoningSummaryTextDeltaEvent) {
                    System.out.print(((ReasoningSummaryTextDeltaEvent) event).getDelta());
                }
                if (event instanceof OutputItemAddedEvent) {
                    System.out.println("OutputItem " + (((OutputItemAddedEvent) event).getItem().getType()) + " Start: ");
                }
                if (event instanceof OutputTextDeltaEvent) {
                    System.out.print(((OutputTextDeltaEvent) event).getDelta());
                }
                if (event instanceof OutputTextDoneEvent) {
                    System.out.println("OutputText End.");
                }
                if (event instanceof OutputItemDoneEvent) {
                    System.out.println("OutputItem " + ((OutputItemDoneEvent) event).getItem().getType() + " End.");
                }
                if (event instanceof FunctionCallArgumentsDoneEvent) {
                    System.out.println("FunctionCall Arguments: " + ((FunctionCallArgumentsDoneEvent) event).getArguments());
                }
                if (event instanceof ResponseCompletedEvent) {
                    System.out.println("Response Completed. Usage = " + ((ResponseCompletedEvent) event).getResponse().getUsage());
                }
            });

arkService.shutdownExecutor();
    }
}

import os
from openai import OpenAI

# Get API Key：https://console.volcengine.com/ark/region:ark+cn-beijing/apikey
api_key = os.getenv('ARK_API_KEY')

client = OpenAI(
    base_url='https://ark.cn-beijing.volces.com/api/v3',
    api_key=api_key,
)

# Create a request
response = client.responses.create(
    model="doubao-seed-2-0-lite-260215",
    input="常见的十字花科植物有哪些？",
    stream=True
)

for event in response:
    if event.type == "response.reasoning_summary_text.delta":
        print(event.delta, end="")
    if event.type == "response.output_item.added":
        print("\noutPutItem " + event.type + " start:")
    if event.type == "response.output_text.delta":
        print(event.delta,end="")
    if event.type == "response.output_item.done":
        print("\noutPutTextDone.")
    if event.type == "response.completed":
        print("\nResponse Completed. Usage = " + event.response.usage.model_dump_json())

Bash
复制
curl https://ark.cn-beijing.volces.com/api/v3/responses \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
      "model": "doubao-seed-2-0-lite-260215",
      "input": "常见的十字花科植物有哪些？",
      "stream": true
  }'

返回示例
流式响应基于Server-Sent Events (SSE) 协议实现，其核心是服务端通过HTTP长连接持续向客户端推送数据片段。每个数据片段（Chunk）由字段行组成。包括模型深度思考内容片段、回复内容片段、工具调用片段等。流式响应结束时，服务端会推送一个特殊片段，通常包含 data: [DONE]

Chat API
Responses API
event: response.created
data: {"type":"response.created","response":{"created_at":1764229579,"id":"resp_021764229578658fe9a0f6cb2cc6c828e7a59adbdb971872aee70","max_output_tokens":32768,"model":"doubao-seed-1-6-251015","object":"response","thinking":{"type":"enabled"},"service_tier":"default","caching":{"type":"disabled"},"store":true,"expire_at":1764488778},"sequence_number":0}

event: response.in_progress
data: {"type":"response.in_progress","response":{"created_at":1764229579,"id":"resp_021764229578658fe9a0f6cb2cc6c828e7a59adbdb971872aee70","max_output_tokens":32768,"model":"doubao-seed-1-6-251015","object":"response","thinking":{"type":"enabled"},"service_tier":"default","caching":{"type":"disabled"},"store":true,"expire_at":1764488778},"sequence_number":1}

event: response.output_item.added
data: {"type":"response.output_item.added","output_index":0,"item":{"id":"rs_02176422957963700000000000000000000ffffac15dd335c9c43","type":"reasoning","status":"in_progress"},"sequence_number":2}

event: response.reasoning_summary_part.added
data: {"type":"response.reasoning_summary_part.added","item_id":"rs_02176422957963700000000000000000000ffffac15dd335c9c43","output_index":0,"summary_index":0,"part":{"type":"summary_text"},"sequence_number":3}

event: response.reasoning_summary_text.delta
data: {"type":"response.reasoning_summary_text.delta","summary_index":0,"delta":"\n","item_id":"rs_02176422957963700000000000000000000ffffac15dd335c9c43","output_index":0,"sequence_number":4}
...
event: response.completed
data: {"type":"response.completed","response":{"created_at":1768809358,"id":"resp_021768809358289649f4507e5505b181d56acee99f33e5a9f1075","max_output_tokens":32768,"model":"doubao-seed-1-6-251015","object":"response","output":[{"id":"rs_02176880935899200000000000000000000ffffac154346d65c7e","type":"reasoning","summary":[{"type":"summary_text","text":"\n...。"}],"status":"completed"},{"type":"message","role":"assistant","content":[{"type":"output_text","text":"..."}],"status":"completed","id":"msg_02176880937345100000000000000000000ffffac154346bd6748"}],"service_tier":"default","status":"completed","usage":{"input_tokens":42,"output_tokens":846,"total_tokens":888,"input_tokens_details":{"cached_tokens":0},"output_tokens_details":{"reasoning_tokens":408}},"caching":{"type":"disabled"},"store":true,"expire_at":1769068558},"sequence_number":851}

data: [DONE]

返回示例说明：（具体字段参见Responses API）
event类型response.reasoning_summary_text.delta，event.delta为模型思考内容。
event类型response.output_text.delta，event.delta为模型生成的消息内容。
event类型response.completed，event.response.usage为本次请求的 token 用量。

JSON
复制
data: {"choices":[{"delta":{"content":"","reasoning_content":"\n","role":"assistant"},"index":0}],"created":1765713048,"id":"021765713047481dd742fe08f96381a9e3cd447cf1b9ac3192379","model":"doubao-seed-1-6-251015","service_tier":"default","object":"chat.completion.chunk","usage":null}
data: {"choices":[{"delta":{"content":"","reasoning_content":"用户","role":"assistant"},"index":0}],"created":1765713048,"id":"021765713047481dd742fe08f96381a9e3cd447cf1b9ac3192379","model":"doubao-seed-1-6-251015","service_tier":"default","object":"chat.completion.chunk","usage":null}
...
data: {"choices":[{"delta":{"content":"","reasoning_content":"。","role":"assistant"},"index":0}],"created":1765713048,"id":"021765713047481dd742fe08f96381a9e3cd447cf1b9ac3192379","model":"doubao-seed-1-6-251015","service_tier":"default","object":"chat.completion.chunk","usage":null}
data: {"choices":[{"delta":{"content":"你","role":"assistant"},"index":0}],"created":1765713048,"id":"021765713047481dd742fe08f96381a9e3cd447cf1b9ac3192379","model":"doubao-seed-1-6-251015","service_tier":"default","object":"chat.completion.chunk","usage":null}
data: {"choices":[{"delta":{"content":"✧","role":"assistant"},"index":0}],"created":1765713048,"id":"021765713047481dd742fe08f96381a9e3cd447cf1b9ac3192379","model":"doubao-seed-1-6-251015","service_tier":"default","object":"chat.completion.chunk","usage":null}
...
data: {"choices":[{"delta":{"content":"","role":"assistant"},"finish_reason":"stop","index":0}],"created":1765713048,"id":"021765713047481dd742fe08f96381a9e3cd447cf1b9ac3192379","model":"doubao-seed-1-6-251015","service_tier":"default","object":"chat.completion.chunk","usage":null}
data: [DONE]

返回格式说明：(具体字段参见Chat API)
choices[0].delta.content: 模型生成的消息内容。
choices[0].delta.reasoning_content: 模型思考内容。
choices[0].finish_reason: 模型停止生成 token 的原因。（仅在最后一个chunk中出现）

API 文档
Chat API
Responses API
更多示例
函数调用流式输出，请参见 流式输出。
