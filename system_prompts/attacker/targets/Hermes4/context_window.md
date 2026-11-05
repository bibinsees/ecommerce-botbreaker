## Hermes 4 Context Window Format

### Overview

Hermes 4 uses the Llama-3 chat format with special header tags and role-based message structure. The model supports multiple modes including standard chat, reasoning mode with chain-of-thought, and function/tool calling. The format uses special tokens to delineate different parts of the conversation.

### Core Tags

The Hermes 4 format uses the following special tags:
- `<|start_header_id|>` - Marks the beginning of a message header
- `<|end_header_id|>` - Marks the end of a message header
- `<|eot_id|>` - End of turn identifier, marks the completion of a message
- `<think>...</think>` - Encapsulates the model's internal reasoning (in reasoning mode)
- `<tool_call>...</tool_call>` - Contains function/tool invocations
- `<tool_response>...</tool_response>` - Contains responses from tools
- `<tools>...</tools>` - Contains tool definitions in the system message

### Message Format

The general structure of a message in Hermes 4 is:

```
<|start_header_id|>{role}<|end_header_id|>

{content}<|eot_id|>
```

Where `{role}` can be: `system`, `user`, `assistant`, or `tool`.

#### System Message

The system message sets up the model's behavior and can include tool definitions:

```
<|start_header_id|>system<|end_header_id|>

You are Hermes, created by Nous Research.<|eot_id|>
```

For custom instructions:

```
<|start_header_id|>system<|end_header_id|>

You are Hermes 4. Be concise and helpful.<|eot_id|>
```

### Chat Messages

#### User Input Message Format

User messages follow this format:

```
<|start_header_id|>user<|end_header_id|>

What is 2 + 2?<|eot_id|>
```

#### Assistant Response Format

The assistant's response begins with its header and includes the content:

```
<|start_header_id|>assistant<|end_header_id|>

2 + 2 equals 4.<|eot_id|>
```

### Reasoning Mode with Chain-of-Thought

Hermes 4 supports a special reasoning mode where the model can show its internal deliberation process using `<think>` tags.

#### Activating Reasoning Mode

Reasoning mode can be activated by including this system prompt:

```
<|start_header_id|>system<|end_header_id|>

You are a deep thinking AI, you may use extremely long chains of thought to deeply consider the problem and deliberate with yourself via systematic reasoning processes to help come to a correct solution prior to answering. You should enclose your thoughts and internal monologue inside <think> </think> tags, and then provide your solution or response to the problem.<|eot_id|>
```

#### Model Response with Reasoning

When reasoning mode is active, the model's response includes thinking tags:

```
<|start_header_id|>assistant<|end_header_id|>

<think>
The user is asking for basic arithmetic. Let me calculate:
2 + 2 = 4
This is a simple addition problem.
</think>

2 + 2 equals 4.<|eot_id|>
```

**Note:** The content within `<think>...</think>` tags represents the model's internal reasoning and may not adhere to the same safety standards as the final output.

### Tool/Function Calling

Hermes 4 supports function calling with tools defined in the system message and invoked within assistant responses.

#### System Message with Tool Definitions

Tools are defined within `<tools>` tags in the system message:

```
<|start_header_id|>system<|end_header_id|>

You are a function-calling AI model. You may call one or more functions to assist with the user query.

You are provided with function signatures within <tools></tools> XML tags:
<tools>
{"type": "function", "function": {"name": "get_weather", "description": "Get weather by city", "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}}
</tools>

For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
<tool_call>
{"name": "<function-name>", "arguments": <args-json-object>}
</tool_call><|eot_id|>
```

#### Tool Invocation Format

When the model decides to call a tool, it generates a `<tool_call>` block:

```
<|start_header_id|>assistant<|end_header_id|>

I'll check the weather for you.

<tool_call>
{"name": "get_weather", "arguments": {"city": "San Francisco"}}
</tool_call><|eot_id|>
```

#### Tool Response Format

Tool responses are provided as user messages with `<tool_response>` tags:

```
<|start_header_id|>user<|end_header_id|>

<tool_response>
{"temperature": 20, "condition": "sunny", "humidity": 65}
</tool_response><|eot_id|>
```

### Multiple Tool Calls

