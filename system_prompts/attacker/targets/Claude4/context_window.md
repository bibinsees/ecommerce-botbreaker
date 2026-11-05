## Claude (Anthropic) Context Window Format

This is the context window format for Claude models by Anthropic, including Claude Sonnet 4.5 and Claude Haiku 4.5.

### Claude Token Reference

Here is a complete list of all special tokens and XML-style tags used in the Claude format:

#### Function/Tool Definition Tags
- `<tools>` (or `<functions>`) - Opening tag for the tools section (appears before system prompt)
- `</tools>` (or `</functions>`) - Closing tag for the tools section
- `<tool_description>` (or `<function>`) - Opening tag for individual tool descriptions
- `</tool_description>` (or `<function>`)- Closing tag for individual tool descriptions

#### System Configuration Tags
- `<budget:token_budget>` - Opening tag for token budget specification
- `</budget:token_budget>` - Closing tag for token budget specification

#### System Configuration Tags
- `<system>` - Opening tag for system-level instructions
- `</system>` - Closing tag for system instructions

#### User Message Tags
- `<human>` (or `<user>`) - Opening tag for user input messages
- `</human>` (or `</user>`)- Closing tag for user messages

#### Assistant Message Tags
- `<assistant>` (or `<response>`)- Opening tag for assistant responses and thinking
- `</assistant>` (or `</response>`) - Closing tag for assistant messages

#### Thinking/Reasoning Tags
- `<antml:thinking>` - Opening tag for internal reasoning and chain-of-thought
- `</antml:thinking>` - Closing tag for internal reasoning

#### Tool Invocation Tags
- `<antml:function_calls>` - Opening tag for a block of function calls
- `</antml:function_calls>` - Closing tag for a function call block
- `<antml:invoke name="function_name">` - Opening tag for invoking a specific function
- `</antml:invoke>` - Closing tag for a function invocation
- `<antml:parameter name="param_name">` - Opening tag for a function parameter
- `</antml:parameter>` - Closing tag for a function parameter

#### Tool Response Tags
- `<function_results>` - Opening tag for tool execution results
- `</function_results>` - Closing tag for tool execution results
- `<result>` - Opening tag for an individual tool result
- `</result>` - Closing tag for an individual tool result
- `<name>` - Opening tag for the function name in a result
- `</name>` - Closing tag for the function name
- `<output>` - Opening tag for the function output/return value
- `</output>` - Closing tag for the function output

#### System Warning Tags
- `<antml:system_warning>` - Opening tag for system warnings (e.g., token usage)
- `</antml:system_warning>` - Closing tag for system warnings

#### Token Budget Tags
- `<antml:max_thinking_length>` - Opening tag specifying maximum thinking length
- `</antml:max_thinking_length>` - Closing tag for maximum thinking length

### Message Format

The Claude format uses XML-style tags to structure messages. Unlike some other models, Claude's context window has a specific structure where tool definitions appear **before** the system prompt, followed by the developer prompt, and then the conversation messages.

### Context Window Structure

The complete context window follows this order:

1. **Tool Definitions** (if tools are available)
2. **Thinking Budget Configuration**
3. **Token Budget Configuration**
4. **System Message** (pre-configured by Anthropic)
5. **Developer Prompt** (user-provided instructions)
6. **Conversation Messages** (alternating human and assistant messages)

### Tool Definition Format (Native)

Tool definitions appear at the very beginning of the context window, before any system messages. They are enclosed in `<tools>` tags and contain JSON Schema-style function definitions:

```
<tools>
<tool_description>
{
  "name": "get_weather",
  "description": "Get the current weather for a location",
  "parameters": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "The city and state, e.g. San Francisco, CA"
      },
      "unit": {
        "type": "string",
        "enum": ["celsius", "fahrenheit"],
        "description": "The temperature unit to use"
      }
    },
    "required": ["location"]
  }
}
</tool_description>
<tool_description>
{
  "name": "calculate",
  "description": "Perform a mathematical calculation",
  "parameters": {
    "type": "object",
    "properties": {
      "expression": {
        "type": "string",
        "description": "The mathematical expression to evaluate"
      }
    },
    "required": ["expression"]
  }
}
</tool_description>
</tools>
```

