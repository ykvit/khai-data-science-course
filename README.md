# KHAI Data Science Labs

This repository contains a set of labs for Data Science tasks developed at KHAI. Each lab is organized in its own folder with Docker support for reproducibility and isolation.



### 🚩 Run Lab 1

Lab 1 Operations with numbers and expressions in Python.

**Build the Docker image:**

```bash
    cd lab1
    docker build -t lab1 .
    docker run --rm lab1
```

**Docker compose:**

```bash
    docker-compose build lab1
    docker-compose run lab1
```

---
### 🚩 Run Lab 2

Lab 2 Processing and analyzing data on people's physical characteristics.


**Build the Docker image:**

```bash
   cd lab2
   docker build -t lab2 .
   docker run --rm -v "$(pwd)/output:/app/output" lab2
```

**Docker compose:**

```bash
    docker-compose build lab2
    docker-compose run lab2
```

---

### 🚩 Run Lab 3

Lab 3 Processing and analyzing student performance data using Pandas.


**Build the Docker image:**

```bash
   cd lab3
   docker build -t lab3 .
   docker run --rm -v "$(pwd)/output:/app/output" lab3
```

**Docker compose:**

```bash
    docker-compose build lab3
    docker-compose run lab3
```

---

### 🚩 Run Lab 6

Lab 6 Using large language models (LLM) to assess text and code integrity.

**Prerequisites:**
*   You need a Google API Key for the Gemini model. Get one from [Google AI Studio](https://aistudio.google.com/app/apikey).
*   Create a file named `.env` inside the `lab6/` directory by copying `lab6/.env.example`.
*   Paste your Google API Key into the `lab6/.env` file:
   
```
GOOGLE_API_KEY=YOUR_API_KEY_HERE
```

**Docker Compose (Recommended):**
*(Requires X11 forwarding configured on the host)*


**(Linux Only) Allow local connections to the X server:**
    ```bash
    xhost +local:docker
    ```
    *(Run this once per session if needed)*

**Docker compose:**

```bash
docker compose build lab6
docker compose run lab6
```

**Local Execution (Without Docker):**

```bash
cd lab6
```
 **Set up a virtual environment (Recommended):**
```bash
    # Create if it doesn't exist (using the name .venv)
    python -m venv ../.venv

    # Activate the environment
    # On Linux/macOS:
    source ../.venv/bin/activate
    # On Windows (Git Bash/WSL):
    # source ../.venv/bin/activate
    # On Windows (Command Prompt/PowerShell):
    # ..\.venv\Scripts\activate
```
**Install dependencies:**
```bash
pip install -r requirements.txt
```
**Run the application:**
```bash
python main.py
```
---

### Cleanup

```bash
    docker system prune
```
