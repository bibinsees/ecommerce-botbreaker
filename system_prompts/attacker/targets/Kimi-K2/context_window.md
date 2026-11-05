# Kimi-K2 Context Window Format

This is the context window format for the Kimi-K2 model, developed by Moonshot AI. Kimi-K2 uses a structured token-based format to represent conversations, system prompts, tool declarations, and tool interactions. Unlike some other models, Kimi-K2 does not employ explicit reasoning channels (such as analysis or commentary) but supports tool calling through dedicated section markers.

## Overview of Kimi-K2 Tags

Kimi-K2 utilizes special tokens to delineate roles, content, and sections within the context window. These tokens are essential for proper formatting and must be used exactly as specified. Below is a comprehensive list of all tags used in the Kimi-K2 format, along with their purposes and usage:

- **<|im_system|>**: Marks the beginning of a system-level message, such as tool declarations or default system prompts. It is followed by a role name (e.g., `tool_declare` or `system`) and then <|im_middle|>.
- **<|im_user|>**: Marks the beginning of a user message. It is followed by the user's name or role identifier and then <|im_middle|>.
- **<|im_assistant|>**: Marks the beginning of an assistant message. It is followed by the assistant's name or role identifier and then <|im_middle|>.
- **<|im_middle|>**: Separates the header (role/name) from the content of a message. All content follows this token until <|im_end|>.
- **<|im_end|>**: Marks the end of a complete message or section. It terminates system, user, assistant, or tool-related messages.
- **<|tool_calls_section_begin|>**: Indicates the start of a section containing one or more tool calls within an assistant message.
- **<|tool_call_begin|>**: Marks the beginning of an individual tool call. It is followed by the tool call ID and then <|tool_call_argument_begin|>.
- **<|tool_call_argument_begin|>**: Separates the tool call ID from the arguments. The arguments (JSON or string) follow this token until <|tool_call_end|>.
- **<|tool_call_end|>**: Marks the end of an individual tool call.
- **<|tool_calls_section_end|>**: Marks the end of the entire tool calls section within an assistant message.
- **<|media_start|>**: Marks the beginning of a media (e.g., image) content block within a message.
- **<|media_content|>**: Placeholder for the actual media content (e.g., image data).
- **<|media_pad|>**: Padding token for media content, ensuring proper alignment.
- **<|media_end|>**: Marks the end of a media content block.

**Unique Formatting Requirements**:
- All messages must start with a role token (e.g., <|im_system|>, <|im_user|>, <|im_assistant|>) followed by a name/role identifier and <|im_middle|>.
- Content is placed after <|im_middle|> and before <|im_end|>.
- Tool calls are nested within assistant messages using the tool-specific tokens.
- If tools are present, a tool declaration section must precede the conversation.
- For multi-turn conversations, each message is self-contained with its own start and end tokens.
- Kimi-K2 does not support explicit reasoning channels; all assistant content (including any internal reasoning) is handled within the message content itself.
- Media content (e.g., images) is supported via dedicated tokens, but the exact media data format must be handled externally.

## Message Format Overview

The Kimi-K2 format structures conversations as a sequence of messages, each beginning with a role token and ending with <|im_end|>. Messages can include text, tool calls, or media. The model may generate multiple messages in response, but each is delimited by these tokens.

The general structure of a message is:

```
{role_token}{name}<|im_middle|>{content}<|im_end|>
```

Where:
- `{role_token}` is one of <|im_system|>, <|im_user|>, or <|im_assistant|>.
- `{name}` is the role or name identifier (e.g., "system", "user", or a custom name).
- `{content}` is the message body, which may include text, tool calls, or media.

## System Message Structure

System messages in Kimi-K2 are used for model identity, instructions, and tool declarations. If tools are provided, the context starts with a tool declaration message. Otherwise, a default system message is inserted if the first user message lacks a system role.

### Default System Message

If the conversation begins without a system message, Kimi-K2 automatically prepends:

```
<|im_system|>system<|im_middle|>You are Kimi, an AI assistant created by Moonshot AI.<|im_end|>
```

