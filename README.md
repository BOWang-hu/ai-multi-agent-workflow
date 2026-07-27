# AI Multi-Agent Workflow

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/LangChain-0.3-green" alt="LangChain">
  <img src="https://img.shields.io/badge/OpenAI-GPT--4o--mini-brightgreen" alt="OpenAI">
  <img src="https://img.shields.io/badge/FastAPI-0.115-teal?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Streamlit-1.43-red?logo=streamlit" alt="Streamlit">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</p>

A multi-agent collaborative workflow system built with **LangChain + OpenAI**. It orchestrates multiple specialized AI agents to work together on complex tasks through a structured pipeline.

## 🤖 Agent Roles

| Role | Name | Description |
|------|------|-------------|
| 🔍 **Researcher** | Researcher | Collects and analyzes information, produces structured reports |
| ✍️ **Writer** | Writer | Creates high-quality content based on research materials |
| ✅ **Reviewer** | Reviewer | Reviews content quality, checks for issues, provides improvement suggestions |
| 🎯 **Coordinator** | Coordinator | Breaks down tasks, manages workflow, integrates outputs |

## 📋 How It Works

### Standard Workflow

A predefined 4-step pipeline that works for most content creation tasks:

```
Input Topic → Researcher → Writer → Reviewer → Coordinator → Final Output
```

1. **Researcher** studies the topic in depth
2. **Writer** creates content based on research
3. **Reviewer** examines quality and suggests improvements
4. **Coordinator** integrates everything into a final deliverable

### Custom Workflow

Define your own sequence of agent roles and tasks — flexible for any use case (e.g., code review pipelines, data analysis chains, multi-step content production).

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API Key

### Local Development

```bash
# Clone the repository
git clone https://github.com/BOWang-hu/ai-multi-agent-workflow.git
cd ai-multi-agent-workflow

# Configure environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# Install dependencies
pip install -r requirements.txt

# Start API server
uvicorn app.main:app --reload
# API runs at http://localhost:8000

# Start Web UI (new terminal)
streamlit run app/ui.py
# UI runs at http://localhost:8501
```

### Docker Deployment

```bash
cp .env.example .env
docker-compose up -d
# UI: http://localhost:8501
# API docs: http://localhost:8000/docs
```

### API Usage

```python
import requests

# Standard workflow
response = requests.post(
    "http://localhost:8000/workflow/standard",
    json={"topic": "Impact of AI on e-commerce"}
)
print(response.json()["final_output"])

# Custom workflow
response = requests.post(
    "http://localhost:8000/workflow/custom",
    json={
        "tasks": [
            {"title": "Research", "description": "Research the topic", "role": "researcher"},
            {"title": "Write", "description": "Write the report", "role": "writer"},
        ]
    }
)
```

## 📁 Project Structure

```
ai-multi-agent-workflow/
├── app/
│   ├── __init__.py      # Configuration management
│   ├── agents.py        # Agent definitions & workflow engine
│   ├── main.py          # FastAPI application entry
│   └── ui.py            # Streamlit user interface
├── .env.example         # Environment variable template
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container build
├── docker-compose.yml   # Container orchestration
└── README.md            # Project documentation
```

## 🛠️ Technical Highlights

1. **Role-Based Architecture**: Each agent has a distinct persona and expertise area
2. **Sequential Pipeline**: Output of one agent feeds as context to the next
3. **Graceful Degradation**: Falls back to mock responses when API Key is not configured
4. **Extensible**: Easy to add new agent roles or workflow patterns
5. **Flexible Orchestration**: Both standard and fully custom workflow modes

## 🚀 Related AI Projects

Check out my other AI agent projects:

| Project | Description |
|---------|-------------|
| [AI Customer Support Agent](https://github.com/BOWang-hu/ai-customer-support-agent) | Intelligent customer service chatbot with order tracking and FAQ |
| [AI RAG Knowledge Agent](https://github.com/BOWang-hu/ai-rag-knowledge-agent) | Document Q&A using RAG with Chroma vector database |
| [AI Code Review Agent](https://github.com/BOWang-hu/ai-code-review-agent) | Automated code review combining static analysis with AI |

---

## 📄 License

MIT — feel free to use, modify, and distribute.
