"""
YouTube Transcript Extractor Module

This module provides functionality to extract transcripts from YouTube videos
using yt-dlp, a powerful command-line tool for downloading videos and extracting metadata.
"""

import yt_dlp


def extract_transcript(youtube_url: str) -> str:
    """
    Extract transcript from a YouTube video.

    This function uses yt-dlp to retrieve the available subtitles/transcripts
    from a YouTube video without downloading the actual video file.

    How yt-dlp works:
    -----------------
    yt-dlp is a fork of youtube-dl that extracts video information and content
    from YouTube and other platforms. It can:
    1. Parse the YouTube URL and extract the video ID
    2. Make API requests to YouTube to fetch video metadata
    3. Access available subtitle tracks (auto-generated or manual)
    4. Download and parse subtitle files in various formats (VTT, SRT, JSON, etc.)

    Args:
        youtube_url (str): The full URL of the YouTube video
                          (e.g., "https://www.youtube.com/watch?v=VIDEO_ID")

    Returns:
        str: The complete transcript text with all subtitle entries concatenated

    Raises:
        ValueError: If the URL is invalid or video doesn't exist
        RuntimeError: If no transcript/subtitles are available for the video
        Exception: For other unexpected errors during extraction

    Example:
        >>> url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        >>> transcript = extract_transcript(url)
        >>> print(transcript)
    """

    # Configure yt-dlp options
    # These options tell yt-dlp what information to extract and how to behave
    ydl_opts = {
        'skip_download': True,  # Don't download the video file itself
        'writesubtitles': True,  # Enable subtitle extraction
        'writeautomaticsub': True,  # Include auto-generated subtitles if manual ones aren't available
        'subtitleslangs': ['en'],  # Prefer English subtitles (can be modified for other languages)
        'quiet': True,  # Suppress console output for cleaner execution
        'no_warnings': True,  # Don't print warnings
        'extract_flat': False,  # Extract full video information, not just playlist info
    }

    try:
        # Create a yt-dlp instance with our configuration
        # This acts as the main interface for interacting with YouTube
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            # Extract video information without downloading
            # This makes a request to YouTube and parses the response
            # The info_dict contains all available metadata about the video
            info_dict = ydl.extract_info(youtube_url, download=False)

            # Check if subtitles are available in the video metadata
            # Subtitles can be either manually uploaded or auto-generated
            subtitles = info_dict.get('subtitles', {})
            automatic_captions = info_dict.get('automatic_captions', {})

            # Try to get English subtitles first from manual, then from auto-generated
            subtitle_data = None

            if 'en' in subtitles:
                # Manual subtitles are generally more accurate
                subtitle_data = subtitles['en']
            elif 'en' in automatic_captions:
                # Fall back to auto-generated captions if manual ones aren't available
                subtitle_data = automatic_captions['en']
            else:
                # No English subtitles found
                raise RuntimeError(
                    f"No English transcript available for this video. "
                    f"Available subtitle languages: {list(subtitles.keys()) or list(automatic_captions.keys())}"
                )

            # Subtitle data is a list of formats (e.g., vtt, srv3, json3)
            # We prefer JSON format as it's easiest to parse programmatically
            json_subtitle = None
            for subtitle_format in subtitle_data:
                if subtitle_format.get('ext') == 'json3':
                    json_subtitle = subtitle_format
                    break

            # If no JSON format, fall back to the first available format
            if not json_subtitle and subtitle_data:
                json_subtitle = subtitle_data[0]

            if not json_subtitle:
                raise RuntimeError("Unable to find a suitable subtitle format")

            # Download the subtitle data
            # This fetches the actual subtitle file from YouTube's servers
            subtitle_url = json_subtitle.get('url')
            if not subtitle_url:
                raise RuntimeError("Subtitle URL not found")

            # Use yt-dlp's internal downloader to fetch the subtitle content
            subtitle_content = ydl.urlopen(subtitle_url).read().decode('utf-8')

            # Parse the subtitle content based on format
            transcript_text = _parse_subtitle_content(subtitle_content, json_subtitle.get('ext'))

            if not transcript_text or transcript_text.strip() == "":
                raise RuntimeError("Transcript extraction resulted in empty content")

            return transcript_text

    except yt_dlp.utils.DownloadError as e:
        # This typically occurs when the URL is invalid or video is unavailable
        error_message = str(e)

        # Check for specific HTTP errors
        if "429" in error_message or "Too Many Requests" in error_message:
            raise RuntimeError(
                "YouTube is rate-limiting requests (HTTP 429). "
                "Please wait a few minutes before trying again. "
                "If this persists, you may need to wait longer or use a different network."
            )
        elif "403" in error_message or "Forbidden" in error_message:
            raise RuntimeError(
                "Access forbidden (HTTP 403). The video may be private, age-restricted, "
                "or blocked in your region."
            )
        elif "404" in error_message or "Not Found" in error_message:
            raise ValueError("Video not found (HTTP 404). Please check the URL.")
        else:
            raise ValueError(f"Invalid YouTube URL or video not accessible: {error_message}")

    except RuntimeError as e:
        # Re-raise our custom RuntimeError for missing transcripts or HTTP errors
        raise e

    except Exception as e:
        # Catch any other unexpected errors
        error_message = str(e)

        # Check if it's an HTTP error that wasn't caught above
        if "HTTP Error" in error_message or "HTTPError" in error_message:
            # Provide specific messages for common HTTP errors
            if "429" in error_message or "Too Many Requests" in error_message:
                raise RuntimeError(
                    "YouTube is rate-limiting requests (HTTP 429). "
                    "Please wait a few minutes before trying again. "
                    "If this persists, you may need to wait longer or use a different network."
                )
            elif "403" in error_message or "Forbidden" in error_message:
                raise RuntimeError(
                    "Access forbidden (HTTP 403). The video may be private, age-restricted, "
                    "or blocked in your region."
                )
            elif "404" in error_message or "Not Found" in error_message:
                raise ValueError("Video not found (HTTP 404). Please check the URL.")
            else:
                raise RuntimeError(f"HTTP Error occurred: {error_message}")

        raise Exception(f"An unexpected error occurred while extracting transcript: {error_message}")


