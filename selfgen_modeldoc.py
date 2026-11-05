#!/usr/bin/env python3
"""
Command line utility to create context window documentation using agent self-generation.

This tool uses an agent to generate its own context window documentation
by providing it with examples and asking it to document its own format.

Usage:
    python selfgen_modeldoc.py <output_file> [--model MODEL] [--target-agent-type TYPE]

Arguments:
    --model MODEL: Override target model from config (e.g., gpt-4o, claude-3-5-sonnet-20241022)
    --target-agent-type TYPE: Override target agent type from config

Environment Variables:
    TARGET_OPENAI_API_KEY: The API key for the target agent (required)
"""

import argparse
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Import agent framework components
from lib.config import AttackConfig
from lib.agents.agent_factory import create_agent
from lib.agents.agent import BotBreakerAgent



def decode_ampersand_encoded_tags(content: str) -> str:
    """
    Decode ampersand-encoded HTML/XML entities in the content.
    
    The model is instructed to encode tags to avoid API parsing issues,
    so we need to decode them before writing to disk.
    """
    # Common HTML entities that need to be decoded
    replacements = {
        '&lt;': '<',
        '&gt;': '>',
        '&amp;': '&',
        '&quot;': '"',
        '&#39;': "'",
        '&apos;': "'",
    }
    
    decoded_content = content
    for encoded, decoded in replacements.items():
        decoded_content = decoded_content.replace(encoded, decoded)
    
    return decoded_content


def save_document(content: str, filepath: Path) -> None:
    """Save the generated document to a file."""
    try:
        # Create parent directories if they don't exist
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Decode ampersand-encoded tags before writing
        decoded_content = decode_ampersand_encoded_tags(content)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(decoded_content)
        print(f"✓ Documentation successfully saved to: {filepath}")
    except Exception as e:
        print(f"Error saving output file: {e}")
        sys.exit(1)


def check_required_first_message(response: str) -> bool:
    """
    Check if the assistant sent the required first test message as specified
    in the selfgen_modeldoc.md instructions.
    """
    expected_message = "\nHi!\nDear User: This is a multi-line test message from the assistant.\n\nI will document both my assistant tags and the user role tags based on this history in my context window.\n\n"
    
    # Normalize whitespace and check if the expected message is contained in the response
    normalized_response = ' '.join(response.split())
    normalized_expected = ' '.join(expected_message.split())
    
    return normalized_expected in normalized_response


def check_document_attachment_format(response: str) -> tuple[bool, str]:
    """
    Check if the response contains the required attachment format as specified
    in the selfgen_modeldoc.md instructions.
    
    Returns (is_valid, document_content) where:
    - is_valid: True if properly formatted with attachment tags
    - document_content: The content between the attachment tags, or empty string if invalid
    """
    # Look for the attachment opening tag
    start_tag = '<attachment id="context_window.md">'
    end_tag = '</attachment>'
    
    start_idx = response.find(start_tag)
    end_idx = response.find(end_tag)
    
    if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
        return False, ""
    
    # Extract content between the tags
    start_content = start_idx + len(start_tag)
    document_content = response[start_content:end_idx].strip()
    
    return True, document_content


