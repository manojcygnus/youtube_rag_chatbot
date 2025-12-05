"""
YouTube Video RAG Chatbot - Streamlit Web Interface

This provides an interactive web interface for the YouTube RAG chatbot,
allowing users to process videos and ask questions through a beautiful UI.
"""

import streamlit as st
from src.pipeline import VideoRAGPipeline
from src.config import validate_config
from datetime import datetime
import re

# Page configuration
st.set_page_config(
    page_title="YouTube RAG Chatbot",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    /* Main header with gradient text */
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: fadeIn 1s ease-in;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }

    /* Video card with glassmorphism */
    .video-card {
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.75rem 0;
        background: rgba(249, 249, 249, 0.8);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }

    .video-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
        border-color: rgba(102, 126, 234, 0.4);
    }

    /* Source card with gradient border */
    .source-card {
        border-left: 3px solid;
        border-image: linear-gradient(180deg, #667eea 0%, #764ba2 100%) 1;
        padding: 1rem;
        margin: 0.75rem 0;
        background: linear-gradient(135deg, rgba(249, 249, 249, 0.9) 0%, rgba(255, 255, 255, 0.9) 100%);
        backdrop-filter: blur(10px);
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }

    /* Button styling with gradient */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border: none;
        color: white;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }

    /* Chat message styling */
    .stChatMessage {
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        animation: slideIn 0.3s ease;
    }

    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-10px); }
        to { opacity: 1; transform: translateX(0); }
    }

    /* Text input with gradient border */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea {
        border-radius: 8px;
        border: 2px solid transparent;
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #667eea 0%, #764ba2 100%) border-box;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(249, 249, 249, 0.95) 0%, rgba(255, 255, 255, 0.95) 100%);
        backdrop-filter: blur(10px);
    }

    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        border-radius: 8px;
        background: rgba(102, 126, 234, 0.05);
    }

    /* Loading spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_pipeline():
    """Initialize the RAG pipeline (cached for performance)."""
    return VideoRAGPipeline()


def extract_video_id_from_url(url: str) -> str:
    """Extract video ID from YouTube URL."""
    patterns = [
        r'(?:v=|/)([0-9A-Za-z_-]{11}).*',
        r'youtu\.be/([0-9A-Za-z_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return url  # Return as-is if not a URL


def show_header():
    """Display the main header."""
    st.markdown('<h1 class="main-header">🎥 YouTube RAG Chatbot</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Ask questions about YouTube video transcripts using AI</p>', unsafe_allow_html=True)
    st.divider()


def show_config_status():
    """Check and display configuration status."""
    config_status = validate_config()

    if not config_status["valid"]:
        st.error("⚠️ Configuration Error")
        for error in config_status["errors"]:
            st.error(f"• {error}")
        st.info("💡 Please check your .env file. See .env.example for instructions.")
        st.stop()


def page_add_video(pipeline):
    """Add video page."""
    st.header("📥 Add New Video")
    st.write("Process a YouTube video to make it searchable and queryable.")

    with st.form("add_video_form"):
        youtube_url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            help="Enter the full YouTube video URL"
        )

        video_title = st.text_input(
            "Custom Title (Optional)",
            placeholder="Leave blank to use video ID",
            help="Give your video a memorable name"
        )

        submit = st.form_submit_button("🚀 Process Video", use_container_width=True)

        if submit:
            if not youtube_url:
                st.error("Please enter a YouTube URL")
                return

            with st.spinner("Processing video... This may take 30-60 seconds"):
                # Show processing steps
                progress_bar = st.progress(0)
                status_text = st.empty()

                status_text.text("📝 Extracting transcript...")
                progress_bar.progress(25)

                result = pipeline.process_video(youtube_url, video_title)

                progress_bar.progress(100)
                status_text.empty()

                if result["success"]:
                    st.success("✅ Video processed successfully!")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Video ID", result["video_id"])
                    with col2:
                        st.metric("Chunks Created", result["num_chunks"])
                    with col3:
                        st.metric("Transcript Length", f"{result['transcript_length']} chars")

                    if result.get("already_exists"):
                        st.info("ℹ️ This video was already in the database.")

                    st.balloons()
                else:
                    st.error("❌ Failed to process video")
                    st.error(f"Error: {result.get('message', 'Unknown error')}")

                    if "API key" in str(result.get("error", "")):
                        st.info("💡 Make sure you have set your API keys in the .env file.")


def page_list_videos(pipeline):
    """List videos page."""
    st.header("📚 Processed Videos")

    videos = pipeline.metadata_manager.get_all_videos()

    if not videos:
        st.info("📭 No videos have been processed yet. Add your first video using the 'Add Video' page!")
        return

    st.write(f"**Total videos:** {len(videos)}")
    st.divider()

    # Display videos in cards
    for i, video in enumerate(videos, 1):
        with st.container():
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"### {i}. {video.get('video_title', 'Unknown Title')}")
                st.write(f"**Video ID:** `{video.get('video_id', 'N/A')}`")
                st.write(f"**URL:** {video.get('video_url', 'N/A')}")

                # Stats in columns
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                with stat_col1:
                    st.metric("Chunks", video.get('num_chunks', 0))
                with stat_col2:
                    st.metric("Length", f"{video.get('transcript_length', 0)} chars")
                with stat_col3:
                    processed_at = video.get('processed_at', 'Unknown')
                    if processed_at and processed_at != 'Unknown':
                        try:
                            dt = datetime.fromisoformat(processed_at)
                            formatted_date = dt.strftime("%Y-%m-%d")
                            st.metric("Processed", formatted_date)
                        except:
                            st.metric("Processed", processed_at)

            with col2:
                if st.button(f"🗑️ Delete", key=f"delete_{video.get('video_id')}"):
                    st.session_state[f"confirm_delete_{video.get('video_id')}"] = True

                # Confirmation dialog
                if st.session_state.get(f"confirm_delete_{video.get('video_id')}", False):
                    st.warning("Are you sure?")
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button("Yes", key=f"yes_{video.get('video_id')}"):
                            result = pipeline.delete_video(video.get('video_id'))
                            if result["success"]:
                                st.success(f"✅ Deleted {result['num_deleted']} chunks")
                                st.rerun()
                            else:
                                st.error(f"❌ Error: {result.get('error')}")
                    with col_no:
                        if st.button("No", key=f"no_{video.get('video_id')}"):
                            st.session_state[f"confirm_delete_{video.get('video_id')}"] = False
                            st.rerun()

            st.divider()


def page_chat(pipeline):
    """Chat page."""
    st.header("💬 Chat with Videos")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Sidebar for chat options
    with st.sidebar:
        st.subheader("Chat Settings")

        # Video filter
        videos = pipeline.metadata_manager.get_all_videos()
        video_options = ["All Videos"] + [f"{v['video_title']} ({v['video_id']})" for v in videos]

        selected_video = st.selectbox(
            "Search in:",
            video_options,
            help="Choose a specific video or search across all videos"
        )

        # Extract video ID if specific video selected
        video_id_filter = None
        if selected_video != "All Videos":
            # Extract video ID from the format "Title (ID)"
            video_id_filter = selected_video.split("(")[-1].strip(")")

        # Number of context chunks
        n_context = st.slider(
            "Context Chunks",
            min_value=1,
            max_value=10,
            value=5,
            help="Number of relevant chunks to retrieve"
        )

        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Display sources if available
            if message["role"] == "assistant" and "sources" in message:
                with st.expander("📚 View Sources"):
                    for i, source in enumerate(message["sources"], 1):
                        metadata = source["metadata"]
                        st.markdown(f"""
                        **Source {i}:** {metadata.get('video_title', 'Unknown')}
                        **Video ID:** `{metadata.get('video_id', 'Unknown')}`
                        **Chunk:** {metadata.get('chunk_index', '?')} | **Similarity:** {1 - source.get('distance', 0):.3f}

                        *Preview:* {source['text'][:200]}...
                        """)
                        st.divider()

    # Chat input hint
    st.markdown("""
        <div style="text-align: center; color: #888; font-size: 0.85rem; margin: 1rem 0;">
            💡 <strong>Tip:</strong> Press <kbd style="background: #f0f0f0; padding: 2px 6px; border-radius: 4px; border: 1px solid #ccc;">Enter</kbd> to send your message
        </div>
    """, unsafe_allow_html=True)

    # Chat input
    if prompt := st.chat_input("✨ Ask a question about the videos..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("✨ Generating answer..."):
                response = pipeline.chat(
                    question=prompt,
                    video_id_filter=video_id_filter,
                    n_context_chunks=n_context
                )

                if response["success"]:
                    st.markdown(response["answer"])

                    # Show metadata
                    metadata = response.get("metadata", {})
                    if "input_tokens" in metadata:
                        st.caption(f"🔢 Tokens: {metadata['input_tokens']} in, {metadata['output_tokens']} out | 🤖 Provider: {metadata.get('provider', 'unknown')}")

                    # Store message with sources
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["answer"],
                        "sources": response.get("sources", [])
                    })
                else:
                    error_msg = f"❌ Error: {response.get('message', 'Failed to generate answer')}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })


def page_stats(pipeline):
    """Statistics page."""
    st.header("📊 Database Statistics")

    result = pipeline.get_stats()

    if result["success"]:
        stats = result["stats"]

        # Main metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Videos", stats.get('total_videos', 0))
        with col2:
            st.metric("Total Chunks", stats.get('total_chunks', 0))
        with col3:
            avg_chunks = stats['total_chunks'] / stats['total_videos'] if stats.get('total_videos', 0) > 0 else 0
            st.metric("Avg Chunks/Video", f"{avg_chunks:.1f}")

        st.divider()

        # Collection info
        st.subheader("Collection Details")
        st.write(f"**Collection Name:** `{stats.get('collection_name', 'N/A')}`")

        # Video IDs
        st.subheader("Video IDs in Database")
        video_ids = stats.get("video_ids", [])
        if video_ids:
            for vid in video_ids:
                st.code(vid)
        else:
            st.info("No videos in database")
    else:
        st.error(f"❌ Error fetching statistics: {result.get('error', 'Unknown error')}")


def main():
    """Main application."""
    show_header()

    # Check configuration
    show_config_status()

    # Initialize pipeline
    try:
        pipeline = initialize_pipeline()
    except Exception as e:
        st.error(f"❌ Failed to initialize pipeline: {str(e)}")
        st.info("💡 Please check your configuration and try again.")
        st.stop()

    # Sidebar navigation
    with st.sidebar:
        st.title("🎯 Navigation")
        page = st.radio(
            "Choose a page:",
            ["💬 Chat", "📥 Add Video", "📚 My Videos", "📊 Statistics"],
            label_visibility="collapsed"
        )

        st.divider()

        # Show current config
        with st.expander("⚙️ Configuration"):
            from src.config import LLM_PROVIDER, GEMINI_MODEL, CLAUDE_MODEL
            st.write(f"**LLM Provider:** {LLM_PROVIDER}")
            if LLM_PROVIDER == "gemini":
                st.write(f"**Model:** {GEMINI_MODEL}")
            else:
                st.write(f"**Model:** {CLAUDE_MODEL}")

    # Route to appropriate page
    if "Chat" in page:
        page_chat(pipeline)
    elif "Add Video" in page:
        page_add_video(pipeline)
    elif "My Videos" in page:
        page_list_videos(pipeline)
    elif "Statistics" in page:
        page_stats(pipeline)


if __name__ == "__main__":
    main()