Each tool is defined as a JSON object within `<tool_description>` tags. The JSON schema follows OpenAPI/JSON Schema conventions with:
- `name`: The function name
- `description`: What the function does
- `parameters`: A JSON Schema object describing parameters
  - `type`: Typically "object"
  - `properties`: Object defining each parameter
  - `required`: Array of required parameter names

### Tool Definition Format (Legacy)

Claude models also support a legacy tool definition format using the tags `<functions>` and `<function>`.

As with the native format, tool definitions appear at the start of the context window, but within within `<functions></functions>` tags. Each function is defined using flatter JSON format within individual `<function></function>` tags:

```json
<functions>
<function>
{"description": "Charge the user's saved payment method for the specified amount. Returns confirmation if successful.", "name": "invoice_user", "parameters": {"amount": {"description": "Parameter amount", "type": "number", "required": true}}}
</function>
<function>
{"description": "Check invoice status and return simplified JSON structure.", "name": "check_invoice", "parameters": {"invoice_id": {"description": "Parameter invoice_id", "type": "string", "required": true}}}
</function>
<function>
{"description": "Search the web for the given query and return up to max_results results.", "name": "search_web", "parameters": {"max_results": {"default": 5, "description": "Parameter max_results", "type": "integer", "required": false}, "query": {"description": "Parameter query", "type": "string", "required": true}}}
</function>
</functions>
```

Each function definition is a complete JSON object on a single line containing:
- `description`: Explanation of what the tool does
- `name`: The function name to be invoked
- `parameters`: Dict of parameter definitions, each with:
  - `name`: Parameter identifier
    - `type`: Data type (string, number, boolean, object, array, etc.)
    - `description`: Explanation of the parameter's purpose
    - `required`: Boolean indicating if the parameter is mandatory

### Configuration Tags

After tool definitions, configuration tags may appear:

```
<antml:max_thinking_length>51200</antml:max_thinking_length>

<budget:token_budget>1000000</budget:token_budget>
```

These specify:
- `<antml:max_thinking_length>`: Maximum tokens for reasoning/thinking
- `<budget:token_budget>`: Total token budget for the conversation

### System Message Format

The system message follows the configuration and precedes the developer prompt. It contains pre-configured instructions from Anthropic:

```
<system>You are Claude, a large language model trained by Anthropic.
Knowledge cutoff: April 2024
Current date: 2025-06-28

You have access to a set of tools you can use to answer the user's question.</system>
```

The system message typically includes:
- Model identity
- Knowledge cutoff date
- Current date
- Information about available tools (if any)

### Developer Prompt Format

The developer prompt (often called "system prompt" by users) comes after the system message and before conversation messages. It contains custom instructions:

```
You are a helpful assistant that can check weather and perform calculations.

When calling functions, ensure you provide all required parameters.
```

In most frameworks, they are inside the `<system>` tag, after the system message.

In some frameworks, developer prompts are included in the `<human>` tag since they represent initial instructions from the user/developer.

### Chat Message Format

Chat messages alternate between `<human>` and `<assistant>` tags.

#### User/Human Message Format

User messages are wrapped in `<human>` tags:

```
<human>What's the weather in San Francisco?</human>
```

For multi-line user messages:

```
<human>I have a few questions:

1. What's the weather in New York?
2. Can you calculate 15% of 240?

Please help with both.</human>
```

In some frameworks, `<user>` may be used instead of `<human>`.

#### Assistant Message Format

Assistant messages are wrapped in `<assistant>` tags:

```
<assistant>The weather in San Francisco is currently sunny with a temperature of 68°F.</assistant>
```

For multi-line assistant messages:

```
<assistant>I'd be happy to help you with both questions!

Let me check the weather and perform that calculation for you.</assistant>
```

In some frameworks, `<response>` may be used instead of `<assistant>`.

### Reasoning/Thinking Format

Claude uses `<antml:thinking>` tags for internal chain-of-thought reasoning. This reasoning appears within the assistant's response but is typically hidden from end users in production applications:

