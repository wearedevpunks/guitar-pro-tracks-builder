# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture

This is a guitar pro tracks builder application with a hybrid Next.js + FastAPI architecture:

- **Frontend**: Next.js 13 React app in `/app` using TypeScript, Tailwind CSS, and the AI SDK for chat interface
- **Backend**: FastAPI Python server in `/api` that provides OpenAI-powered chat completion with tool calling
- **Deployment**: Configured for Vercel with API rewrites to proxy FastAPI endpoints

The frontend uses the AI SDK's `useChat` hook to communicate with the FastAPI backend, which implements OpenAI's streaming protocol with tool support (currently weather tools).

## Development Commands

### Setup
```bash
# Install Node dependencies
pnpm install

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

### Running Development Server
```bash
# Run both Next.js and FastAPI concurrently
pnpm dev

# Or run individually:
pnpm next-dev  # Next.js on port 3021
pnpm fastapi-dev  # FastAPI on port 8000
```

### Build and Deploy
```bash
pnpm build     # Build Next.js for production
pnpm start     # Start production server
pnpm lint      # Run ESLint
```

## Key Integration Points

- API routes are proxied through Next.js config (`next.config.js`) to FastAPI in development
- FastAPI implements AI SDK Data Stream Protocol for real-time chat streaming
- Tool calling system in `/api/utils/tools.py` with registration in main FastAPI app
- Frontend chat component uses AI SDK's `useChat` with streaming support

## Environment Requirements

- Node.js with pnpm
- Python 3.x with virtual environment
- OpenAI API key (required for chat functionality)