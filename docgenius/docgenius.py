import os
import typer
from rich.markdown import Markdown
from rich.console import Console
from docgenius.ingest import ingest_repo
import google.generativeai as genai
import psycopg2
from psycopg2.extras import Json
import sys

app = typer.Typer(name="DocGenius", help="DocGenius: AI-powered code context and Q&A CLI tool")
console = Console()

DB_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'password',
    'host': 'localhost',
    'port': 5432,
}


def get_valid_api_key(api_key_arg: str = None):
    if api_key_arg:
        return api_key_arg
    env_key = os.environ.get('DOCGENIUS_API_KEY')
    if env_key:
        return env_key
    return typer.prompt('Please provide an API key', hide_input=True)

@app.command()
def sync(path: str = typer.Option('.', help="Path to git repo"), api_key: str = typer.Option(None, help="Gemini API Key")):
    valid_key = get_valid_api_key(api_key)
    ingest_repo(path, valid_key)

@app.command()
def ask(query: str = typer.Argument(..., help="Your question"), api_key: str = typer.Option(None, help="Gemini API Key")):
    valid_key = get_valid_api_key(api_key)
    genai.configure(api_key=valid_key)

    # Generate embedding for the query
    emb_response = genai.embed_content(model='models/text-embedding-004', content=[query])
    query_emb = emb_response['embeddings'][0]

    # Fetch top 5 closest chunks by cosine similarity
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT content, metadata, embedding <=> %s as similarity
        FROM code_context
        ORDER BY similarity ASC
        LIMIT 5;
    """, (query_emb,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    context_chunks = '\n'.join(row[0] for row in rows)
    prompt = f"Context:\n{context_chunks}\n\nQuestion: {query}"
    
    # Call Gemini completion
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt, stream=True)
    
    # Stream output as markdown
    for chunk in response:
        if hasattr(chunk, 'text'):
            console.print(Markdown(chunk.text), end="")

if __name__ == "__main__":
    app()