```
<assistant>
<antml:thinking>
The user is asking for weather information. I should use the get_weather function with location set to "San Francisco, CA". I'll need to make a function call to retrieve this information.
</antml:thinking>

Let me check the weather for you.
</assistant>
```

**Important Notes About Thinking:**
- Thinking content appears at the start of assistant messages
- It is visible in the most recent assistant turn in the context window
- Previous thinking from earlier turns may be removed by the framework to save context
- Thinking allows the model to reason before responding or calling tools
- The content in thinking tags has not been trained to the same safety standards as final output

### Tool Invocation Format

When Claude calls tools, it uses a structured XML format within `<antml:function_calls>` tags:

#### Single Tool Call

```
<assistant>
<antml:function_calls>
<antml:invoke name="get_weather">
<antml:parameter name="location">San Francisco, CA</antml:parameter>
<antml:parameter name="unit">fahrenheit</antml:parameter>
</antml:invoke>
</antml:function_calls>
</assistant>
```

#### Multiple Tool Calls

Claude can invoke multiple independent tools in a single function_calls block:

```
<assistant>
<antml:function_calls>
<antml:invoke name="get_weather">
<antml:parameter name="location">New York, NY</antml:parameter>
</antml:invoke>
<antml:invoke name="calculate">
<antml:parameter name="expression">240 * 0.15</antml:parameter>
</antml:invoke>
</antml:function_calls>
</assistant>
```

#### Tool Calls with Complex Parameters

For parameters that are arrays or objects, Claude uses JSON formatting:

```
<assistant>
<antml:function_calls>
<antml:invoke name="process_items">
<antml:parameter name="items">[{"name": "item1", "value": 10}, {"name": "item2", "value": 20}]</antml:parameter>
</antml:invoke>
</antml:function_calls>
</assistant>
```

#### Tool Calls with Thinking

Typically, tool calls are preceded by reasoning:

```
<assistant>
<antml:thinking>
The user wants weather for San Francisco. I need to call get_weather with location="San Francisco, CA". They didn't specify a unit, so I'll use fahrenheit as it's common in the US.
</antml:thinking>

<antml:function_calls>
<antml:invoke name="get_weather">
<antml:parameter name="location">San Francisco, CA</antml:parameter>
<antml:parameter name="unit">fahrenheit</antml:parameter>
</antml:invoke>
</antml:function_calls>
</assistant>
```

### Tool Response Format

Tool execution results are provided back to the model using `<function_results>` tags:

#### Single Tool Response

```
<function_results>
<result>
<name>get_weather</name>
<output>{"temperature": 68, "condition": "sunny", "humidity": 65}</output>
</result>
</function_results>
```

#### Multiple Tool Responses

When multiple tools were called, results are provided in the same order:

```
<function_results>
<result>
<name>get_weather</name>
<output>{"temperature": 72, "condition": "partly cloudy", "humidity": 70}</output>
</result>
<result>
<name>calculate</name>
<output>{"result": 36}</output>
</result>
</function_results>
```

#### Error Responses

Tool errors are also provided in the output field:

```
<function_results>
<result>
<name>check_invoice</name>
<output>{"error": "Invoice not found"}</output>
</result>
</function_results>
```

### System Warnings

After tool results, the system may inject warnings about resource usage:

```
<antml:system_warning>Token usage: 11691/1000000; 988309 remaining</antml:system_warning>
```

These warnings inform about:
- Current token usage
- Total token budget
- Remaining tokens available

### Full Context Window Example

Here is a comprehensive example showing a complete context window with all elements:

