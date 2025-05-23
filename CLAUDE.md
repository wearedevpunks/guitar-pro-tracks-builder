# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture

This is a Guitar Pro Tracks Builder application with a hybrid Next.js + FastAPI architecture:

- **Frontend**: Next.js 13 React app with homepage (`/`) for file upload and track builder (`/track`) using TypeScript, Tailwind CSS, and the AI SDK for chat interface
- **Backend**: FastAPI Python server in `/api` that provides OpenAI-powered chat completion with tool calling
- **Deployment**: Configured for Vercel with API rewrites to proxy FastAPI endpoints

The frontend uses the AI SDK's `useChat` hook to communicate with the FastAPI backend, which implements OpenAI's streaming protocol with tool support (currently weather tools).

### Frontend Structure

- **Components**: Split into UI and functional components
  - `/components/ui/` - Reusable UI components
  - `/components/ui/metal/` - Metal-themed UI components (buttons, logos, backgrounds, forms, containers)
- **Features**: Business logic organized by feature with granular components
  - `/features/file-upload/` - File upload functionality
    - `components/` - Drop zone, action buttons, containers
    - `hooks/` - Upload logic and state management
  - `/features/chat/` - Chat functionality with AI integration
    - `components/` - Messages area, input area, overview
    - `components/messages/` - Message container, list, scroll anchor
    - `hooks/` - Chat logic and API integration
- **Containers**: Page-level components that aggregate features
  - `/containers/home/` - Homepage container with hero section and file upload
  - `/containers/track/` - Track builder page container with chat interface
- **Stores**: Zustand state management
  - `/stores/file-upload-store.ts` - File upload state management
  - `/stores/chat-store.ts` - Chat state and message management

### Component Breakdown Principles

- **Single Responsibility**: Each component has one clear purpose
- **Composition**: Components are composed together rather than monolithic
- **Hooks**: Business logic extracted into custom hooks
- **Separation**: UI components separated from logic components
- **Reusability**: Granular components can be reused across features

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

## Code Structure Guidelines

- Always split UI components and functional components
- Create a `features` folder with a subfolder for each business feature
- Place functional components inside their respective feature subfolder
- Add Zustand state management as necessary for each feature
- Organize related utilities, hooks, and state management within feature-specific folders
- To keep app routes clean create a page component under a folder named containers inside a subfolder named under the page. The container is built aggregating one or more feature components / ui components