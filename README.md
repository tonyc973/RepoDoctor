# 🩺 Repo Doctor

> **Autonomous Code Auditor powered by AutoGen 0.4 & Model Context Protocol (MCP)**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![AutoGen](https://img.shields.io/badge/AutoGen-0.4-purple)
![MCP](https://img.shields.io/badge/Protocol-MCP-green)

**Repo Doctor** is an AI Agent Swarm that autonomously navigates, analyzes, and critiques remote GitHub repositories. 

Unlike standard "Chat with Code" tools, Repo Doctor uses an **event-driven agentic workflow**:
1.  **The Navigator** agent explores the file tree via the GitHub API to identify core logic.
2.  **The Analyst** agent reads specific files, detecting bugs, security risks, and patterns.
3.  **The Result** is a detailed `IMPROVEMENTS.md` report saved directly to your local machine.

---

## 🏗 Architecture

The system decouples the **Tool** (GitHub API access) from the **Agent** (Logic) using the well-known Model Context Protocol (MCP).The MCP server exposes 2 functions that enable us to interact with github: list_files and read_files.

## 🚀 Installation

```bash
git clone https://github.com/tonyc973/RepoDoctor.git
cd RepoDoctor
```
Install dependencies
```bash
pip install -r requirements.txt
```
Configure Environment
```bash
cp .env.example .env
OPENAI_API_KEY=""
GITHUB_TOKEN=""
```

💻 Usage
```bash
python repo_doctor.py
```
