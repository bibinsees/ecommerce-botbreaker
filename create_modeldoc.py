#!/usr/bin/env python3
"""
Command line utility to create context window documentation for AI models.

This tool uses an LLM to generate comprehensive context window documentation
based on a Jinja template, using the OpenAI Harmony format as a reference.

Usage:
    python create_modeldoc.py <jinja_file> <output_file>

Environment Variables:
    EDITOR_LLM_MODEL: The LLM model to use for generation (required)
"""

import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

from lib.config import AttackConfig


def load_file_content(filepath: Path) -> str:
    """Load and return the content of a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{filepath}': {e}")
        sys.exit(1)


def get_llm_model() -> str:
    """Get the LLM model from configuration."""
    return AttackConfig.get_instance().get_model('editor')


def create_context_window_doc(
    jinja_content: str,
    openai_harmony_content: str,
    reformatting_prompt: str,
    model: str,
    model_name: str
) -> str:
    """
    Generate context window documentation using the LLM.
    
    Args:
        jinja_content: Content of the Jinja template
        openai_harmony_content: Content of the OpenAI Harmony reference document
        reformatting_prompt: The prompt for reformatting
        model: The LLM model to use
        model_name: The name of the target model for documentation
        
    Returns:
        Generated context window documentation
    """
    # Initialize OpenAI client with editor credentials
    config = AttackConfig.get_instance()
    client = OpenAI(
        api_key=config.get_api_key('editor'),
        base_url=config.get_base_url('editor')
    )
    
    # Construct the full prompt
    full_prompt = f"""
{reformatting_prompt}

---

## Target Model Name: {model_name}

---

## Reference Document: OpenAI Harmony Context Window Format

{openai_harmony_content}

---

## Target Jinja Template for {model_name}

```jinja
{jinja_content}
```

---

Based on the above reference document and Jinja template, create a comprehensive context window documentation for the {model_name} model.

Important:
- Use "{model_name}" as the model name throughout the documentation
- Title the document appropriately for {model_name}
- Refer to the model as "{model_name}" in all examples and descriptions
- Follow all the requirements specified in the reformatting prompt
"""
    
    try:
        # Get model settings from config
        model_settings = config.get_model_settings('editor')
        
        # Build completion arguments
        completion_args = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a technical documentation expert specializing in AI model context window formats. Create clear, comprehensive, and accurate documentation."
                },
                {
                    "role": "user",
                    "content": full_prompt
                }
            ]
        }
        
        # Add temperature, seed, and reasoning_effort from config
        # None values will be ignored by the API
        if model_settings['temperature'] is not None:
            completion_args['temperature'] = model_settings['temperature']
        if model_settings['seed'] is not None:
            completion_args['seed'] = model_settings['seed']
        if model_settings['reasoning'] is not None:
            completion_args['reasoning_effort'] = model_settings['reasoning']
        
        # Make the API call
        print(f"Generating documentation using {model}...")
        response = client.chat.completions.create(**completion_args)
        
        content = response.choices[0].message.content
        if content is None:
            print("Error: LLM returned empty response")
            sys.exit(1)
        return content
        
    except Exception as e:
        print(f"Error calling LLM API: {e}")
        sys.exit(1)


def save_output(content: str, filepath: Path) -> None:
    """Save the generated content to a file."""
    try:
        # Create parent directories if they don't exist
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Documentation successfully saved to: {filepath}")
    except Exception as e:
        print(f"Error saving output file: {e}")
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    # Load environment variables from .env file
    load_dotenv()

    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Generate context window documentation for AI models based on Jinja templates.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python create_modeldoc.py template.jinja "Claude-4" system_prompts/attacker/targets/claude4/context_window.md
  python create_modeldoc.py llama.jinja "Llama-4" system_prompts/attacker/targets/llama4/context_window.md
       """
    )

    parser.add_argument(
        'jinja_file',
        type=str,
        help='Path to the Jinja template file'
    )

    parser.add_argument(
        'model_name',
        type=str,
        help='Name of the target model (e.g., "Claude-3", "GPT-4", "Llama-3")'
    )

    parser.add_argument(
        'output_file',
        type=str,
        help='Path for the output documentation file'
    )

    parser.add_argument(
        "--conf",
        default="conf/create_modeldoc.yaml",
        help="Path to the attack configuration YAML file"
    )

    parser.add_argument(
        '--reference-modeldoc',
        type=str,
        default=None,
        help='Path to an alternate reference context window doc (default: from config)'
    )

    # Parse arguments to get conf first
    temp_args, _ = parser.parse_known_args()

    # Initialize config
    AttackConfig.initialize(temp_args.conf)
    config = AttackConfig.get_instance()

    # Parse arguments
    args = parser.parse_args()

    # Set default for reference_modeldoc from config if not provided
    if args.reference_modeldoc is None:
        args.reference_modeldoc = config.reference_modeldoc
    
    # Convert to Path objects
    jinja_path = Path(args.jinja_file)
    output_path = Path(args.output_file)
    
    prompt_file = config.get_editor_prompt('newmodel')
    if not prompt_file:
         print("Error: No newmodel_prompt specified in editor configuration")
         sys.exit(1)
    prompt_path = Path(prompt_file)

    if args.reference_modeldoc:
        reference_path = Path(args.reference_modeldoc)
    else:
        reference_path = config.reference_modeldoc
    
    # Validate input files exist
    if not jinja_path.exists():
        print(f"Error: Jinja file '{jinja_path}' does not exist.")
        sys.exit(1)
    
    if not prompt_path.exists():
        print(f"Error: Prompt file '{prompt_path}' does not exist.")
        sys.exit(1)
        
    if not reference_path.exists():
        print(f"Error: Reference file '{reference_path}' does not exist.")
        sys.exit(1)
    
    # Get the LLM model
    model = get_llm_model()
    
    print(f"Target model name: {args.model_name}")
    print(f"Using LLM model as editor: {model}")
    print(f"Reading Jinja template: {jinja_path}")
    print(f"Reading reference document: {reference_path}")
    print(f"Reading reformatting prompt: {prompt_path}")
    
    # Load file contents
    jinja_content = load_file_content(jinja_path)
    openai_harmony_content = load_file_content(reference_path)
    reformatting_prompt = load_file_content(prompt_path)
    
    # Generate the documentation
    generated_doc = create_context_window_doc(
        jinja_content,
        openai_harmony_content,
        reformatting_prompt,
        model,
        args.model_name
    )
    
    # Save the output
    save_output(generated_doc, output_path)
    

if __name__ == "__main__":
    main()