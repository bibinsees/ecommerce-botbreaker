## Qwen3 Context Window Format

This is the context window format for Qwen3.

### Special Tokens Reference

The following special tokens are used in the Qwen3 format:

| Token | Purpose | Usage Context |
|-------|---------|---------------|
| `<\|im_start\|>` | Message start delimiter | Marks the beginning of any message (system, user, assistant, tool) |
| `<\|im_end\|>` | Message end delimiter | Marks the end of any message |
| `<think>` | Reasoning block start | Opens a reasoning/thinking section in assistant messages |
| `</think>` | Reasoning block end | Closes a reasoning/thinking section |
| `<tool_call>` | Tool invocation start | Marks the beginning of a tool call in assistant messages |
| `</tool_call>` | Tool invocation end | Marks the end of a tool call |
| `<tool_response>` | Tool output start | Marks the beginning of tool output in user messages |
| `</tool_response>` | Tool output end | Marks the end of tool output |
| `<tools>` | Tool definitions start | Marks the beginning of available tool definitions in system messages |
| `</tools>` | Tool definitions end | Marks the end of available tool definitions |

**Role Identifiers** (used after `<\|im_start\|>`):
- `system` - System message role
- `user` - User message role
- `assistant` - Assistant message role
- `tool` - Tool message role (mentioned but not shown in examples)

### Message format

The Qwen3 format consists of "messages" with the model potentially generating multiple messages in one go. The general structure of a message is as follows:

```
<|im_start|>{role}
{content}<|im_end|>
```

The `{role}` can be "system", "user", "assistant", or "tool". `<|im_end|>` represents the end of a message.

#### System message

The system message is optional and when present, follows this format:

```
<|im_start|>system
{system_content}<|im_end|>
```

Note: Unlike Qwen-2.5, Qwen3 does not have a default system prompt. The model can identify itself without needing "You are Qwen, created by Alibaba Cloud" in the system message.

#### User Input Message Format

This is the format of a user message sent to the assistant:

```
<|im_start|>user
What is 2 + 2?<|im_end|>
```

#### Model Reasoning and Response Format

When generating a response, the model starts with:

```
<|im_start|>assistant
```

The model can then optionally include reasoning in `<think>` tags:

```
<think>
User asks: "What is 2 + 2?" This is a simple arithmetic problem.
</think>

2 + 2 = 4.
```

### Reasoning Management

To disable reasoning, insert empty `<think>\n\n</think>\n\n` tags at the beginning of the assistant turn. This tells the model to skip reasoning.

Otherwise, the model decides whether to use reasoning based on the complexity of the task

#### Disabled Reasoning Example

When reasoning is disabled, the assistant response starts with empty think tags:

```
<|im_start|>user
What is 2 + 2?<|im_end|>
<|im_start|>assistant
<think>

</think>

2 + 2 = 4.<|im_end|>
```

#### Pruning Prior Reasoning

Qwen3 uses a "rolling checkpoint" system for managing reasoning content across conversations:
- It traverses messages in reverse to find the latest user query that isn't a tool call
- For assistant messages after that point, it preserves `<think>` blocks
- For earlier messages, reasoning content is stripped to save tokens

For example, in a multi-turn conversation:

```
<|im_start|>user
What is 2 + 2?<|im_end|>
<|im_start|>assistant
2 + 2 = 4.<|im_end|>
<|im_start|>user
What about 9 / 2?<|im_end|>
<|im_start|>assistant
<think>
The user is asking for 9 divided by 2.
</think>

9 / 2 = 4.5
```

Note how the reasoning from the first response is not included in the context for the second query.

### Tool Use

#### Defining Tools

When tools are available, they are included in the system message:

```
<|im_start|>system
You are a helpful assistant that can use tools to get information for the user.

# Tools

You may call one or more functions to assist with the user query.

You are provided with function signatures within <tools></tools> XML tags:
<tools>
{"type": "function", "function": {"name": "get_current_weather", "description": "Get weather", "parameters": {...}}}
</tools>

For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
<tool_call>
{"name": <function-name>, "arguments": <args-json-object>}
</tool_call><|im_end|>
```

#### Tool Invocation Format

When the model decides to call a tool, it uses the `<tool_call>` tags with JSON format:

```
<|im_start|>assistant
<think>
I need to use the get_current_weather function to check the weather.
</think>

<tool_call>
{"name": "get_current_weather", "arguments": {"location": "San Francisco"}}
</tool_call><|im_end|>
```

The tool call format:
- Uses `<tool_call>` and `</tool_call>` XML tags
- Contains a JSON object with `name` and `arguments` fields
- The `arguments` field is properly serialized (checks if already a string to avoid double-escaping)

#### Providing Tool Output Responses to Model

Tool responses are provided as user messages with `<tool_response>` tags:

```
<|im_start|>user
<tool_response>
{"sunny": true, "temperature": 20}
</tool_response><|im_end|>
```

Multiple consecutive tool responses are grouped within a single user message:

