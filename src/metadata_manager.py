"""
Video Metadata Manager Module

This module handles tracking metadata about processed videos in a JSON file.
It provides a simple way to store and retrieve information about videos
that have been added to the RAG system.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class VideoMetadataManager:
    """
    Manages metadata about processed videos.

    This class provides a simple JSON-based storage system for tracking:
    - Video IDs and URLs
    - Video titles
    - When videos were processed
    - Number of chunks created
    - Any other relevant metadata

    Why Track Metadata Separately?
    -------------------------------
    ChromaDB stores embeddings and associated text/metadata, but:
    1. Querying ChromaDB for all videos requires loading the entire collection
    2. We want quick access to video lists without database queries
    3. We can store additional info not needed for retrieval (processing time, etc.)
    4. Provides a human-readable record of what's been processed
    5. Easy to backup and version control
    """

    def __init__(self, metadata_file: Optional[str] = None):
        """
        Initialize the metadata manager.

        Args:
            metadata_file: Path to JSON file (default: data/videos.json)
        """
        if metadata_file is None:
            # Default to data/videos.json in project root
            project_root = Path(__file__).parent.parent
            metadata_file = project_root / "data" / "videos.json"

        self.metadata_file = Path(metadata_file)

        # Ensure the directory exists
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize file if it doesn't exist
        if not self.metadata_file.exists():
            self._initialize_file()

    def _initialize_file(self):
        """Create an empty metadata file with proper structure."""
        initial_data = {
            "videos": [],
            "metadata": {
                "last_updated": None,
                "total_videos": 0
            }
        }
        self._save(initial_data)

    def _load(self) -> Dict[str, Any]:
        """Load metadata from JSON file."""
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # If file is corrupted, reinitialize
            print(f"⚠️  Corrupted metadata file. Reinitializing...")
            self._initialize_file()
            return self._load()
        except Exception as e:
            print(f"❌ Error loading metadata: {str(e)}")
            raise

    def _save(self, data: Dict[str, Any]):
        """Save metadata to JSON file."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"❌ Error saving metadata: {str(e)}")
            raise

    def add_video(
        self,
        video_id: str,
        video_url: str,
        video_title: str,
        num_chunks: int,
        transcript_length: int = 0
    ) -> None:
        """
        Add or update a video's metadata.

        If the video already exists, updates its information.
        Otherwise, adds a new entry.

        Args:
            video_id: Unique video identifier (e.g., YouTube video ID)
            video_url: Full URL to the video
            video_title: Title of the video
            num_chunks: Number of text chunks created
            transcript_length: Length of transcript in characters
        """
        data = self._load()

        # Check if video already exists
        existing_video = None
        for video in data["videos"]:
            if video["video_id"] == video_id:
                existing_video = video
                break

        video_info = {
            "video_id": video_id,
            "video_url": video_url,
            "video_title": video_title,
            "num_chunks": num_chunks,
            "transcript_length": transcript_length,
            "processed_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }

        if existing_video:
            # Update existing video
            existing_video.update(video_info)
        else:
            # Add new video
            data["videos"].append(video_info)

        # Update metadata
        data["metadata"]["last_updated"] = datetime.now().isoformat()
        data["metadata"]["total_videos"] = len(data["videos"])

        self._save(data)

    def get_video(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific video.

        Args:
            video_id: The video ID to look up

        Returns:
            Dictionary with video metadata, or None if not found
        """
        data = self._load()

        for video in data["videos"]:
            if video["video_id"] == video_id:
                return video

        return None

    def get_all_videos(self) -> List[Dict[str, Any]]:
        """
        Get metadata for all videos.

        Returns:
            List of video metadata dictionaries
        """
        data = self._load()
        return data["videos"]

    def delete_video(self, video_id: str) -> bool:
        """
        Delete a video's metadata.

        Args:
            video_id: The video ID to delete

        Returns:
            True if video was found and deleted, False otherwise
        """
        data = self._load()

        # Find and remove the video
        original_count = len(data["videos"])
        data["videos"] = [v for v in data["videos"] if v["video_id"] != video_id]

        if len(data["videos"]) < original_count:
            # Video was found and removed
            data["metadata"]["last_updated"] = datetime.now().isoformat()
            data["metadata"]["total_videos"] = len(data["videos"])
            self._save(data)
            return True

        return False

    def video_exists(self, video_id: str) -> bool:
        """
        Check if a video exists in metadata.

        Args:
            video_id: The video ID to check

        Returns:
            True if video exists, False otherwise
        """
        return self.get_video(video_id) is not None

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about processed videos.

        Returns:
            Dictionary with statistics
        """
        data = self._load()
        videos = data["videos"]

        if not videos:
            return {
                "total_videos": 0,
                "total_chunks": 0,
                "total_transcript_length": 0,
                "last_updated": None
            }

        total_chunks = sum(v.get("num_chunks", 0) for v in videos)
        total_length = sum(v.get("transcript_length", 0) for v in videos)

        return {
            "total_videos": len(videos),
            "total_chunks": total_chunks,
            "total_transcript_length": total_length,
            "average_chunks_per_video": total_chunks / len(videos) if videos else 0,
            "last_updated": data["metadata"].get("last_updated")
        }

    def get_video_ids(self) -> List[str]:
        """
        Get a list of all video IDs.

        Returns:
            List of video ID strings
        """
        data = self._load()
        return [v["video_id"] for v in data["videos"]]


if __name__ == "__main__":
    # Example usage and testing
    print("=" * 70)
    print("Video Metadata Manager Test")
    print("=" * 70)

    manager = VideoMetadataManager()

    # Add a test video
    print("\nAdding test video...")
    manager.add_video(
        video_id="test123",
        video_url="https://youtube.com/watch?v=test123",
        video_title="Test Video",
        num_chunks=10,
        transcript_length=5000
    )
    print("✓ Video added")

    # Get all videos
    print("\nAll videos:")
    for video in manager.get_all_videos():
        print(f"  - {video['video_id']}: {video['video_title']} ({video['num_chunks']} chunks)")

    # Get stats
    print("\nStatistics:")
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Check if video exists
    print(f"\nVideo 'test123' exists: {manager.video_exists('test123')}")
    print(f"Video 'unknown' exists: {manager.video_exists('unknown')}")

    print("\n" + "=" * 70)
