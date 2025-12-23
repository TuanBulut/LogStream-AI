# LogStream-AI: Self-Healing Polyglot Observability

**LogStream-AI** is a proof-of-concept **Autonomous SRE (Site Reliability Engineering) Platform**. It demonstrates a fully closed-loop system where an AI agent monitors a polyglot microservices architecture, detects failures in real-time via Kafka, and autonomously repairs the infrastructure using Docker commands.

---

## System Architecture

The system operates on an Event-Driven Architecture (EDA). A Chaos Generator monitors services and pushes health logs to Kafka. The Dashboard visualizes this data live, while the AI Worker consumes critical alerts to trigger self-healing protocols.

```mermaid
graph TD
    subgraph Infrastructure
        S1[Payment Service<br/>(Nginx/8080)]
        S2[Inventory Service<br/>(Nginx/8081)]
    end

    subgraph Monitoring Loop
        Gen[Chaos Generator<br/>Python] -->|HTTP Ping| S1
        Gen -->|HTTP Ping| S2
        Gen -->|Produces Log| Kafka{Apache Kafka}
    end

    subgraph Visualization
        Kafka -->|Consumes| Dash[Dashboard Backend<br/>C# .NET 9]
        Dash -->|SignalR WebSocket| Browser[Web UI<br/>Real-Time Graph]
    end

    subgraph Self-Healing Pipeline
        Kafka -->|Consumes Critical Log| Worker[AI Worker<br/>Python]
        Worker -->|1. Send Error Context| LLM[Ollama API<br/>DeepSeek-R1]
        LLM -->|2. Generate Fix Command| Worker
        Worker -->|3. Execute Shell Command| Docker[Docker CLI]
        Docker -->|Restart Container| S1
        Docker -->|Restart Container| S2
    end

    style Kafka fill:#333,stroke:#fff,stroke-width:2px,color:#fff
    style LLM fill:#6f42c1,stroke:#333,stroke-width:2px,color:#fff
    style Worker fill:#2ea44f,stroke:#333,stroke-width:2px,color:#fff
    style Dash fill:#512bd4,stroke:#333,stroke-width:2px,color:#fff
```

## Features

- **Polyglot Tech Stack**: Seamless integration of Python (Agents), C# (Web Backend), and Java/Nginx (Services).
- **Real-Time Visualization**: A .NET 9 Minimal API serving a dashboard that updates instantly via SignalR WebSockets.
- **AI Auto-Remediation**: Uses local LLMs (DeepSeek-R1 via Ollama) to interpret logs and generate valid Docker fix commands without human intervention.
- **Chaos Engineering**: Includes a generator script that simulates monitoring and detects outages (HTTP 500/Connection Refused).
- **Event Streaming**: Apache Kafka serves as the central nervous system, decoupling monitoring from visualization and remediation.

## Prerequisites

Before running the system, ensure you have the following installed:

- Docker Desktop (with Linux containers enabled)
- Python 3.8+
- .NET 9.0 SDK
- Ollama (for local AI inference)

## Installation & Setup

### 1. Setup the AI Model

Start your local Ollama instance and pull the reasoning model:

```bash
ollama pull deepseek-r1:1.5b
ollama serve
```

### 2. Start Infrastructure

Launch Zookeeper, Kafka, and the dummy microservices using Docker Compose:

```bash
docker-compose up -d
```

Wait about 30 seconds for Kafka to initialize completely.

### 3. Install Python Dependencies

Install the required libraries for the generator and the worker:

```bash
pip install kafka-python requests
```

### 4. Launch the Dashboard

Navigate to the dashboard directory and run the .NET application:

```bash
cd dashboard/LogStreamDashboard
dotnet run
```

Note the URL displayed in the terminal (usually `http://localhost:5000` or `http://localhost:5166`). Open this in your browser.

## How to Run the Demo

Open two separate terminal windows to run the background processes.

### Terminal A: The Monitor (Chaos Generator)

This script acts as the monitoring agent. It pings the services and writes logs to Kafka.

```bash
python chaos_generator/generator.py
```

**Output**: You should see "🟢 Payment Service is UP" logs.

### Terminal B: The SRE (AI Worker)

This script listens for failures and talks to the AI.

```bash
python ai_worker/worker.py
```

**Output**: "✅ AI Worker Connected! Waiting for disasters..."

### Trigger a Disaster

To test the self-healing capability, manually kill a service:

```bash
docker stop payment-service
```

### Watch the Result

- **Dashboard**: The "Payment Service" card turns RED. The "AI SRE Agent" status changes to FIXING.
- **AI Worker**:
  - Detects DOWN status
  - Prompts DeepSeek: "Service failed. How do I fix it?"
  - Receives command: `docker restart payment-service`
  - Executes command
- **Recovery**: The service restarts, the generator sees it coming back up, and the Dashboard turns GREEN automatically.

## Project Structure

```
LOGSTREAM-AI/
├── ai_worker/
│   ├── requirements.txt      # python dependencies
│   └── worker.py             # AI logic & Docker execution
├── chaos_generator/
│   ├── requirements.txt
│   └── generator.py          # Service poller & Kafka producer
├── dashboard/LogStreamDashboard/
│   ├── Program.cs            # .NET 9 Minimal API & Config
│   ├── KafkaConsumerService.cs # Background Task for Kafka
│   ├── LogHub.cs             # SignalR Hub
│   └── LogStreamDashboard.csproj
├── docker-compose.yml        # Infra definition (Kafka, ZK, Nginx)
└── README.md
```

## Security Disclaimer

**Use with caution.** The `ai_worker/worker.py` script executes shell commands generated by an LLM directly on your host machine via `subprocess.run`.

- Do not run this in a production environment without strict sandboxing
- Do not expose the Kafka ports or the dashboard to the public internet

## Troubleshooting

- **Kafka Connection Refused**: Ensure the Docker container `kafka` is running. If running scripts outside Docker, ensure `127.0.0.1:9092` is accessible.
- **Ollama Connection Error**: Ensure Ollama is running (`ollama serve`) and the model `deepseek-r1:1.5b` is downloaded.
- **Docker Permission Denied**: If running on Linux/Mac, the Python script might need `sudo` (or add your user to the docker group) to execute `docker restart`.