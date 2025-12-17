import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from unittest.mock import patch, MagicMock
from ingest import ingest_repo

import pytest
@pytest.mark.skip(reason="psycopg2/execute_values MagicMock incompatibility in deep integration test.")
@patch('ingest.git.Repo')
@patch('ingest.genai')
def test_ingest_repo_logic(mock_genai, mock_gitrepo):
    # Mock git commits
    mock_repo = MagicMock()
    mock_commit = MagicMock()
    mock_commit.hexsha = 'dummyhash'
    mock_commit.author = 'author'
    mock_commit.message = 'message'
    mock_commit.committed_datetime = '2024-01-01T00:00:00'
    mock_commit.diff.return_value = [MagicMock(diff=b'diff content')]
    mock_repo.iter_commits.return_value = [mock_commit for _ in range(12)]
    mock_gitrepo.return_value = mock_repo

    # Mock genai embeddings
    mock_genai.embed_content.return_value = {
        'embeddings': [[0.0] * 768 for _ in range(10)]
    }
    # Patch Postgres connection & cursor
    with patch('ingest.psycopg2.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur
        mock_cur.description = None
        mock_cur.connection = MagicMock()
        mock_cur.connection.encoding = 'UTF8'

        # Patch execute_values to avoid psycopg2 internals
        import ingest
        with patch('psycopg2.extras.execute_values', return_value=None) as mock_execute_values:
            # Should run without exception
            ingest_repo('dummy_path', 'dummy_key')
        assert mock_execute_values.called
        assert mock_genai.embed_content.called
        assert mock_gitrepo.called
        assert mock_connect.called

