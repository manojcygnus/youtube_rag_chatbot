# Contributing to YouTube RAG Chatbot

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Keep discussions professional and on-topic

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/youtube-rag-chatbot.git
   cd youtube-rag-chatbot
   ```
3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/original-owner/youtube-rag-chatbot.git
   ```

## Development Setup

1. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your `.env` file:
   ```bash
   cp .env.example .env
   # Add your API keys
   ```

4. Verify installation:
   ```bash
   python src/config.py
   ```

## Making Changes

### Before You Start

1. Check if an issue exists for your proposed change
2. If not, create an issue to discuss it first
3. Get feedback before writing code

### Branch Naming

Use descriptive branch names:
- `feature/add-timestamp-links` - New features
- `fix/rate-limit-handling` - Bug fixes
- `docs/improve-readme` - Documentation
- `refactor/simplify-pipeline` - Code refactoring

### Workflow

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes:
   - Write clean, readable code
   - Add comments for complex logic
   - Follow existing code style
   - Update documentation as needed

3. Test your changes:
   ```bash
   # Test manually
   python test_manual.py
   python test_embeddings.py

   # Test web interface
   streamlit run streamlit_app.py

   # Test CLI
   python main.py
   ```

4. Commit your changes:
   ```bash
   git add .
   git commit -m "feat: add timestamp links to sources"
   ```

## Submitting Changes

### Pull Request Process

1. Update your branch with latest upstream:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

3. Create a Pull Request on GitHub

4. Fill out the PR template:
   - **Description**: What does this PR do?
   - **Issue**: Link related issue(s)
   - **Testing**: How did you test this?
   - **Screenshots**: If UI changes, include before/after

### PR Review Checklist

Before submitting, ensure:
- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] No sensitive data (API keys) in commits
- [ ] Commit messages are clear and descriptive
- [ ] PR description explains the changes

## Coding Standards

### Python Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Write docstrings for functions/classes
- Keep functions focused and small
- Maximum line length: 100 characters

**Example:**

```python
def extract_video_id(youtube_url: str) -> str:
    """
    Extract video ID from YouTube URL.

    Args:
        youtube_url: Full YouTube URL

    Returns:
        11-character video ID

    Raises:
        ValueError: If URL format is invalid
    """
    # Implementation here
    pass
```

### Code Organization

- Keep related functions together
- Use meaningful file/module names
- Separate concerns (retrieval, generation, UI)
- Avoid circular imports

### Comments

- Explain **why**, not **what**
- Use comments for complex logic
- Keep comments up-to-date
- Remove commented-out code

### Error Handling

```python
# Good: Specific error handling
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    return {"success": False, "error": str(e)}

# Bad: Catching all exceptions
try:
    result = risky_operation()
except:
    pass
```

## Testing

### Manual Testing

Test all affected functionality:

```bash
# Test transcript extraction
python -c "from src.transcript_extractor import extract_transcript; print(extract_transcript('VIDEO_URL'))"

# Test embedding creation
python test_embeddings.py

# Test full pipeline
python main.py  # Try all menu options

# Test web interface
streamlit run streamlit_app.py  # Test all pages
```

### Test Cases to Verify

When making changes, test:
- ✅ Processing new videos
- ✅ Asking questions (various types)
- ✅ Viewing video list
- ✅ Deleting videos
- ✅ Error handling (invalid URLs, API errors)
- ✅ Both CLI and web interfaces
- ✅ Configuration changes

## Documentation

### What to Document

- New features and how to use them
- Configuration options
- API changes
- Breaking changes
- Migration guides (if needed)

### Where to Document

- **README.md**: User-facing documentation
- **Code comments**: Implementation details
- **Docstrings**: Function/class documentation
- **CONTRIBUTING.md**: Development guidelines (this file)

### Documentation Style

- Use clear, simple language
- Include code examples
- Add screenshots for UI changes
- Explain the "why" behind decisions

## Areas for Contribution

### High Priority

- [ ] Add video timestamp links in source attribution
- [ ] Support for multiple languages
- [ ] Batch video processing
- [ ] Docker containerization
- [ ] Improved error messages

### Medium Priority

- [ ] Export chat history
- [ ] Custom embedding models
- [ ] Video metadata editing
- [ ] Advanced search filters
- [ ] Performance optimizations

### Documentation

- [ ] Video tutorials
- [ ] Architecture diagrams
- [ ] API documentation
- [ ] Troubleshooting guides
- [ ] Use case examples

### Testing

- [ ] Unit tests
- [ ] Integration tests
- [ ] Performance benchmarks
- [ ] CI/CD pipeline

## Questions?

- Open an issue for questions
- Check existing issues and PRs
- Read the main README.md
- Review closed PRs for examples

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Thanked in the README

Thank you for contributing! 🎉
