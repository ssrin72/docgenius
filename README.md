# DocGenius

AI-powered code context and Q&A CLI tool.

## Installation (dev mode)

```bash
pip install -e .
```

or

```bash
python -m pip install --editable .
```

## Usage

```bash
docgenius --help
```

### Example: Ingest codebase

```bash
docgenius sync --path . --api-key <YOUR_GEMINI_API_KEY>
```

or set your API key globally:

```bash
export DOCGENIUS_API_KEY=sk-...
docgenius sync --path .
```

### Example: Ask a question

```bash
docgenius ask "What is the main authentication flow?" --api-key <YOUR_GEMINI_API_KEY>
```

---

**Note**: Ensure your dockerized Postgres/pgvector is running, and tables are initialized using:

```bash
docker-compose up -d
python db_setup.py
```

---

## Development
Test with pytest:
```bash
pytest
```

---

## License
MIT

