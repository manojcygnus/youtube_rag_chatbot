"""
YouTube Video RAG Chatbot - Main Application

This is the main entry point for the YouTube RAG chatbot. It provides an
interactive command-line interface for processing videos and asking questions.
"""

import sys
from typing import Optional
from src.pipeline import VideoRAGPipeline
from src.config import validate_config, print_config_status


def print_banner():
    """Display application banner."""
    print("\n" + "=" * 70)
    print("  YouTube Video RAG Chatbot")
    print("  Ask questions about YouTube video transcripts using AI")
    print("=" * 70)


def print_menu():
    """Display the main menu."""
    print("\n" + "-" * 70)
    print("MAIN MENU")
    print("-" * 70)
    print("1. Add a new video")
    print("2. List all processed videos")
    print("3. Chat with videos")
    print("4. Delete a video")
    print("5. Show database statistics")
    print("6. Exit")
    print("-" * 70)


def add_video(pipeline: VideoRAGPipeline):
    """
    Handle adding a new video to the system.

    Args:
        pipeline: The initialized VideoRAGPipeline instance
    """
    print("\n" + "=" * 70)
    print("ADD NEW VIDEO")
    print("=" * 70)

    # Get YouTube URL from user
    print("\nEnter the YouTube URL:")
    print("Example: https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    youtube_url = input("\nURL: ").strip()

    if not youtube_url:
        print("\n❌ No URL provided. Returning to main menu.")
        return

    # Optional: Get custom title
    print("\nOptional: Enter a custom title for this video (or press Enter to skip):")
    video_title = input("Title: ").strip()
    video_title = video_title if video_title else None

    # Process the video
    print("\n" + "=" * 70)
    print("PROCESSING VIDEO...")
    print("=" * 70)
    print("\nThis will take 30-60 seconds depending on video length.")
    print("Processing stages:")
    print("  1. Extracting transcript from YouTube")
    print("  2. Chunking text into segments")
    print("  3. Creating embeddings")
    print("  4. Storing in vector database")
    print("\nPlease wait...\n")

    try:
        result = pipeline.process_video(youtube_url, video_title)

        print("\n" + "=" * 70)
        if result["success"]:
            print("✓ VIDEO PROCESSED SUCCESSFULLY!")
            print("=" * 70)
            print(f"\nVideo ID: {result['video_id']}")
            print(f"Title: {result.get('video_title', 'N/A')}")
            print(f"Chunks stored: {result['num_chunks']}")

            if result.get("already_exists"):
                print("\n⚠️  Note: This video was already in the database.")

            print(f"\nTranscript length: {result.get('transcript_length', 'N/A')} characters")
            print("\nYou can now chat with this video using option 3 from the main menu.")
        else:
            print("✗ VIDEO PROCESSING FAILED")
            print("=" * 70)
            print(f"\nError: {result.get('error', 'Unknown error')}")
            print(f"Message: {result.get('message', 'No additional information')}")

            # Provide helpful suggestions based on error type
            if "API key" in str(result.get("error", "")):
                print("\n💡 Tip: Make sure you have set your API keys in the .env file.")
                print("   See .env.example for instructions.")
            elif "transcript" in str(result.get("error", "")).lower():
                print("\n💡 Tip: Make sure the video has captions/subtitles enabled.")
                print("   Try a different video or wait a few minutes if rate-limited.")

        print("=" * 70)

    except KeyboardInterrupt:
        print("\n\n⚠️  Video processing interrupted by user.")
    except Exception as e:
        print("\n" + "=" * 70)
        print("✗ UNEXPECTED ERROR")
        print("=" * 70)
        print(f"\n{str(e)}")
        print("\nPlease try again or check the logs for details.")
        print("=" * 70)

    input("\nPress Enter to return to main menu...")


def list_videos(pipeline: VideoRAGPipeline):
    """
    List all processed videos in the database.

    Args:
        pipeline: The initialized VideoRAGPipeline instance
    """
    print("\n" + "=" * 70)
    print("PROCESSED VIDEOS")
    print("=" * 70)

    try:
        # Get all videos from metadata manager
        videos = pipeline.metadata_manager.get_all_videos()

        if not videos:
            print("\n⚠️  No videos have been processed yet.")
            print("   Use option 1 to add your first video!")
        else:
            print(f"\nTotal videos: {len(videos)}")
            print("\nVideo Details:")
            print("-" * 70)

            for i, video in enumerate(videos, 1):
                print(f"\n{i}. {video.get('video_title', 'Unknown Title')}")
                print(f"   ID: {video.get('video_id', 'N/A')}")
                print(f"   URL: {video.get('video_url', 'N/A')}")
                print(f"   Chunks: {video.get('num_chunks', 0)}")
                print(f"   Transcript Length: {video.get('transcript_length', 0)} characters")

                # Format processed date
                processed_at = video.get('processed_at', 'Unknown')
                if processed_at and processed_at != 'Unknown':
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(processed_at)
                        formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S")
                        print(f"   Processed: {formatted_date}")
                    except:
                        print(f"   Processed: {processed_at}")

            print("-" * 70)
            print("\n💡 Use the video IDs when chatting (option 3)")
            print("   Or leave blank to search across all videos")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

    print("=" * 70)
    input("\nPress Enter to return to main menu...")


def chat_with_videos(pipeline: VideoRAGPipeline):
    """
    Interactive chat interface for asking questions.

    Args:
        pipeline: The initialized VideoRAGPipeline instance
    """
    print("\n" + "=" * 70)
    print("CHAT WITH VIDEOS")
    print("=" * 70)

    # Ask if user wants to filter by specific video
    print("\nDo you want to chat with a specific video or search all videos?")
    print("1. Search all videos")
    print("2. Chat with specific video")
    choice = input("\nChoice (1 or 2): ").strip()

    video_id_filter = None
    if choice == "2":
        print("\nEnter the Video ID:")
        video_id_filter = input("Video ID: ").strip()
        if video_id_filter:
            print(f"\n✓ Filtering results to video: {video_id_filter}")
        else:
            print("\n⚠️  No video ID provided. Searching all videos.")

    print("\n" + "=" * 70)
    print("CHAT SESSION STARTED")
    print("=" * 70)
    if video_id_filter:
        print(f"\nSearching in: {video_id_filter}")
    else:
        print("\nSearching across: All videos")
    print("\nAsk questions about the video content.")
    print("Type 'done' to return to the main menu.")
    print("Type 'sources' after a question to see detailed source information.")
    print("=" * 70)

    last_response = None

    while True:
        # Get question from user
        print("\n" + "-" * 70)
        question = input("\n❓ Your question: ").strip()
        print()

        # Check for exit command
        if question.lower() in ['done', 'exit', 'quit']:
            print("Ending chat session. Returning to main menu...")
            break

        # Handle 'sources' command to show detailed sources from last response
        if question.lower() == 'sources':
            if last_response and last_response.get("sources"):
                print("=" * 70)
                print("DETAILED SOURCES FROM LAST ANSWER")
                print("=" * 70)
                for i, source in enumerate(last_response["sources"], 1):
                    metadata = source["metadata"]
                    print(f"\n📄 Source {i}:")
                    print(f"   Video: {metadata.get('video_title', 'Unknown')}")
                    print(f"   Video ID: {metadata.get('video_id', 'Unknown')}")
                    print(f"   URL: {metadata.get('video_url', 'N/A')}")
                    print(f"   Chunk: {metadata.get('chunk_index', '?')}")
                    print(f"   Similarity: {1 - source.get('distance', 0):.3f}")
                    print(f"\n   Content preview:")
                    print(f"   {source['text'][:200]}...")
                print("=" * 70)
            else:
                print("⚠️  No previous answer or sources available.")
            continue

        # Validate question
        if not question:
            print("⚠️  Please enter a question.")
            continue

        # Process the question
        print("🔍 Searching for relevant information...")
        print("🤖 Generating answer with Claude...\n")

        try:
            response = pipeline.chat(
                question=question,
                video_id_filter=video_id_filter,
                n_context_chunks=5
            )

            if response["success"]:
                # Display the answer
                print("=" * 70)
                print("💬 ANSWER:")
                print("=" * 70)
                print(f"\n{response['answer']}\n")
                print("=" * 70)

                # Display source summary
                sources = response.get("sources", [])
                if sources:
                    print(f"\n📚 Sources: {len(sources)} relevant chunks found")

                    # Show brief source summary
                    unique_videos = set()
                    for source in sources:
                        video_title = source["metadata"].get("video_title", "Unknown")
                        unique_videos.add(video_title)

                    print("   From videos:")
                    for video in unique_videos:
                        print(f"   - {video}")

                    print("\n💡 Type 'sources' to see detailed source information")

                # Display metadata
                metadata = response.get("metadata", {})
                if "input_tokens" in metadata:
                    print(f"\n📊 Tokens used: {metadata['input_tokens']} input, "
                          f"{metadata['output_tokens']} output")

                # Save response for 'sources' command
                last_response = response

            else:
                print("=" * 70)
                print("❌ ERROR")
                print("=" * 70)
                print(f"\n{response.get('message', 'Failed to generate answer')}")
                if response.get("error"):
                    print(f"Error details: {response['error']}")
                print("\n💡 Try rephrasing your question or check your configuration.")
                print("=" * 70)

        except KeyboardInterrupt:
            print("\n\n⚠️  Question interrupted by user.")
            continue
        except Exception as e:
            print("=" * 70)
            print("❌ UNEXPECTED ERROR")
            print("=" * 70)
            print(f"\n{str(e)}")
            print("\nPlease try again or check the logs.")
            print("=" * 70)

    print()


def delete_video(pipeline: VideoRAGPipeline):
    """
    Handle deleting a video from the database.

    Args:
        pipeline: The initialized VideoRAGPipeline instance
    """
    print("\n" + "=" * 70)
    print("DELETE VIDEO")
    print("=" * 70)

    # First show available videos
    try:
        videos = pipeline.metadata_manager.get_all_videos()

        if not videos:
            print("\n⚠️  No videos in database.")
            input("\nPress Enter to return to main menu...")
            return

        print("\nAvailable videos:")
        for i, video in enumerate(videos, 1):
            video_id = video.get('video_id', 'N/A')
            video_title = video.get('video_title', 'Unknown')
            print(f"{i}. {video_id} - {video_title}")
    except Exception as e:
        print(f"\n❌ Error fetching video list: {str(e)}")
        input("\nPress Enter to return to main menu...")
        return

    # Get video ID to delete
    print("\nEnter the Video ID to delete (or press Enter to cancel):")
    video_id = input("Video ID: ").strip()

    if not video_id:
        print("\n⚠️  Cancelled. Returning to main menu.")
        input("\nPress Enter to continue...")
        return

    # Confirm deletion
    print(f"\n⚠️  Are you sure you want to delete video '{video_id}'?")
    print("This will remove all associated chunks from the database.")
    confirm = input("Type 'yes' to confirm: ").strip().lower()

    if confirm != 'yes':
        print("\n✓ Deletion cancelled.")
        input("\nPress Enter to return to main menu...")
        return

    # Delete the video
    try:
        result = pipeline.delete_video(video_id)

        print("\n" + "=" * 70)
        if result["success"]:
            print("✓ VIDEO DELETED SUCCESSFULLY")
            print("=" * 70)
            print(f"\nDeleted {result.get('num_deleted', 0)} chunks for video '{video_id}'")
        else:
            print("✗ DELETION FAILED")
            print("=" * 70)
            print(f"\nError: {result.get('error', 'Unknown error')}")
        print("=" * 70)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

    input("\nPress Enter to return to main menu...")


def show_stats(pipeline: VideoRAGPipeline):
    """
    Display detailed database statistics.

    Args:
        pipeline: The initialized VideoRAGPipeline instance
    """
    print("\n" + "=" * 70)
    print("DATABASE STATISTICS")
    print("=" * 70)

    try:
        result = pipeline.get_stats()

        if result["success"]:
            stats = result["stats"]

            print(f"\nCollection: {stats.get('collection_name', 'N/A')}")
            print(f"Total videos: {stats.get('total_videos', 0)}")
            print(f"Total chunks: {stats.get('total_chunks', 0)}")

            if stats.get('total_videos', 0) > 0:
                avg_chunks = stats['total_chunks'] / stats['total_videos']
                print(f"Average chunks per video: {avg_chunks:.1f}")

            print(f"\nVideo IDs in database:")
            video_ids = stats.get("video_ids", [])
            if video_ids:
                for vid in video_ids:
                    print(f"  - {vid}")
            else:
                print("  (none)")
        else:
            print("\n❌ Error fetching statistics")
            print(f"Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

    print("=" * 70)
    input("\nPress Enter to return to main menu...")


def main():
    """Main application loop."""
    print_banner()

    # Validate configuration before starting
    print("\nChecking configuration...")
    config_status = validate_config()

    if not config_status["valid"]:
        print("\n" + "=" * 70)
        print("❌ CONFIGURATION ERRORS")
        print("=" * 70)
        for error in config_status["errors"]:
            print(f"  • {error}")
        print("\n💡 Please fix these configuration issues:")
        print("  1. Copy .env.example to .env")
        print("  2. Add your API keys to the .env file")
        print("  3. See .env.example for instructions on obtaining keys")
        print("=" * 70)
        sys.exit(1)

    print("✓ Configuration valid")

    # Initialize the pipeline
    print("\nInitializing RAG pipeline...")
    try:
        pipeline = VideoRAGPipeline()
        print("✓ Pipeline initialized successfully\n")
    except Exception as e:
        print(f"\n❌ Failed to initialize pipeline: {str(e)}")
        print("\nPlease check your configuration and try again.")
        sys.exit(1)

    # Main application loop
    while True:
        print_menu()
        choice = input("\nEnter your choice (1-6): ").strip()

        if choice == "1":
            add_video(pipeline)

        elif choice == "2":
            list_videos(pipeline)

        elif choice == "3":
            chat_with_videos(pipeline)

        elif choice == "4":
            delete_video(pipeline)

        elif choice == "5":
            show_stats(pipeline)

        elif choice == "6":
            print("\n" + "=" * 70)
            print("Thank you for using YouTube Video RAG Chatbot!")
            print("Goodbye!")
            print("=" * 70 + "\n")
            sys.exit(0)

        else:
            print("\n⚠️  Invalid choice. Please enter a number between 1 and 6.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("Application interrupted by user. Goodbye!")
        print("=" * 70 + "\n")
        sys.exit(0)
    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ FATAL ERROR")
        print("=" * 70)
        print(f"\n{str(e)}")
        print("\nThe application encountered an unexpected error and must exit.")
        print("=" * 70 + "\n")
        sys.exit(1)
