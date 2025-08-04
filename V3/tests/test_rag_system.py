import pytest
from unittest.mock import MagicMock, patch
from src.backend.core.rag_system import RAGSystem

@pytest.fixture
def rag_system():
    """Fixture to create a RAGSystem instance with mocked external dependencies."""
    with patch('src.backend.core.rag_system.HuggingFaceEmbeddings'), \
         patch('src.backend.core.rag_system.CrossEncoder') as mock_cross_encoder, \
         patch('src.backend.core.rag_system.chromadb.HttpClient'), \
         patch('src.backend.core.rag_system.LLMChain') as mock_llm_chain:

        system = RAGSystem()
        # Mock the predict method of the reranker
        system.reranker.predict = MagicMock(return_value=[0.1, 0.9, 0.5])
        # Mock the invoke method of the llm_chain
        mock_llm_chain.return_value.invoke = MagicMock(return_value={"text": "Mocked LLM answer"})

        return system

def test_keyword_search(rag_system):
    docs = ["the quick brown fox", "jumps over the lazy dog", "a lazy fox"]
    query = "lazy fox"
    results = rag_system._keyword_search(query, docs)
    assert len(results) == 2
    assert "the quick brown fox" not in results

def test_rerank_documents(rag_system):
    docs = ["doc a", "doc b", "doc c"]
    query = "test query"
    # The mock predict will return [0.1, 0.9, 0.5]
    # So the expected order is doc b, doc c, doc a
    reranked = rag_system._rerank_documents(query, docs)
    assert reranked == ["doc b", "doc c", "doc a"]

def test_conversation_history_formatting(rag_system):
    conv_id = "test_conv"
    rag_system.conversations[conv_id] = [
        {"human": "Hello", "ai": "Hi there!"},
        {"human": "How are you?", "ai": "I am fine, thank you."}
    ]
    history_str = rag_system._get_conversation_history(conv_id)
    assert "Human: Hello" in history_str
    assert "AI: Hi there!" in history_str
    assert "Human: How are you?" in history_str
    assert "AI: I am fine, thank you." in history_str

def test_query_pipeline_orchestration(rag_system):
    # Mock the collection's query method
    rag_system.collection.query = MagicMock(return_value={'documents': [['doc1', 'doc2', 'doc3']]})

    # Spy on the internal methods
    with patch.object(rag_system, '_keyword_search', wraps=rag_system._keyword_search) as spy_keyword, \
         patch.object(rag_system, '_rerank_documents', wraps=rag_system._rerank_documents) as spy_rerank, \
         patch.object(rag_system, '_get_llm_chain', wraps=rag_system._get_llm_chain) as spy_llm:

        rag_system.query("test question", [1, 2], {}, conversation_id=None)

        # Assert that our pipeline methods were called
        spy_keyword.assert_called_once()
        spy_rerank.assert_called_once()
        spy_llm.assert_called_once()