def _parse_subtitle_content(content: str, format_ext: str) -> str:
    """
    Parse subtitle content based on its format.

    Different subtitle formats require different parsing strategies:
    - JSON3: YouTube's JSON format with events and segments
    - VTT: WebVTT format with timestamps
    - SRT: SubRip format with numbered entries

    Args:
        content (str): Raw subtitle content
        format_ext (str): File extension indicating the format (json3, vtt, srv3, etc.)

    Returns:
        str: Parsed transcript text with subtitle entries concatenated
    """
    import json
    import re

    if format_ext == 'json3':
        # YouTube JSON3 format contains events with segments (individual words/phrases)
        try:
            data = json.loads(content)
            transcript_parts = []

            # Navigate the JSON structure to find subtitle segments
            events = data.get('events', [])
            for event in events:
                # Each event may contain multiple segments
                segments = event.get('segs', [])
                for segment in segments:
                    text = segment.get('utf8', '').strip()
                    if text:
                        transcript_parts.append(text)

            return ' '.join(transcript_parts)
        except json.JSONDecodeError:
            raise RuntimeError("Failed to parse JSON subtitle format")

    elif format_ext in ['vtt', 'srv3']:
        # VTT format has timestamps followed by text
        # Example:
        # 00:00:00.000 --> 00:00:05.000
        # This is the subtitle text

        # Remove VTT headers and timestamp lines, keep only the text
        lines = content.split('\n')
        transcript_parts = []

        for line in lines:
            line = line.strip()
            # Skip empty lines, headers, and timestamp lines
            if line and not line.startswith('WEBVTT') and '-->' not in line and not re.match(r'^\d+$', line):
                transcript_parts.append(line)

        return ' '.join(transcript_parts)

    else:
        # For other formats, attempt basic text extraction
        # Remove common subtitle formatting and timestamps
        cleaned = re.sub(r'\d{2}:\d{2}:\d{2}[.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[.,]\d{3}', '', content)
        cleaned = re.sub(r'^\d+$', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'\n\n+', '\n', cleaned)

        return ' '.join(line.strip() for line in cleaned.split('\n') if line.strip())


if __name__ == "__main__":
    # Example usage and testing
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    try:
        transcript = extract_transcript(test_url)
        print(f"Successfully extracted transcript ({len(transcript)} characters)")
        print(f"\nFirst 500 characters:\n{transcript[:500]}...")
    except ValueError as e:
        print(f"Error: {e}")
    except RuntimeError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
