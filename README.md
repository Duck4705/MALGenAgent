[🇻🇳 Vietnamese version](README_vi.md)

# MALGenAgent (MGA): Malware Generator Agent

## Table of Contents
- [Overview](#overview)
- [MalGenAgent Architecture](#malgenagent-architecture)
- [Installation](#installation)
- [Features](#features)
- [Development Guide](#development-guide)
- [Disclaimer](#disclaimer)
- [Conclusion](#conclusion)

## Overview
As malware attacks become increasingly sophisticated, especially with the rise of large language models (LLMs) automating malware creation for high-value targets and shortening development time, traditional defense systems face new challenges. The increase in AI-generated malware attacks demands more effective defense methods for Blue Team researchers, though results remain limited. Meanwhile, Red Team researchers need automated tools to quickly exploit vulnerabilities, optimize malware development, and assess target effectiveness.

To address these practical needs, we propose an automated malware development agent framework based on LLMs, called MalGenAgent. MalGenAgent can automatically generate complete malware binaries from user functional requirements, without requiring deep malware or programming knowledge. MalGenAgent is inspired by and built upon the MalGen agent framework presented in the paper [MalGEN: A Generative Agent Framework for Modeling Malicious Software in Cybersecurity](https://arxiv.org/pdf/2506.07586).

## MalGenAgent Architecture
![image-MalGenAgent](image/1_MalGenAgentImage.png)

MalGenAgent consists of 4 main agents:
- **Planner Agent**: Receives user input and breaks it into subtasks to implement desired functions. Each subtask is a small malware requirement. These subtasks are sent to the Developer Agent to generate code snippets and their descriptions. If the user does not specify a programming language, Python is used by default.
- **Developer Agent**: Receives each subtask from the Planner Agent and generates code samples with descriptions of their functionality and required libraries.
- **Coder Agent**: Aggregates code and descriptions from the Developer Agent and builds a complete, runnable code.
- **Executable Builder**: Builds the complete code into an executable file (.exe for Windows, .elf for Linux). Bash scripts do not require building (not yet tested or implemented).
- **Checker Agent**: Receives output from the Executable Builder, detects errors, and fixes code. If the code is fixed, it is sent back to the Executable Builder for rebuilding. If the build is successful, the malware creation process stops.

## Installation
MALGenAgent works best on [Kali Linux](https://www.kali.org/get-kali/#kali-platforms) with at least 8 GB RAM, 8 core CPU, and 80GB hard disk. For Windows, see the installation guide [Guide_For_Window](./docs/Guide_For_Window.md).

Install MalGenAgent:
```bash
git clone https://github.com/your-org/MALGenAgent.git
cd MALGenAgent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Create .env file:
```bash
echo -e "LANGCHAIN_API_KEY=\nLANGCHAIN_TRACING_V2=true" > .env
```
Create a LangChain account and get your LANGCHAIN_API_KEY at https://www.langchain.com/
```.env
LANGCHAIN_API_KEY="replace this by langchain api key"
LANGCHAIN_TRACING_V2=true
OLLAMA=false # true if use Ollama
BASE_URL= # If not specified, default OpenAI URL is used.
MODEL=
API_KEY=
```
MalGenAgent currently uses Ollama for open-source LLMs. You can switch to OpenAI or other platforms via [docs](./docs/Guide_Change_Model_LLM.md).
Download Ollama and models ([see available models here](https://ollama.com/search)):
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5-coder:7b
```
If the folders **dist, dist_C++, dist_Go, bash_script, tmp_file** do not exist, create them in the root directory.
These folders are the output executables for **Python, C++, Go, bash script** respectively.

Start the program:
```
langgraph dev
```
Enter your input at the INPUT prompt.

## Features
Currently, MalGenAgent (MGA) supports:
- On Linux: Python and C++ code built as ELF binaries
- On Windows: Python and C++ code built as EXE binaries

## Development Guide
MalGenAgent is developed for research purposes and is not yet deployed in practical applications. The system currently supports Python and C++. Future plans include expanding support to C#, Java, bash script, etc., to meet diverse research and application needs.

Advanced features such as malware packing, obfuscation, and code confusion will be researched and integrated in future versions. Example prompts for users and developers:
> Build me a Linux malware in Python that enumerates all running processes and then attempts to exfiltrate this process list to a remote server at 192.168.1.50 over TCP.

> Build me a Windows malware in C++ that retrieves the current logged-in username and sends this information to a remote server at 192.168.1.80 using a TCP connection.

## Disclaimer
MalGenAgent is intended for research, education, and testing in controlled, safe environments only. The project is not designed or encouraged for unauthorized attacks, malware distribution, or illegal system access.
Users must:
- Comply with all legal and ethical standards when using MalGenAgent (MGA).
- Deploy only in legal test environments (e.g., sandbox, internal lab, CTF, academic exercises).
- Understand that the development team is not legally responsible for any misuse.
MalGenAgent aims to support Red Team/Blue Team communities, security researchers, and students by:
  - Enhancing understanding of malware creation and detection techniques.
  - Developing effective defense solutions against increasingly sophisticated threats.

## Conclusion
MalGenAgent is an experimental step in applying LLMs to automate malware development simulation. We hope this project will:
- Inspire the research community to explore new approaches.
- Provide a foundation for developing more features for academic, research, and security training purposes.
- Foster collaboration among researchers, students, and the community to build a safe, transparent, and educational research ecosystem.

We hope MalGenAgent will receive support, ideas, and contributions from the community to improve and help strengthen global network defense.