This ensures the model has a baseline identity.

### Tool Declaration Format

If tools are available, they are declared at the beginning of the context using:

```
<|im_system|>tool_declare<|im_middle|>
# Tools
{tools_json}<|im_end|>
```

Where `{tools_json}` is a JSON representation of the available tools (e.g., their names, parameters, and descriptions). This section is optional and only included if tools are provided.

## Developer/System Prompt Format

Kimi-K2 integrates system prompts directly into system messages. There is no separate "developer" role; instead, custom instructions are placed in a system message at the start of the conversation.

Example of a custom system prompt:

```
<|im_system|>system<|im_middle|># Instructions

You are a helpful assistant that can provide weather information and perform calculations. Always respond clearly and accurately.<|im_end|>
```

If tools are also present, the tool declaration follows immediately after the system prompt in the same or a subsequent system message.

## Chat Message Formats

Chat messages in Kimi-K2 follow a simple structure without dedicated reasoning channels. User and assistant messages alternate, with optional tool interactions.

### User Message Format

User messages are straightforward:

```
<|im_user|>{name}<|im_middle|>{content}<|im_end|>
```

Where `{name}` is typically "user" or a custom identifier, and `{content}` is the user's input (text or media).

Example:

```
<|im_user|>user<|im_middle|>What is the weather in San Francisco?<|im_end|>
```

### Assistant Message Format

Assistant messages include the response content and any tool calls:

```
<|im_assistant|>{name}<|im_middle|>{content}{tool_calls}<|im_end|>
```

Where:
- `{name}` is typically "assistant".
- `{content}` is the assistant's text response (optional if only tool calls are present).
- `{tool_calls}` is a tool calls section if applicable.

Example without tool calls:

```
<|im_assistant|>assistant<|im_middle|>The weather in San Francisco is sunny with a temperature of 68°F.<|im_end|>
```

Kimi-K2 does not have built-in reasoning channels like analysis or commentary. Any internal reasoning must be included in the message content or omitted.

## Tool/Function Definition Formats

Tool definitions in Kimi-K2 are provided as JSON in the tool declaration section at the start of the context. Unlike some formats, Kimi-K2 does not use TypeScript-style type definitions; instead, tools are described in a structured JSON object.

Example tool declaration:

```
<|im_system|>tool_declare<|im_middle|>
# Tools
{
  "get_current_weather": {
    "description": "Get the current weather for a location",
    "parameters": {
      "type": "object",
      "properties": {
        "location": {
          "type": "string",
          "description": "The city and state, e.g., San Francisco, CA"
        },
        "unit": {
          "type": "string",
          "enum": ["celsius", "fahrenheit"],
          "default": "fahrenheit"
        }
      },
      "required": ["location"]
    }
  },
  "calculate": {
    "description": "Perform a calculation",
    "parameters": {
      "type": "object",
      "properties": {
        "expression": {
          "type": "string",
          "description": "Mathematical expression to evaluate"
        }
      },
      "required": ["expression"]
    }
  }
}<|im_end|>
```

**Notes on Tool Definitions**:
- Tools are defined in JSON schema format, supporting basic types (string, number, boolean), arrays, enums, and optional/default parameters.
- No namespaces are used; tools are listed as top-level objects.
- Complex objects and unions are supported via JSON schema properties.

## Tool Invocation Formats

If the assistant decides to call a tool, it includes a tool calls section within its message. Tool calls are formatted with dedicated tokens and end the assistant's message.

### Tool Call Format

Within an assistant message:

```
{content}<|tool_calls_section_begin|>
<|tool_call_begin|>{tool_call_id}<|tool_call_argument_begin|>{arguments}<|tool_call_end|>
{additional_tool_calls}
<|tool_calls_section_end|>
```

Where:
- `{tool_call_id}` is a unique identifier for the tool call.
- `{arguments}` is the JSON-stringified arguments for the tool.

Example:

