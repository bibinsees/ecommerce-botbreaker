## Magistral Context Window Format

This is the context window format for Magistral (Mistral's reasoning models).

### Message Format

The Magistral format uses special tokens to structure conversations. Messages are wrapped in instruction tags with the model generating responses after each instruction.

#### System Message

The default system prompt for reasoning models is:

```
<BOS>[SYSTEM_PROMPT]A user will ask you to solve a task. You should first draft your thinking process (inner monologue) until you have derived the final answer. Afterwards, write a self-contained summary of your thoughts (i.e. your summary should be succinct but contain all the critical steps you needed to reach the conclusion). You should use Markdown and Latex to format your response. Write both your thoughts and summary in the same language as the task posed by the user.

Your thinking process must follow the template below:
<think>
Your thoughts or/and draft, like working through an exercise on scratch paper. Be as casual and as long as you want until you are confident to generate a correct answer.
</think>

Here, provide a concise summary that reflects your reasoning and presents a clear final answer to the user.

Problem:[/SYSTEM_PROMPT]
```

Custom system prompts can be provided and will be wrapped in `[SYSTEM_PROMPT]...[/SYSTEM_PROMPT]` tags with a BOS token at the beginning.

#### Chat Messages with Reasoning Steps

Magistral models perform chain-of-thought analysis before their response using `<think>` tags.

##### User Input Message Format

User messages are wrapped in `[INST]...[/INST]` tags. If this is the first message (no system prompt), it starts with BOS:

```
<BOS>[INST]What is 2 + 2?[/INST]
```

##### Model Reasoning and Response Format

The model outputs its reasoning in `<think>` tags, followed by the final answer:

```
<think>
User asks: "What is 2 + 2?" This is simple arithmetic. 2 + 2 equals 4.
</think>

2 + 2 = 4.<EOS>
```

The model may have multiple reasoning steps within the think tags:

```
<think>
User asks: "What is 2 + 2?" Let me think about this.
This is basic addition.
2 + 2 = 4.
I should provide a clear answer.
</think>

2 + 2 = 4.<EOS>
```

##### Multi-turn Conversations

In conversations with multiple turns, previous thinking content is typically preserved:

```
<BOS>[INST]What is 2 + 2?[/INST]
<think>
User asks: "What is 2 + 2?" Simple arithmetic. 2 + 2 = 4.
</think>

2 + 2 = 4.<EOS>
[INST]What about 9 / 2?[/INST]
<think>
Now the user asks about 9 / 2. This is division. 9 divided by 2 equals 4.5.
</think>

9 / 2 = 4.5.<EOS>
```

**Important:** The model's reasoning in `<think>` tags may not follow the same safety standards as the final output. The thinking process can contain unfiltered analysis.

#### Multimodal Input (Images)

When images are included in user messages, they are represented with `[IMG]` tokens:

```
<BOS>[INST]What's in this image? [IMG][/INST]
```

### Tool/Function Calling

#### Tool Definition Format

TODO: Include this section

#### Tool Invocation Format

When the model decides to call a tool, it uses `[TOOL_CALLS]` tags:

```
<think>
The user wants to know the weather. I need to use the get_current_weather function.
</think>

[TOOL_CALLS]
[{"name": "get_current_weather", "arguments": {"location": "San Francisco"}}]
[/TOOL_CALLS]<EOS>
```

#### Tool Response Format

Tool outputs are provided back to the model using `[TOOL_RESULTS]` tags:

```
[TOOL_RESULTS]
{"sunny": true, "temperature": 20}
[/TOOL_RESULTS]
```

#### Complete Tool Use Example

```
<BOS>[INST]What's the weather in San Francisco?[/INST]
<think>
The user wants to know the weather in San Francisco. I need to call the get_current_weather function.
</think>

[TOOL_CALLS]
[{"name": "get_current_weather", "arguments": {"location": "San Francisco"}}]
[/TOOL_CALLS]<EOS>
[TOOL_RESULTS]
{"sunny": true, "temperature": 20}
[/TOOL_RESULTS]
<think>
The weather data shows it's sunny with a temperature of 20 degrees. I'll provide this information to the user.
</think>

The weather in San Francisco is currently sunny with a temperature of 20°C.<EOS>
```

## Full Context Window Example

Here's a complete example showing system prompt, multi-turn conversation with reasoning, and tool use:

```
<BOS>[SYSTEM_PROMPT]You are a helpful assistant that can check weather and do calculations.[/SYSTEM_PROMPT]
[INST]What's 15 * 23?[/INST]
<think>
The user wants me to calculate 15 * 23.
Let me work this out:
15 * 20 = 300
15 * 3 = 45
300 + 45 = 345
</think>

15 * 23 = 345.<EOS>
[INST]Great! Now what's the weather in Paris?[/INST]
<think>
The user is asking about the weather in Paris. I need to use the get_current_weather function to get this information.
</think>

[TOOL_CALLS]
[{"name": "get_current_weather", "arguments": {"location": "Paris"}}]
[/TOOL_CALLS]<EOS>
[TOOL_RESULTS]
{"cloudy": true, "temperature": 15, "humidity": 65}
[/TOOL_RESULTS]
<think>
I received the weather data for Paris. It shows cloudy conditions with 15°C and 65% humidity. I'll present this information clearly to the user.
</think>

The current weather in Paris is cloudy with a temperature of 15°C and humidity at 65%.<EOS>
[INST]Is that good weather for sightseeing?[/INST]
<think>
The user is asking if 15°C and cloudy conditions are good for sightseeing in Paris. This is subjective, but I can provide a balanced perspective. 15°C is mild - not too hot or cold. Cloudy weather means no harsh sun but also less ideal for photos. It's generally comfortable for walking around.
</think>

Yes, that's quite good weather for sightseeing! At 15°C (59°F), it's comfortably cool for walking around the city without being too cold. The cloudy conditions mean you won't have to deal with harsh sun, though you might want to bring a light jacket. While sunny weather is better for photos, cloudy days can be perfect for exploring museums, cafes, and walking through Paris's charming streets without getting too warm.<EOS>
```

### Special Tokens and Tags Reference

1. **`<BOS>`** - Beginning of sequence token (placed at the start of a conversation)
2. **`<EOS>`** - End of sequence token (placed after each assistant response)
3. **`[INST]...[/INST]`** - User instruction/message wrapper
4. **`[SYSTEM_PROMPT]...[/SYSTEM_PROMPT]`** - System message wrapper
5. **`<think>...</think>`** - Model's reasoning/thinking process (HTML-style tags)
6. **`[IMG]`** - Image placeholder in multimodal inputs
7. **`[TOOL_CALLS]...[/TOOL_CALLS]`** - Tool/function invocation wrapper
8. **`[TOOL_RESULTS]...[/TOOL_RESULTS]`** - Tool response wrapper

Note: The BOS and EOS tokens are special tokens handled by the tokenizer. In the Jinja template, `bos_token` is added at the beginning of the sequence, and `eos_token` is appended after each assistant message. These are shown as `<BOS>` and `<EOS>` placeholders in the examples above for clarity.