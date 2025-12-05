"""
Manual Test Script for YouTube Transcript Extractor and Text Chunking

This script provides an interactive way to test the transcript extraction and
text chunking functionality. Run this script and enter a YouTube URL to extract
its transcript and see it split into chunks.
"""

import sys
from src.transcript_extractor import extract_transcript
from src.text_chunker import chunk_transcript


def main():
    """
    Main function to run the interactive transcript extraction test.
    """
    print("=" * 60)
    print("YouTube Transcript Extractor - Manual Test")
    print("=" * 60)
    print()

    # Prompt user for YouTube URL
    print("Enter a YouTube URL to extract its transcript.")
    print("Example: https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    print()

    youtube_url = input("YouTube URL: ").strip()

    # Validate that user entered something
    if not youtube_url:
        print("\n❌ Error: No URL provided. Please try again.")
        sys.exit(1)

    print("\n" + "-" * 60)
    print("Extracting transcript... This may take a few seconds.")
    print("-" * 60 + "\n")

    try:
        # Call the extract_transcript function
        transcript = extract_transcript(youtube_url)

        # Display success message and transcript
        print("✓ Transcript extracted successfully!")
        print(f"✓ Total characters: {len(transcript)}")
        print(f"✓ Total words (approx.): {len(transcript.split())}")
        print("\n" + "=" * 60)
        print("TRANSCRIPT")
        print("=" * 60 + "\n")
        print(transcript)
        print("\n" + "=" * 60)

        # Demonstrate text chunking
        print("\n" + "-" * 60)
        print("Chunking transcript for RAG processing...")
        print("-" * 60 + "\n")

        # Chunk the transcript with default settings (1000 chars, 200 overlap)
        chunks = chunk_transcript(transcript)

        print("✓ Chunking completed!")
        print(f"✓ Number of chunks created: {len(chunks)}")
        print(f"✓ Chunk size: 1000 characters (target)")
        print(f"✓ Overlap: 200 characters")

        if len(chunks) >= 2:
            print("\n" + "=" * 60)
            print("FIRST TWO CHUNKS (showing overlap)")
            print("=" * 60 + "\n")

            # Display first chunk
            print("CHUNK 1:")
            print("-" * 60)
            print(f"Length: {len(chunks[0])} characters")
            print("-" * 60)
            print(chunks[0])
            print("\n")

            # Display second chunk
            print("CHUNK 2:")
            print("-" * 60)
            print(f"Length: {len(chunks[1])} characters")
            print("-" * 60)
            print(chunks[1])
            print("\n")

            # Show the overlap
            print("=" * 60)
            print("OVERLAP DEMONSTRATION")
            print("=" * 60)
            print("\nEnd of Chunk 1 (last 200 chars):")
            print("-" * 60)
            print(chunks[0][-200:])
            print("\nStart of Chunk 2 (first 200 chars):")
            print("-" * 60)
            print(chunks[1][:200])
            print("\n" + "=" * 60)
        elif len(chunks) == 1:
            print("\nNote: Transcript is short enough to fit in a single chunk.")
            print(f"Chunk length: {len(chunks[0])} characters")
        else:
            print("\nNote: No chunks created (empty transcript).")

    except ValueError as e:
        # Handle invalid URL or inaccessible video errors
        print(f"❌ Invalid URL Error:")
        print(f"   {str(e)}")
        print("\nPlease check that:")
        print("  • The URL is correctly formatted")
        print("  • The video exists and is publicly accessible")
        print("  • You have an active internet connection")
        sys.exit(1)

    except RuntimeError as e:
        # Handle missing transcript errors and other runtime issues (rate limiting, etc.)
        print(f"❌ Error:")
        print(f"   {str(e)}")
        sys.exit(1)

    except Exception as e:
        # Handle any other unexpected errors
        print(f"❌ Unexpected Error:")
        print(f"   {str(e)}")
        print("\nAn unexpected error occurred. Please try again or check the logs.")
        sys.exit(1)


if __name__ == "__main__":
    main()