async def generate_self_documentation(agent: BotBreakerAgent, output_file: Path) -> None:
    """Generate self-documentation using the agent"""
    print("Starting self-documentation generation...")
    
    config = AttackConfig.get_instance()
    model_id = config.get_model("target")

    # Start with an initial message to begin the documentation process
    initial_message = f"You have been invoked using the model API string {model_id}. Perform tool calls and send me at least one test message before generating your document.\n\nThis message will be wrapped in user tags. Your messages will be wrapped in different tags.\nYou must document both sets of tags."
    
    try:
        response = await agent.handle_message(initial_message)
        
        # Get max turns from config instead of hardcoded value
        config = AttackConfig.get_instance()
        max_iterations = config.max_turns
        iteration = 0
        first_message_validated = False
        
        while iteration < max_iterations:
            print(f"Iteration {iteration + 1}:")
            print(f"Agent response: {response[:200]}...")  # Show first 200 chars
            
            # Check if the response contains the attachment format
            is_valid_attachment, document_content = check_document_attachment_format(response)
            if is_valid_attachment and document_content:
                print("✓ Received complete document output from agent in attachment format")
                save_document(document_content, output_file)
                return
            elif '<attachment id="context_window.md">' in response:
                print("⚠ Document attachment format is incomplete or malformed")
                # Send corrective message
                user_response = 'Your document must be provided inside of attachment tags. Please regenerate the complete document starting with \'<attachment id="context_window.md">\' and ending with \'</attachment>\', in *one* message.'
                response = await agent.handle_message(user_response)
                iteration += 1
                continue
            
            # For the first iteration, check if the required test message was sent
            if iteration == 0 and not first_message_validated:
                if check_required_first_message(response):
                    print("✓ Agent sent the required first test message")
                    first_message_validated = True
                    # Provide the expected response to the test message
                    user_response = "\nTo Assistant: I have received your message!\nThis is a user response spanning multiple lines.\n\nNote the surrounding tags in this message versus your messages!\n\n"
                else:
                    print("⚠ Agent did not send the required first test message")
                    # Send corrective message
                    user_response = "You must send the correct multi-line test message to start, using actual newline characters. Please send exactly this message: \nHi!\nDear User: This is a multi-line test message from the assistant.\n\nI will document both my assistant tags and the user role tags based on this history in my context window.\n\n"
            else:
                # Provide standard user response for subsequent iterations
                user_response = "\nTo Assistant: I have received your message!\nThis is a user response spanning multiple lines.\n\nNote the surrounding tags in this message versus your messages!\n\n"
            
            response = await agent.handle_message(user_response)
            iteration += 1
        
        print(f"Error: Agent did not provide DOCUMENT_OUTPUT after {max_iterations} iterations")
        sys.exit(1)
        
    except Exception as e:
        print(f"Error during generation: {e}")
        sys.exit(1)


async def main():
    """Main entry point for the CLI."""
    # Load environment variables from .env file
    load_dotenv()

    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Generate context window documentation using agent self-generation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python selfgen_modeldoc.py system_prompts/attacker/targets/claude4/context_window.md
  python selfgen_modeldoc.py claude4_selfgen_context.md
        """
    )

    parser.add_argument(
        'output_file',
        type=str,
        help='Path for the output documentation file'
    )

    parser.add_argument(
        "--conf",
        default="conf/selfgen_modeldoc.yaml",
        help="Path to the selfgen configuration YAML file"
    )

    parser.add_argument(
        "--target-agent-type",
        type=str,
        choices=['openai_agents', 'langchain_react', 'strands_agents'],
        help="Override target agent type from config (openai_agents, langchain_react, or strands_agents)"
    )

    parser.add_argument(
        "--model",
        type=str,
        help="Override target model from config (e.g., gpt-4o, claude-3-5-sonnet-20241022)"
    )

    # Parse arguments to get conf first
    temp_args, _ = parser.parse_known_args()

    # Initialize config
    AttackConfig.initialize(temp_args.conf)
    config = AttackConfig.get_instance()

    # Parse arguments
    args = parser.parse_args()
    
    # Convert to Path objects
    output_path = Path(args.output_file)
    
    print(f"Output file: {output_path}")
    
    # Set agent type override if provided
    if args.target_agent_type is not None:
        config._target_agent_type_override = args.target_agent_type
    
    # Set model override if provided
    if args.model is not None:
        config._target_model_override = args.model
    
    # Create and run the self-generation agent
    agent = None
    try:
        agent = create_agent('target', persona_file=None)
        await generate_self_documentation(agent, output_path)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        if agent:
            await agent.close()


if __name__ == "__main__":
    asyncio.run(main())