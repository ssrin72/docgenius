import os
import sys
import google.generativeai as genai
import git
import psycopg2
from psycopg2.extras import execute_values
from rich.progress import track
from typing import List

DB_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'password',
    'host': 'localhost',
    'port': 5432,
}

def ingest_repo(repo_path: str, api_key: str):
    genai.configure(api_key=api_key)
    repo = git.Repo(repo_path)
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    commits = list(repo.iter_commits('HEAD', max_count=100))
    batch = []
    metadata_batch = []
    commit_chunks: List[str] = []

    # Use rich progress bar
    for commit in track(commits, description="Ingesting commits..."):
        diff = commit.diff(create_patch=True, parents=True)
        diff_str = '\n'.join(d.diff.decode('utf-8', errors='ignore') if d.diff else '' for d in diff)
        chunk = f"Commit {commit.hexsha} by {commit.author}: {commit.message.strip()}. Diff: {diff_str}"
        commit_chunks.append(chunk)
        metadata_batch.append({
            'hash': commit.hexsha,
            'author': str(commit.author),
            'date': str(commit.committed_datetime),
        })

        if len(commit_chunks) == 10:
            # Get embeddings for the batch
            embeddings = genai.embed_content(model='models/text-embedding-004', content=commit_chunks)
            upsert_chunks_to_db(cur, commit_chunks, metadata_batch, embeddings)
            commit_chunks.clear()
            metadata_batch.clear()

    # Handle any final leftover chunks
    if commit_chunks:
        embeddings = genai.embed_content(model='models/text-embedding-004', content=commit_chunks)
        upsert_chunks_to_db(cur, commit_chunks, metadata_batch, embeddings)

    conn.commit()
    cur.close()
    conn.close()

def upsert_chunks_to_db(cur, chunk_batch, metadata_batch, embedding_batch):
    assert len(chunk_batch) == len(metadata_batch) == len(embedding_batch['embeddings'])
    data = [
        (chunk, meta, embedding)
        for chunk, meta, embedding in zip(chunk_batch, metadata_batch, embedding_batch['embeddings'])
    ]
    query = """
    INSERT INTO code_context (content, metadata, embedding)
    VALUES %s
    ON CONFLICT (content) DO NOTHING;
    """
    execute_values(cur, query, data)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ingest git repo commits into Postgres with embeddings.")
    parser.add_argument('--repo_path', type=str, required=True, help='Path to the git repository')
    parser.add_argument('--api_key', type=str, required=True, help='Gemini API Key')
    args = parser.parse_args()
    ingest_repo(args.repo_path, args.api_key)