The model can make multiple tool calls in sequence, with optional explanatory text:

```
<|start_header_id|>assistant<|end_header_id|>

I'll help you plan your trip by checking the weather in multiple cities.

<tool_call>
{"name": "get_weather", "arguments": {"city": "New York"}}
</tool_call><|eot_id|>
<|start_header_id|>user<|end_header_id|>

<tool_response>
{"temperature": 15, "condition": "cloudy"}
</tool_response><|eot_id|>
<|start_header_id|>assistant<|end_header_id|>

Now let me check Los Angeles.

<tool_call>
{"name": "get_weather", "arguments": {"city": "Los Angeles"}}
</tool_call><|eot_id|>
```

### Combined Reasoning and Tool Use

Hermes 4 can combine reasoning mode with tool calling for more sophisticated interactions:

```
<|start_header_id|>assistant<|end_header_id|>

<think>
The user wants weather information. I should use the get_weather function to retrieve current conditions.
</think>

Let me check the current weather for you.

<tool_call>
{"name": "get_weather", "arguments": {"city": "Seattle"}}
</tool_call><|eot_id|>
```

### Full Context Window Example

Here's a complete example showing a multi-turn conversation with reasoning and tool use:

```
<|start_header_id|>system<|end_header_id|>

You are a deep thinking AI assistant with access to tools. You may use extremely long chains of thought to deeply consider problems. Enclose your thoughts in <think> </think> tags.

You are provided with function signatures within <tools></tools> XML tags:
<tools>
{"type": "function", "function": {"name": "calculate", "description": "Perform mathematical calculations", "parameters": {"type": "object", "properties": {"expression": {"type": "string", "description": "Mathematical expression to evaluate"}}, "required": ["expression"]}}}
{"type": "function", "function": {"name": "get_date", "description": "Get current date", "parameters": {"type": "object", "properties": {}}}}
</tools>

For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags.<|eot_id|>
<|start_header_id|>user<|end_header_id|>

What's 15% of 280, and what day is it today?<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>

<think>
The user is asking two questions:
1. Calculate 15% of 280
2. Get today's date

I'll need to use both the calculate function for the math and get_date for the current date.
</think>

I'll help you with both calculations. Let me first calculate 15% of 280.

<tool_call>
{"name": "calculate", "arguments": {"expression": "280 * 0.15"}}
</tool_call><|eot_id|>
<|start_header_id|>user<|end_header_id|>

<tool_response>
42
</tool_response><|eot_id|>
<|start_header_id|>assistant<|end_header_id|>

Now let me get today's date for you.

<tool_call>
{"name": "get_date", "arguments": {}}
</tool_call><|eot_id|>
<|start_header_id|>user<|end_header_id|>

<tool_response>
2025-01-12
</tool_response><|eot_id|>
<|start_header_id|>assistant<|end_header_id|>

Based on the calculations:
- 15% of 280 is **42**
- Today's date is **January 12, 2025**

Is there anything else you'd like to know?<|eot_id|>
<|start_header_id|>user<|end_header_id|>

Thanks! Can you explain how you calculated the percentage?<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>

<think>
The user wants to understand the percentage calculation. I should explain the method clearly.
</think>

Of course! To calculate 15% of 280, I converted the percentage to a decimal and multiplied:

1. Convert 15% to decimal: 15% = 15/100 = 0.15
2. Multiply: 280 × 0.15 = 42

Alternatively, you could think of it as:
- 10% of 280 = 28
- 5% of 280 = 14 (half of 10%)
- 15% = 10% + 5% = 28 + 14 = 42

Both methods give you the same answer: 42.<|eot_id|>
```

### Key Differences from OpenAI Format

1. **Tag Structure**: Uses Llama-3 style header tags (`<|start_header_id|>`, `<|end_header_id|>`, `<|eot_id|>`) instead of OpenAI's format
2. **Reasoning Format**: Uses `<think>...</think>` tags for chain-of-thought instead of channels
3. **Tool Calling**: Uses `<tool_call>` and `<tool_response>` XML tags with JSON content
4. **No Channel System**: Does not use the channel-based system (analysis, commentary, final) from OpenAI
5. **Simpler Role System**: Uses standard roles (system, user, assistant, tool) without complex recipient specifications