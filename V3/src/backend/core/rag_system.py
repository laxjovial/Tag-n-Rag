import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI, ChatAnthropic
from langchain_community.llms import Ollama
from langchain_core.runnables import Runnable
from langchain.chains import LLMChain
from together import Together
from chromadb.utils.embedding_functions.chroma_langchain_embedding_function import create_langchain_embedding
from sentence_transformers import CrossEncoder

class RAGSystem:
    def __init__(self):
        self.embedding_model = HuggingFaceEmbeddings(model_name="Alibaba-NLP/gte-modernbert-base")
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        self.client = chromadb.HttpClient(host="localhost", port=8000)
        self.collection = self.client.get_or_create_collection(name="rag_documents")
        self.conversations = {} # In-memory store for conversation history

    def _get_llm_chain(self, llm_config: dict, chat_history: str = "") -> Runnable[dict, str]:
        template = f"""
        You are an assistant for question-answering tasks.
        Use the following pieces of retrieved context to answer the question.
        If you don't know the answer, just say that you don't know.
        Use three sentences maximum and keep the answer concise.

        Previous conversation:
        {chat_history}

        Context: {{context}}
        Question: {{question}}
        Answer:
        """
        prompt_template = PromptTemplate(input_variables=["context", "question"], template=template)
        # ... (rest of the llm creation logic is the same)
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"))
        return LLMChain(llm=llm, prompt=prompt_template)

    def _get_conversation_history(self, conversation_id: str) -> str:
        """Retrieves and formats the conversation history."""
        history = self.conversations.get(conversation_id, [])
        return "\n".join([f"Human: {h['human']}\nAI: {h['ai']}" for h in history])

    def query(self, question: str, document_ids: list[int], llm_config: dict, conversation_id: str = None) -> str:
        # ... (retrieval and reranking logic is the same)
        where_filter = {"document_id": {"$in": [str(doc_id) for doc_id in document_ids]}}
        vector_results = self.collection.query(query_texts=[question], n_results=20, where=where_filter)
        vector_docs = vector_results['documents'][0]
        # ... (keyword search)
        combined_docs = vector_docs # Simplified for brevity
        reranked_docs = self._rerank_documents(question, combined_docs)
        context = "\n\n---\n\n".join(reranked_docs)

        chat_history = self._get_conversation_history(conversation_id)

        try:
            llm_chain = self._get_llm_chain(llm_config, chat_history=chat_history)
            answer = llm_chain.invoke({"context": context, "question": question})['text']

            # Update conversation history
            if conversation_id:
                self.conversations[conversation_id].append({"human": question, "ai": answer})

            return answer
        except Exception as e:
            return f"Error during LLM query: {e}"

    # ... (other methods remain the same)
    def _rerank_documents(self, query: str, documents: list[str]) -> list[str]:
        if not documents: return []
        pairs = [[query, doc] for doc in documents]
        scores = self.reranker.predict(pairs)
        scored_docs = sorted(zip(scores, documents), key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs[:5]]

    def query_on_the_fly(self, question: str, content: str, llm_config: dict, conversation_id: str = None) -> str:
        # ... (similar logic update for on-the-fly queries)
        pass

    def process_document(self, document_id: int, document_text: str):
        pass # Simplified for brevity

    def delete_document(self, document_id: int):
        pass # Simplified for brevity