```
<tools>
<tool_description>
{
  "name": "get_weather",
  "description": "Get the current weather for a location",
  "parameters": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "The city and state, e.g. San Francisco, CA"
      },
      "unit": {
        "type": "string",
        "enum": ["celsius", "fahrenheit"],
        "description": "The temperature unit to use"
      }
    },
    "required": ["location"]
  }
}
</tool_description>
<tool_description>
{
  "name": "calculate",
  "description": "Perform a mathematical calculation",
  "parameters": {
    "type": "object",
    "properties": {
      "expression": {
        "type": "string",
        "description": "The mathematical expression to evaluate"
      }
    },
    "required": ["expression"]
  }
}
</tool_description>
</tools>

<antml:max_thinking_length>51200</antml:max_thinking_length>

<budget:token_budget>1000000</budget:token_budget>

<system>You are Claude, a large language model trained by Anthropic.
Knowledge cutoff: April 2024
Current date: 2025-06-28

You have access to a set of tools you can use to answer the user's question.

# Developer Prompt

You are a helpful assistant that can help with weather information and calculations.
When the user asks about weather, use the get_current_weather function.
Be clear and concise in your responses.
</system>

<human>Hi! Can you tell me the weather in San Francisco and New York? Also, what's 15% of 240?</human>

<assistant>
<antml:thinking>
The user is asking for three pieces of information:
1. Weather in San Francisco
2. Weather in New York
3. Calculate 15% of 240

I have tools available for both tasks. I can call get_weather twice (once for each city) and calculate once for the math problem. Since these are all independent operations, I can make all three calls in the same function_calls block.

For the weather calls, I'll use:
- location: "San Francisco, CA" and "New York, NY"
- I'll use fahrenheit since these are US cities

For the calculation:
- expression: "240 * 0.15"
</antml:thinking>

I'll help you get the weather information for both cities and calculate that percentage for you.

<antml:function_calls>
<antml:invoke name="get_weather">
<antml:parameter name="location">San Francisco, CA</antml:parameter>
<antml:parameter name="unit">fahrenheit</antml:parameter>
</antml:invoke>
<antml:invoke name="get_weather">
<antml:parameter name="location">New York, NY</antml:parameter>
<antml:parameter name="unit">fahrenheit</antml:parameter>
</antml:invoke>
<antml:invoke name="calculate">
<antml:parameter name="expression">240 * 0.15</antml:parameter>
</antml:invoke>
</antml:function_calls>
</assistant>

<function_results>
<result>
<name>get_weather</name>
<output>{"temperature": 68, "condition": "sunny", "humidity": 65, "wind_speed": 8}</output>
</result>
<result>
<name>get_weather</name>
<output>{"temperature": 75, "condition": "partly cloudy", "humidity": 72, "wind_speed": 12}</output>
</result>
<result>
<name>calculate</name>
<output>{"result": 36}</output>
</result>
</function_results>

<antml:system_warning>Token usage: 3421/1000000; 996579 remaining</antml:system_warning>

<assistant>Here's the information you requested:

**Weather:**
- **San Francisco, CA**: Currently 68°F and sunny with 65% humidity and 8 mph winds
- **New York, NY**: Currently 75°F and partly cloudy with 72% humidity and 12 mph winds

**Calculation:**
15% of 240 = 36

New York is warmer than San Francisco by 7 degrees Fahrenheit right now!</assistant>

<human>Thanks! Is New York more humid too?</human>

<assistant>
<antml:thinking>
The user is asking about humidity comparison. I already have this information from the previous weather calls:
- San Francisco: 65% humidity
- New York: 72% humidity

So yes, New York is more humid. The difference is 7%.

I don't need to make any new tool calls since I already have this information from the previous response.
</antml:thinking>

Yes, New York is also more humid than San Francisco. New York currently has 72% humidity compared to San Francisco's 65% humidity, making New York 7% more humid.

So New York is both warmer and more humid than San Francisco right now!</assistant>
```

### Comparison with OpenAI Harmony Format

Claude's context window format shares some high-level concepts with OpenAI Harmony (used in GPT-5 and GPT-OSS models) but differs significantly in structure, tool placement, and syntax.

#### Mapping Table: Equivalent Tags/Tokens

