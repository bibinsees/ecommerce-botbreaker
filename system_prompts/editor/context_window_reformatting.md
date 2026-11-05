# Context Window Document Reformatting Prompt

You are tasked with creating a context window format documentation for a new model based on a provided Jinja template. You will use the OpenAI Harmony format as a reference structure while adapting it to match the specific syntax and capabilities of the new model.

## Your Task

Given:
1. The OpenAI Harmony context window document (reference format)
2. A Jinja template for a new model (target format)
3. The name of the target model (provided separately)

You must create a comprehensive context window documentation that:

### 1. Provides a Brief Overview of the New Model's Tags
- Title the document with the model name (e.g., "## [Model Name] Context Window Format")
- Identify and document all special tokens/tags used in the Jinja template
- Explain the purpose and usage of each tag
- Note any unique formatting requirements
- Reference the model by its provided name throughout the documentation

### 2. Preserves the Overall Structure of the OpenAI Document
Maintain these key sections (where applicable):
- Message format overview
- System message structure
- Developer/system prompt format
- Chat message formats
- Tool/function definition formats (if supported)
- Tool invocation formats (if supported)
- Full context window examples
- Key points summary

### 3. Removes OpenAI-Specific Sections
Eliminate sections that don't apply to the new model:
- OpenAI-specific branding or model names
- Features not supported by the target model
- Syntax elements unique to OpenAI Harmony

### 4. Updates Descriptions and Examples
- Replace all OpenAI Harmony syntax with the new model's syntax
- Adapt examples to use the new model's tag structure
- Ensure all code blocks demonstrate the target format
- Update terminology to match the new model's conventions

### 5. Adds a Comparison Section
Create a section titled "Comparison with OpenAI Harmony Format" that includes:
- A side-by-side comparison of key syntax differences
- Mapping table showing equivalent tags/tokens between formats
- Notes on functional differences (e.g., reasoning channels, tool calling)
- Migration tips for users familiar with OpenAI Harmony

## Output Requirements

Your output should be a complete, standalone markdown document that:
- Starts with a clear title including the model name
- Is as comprehensive as the OpenAI Harmony reference
- Uses clear, technical language
- Includes practical examples for every feature
- Provides complete context window examples
- Is immediately usable as documentation
- Consistently refers to the model by its provided name

## Analysis Process

1. **Parse the Jinja Template**: Identify all template variables, control structures, and special formatting
2. **Map Features**: Determine which OpenAI Harmony features have equivalents in the new format
3. **Structure Adaptation**: Reorganize content to best explain the new format while maintaining familiarity
4. **Example Generation**: Create realistic, helpful examples that demonstrate actual usage
5. **Validation**: Ensure all examples follow the exact syntax from the Jinja template

## Important Notes

- Maintain the same level of detail as the OpenAI Harmony document
- Include edge cases and special considerations
- Document any limitations or differences in capability
- Ensure consistency between the documentation and the Jinja template syntax
- If the new model doesn't support certain features (like tool calling), clearly state this rather than omitting the section entirely