```
<|im_assistant|>assistant<|im_middle|>I'll check the weather for you.<|tool_calls_section_begin|>
<|tool_call_begin|>call_123<|tool_call_argument_begin|>{"location": "San Francisco, CA"}<|tool_call_end|>
<|tool_calls_section_end|><|im_end|>
```

**Important Notes on Tool Calls**:
- Tool calls must be placed in the tool calls section within an assistant message.
- Arguments are JSON-formatted.
- Multiple tool calls can be included sequentially in the same section.
- The assistant message ends with <|im_end|> after the tool calls section.

### Providing Tool Output Responses

Tool outputs are provided as separate messages from the tool's perspective:

```
<|im_system|>tool<|im_middle|>## Return of {tool_call_id}
{output}<|im_end|>
```

Where `{output}` is the JSON or text response from the tool.

Example:

```
<|im_system|>tool<|im_middle|>## Return of call_123
{"temperature": 68, "condition": "sunny"}<|im_end|>
```

The conversation then continues with the assistant processing the output.

## Full Context Window Examples

### Simple Conversation Without Tools

```
<|im_system|>system<|im_middle|>You are Kimi, an AI assistant created by Moonshot AI.<|im_end|>
<|im_user|>user<|im_middle|>What is 2 + 2?<|im_end|>
<|im_assistant|>assistant<|im_middle|>2 + 2 = 4.<|im_end|>
<|im_user|>user<|im_middle|>What about 9 / 2?<|im_end|>
<|im_assistant|>assistant<|im_middle|>9 / 2 = 4.5.<|im_end|>
```

### Conversation with Tools

```
<|im_system|>tool_declare<|im_middle|>
# Tools
{
  "get_current_weather": {
    "description": "Get the current weather for a location",
    "parameters": {
      "type": "object",
      "properties": {
        "location": {"type": "string"},
        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"], "default": "fahrenheit"}
      },
      "required": ["location"]
    }
  },
  "calculate": {
    "description": "Perform a calculation",
    "parameters": {
      "type": "object",
      "properties": {
        "expression": {"type": "string"}
      },
      "required": ["expression"]
    }
  }
}<|im_end|>
<|im_system|>system<|im_middle|>You are a helpful assistant that can help with weather information and calculations.<|im_end|>
<|im_user|>user<|im_middle|>What's the weather in San Francisco and what's 15% of 240?<|im_end|>
<|im_assistant|>assistant<|im_middle|>I'll check the weather and perform the calculation.<|tool_calls_section_begin|>
<|tool_call_begin|>call_456<|tool_call_argument_begin|>{"location": "San Francisco, CA"}<|tool_call_end|>
<|tool_call_begin|>call_789<|tool_call_argument_begin|>{"expression": "240 * 0.15"}<|tool_call_end|>
<|tool_calls_section_end|><|im_end|>
<|im_system|>tool<|im_middle|>## Return of call_456
{"temperature": 68, "condition": "sunny"}<|im_end|>
<|im_system|>tool<|im_middle|>## Return of call_789
{"result": 36}<|im_end|>
<|im_assistant|>assistant<|im_middle|>The weather in San Francisco is 68°F and sunny. 15% of 240 is 36.<|im_end|>
```

### Conversation with Media

```
<|im_user|>user<|im_middle|>Describe this image.<|media_start|>image<|media_content|>{image_data}<|media_pad|><|media_end|><|im_end|>
<|im_assistant|>assistant<|im_middle|>This appears to be a sunny landscape with mountains in the background.<|im_end|>
```

## Key Points Summary

1. **System Messages**: Used for identity, instructions, and tool declarations. Default system message is auto-inserted if needed.
2. **Message Structure**: Each message follows `{role_token}{name}<|im_middle|>{content}<|im_end|>`. Roles are system, user, or assistant.
3. **Tool Support**: Tools are declared in JSON at the start. Calls use dedicated section tokens within assistant messages. Outputs are separate tool messages.
4. **No Reasoning Channels**: Kimi-K2 does not have analysis, commentary, or final channels; all content is in the message body.
5. **Media Handling**: Images are supported via <|media_start|> tokens, but require external handling for content.
6. **Context Management**: Full conversation history is retained; no dropping of prior content is specified.
7. **Limitations**: Kimi-K2 does not support advanced features like TypeScript-style tool definitions or explicit reasoning separation. Tool calling is simpler but functional.

