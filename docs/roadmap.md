# MemGrep Project Roadmap

This roadmap outlines the planned improvements and modernization efforts for the MemGrep project.

## 1. Modernize OCR and Image Embeddings

### Current State
- Using EasyOCR and Tesseract for text extraction
- Using BLIP for image captioning

### Planned Improvements
- **Implement Google/Gemini Vision API Integration**
  - Replace current OCR with Google Cloud Vision API or Gemini Pro Vision for improved accuracy
  - Leverage Gemini's multimodal capabilities for better understanding of meme context
  - Steps:
    1. Add Google Cloud Vision/Gemini client libraries to dependencies
    2. Create a new adapter in the extraction module
    3. Update the OCR extraction pipeline to use the new models
    4. Implement fallback to local models when API is unavailable

- **Enhance Image Embeddings**
  - Implement CLIP or Gemini embeddings for better semantic search
  - Steps:
    1. Research optimal embedding models (CLIP, Gemini, etc.)
    2. Create embedding generation pipeline
    3. Update the search functionality to use these embeddings

## 2. Migrate from Redis to Pinecone

### Current State
- Using Redis Stack for vector storage and search
- Implementation in `data/redis_db.py`

### Migration Plan
1. **Research and Evaluation**
   - Compare Redis performance with Pinecone for vector search
   - Benchmark query performance and scalability
   - Evaluate cost implications

2. **Implementation Steps**
   - Create a new `data/pinecone_db.py` module
   - Implement the same interface as the current Redis implementation
   - Add Pinecone client to project dependencies
   - Create abstraction layer to allow switching between Redis and Pinecone

3. **Data Migration Strategy**
   - Develop a migration script to transfer existing vectors to Pinecone
   - Implement feature flag to switch between Redis and Pinecone
   - No need to migrate existing data for initial implementation

## 3. Simplify Build Process

### Current State
- Using Docker Compose with multiple services
- Mixed dependency management (pip, poetry, Pipfile)

### Planned Improvements
1. **Single Dockerfile Approach**
   - Create a comprehensive Dockerfile that includes all necessary dependencies
   - Use multi-stage builds to optimize image size
   - Include optional components as build arguments

2. **Makefile for Local Development**
   - Create a Makefile with common commands:
     - `make setup`: Install dependencies
     - `make run`: Run the application
     - `make test`: Run tests
     - `make build`: Build Docker image
     - `make clean`: Clean up resources

3. **Dependency Management**
   - Consolidate all dependencies in a single `pyproject.toml`
   - Remove Pipfile and requirements.txt
   - Document all dependencies clearly

## 4. Adopt UV for Package Management

### Current State
- Using a mix of pip, poetry, and Pipfile

### Migration Plan
1. **Setup UV**
   - Add UV installation to setup documentation
   - Create UV configuration files

2. **Update Dependencies**
   - Audit and update all dependencies to latest compatible versions
   - Remove deprecated packages
   - Consolidate duplicate functionality

3. **Documentation**
   - Update all documentation to reference UV for package management
   - Provide migration guide for existing users

## 5. Verify Telegram API Functionality

### Current State
- Using Telethon 1.16.1 for Telegram API access
- Bot implementation using python-telegram-bot

### Verification Steps
1. **API Compatibility Check**
   - Verify compatibility with latest Telegram API changes
   - Update Telethon to the latest version (currently at 1.27.0)
   - Test all Telegram-related functionality

2. **Bot Functionality**
   - Test and verify all bot commands
   - Ensure proper error handling for API rate limits
   - Implement reconnection logic for better reliability

3. **Authentication Flow**
   - Review and improve the authentication process
   - Implement better session management
   - Add proper logging for API interactions

## 6. Improve Testing Coverage

### Current State
- Limited or no automated tests
- No CI/CD pipeline for testing

### Testing Strategy
1. **Unit Tests**
   - Implement unit tests for core functionality:
     - OCR extraction
     - Search functionality
     - Data storage operations
   - Use pytest as the testing framework

2. **Integration Tests**
   - Create integration tests for:
     - API endpoints
     - Database interactions
     - External service integrations

3. **End-to-End Tests**
   - Implement E2E tests for critical user flows:
     - Meme scraping
     - Search functionality
     - Bot interactions

4. **CI/CD Integration**
   - Set up GitHub Actions for automated testing
   - Implement test coverage reporting
   - Add pre-commit hooks for code quality

## Timeline and Priorities

1. **Short-term (1-2 months)**
   - Verify Telegram API functionality
   - Simplify build process with Makefile
   - Adopt UV for package management

2. **Medium-term (2-4 months)**
   - Implement testing infrastructure
   - Modernize OCR with Google/Gemini models
   - Create single Dockerfile solution

3. **Long-term (4-6 months)**
   - Migrate from Redis to Pinecone
   - Enhance image embeddings
   - Implement comprehensive E2E testing