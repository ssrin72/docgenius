# DocGenius

AI-powered code context and Q&A CLI tool.

---

## Getting Started (Clone and Use in Any Repo)

1. **Clone this Repo**
    ```bash
    git clone https://github.com/ssrin72/docgenius.git
    cd docgenius
    ```
2. **(Recommended) Create a Virtualenv**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
3. **Install the CLI Locally**
    ```bash
    pip install -e .
    # or
    python -m pip install --editable .
    ```
4. **Verify Installation**
    ```bash
    docgenius --help
    ```
5. **Set Up Database and Environment**
    - Start Postgres/pgvector (Docker Compose):
      ```bash
      docker-compose up -d
      ```
    - Initialize the database table:
      ```bash
      python -m docgenius.db_setup
      ```
    - Provide your API Key (one-off or export):
      ```bash
      export DOCGENIUS_API_KEY=sk-...
      # or pass --api-key <YOUR_KEY> to each command
      ```
6. **Ingest Your Codebase into the DB**
    ```bash
    docgenius sync --path .     # with env key OR use --api-key ...
    ```
7. **Ask a Question**
    ```bash
    docgenius ask "How does authentication work?"  # --api-key optional, uses env
    ```

---

## Usage Reference

```bash
docgenius --help
```
- Lists all commands (`sync` / `ask` etc).

---

## Example: Ingestion & Q&A
```bash
docgenius sync --path . --api-key <YOUR_GEMINI_API_KEY>
docgenius ask "How does the routing work?" --api-key <YOUR_GEMINI_API_KEY>
```
Or use exported key for all sessions:
```bash
export DOCGENIUS_API_KEY=sk-...
docgenius sync --path .
docgenius ask "What is our product model?"
```

---

## Run the Test Suite (requires dev dependencies)
```bash
pytest
```

---

## License
MIT