## Comparison with OpenAI Harmony Format

Kimi-K2's format is simpler and more linear than OpenAI Harmony's, lacking reasoning channels and using JSON for tool definitions instead of TypeScript namespaces.

### Side-by-Side Comparison of Key Syntax Differences

| Aspect                  | OpenAI Harmony                          | Kimi-K2                                |
|-------------------------|-----------------------------------------|----------------------------------------|
| Message Start           | `<|start|>{role}`                      | `{role_token}{name}` (e.g., <|im_user|>user) |
| Message Separator       | `<|message|>`                          | `<|im_middle|>`                        |
| Message End             | `<|end|>`, `<|call|>`, `<|return|>`    | `<|im_end|>`                          |
| Channels                | `analysis`, `commentary`, `final`       | None (no channels)                     |
| Tool Definitions        | TypeScript namespace syntax            | JSON schema                           |
| Tool Calls              | `to=functions.{name}` in header         | `<|tool_call_begin|>{id}<|tool_call_argument_begin|>{args}` |
| Tool Outputs            | `<|start|>functions.{name} to=assistant` | `<|im_system|>tool<|im_middle|>## Return of {id}` |
| Reasoning               | Separate channels for CoT              | Integrated in message content          |

### Mapping Table: Equivalent Tags/Tokens

| OpenAI Harmony Token/Concept | Kimi-K2 Equivalent                  | Notes |
|------------------------------|-------------------------------------|-------|
| `<|start|>system`            | `<|im_system|>system`              | Role-based start token |
| `<|start|>user`              | `<|im_user|>user`                  | Role-based start token |
| `<|start|>assistant`         | `<|im_assistant|>assistant`        | Role-based start token |
| `<|channel|>analysis`        | N/A (no equivalent)                 | Kimi-K2 lacks channels; reasoning in content |
| `<|channel|>commentary`      | N/A (integrated in assistant message) | Tool calls are in message body |
| `<|channel|>final`           | N/A (no equivalent)                 | All responses are final |
| Tool namespace (e.g., `functions.get_current_weather`) | Tool name in JSON (e.g., `"get_current_weather"`) | Simpler naming without namespaces |
| `<|constrain|>json`          | Implicit (arguments always JSON)    | No explicit constraint token |
| `<|call|>`                   | `<|tool_call_end|>`                 | Ends tool call section |
| `<|return|>`                 | N/A (no equivalent)                 | Kimi-K2 uses <|im_end|> for all endings |

### Functional Differences

- **Reasoning**: OpenAI Harmony separates chain-of-thought (analysis) from user-facing responses (final). Kimi-K2 integrates everything into the message content, making it less structured for internal reasoning.
- **Tool Calling**: OpenAI uses recipient headers and channels; Kimi-K2 uses nested tokens within assistant messages for simplicity.
- **Complexity**: Kimi-K2 is more straightforward, with fewer tokens and no channel management, making it easier for basic interactions but less flexible for complex reasoning or multi-step tool plans.
- **Safety**: OpenAI notes that analysis channel content may be unsafe; Kimi-K2 has no such distinction, so all content should be treated as potentially user-facing.

### Migration Tips for Users Familiar with OpenAI Harmony

- **Replace Channels**: Remove `<|channel|>` tags and integrate any reasoning into the assistant's content.
- **Simplify Tool Definitions**: Convert TypeScript namespaces to JSON schema.
- **Adjust Message Structure**: Use Kimi-K2's role tokens instead of `<|start|>` and `<|message|>`.
- **Handle Tool Calls**: Nest tool calls in assistant messages using the section tokens; provide outputs as separate tool messages.
- **Test Thoroughly**: Since Kimi-K2 lacks reasoning channels, ensure that any CoT is explicitly included in responses if needed for clarity.