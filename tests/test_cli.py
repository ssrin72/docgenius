import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
import docgenius

runner = CliRunner()

# Test sync fails gracefully when API key missing
@patch('docgenius.ingest_repo')
def test_sync_no_api_key(mock_ingest):
    # Unset env var in test
    if 'DOCGENIUS_API_KEY' in os.environ:
        del os.environ['DOCGENIUS_API_KEY']
    result = runner.invoke(docgenius.app, ['sync', '--path', '.'])
    assert 'Please provide an API key' in result.output
    assert result.exit_code == 0 or result.exit_code == 1  # Could be 0 if prompt caught, or 1 if prompt not available
    mock_ingest.assert_not_called()

# Test ask command context prompt formatting
@patch('docgenius.genai')
@patch('docgenius.psycopg2.connect')
def test_ask_prompt_format(mock_connect, mock_genai):
    mock_model = MagicMock()
    mock_stream = [MagicMock(text="Test answer.")]
    mock_model.generate_content.return_value = mock_stream
    mock_genai.GenerativeModel.return_value = mock_model
    mock_genai.embed_content.return_value = {'embeddings': [[0.1]*768]}
  
    # Mock DB connection and context fetch
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    mock_cur.fetchall.return_value = [
        ("chunk1", {"hash": "h1"}, 0.06),
        ("chunk2", {"hash": "h2"}, 0.08),
    ]

    result = runner.invoke(docgenius.app, ['ask', 'What is foo?', '--api-key', 'dummy'])
    # Assert output contains only model's answer (streamed output)
    assert "Test answer." in result.output
    # Prompt passed to model should contain contexts and the query
    assert mock_model.generate_content.called
    prompt_used = mock_model.generate_content.call_args[0][0]
    assert "chunk1" in prompt_used
    assert "chunk2" in prompt_used
    assert "What is foo?" in prompt_used

