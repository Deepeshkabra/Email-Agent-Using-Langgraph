# 📧 Email Agent Using LangGraph

**An intelligent email assistant that learns your preferences over time, triages your inbox, drafts responses, and schedules meetings—all with human-in-the-loop oversight.**

---

## 🎥 Demo

_Attach a video demo or GIF here showcasing the LangGraph workflow in action._

> The demo should illustrate the complete email processing flow: triage classification, human review via Agent Inbox, email response drafting, and how the system learns from user feedback to improve future interactions.

---

## 📖 Introduction

Managing email is a time sink. This project tackles that problem by building a **production-grade email assistant** using [LangGraph](https://langchain-ai.github.io/langgraph/)—a framework for building stateful, multi-actor AI applications with cycles, controllability, and persistence.

### Why LangGraph?

Traditional LLM chains are linear and stateless. Email management, however, requires:

- **Stateful workflows**: Remembering conversation context across multiple interactions
- **Conditional routing**: Different emails need different handling (ignore, notify, respond)
- **Human-in-the-loop control**: Critical actions like sending emails require human approval
- **Persistent memory**: Learning user preferences over time to improve triage and response quality
- **Interruptible execution**: Pausing workflows for human review and resuming with feedback

LangGraph provides all of these capabilities through its graph-based architecture, making it the ideal choice for this use case.

### What Makes This Project Non-Trivial

1. **Multi-stage triage with adaptive learning**: The system classifies emails into three categories and learns from corrections
2. **Nested graph composition**: A response agent subgraph handles the actual email drafting
3. **Bidirectional HITL**: Humans can approve, edit, provide feedback, or ignore at multiple decision points
4. **Memory profiles**: Three separate memory stores (triage, response, calendar) that evolve with usage
5. **Real Gmail integration**: Not just a demo—connects to actual Gmail/Google Calendar APIs
6. **Production deployment**: Docker support, cron jobs, and LangGraph Platform deployment

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **Smart Email Triage** | Classifies incoming emails as `ignore`, `notify`, or `respond` based on configurable rules |
| **Human-in-the-Loop** | All critical actions (sending emails, scheduling meetings) require human approval |
| **Adaptive Memory** | Learns from user feedback to improve triage decisions and response quality over time |
| **Gmail Integration** | Full integration with Gmail API for fetching, sending, and marking emails as read |
| **Calendar Management** | Checks availability and schedules meetings via Google Calendar API |
| **Agent Inbox Compatible** | Works with [Agent Inbox](https://dev.agentinbox.ai/) for a polished human review experience |
| **Automated Ingestion** | Cron jobs for continuous email processing on hosted deployments |
| **Stateful Execution** | Checkpointing enables pause/resume workflows across sessions |

### LangGraph Concepts Demonstrated

- **StateGraph**: Typed state management with Pydantic schemas
- **Command-based routing**: Dynamic edge traversal with `Command` objects
- **Interrupts**: `interrupt()` for human-in-the-loop checkpoints
- **Subgraph composition**: Response agent as a nested, reusable graph
- **BaseStore integration**: Persistent memory with namespace-based organization
- **Conditional edges**: Runtime routing based on state and LLM decisions

---

## 🏗 Architecture Overview

The email assistant is built as a hierarchical graph with two main components:

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           EMAIL ASSISTANT WORKFLOW                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────┐    ┌──────────────────┐                                            │
│  │  START  │───▶│   Triage Router  │                                            │
│  └─────────┘    └──────────────────┘                                            │
│                          │                                                       │
│          ┌───────────────┼───────────────┐                                      │
│          ▼               ▼               ▼                                      │
│    ┌──────────┐   ┌─────────────┐   ┌────────────────────┐                     │
│    │  IGNORE  │   │   RESPOND   │   │  NOTIFY (HITL)     │                     │
│    │  (END)   │   │             │   │                    │                     │
│    └──────────┘   └──────┬──────┘   └─────────┬──────────┘                     │
│                          │                     │                                │
│                          ▼                     ▼                                │
│                   ┌──────────────┐   ┌─────────────────────┐                   │
│                   │   Response   │◀──│ Triage Interrupt    │                   │
│                   │    Agent     │   │     Handler         │                   │
│                   │  (Subgraph)  │   └─────────────────────┘                   │
│                   └──────┬───────┘             │                               │
│                          │                     ▼                               │
│                          ▼                   (END)                             │
│                   ┌──────────────┐                                              │
│                   │ Mark as Read │                                              │
│                   └──────┬───────┘                                              │
│                          ▼                                                      │
│                        (END)                                                    │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Response Agent Subgraph

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           RESPONSE AGENT (SUBGRAPH)                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────┐    ┌───────────────┐    ┌────────────────────┐                    │
│  │  START  │───▶│   LLM Call    │───▶│  Should Continue?  │                    │
│  └─────────┘    │  (with tools) │    │                    │                    │
│                 └───────────────┘    └────────────────────┘                    │
│                        ▲                      │                                 │
│                        │          ┌───────────┴───────────┐                    │
│                        │          ▼                       ▼                    │
│                        │   ┌─────────────────┐    ┌──────────────┐             │
│                        │   │    Interrupt    │    │   Done Tool  │             │
│                        │   │    Handler      │    │   Called     │             │
│                        │   │    (HITL)       │    └──────┬───────┘             │
│                        │   └────────┬────────┘           │                     │
│                        │            │                    ▼                     │
│                        │            │             ┌──────────────┐             │
│                        └────────────┘             │ Mark as Read │             │
│                                                   └──────┬───────┘             │
│                                                          ▼                     │
│                                                        (END)                   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Agent Responsibilities

| Component | Responsibility |
|-----------|----------------|
| **Triage Router** | Classifies emails using an LLM with structured output (`RouterSchema`) |
| **Triage Interrupt Handler** | Presents notifications to humans, handles feedback for reclassification |
| **Response Agent** | Drafts emails, checks calendars, schedules meetings using bound tools |
| **Interrupt Handler** | HITL checkpoint for send_email, schedule_meeting, and Question tools |
| **Memory System** | Three namespaced stores for triage, response, and calendar preferences |

### State Transitions

```
State: {
  email_input: dict          # Raw email data from Gmail
  messages: List[Message]    # Conversation history with LLM
  classification_decision:   # "ignore" | "notify" | "respond"
}
```

State flows through the graph, accumulating messages and decisions. The `Command` pattern enables dynamic routing based on classification results and human feedback.

---

## 🛠 Tech Stack

| Category | Technology |
|----------|------------|
| **Agent Framework** | [LangGraph](https://langchain-ai.github.io/langgraph/) 1.0+ |
| **LLM Integration** | [LangChain](https://python.langchain.com/) with OpenAI/Gemini via OpenRouter |
| **Schema Validation** | Pydantic v2 |
| **Email API** | Gmail API (google-api-python-client) |
| **Calendar API** | Google Calendar API |
| **Testing** | Pytest with [LangSmith](https://smith.langchain.com/) integration |
| **Deployment** | Docker, LangGraph Platform |
| **Human Review** | [Agent Inbox](https://dev.agentinbox.ai/) |
| **Package Management** | uv / pip with pyproject.toml |

---

## 📁 Project Structure

```
Email-Agent-Using-Langgraph/
├── src/
│   └── email_assistant/
│       ├── __init__.py
│       ├── email_assistant.py              # Basic agent workflow
│       ├── email_assistant_hitl.py         # + Human-in-the-loop
│       ├── email_assistant_hitl_memory.py  # + Memory/learning
│       ├── email_assistant_hitl_memory_gmail.py  # + Gmail integration (main)
│       ├── prompts.py                      # System prompts and templates
│       ├── schemas.py                      # Pydantic models (State, RouterSchema)
│       ├── configuration.py                # Runtime configuration
│       ├── cron.py                         # Scheduled ingestion graph
│       ├── utils.py                        # Helper functions
│       ├── eval/
│       │   ├── email_dataset.py            # Test email corpus with ground truth
│       │   └── prompts.py                  # Evaluation prompts
│       └── tools/
│           ├── __init__.py
│           ├── base.py                     # Tool registry and loading
│           ├── default/
│           │   ├── email_tools.py          # write_email, Done, Question
│           │   ├── calendar_tools.py       # schedule_meeting, check_calendar
│           │   └── prompt_templates.py     # Tool descriptions for prompts
│           └── gmail/
│               ├── gmail_tools.py          # Gmail API wrappers
│               ├── setup_gmail.py          # OAuth setup script
│               ├── run_ingest.py           # Email ingestion CLI
│               ├── setup_cron.py           # Cron job configuration
│               └── README.md               # Gmail-specific docs
├── tests/
│   ├── conftest.py                         # Pytest fixtures
│   ├── test_response.py                    # Response quality tests
│   └── run_all_tests.py                    # Test runner
├── pyproject.toml                          # Dependencies and metadata
├── langgraph.json                          # LangGraph deployment config
├── Dockerfile                              # Container definition
└── README.md
```

### Key Directories

| Directory | Purpose |
|-----------|---------|
| `src/email_assistant/` | Core agent implementation with progressive feature additions |
| `src/email_assistant/tools/` | Modular tool implementations (default mock + Gmail API) |
| `src/email_assistant/eval/` | Evaluation dataset with 16 diverse email scenarios |
| `tests/` | Pytest-based test suite with LangSmith integration |

---

## 🚀 Setup & Installation

### Prerequisites

- Python 3.13+
- A Gmail account (for full functionality)
- OpenRouter API key or OpenAI API key

### 1. Clone and Install Dependencies

```bash
git clone https://github.com/yourusername/Email-Agent-Using-Langgraph.git
cd Email-Agent-Using-Langgraph

# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# LLM Provider (OpenRouter)
OPENROUTER_PERSONAL_BILLED_KEY=your_openrouter_key

# Or use OpenAI directly
OPENAI_API_KEY=your_openai_key

# LangSmith (optional, for tracing)
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=email-assistant
```

### 3. Set Up Gmail Integration (Optional)

For real Gmail functionality, follow the detailed setup in `src/email_assistant/tools/gmail/README.md`:

```bash
# 1. Create secrets directory
mkdir -p src/email_assistant/tools/gmail/.secrets

# 2. Download OAuth credentials from Google Cloud Console
# Save as: src/email_assistant/tools/gmail/.secrets/secrets.json

# 3. Run OAuth flow
python src/email_assistant/tools/gmail/setup_gmail.py
```

### 4. Run Locally with LangGraph Dev Server

```bash
# Start the development server
langgraph dev

# In another terminal, ingest emails
python src/email_assistant/tools/gmail/run_ingest.py \
  --email your@email.com \
  --minutes-since 1000
```

### 5. Connect to Agent Inbox

Open [Agent Inbox](https://dev.agentinbox.ai/) and connect:

- **Deployment URL**: `http://127.0.0.1:2024`
- **Graph ID**: `email_assistant_hitl_memory_gmail`

---

## 🔍 How the LangGraph Works (Deep Dive)

### Nodes

The workflow consists of these key nodes:

#### 1. `triage_router`
```python
def triage_router(state: State, store: BaseStore) -> Command[...]:
    """Classifies emails into ignore/notify/respond using structured LLM output."""
    # Fetches triage preferences from memory store
    # Uses RouterSchema for structured classification
    # Returns Command with goto and state update
```

#### 2. `triage_interrupt_handler`
```python
def triage_interrupt_handler(state: State, store: BaseStore) -> Command[...]:
    """HITL checkpoint for 'notify' classifications."""
    # Calls interrupt() to pause execution
    # Waits for human response via Agent Inbox
    # Updates memory based on human decision
```

#### 3. `llm_call` (in Response Agent)
```python
def llm_call(state: State, store: BaseStore):
    """Invokes LLM with tools to generate responses."""
    # Fetches calendar and response preferences from memory
    # Uses tool_choice="required" to enforce tool usage
```

#### 4. `interrupt_handler` (in Response Agent)
```python
def interrupt_handler(state: State, store: BaseStore) -> Command[...]:
    """HITL for send_email, schedule_meeting, and Question tools."""
    # Different handling for each tool type
    # Supports: accept, edit, ignore, respond actions
    # Updates memory when user edits or provides feedback
```

### Edges

The graph uses both static and conditional edges:

```python
# Static edges
agent_builder.add_edge(START, "llm_call")
agent_builder.add_edge("mark_as_read_node", END)

# Conditional edges with Command pattern
def should_continue(state: State, store: BaseStore) -> Literal[...]:
    """Routes based on tool calls in last message."""
    if tool_call["name"] == "Done":
        return "mark_as_read_node"
    else:
        return "interrupt_handler"
```

### State Management

State is managed through `MessagesState` (built-in message accumulation) extended with custom fields:

```python
class State(MessagesState):
    email_input: dict                                    # Raw email
    classification_decision: Literal["ignore", "respond", "notify"]
```

### Control Flow Decisions

1. **Triage Decision**: LLM classifies → routes to different branches
2. **HITL at Notify**: Human decides to respond or ignore
3. **Tool Execution**: Non-HITL tools execute immediately
4. **HITL at Critical Tools**: send_email, schedule_meeting, Question pause for approval
5. **Memory Updates**: User edits/feedback update relevant memory profiles

---

## 📋 Example Flow / Execution

### Scenario: Meeting Request Email

**Input Email:**
```
From: Sarah Johnson <sarah.j@partner.com>
Subject: Joint presentation next month
Body: Could we schedule 60 minutes to collaborate on slides?
```

**Step-by-Step Execution:**

1. **Triage Router**
   - Fetches triage preferences from memory
   - LLM classifies as `respond` (direct question requiring action)
   - Routes to `response_agent`

2. **LLM Call (Response Agent)**
   - Fetches calendar preferences (30-min meetings preferred)
   - Fetches response preferences (verify calendar, propose times)
   - LLM calls `check_calendar_tool` with dates

3. **Tool Execution (No HITL)**
   - Calendar check executes immediately
   - Returns: "Available: 10:00 AM - 12:00 PM, 2:00 PM - 4:00 PM"

4. **LLM Call (Second Pass)**
   - LLM calls `schedule_meeting_tool` with proposed time
   - Routes to `interrupt_handler`

5. **Interrupt Handler (HITL)**
   - Pauses execution, sends to Agent Inbox
   - Human reviews meeting details
   - Human edits duration from 30 to 60 minutes
   - Memory updated with new calendar preference

6. **Tool Execution**
   - Meeting scheduled with edited parameters
   - LLM drafts confirmation email

7. **Interrupt Handler (HITL for Email)**
   - Human approves email draft
   - Email sent via Gmail API

8. **Mark as Read**
   - Original email marked as read in Gmail

---

## 🎯 Design Decisions

### Why Three Separate Memory Stores?

Different aspects of email handling require different learning:

- **Triage Preferences**: Which senders/subjects to prioritize
- **Response Preferences**: Tone, structure, acknowledgment patterns
- **Calendar Preferences**: Meeting duration, time-of-day preferences

Separating these prevents unrelated feedback from corrupting other preferences.

### Why Command Pattern Over Conditional Edges?

`Command` objects provide:
- Atomic state updates with routing decisions
- Cleaner code than separate edge functions
- Type-safe routing with `Literal` types

### Why Subgraph for Response Agent?

The response agent is reusable:
- Called from both triage_router and triage_interrupt_handler
- Encapsulates the LLM loop with HITL
- Could be swapped for different response strategies

### Why OpenRouter Instead of Direct OpenAI?

- Access to multiple model providers (Google, Anthropic, OpenAI)
- Easy model switching for cost/performance optimization
- Provider fallback capabilities

---

## 💼 Use Cases

This architecture pattern applies beyond email:

| Use Case | Application |
|----------|-------------|
| **Customer Support** | Triage tickets, draft responses, escalate when needed |
| **Legal Document Review** | Classify documents, extract key terms, flag issues |
| **Sales Pipeline** | Qualify leads, draft outreach, schedule demos |
| **Content Moderation** | Classify content, take action, learn from corrections |
| **IT Helpdesk** | Categorize requests, suggest solutions, route to specialists |

The core pattern—**triage → decide → act with oversight → learn**—is universal for any domain where AI assists human decision-making.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`pytest tests/`)
5. Submit a Pull Request

For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

This project is open source. See the LICENSE file for details.

---

<div align="center">

**Built with [LangGraph](https://langchain-ai.github.io/langgraph/) 🦜🔗**

*Star this repo if you found it useful!*

</div>