| OpenAI Harmony | Claude Equivalent | Notes |
|----------------|-------------------|-------|
| `<|start|>system<|message|>...<|end|>` | `<system>...</system>` | Claude system is pre-configured by Anthropic |
| `<|start|>developer<|message|>...<|end|>` | `<system>...</system>` | Developer prompt appended to system |
| `<|start|>user<|message|>...<|end|>` | `<human>...</human>` | Direct mapping for user input |
| `<|start|>assistant<|message|>...<|end|>` | `<assistant>...</assistant>` | Direct mapping for assistant output |
| `<|channel|>analysis<|message|>{cot}<|end|>` | `<antml:thinking>{cot}</antml:thinking>` | Thinking within assistant message |
| `<|channel|>final<|message|>{response}<|end|>` | `{response}` (in assistant) | No separate final channel |
| Tool definitions in developer message | `<tools><tool_description>{json}</tool_description></tools>` | Tools appear before system message |
| `namespace functions { type {name} = ... }` | JSON Schema object | Different definition format |
| `to=functions.{name}<|constrain|>json<|message|>{args}<|call|>` | `<antml:invoke name="{name}"><antml:parameter>...` | Structured XML format |
| `<|start|>functions.{name}...<|message|>{output}<|end|>` | `<function_results><result><name>...<output>...` | XML result structure |
| `<|channel|>commentary` (for tools) | (none) | No separate commentary channel |
| `<|end|>` | `</assistant>`, `</human>` | XML closing tags |

#### Migration Tips for Users Familiar with OpenAI Harmony

**Restructure Context Window:**
- Move tool definitions from developer message to the beginning of the context
- Place them in `<tools>` tags before the system message
- Convert TypeScript definitions to JSON Schema format

**Convert Tool Definitions:**
- Transform `namespace functions { type name = (_: {...}) => any; }` 
- Into JSON: `{"name": "...", "description": "...", "parameters": {...}}`
- Each tool needs its own `<tool_description>` tags

**Adapt Message Structure:**
- Replace `<|start|>{role}<|message|>...<|end|>` with `<{role}>...</{role}>`
- Change "user" to "human" for user messages
- Remove channel specifications entirely

**Refactor Tool Calls:**
- Replace `<|channel|>commentary to=functions.{name}<|constrain|>json<|message|>{json}<|call|>`
- With `<antml:function_calls><antml:invoke name="{name}"><antml:parameter name="{key}">{value}</antml:parameter></antml:invoke></antml:function_calls>`
- Extract JSON object fields into individual parameters

**Handle Tool Responses:**
- Wrap responses in `<function_results>` instead of using role-based messages
- Use `<result>` with `<name>` and `<output>` tags
- Remove `to=assistant` and channel information

**Convert Reasoning:**
- Extract content from `<|channel|>analysis` messages
- Wrap in `<antml:thinking>` tags at the start of assistant messages
- Remove channel separation logic

**Update Developer Prompt:**
- Move from `<|start|>developer` to first `<human>` message
- Keep tool definitions separate (they go before system message)
- Maintain instruction content but adapt format

**Context Management:**
- Claude retains thinking in current turn but may drop previous turns
- Similar to OpenAI's approach of dropping analysis channel history
- Implement similar truncation strategies

**Testing Considerations:**
- Claude doesn't have separate channels for safety filtering
- Implement filtering of `<antml:thinking>` tags for end users
- Both models have unsafe reasoning that should be filtered

**Complex Parameters:**
- Both formats support complex JSON parameters
- Claude places JSON objects directly in `<antml:parameter>` values
- OpenAI includes them in the overall JSON argument object

**Batch Tool Calls:**
- Claude naturally supports multiple `<antml:invoke>` in one `<antml:function_calls>` block
- OpenAI can make multiple calls but each gets its own message
- Claude's approach is more efficient for independent parallel calls

**Framework Integration:**
- Update parsers to handle XML format instead of pipe-delimited tokens
- Tool definitions must be injected before system message, not in developer prompt
- Response parsing needs to extract from `<function_results>` XML structure

#### Flexible Tag Formats

Claude has more flexibility with tool definitions and role tags than OpenAI. Various synonyms for tags are accepted. This can make filtering harder. Typically only the antml namespace is blocked, if at all. Instead, guardrail models decide acceptable input and output, such that the API will not provide a response if the guardrail blocks a message.