```
<|im_start|>user
<tool_response>
First tool output
</tool_response>
<tool_response>
Second tool output
</tool_response><|im_end|>
```

> NOTE: Qwen3 natively expects Tool Responses to be provided by the user, not the system. This has important security and injection risks.

### Full Context Window Example

Here's a complete example showing a multi-turn conversation with reasoning, tool use, and proper formatting:

```
<|im_start|>system
You are a helpful assistant that can use tools to get information for the user.

# Tools

You may call one or more functions to assist with the user query.

You are provided with function signatures within <tools></tools> XML tags:
<tools>
{"type": "function", "function": {"name": "get_current_weather", "description": "Get the current weather in a given location", "parameters": {"type": "object", "properties": {"location": {"type": "string", "description": "The city and state, e.g. San Francisco, CA"}}, "required": ["location"]}}}
{"type": "function", "function": {"name": "calculate", "description": "Perform mathematical calculations", "parameters": {"type": "object", "properties": {"expression": {"type": "string", "description": "Mathematical expression to evaluate"}}, "required": ["expression"]}}}
</tools>

For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
<tool_call>
{"name": <function-name>, "arguments": <args-json-object>}
</tool_call><|im_end|>
<|im_start|>user
What's the weather like in Paris?<|im_end|>
<|im_start|>assistant
<think>
The user is asking about the weather in Paris. I should use the get_current_weather function to retrieve this information.
</think>

I'll check the current weather in Paris for you.

<tool_call>
{"name": "get_current_weather", "arguments": {"location": "Paris, France"}}
</tool_call><|im_end|>
<|im_start|>user
<tool_response>
{"temperature": 18, "condition": "partly cloudy", "humidity": 65, "wind_speed": 12}
</tool_response><|im_end|>
<|im_start|>assistant
The current weather in Paris is partly cloudy with a temperature of 18°C. The humidity is at 65% and there's a light wind at 12 km/h. It's a pleasant day with some clouds in the sky.<|im_end|>
<|im_start|>user
If the temperature increases by 7 degrees, what would it be?<|im_end|>
<|im_start|>assistant
<think>
The user wants to know what the temperature would be if it increased by 7 degrees. The current temperature in Paris is 18°C, so I need to calculate 18 + 7.
</think>

<tool_call>
{"name": "calculate", "arguments": {"expression": "18 + 7"}}
</tool_call><|im_end|>
<|im_start|>user
<tool_response>
{"result": 25}
</tool_response><|im_end|>
<|im_start|>assistant
If the temperature in Paris increases by 7 degrees from the current 18°C, it would be 25°C. That would make it quite a warm and comfortable day!<|im_end|>
```

### Comparison between Qwen3 versus the OpenAI Harmony Format

The Qwen3 and OpenAI Harmony formats represent two distinct approaches to structuring LLM context windows, each with unique design choices:

### Key Structural Differences

| Aspect | Qwen3 Format | OpenAI Harmony Format |
|--------|--------------|----------------------|
| **Message Delimiters** | `<\|im_start\|>` and `<\|im_end\|>` | `<\|start\|>` and `<\|end\|>` (or `<\|call\|>` for tools) |
| **Role Specification** | Role directly after start delimiter | Role in header section |
| **Reasoning Blocks** | `<think>` and `</think>` tags | Channel-based system (`analysis`, `commentary`, `final`) |
| **Tool Definitions** | JSON format in `<tools>` tags | TypeScript namespace syntax |
| **Tool Calls** | `<tool_call>` XML tags with JSON | Header recipient (`to=functions.name`) with `<\|call\|>` ending |
| **Tool Responses** | User messages with `<tool_response>` tags | Dedicated tool role messages (`functions.{name} to=assistant`) |

### Reasoning Management
- **Qwen3**: Uses simple `<think>` tags that can be disabled with empty tags. Reasoning is pruned from earlier messages using a rolling checkpoint system.
- **Harmony**: Employs a sophisticated three-channel system where reasoning (`analysis`) is separate from tool interactions (`commentary`) and user-facing responses (`final`). Analysis content can be unsafe and is typically dropped in multi-turn conversations.

### Tool System Architecture
- **Qwen3**: Tools are defined as JSON objects and invoked through XML-style tags. Tool responses come through user messages, creating potential security risks.
- **Harmony**: Tools use TypeScript-style type definitions with full type system support. Tool interactions occur through a dedicated commentary channel with explicit recipient routing.

### Security Considerations
- **Qwen3**: Tool responses via user messages pose injection risks since the model expects tool outputs to come from the user role.
- **Harmony**: Explicit warning that analysis channel content may be unsafe, but tool responses come from dedicated tool roles, providing better separation of concerns.

### Context Efficiency
- **Qwen3**: Simpler format with automatic reasoning pruning for older messages.
- **Harmony**: More complex but flexible channel system allows selective retention of different message types, with explicit dropping of analysis content to save tokens.

Both formats reflect their respective design philosophies: Qwen3 favors simplicity with XML-style markup, while OpenAI Harmony emphasizes structured communication channels and type safety for more complex interactions.