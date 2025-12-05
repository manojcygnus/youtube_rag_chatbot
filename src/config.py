"""
Configuration Module

This module loads environment variables from a .env file and provides
them as configuration values for the YouTube RAG chatbot application.

The module uses python-dotenv to load variables from a .env file in the
project root directory.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Get the project root directory (parent of src/)
# This ensures we load the .env file from the project root regardless of where
# the script is run from
PROJECT_ROOT = Path(__file__).parent.parent

# Load environment variables from .env file
# The .env file should be in the project root directory
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")


# =============================================================================
# Required API Keys
# =============================================================================

def get_gemini_api_key() -> str:
    """
    Get the Google Gemini API key from environment variables.

    Returns:
        str: The Gemini API key

    Raises:
        ValueError: If the API key is not set
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found in environment variables. "
            "Please set it in your .env file. "
            "See .env.example for instructions on how to obtain this key."
        )
    return api_key


def get_anthropic_api_key() -> str:
    """
    Get the Anthropic API key from environment variables.

    Returns:
        str: The Anthropic API key

    Raises:
        ValueError: If the API key is not set
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not found in environment variables. "
            "Please set it in your .env file. "
            "See .env.example for instructions on how to obtain this key."
        )
    return api_key


def get_voyage_api_key() -> str:
    """
    Get the Voyage AI API key from environment variables.

    Returns:
        str: The Voyage AI API key

    Raises:
        ValueError: If the API key is not set
    """
    api_key = os.getenv("VOYAGE_API_KEY")
    if not api_key:
        raise ValueError(
            "VOYAGE_API_KEY not found in environment variables. "
            "Please set it in your .env file. "
            "See .env.example for instructions on how to obtain this key."
        )
    return api_key


# Expose API keys as module-level variables for convenience
# These will raise an error if not set, preventing the app from running
# with missing credentials
try:
    GEMINI_API_KEY = get_gemini_api_key()
except ValueError:
    GEMINI_API_KEY = None

try:
    ANTHROPIC_API_KEY = get_anthropic_api_key()
except ValueError:
    ANTHROPIC_API_KEY = None

try:
    VOYAGE_API_KEY = get_voyage_api_key()
except ValueError:
    VOYAGE_API_KEY = None


# =============================================================================
# Model Configuration
# =============================================================================

# Gemini model to use for generating responses
# Default: gemini-2.5-flash (fast, efficient, free tier)
# Options: gemini-2.5-flash, gemini-2.5-pro, gemini-flash-latest
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Claude model to use for generating responses
# Default: claude-3-5-sonnet-20241022 (most capable and balanced model)
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

# Voyage embedding model to use for creating text embeddings
# Default: voyage-3 (latest and most capable general-purpose model)
VOYAGE_MODEL = os.getenv("VOYAGE_MODEL", "voyage-3")

# LLM provider to use: "gemini" or "anthropic"
# Default: gemini (free tier available)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")


# =============================================================================
# Vector Database Configuration (ChromaDB)
# =============================================================================

# Collection name for storing video transcript embeddings
# Each collection is like a table in a database
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "youtube_transcripts")

# Directory where ChromaDB will persist its data
# This allows embeddings to be saved and reused across sessions
CHROMA_PERSIST_DIRECTORY = os.getenv(
    "CHROMA_PERSIST_DIRECTORY",
    str(PROJECT_ROOT / "data" / "chroma_db")
)


# =============================================================================
# Text Processing Configuration
# =============================================================================

# Chunk size for splitting transcripts (in characters)
# Larger chunks preserve more context but are less precise for retrieval
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))

# Overlap between consecutive chunks (in characters)
# Overlap helps preserve context at chunk boundaries
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))


# =============================================================================
# Validation and Information
# =============================================================================

def validate_config() -> dict:
    """
    Validate that all required configuration is present and return status.

    Returns:
        dict: Configuration status with 'valid' boolean and any 'errors'
    """
    errors = []

    # Check that at least one LLM API key is set
    if not GEMINI_API_KEY and not ANTHROPIC_API_KEY:
        errors.append(
            "No LLM API key is set. Please set either GEMINI_API_KEY (recommended) "
            "or ANTHROPIC_API_KEY in your .env file"
        )

    # Check based on selected provider
    if LLM_PROVIDER == "gemini" and not GEMINI_API_KEY:
        errors.append(
            "LLM_PROVIDER is set to 'gemini' but GEMINI_API_KEY is not set. "
            "Please add GEMINI_API_KEY to your .env file or change LLM_PROVIDER to 'anthropic'"
        )
    elif LLM_PROVIDER == "anthropic" and not ANTHROPIC_API_KEY:
        errors.append(
            "LLM_PROVIDER is set to 'anthropic' but ANTHROPIC_API_KEY is not set. "
            "Please add ANTHROPIC_API_KEY to your .env file or change LLM_PROVIDER to 'gemini'"
        )

    if not VOYAGE_API_KEY:
        errors.append("VOYAGE_API_KEY is not set")

    if CHUNK_OVERLAP >= CHUNK_SIZE:
        errors.append(
            f"CHUNK_OVERLAP ({CHUNK_OVERLAP}) must be less than CHUNK_SIZE ({CHUNK_SIZE})"
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def print_config_status():
    """
    Print the current configuration status to help with debugging.
    Does not print actual API keys for security reasons.
    """
    print("=" * 70)
    print("Configuration Status")
    print("=" * 70)
    print(f"LLM_PROVIDER: {LLM_PROVIDER}")
    print(f"GEMINI_API_KEY: {'✓ Set' if GEMINI_API_KEY else '✗ Not set'}")
    print(f"ANTHROPIC_API_KEY: {'✓ Set' if ANTHROPIC_API_KEY else '✗ Not set'}")
    print(f"VOYAGE_API_KEY: {'✓ Set' if VOYAGE_API_KEY else '✗ Not set'}")
    print(f"GEMINI_MODEL: {GEMINI_MODEL}")
    print(f"CLAUDE_MODEL: {CLAUDE_MODEL}")
    print(f"VOYAGE_MODEL: {VOYAGE_MODEL}")
    print(f"CHROMA_COLLECTION_NAME: {CHROMA_COLLECTION_NAME}")
    print(f"CHROMA_PERSIST_DIRECTORY: {CHROMA_PERSIST_DIRECTORY}")
    print(f"CHUNK_SIZE: {CHUNK_SIZE}")
    print(f"CHUNK_OVERLAP: {CHUNK_OVERLAP}")
    print("=" * 70)

    validation = validate_config()
    if not validation["valid"]:
        print("\n⚠️  Configuration Errors:")
        for error in validation["errors"]:
            print(f"  - {error}")
        print("\nPlease check your .env file and fix these issues.")
        print("See .env.example for reference.")
    else:
        print("\n✓ Configuration is valid!")


if __name__ == "__main__":
    # When run directly, print configuration status
    print_config_status()
