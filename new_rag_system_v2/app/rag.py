import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
import chromadb
# Corrected import for HuggingFaceEmbeddings based on deprecation warning
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI, ChatAnthropic
from langchain_community.llms import Ollama
from langchain_core.runnables import Runnable
from langchain.chains import LLMChain
from together import Together

# Import ChromaDB's LangChain adapter
from chromadb.utils.embedding_functions.chroma_langchain_embedding_function import create_langchain_embedding


class RAGSystem:
    def __init__(self):
        """Initializes the RAG system with a fixed embedding model and vector store."""
        # Initialize your desired embedding model from the new package
        self.embedding_model = HuggingFaceEmbeddings(model_name="Alibaba-NLP/gte-modernbert-base")

        # Wrap the LangChain embedding model with ChromaDB's adapter
        # This makes it compatible with ChromaDB's expected EmbeddingFunction interface
        chroma_embedding_function = create_langchain_embedding(self.embedding_model)

        # Connect to your running ChromaDB server
        self.client = chromadb.HttpClient(host="localhost", port=8000)

        # Pass the adapted embedding_function to get_or_create_collection
        self.collection = self.client.get_or_create_collection(
            name="rag_documents",
            embedding_function=chroma_embedding_function # <--- Use the adapted function here
        )


    def _get_llm_chain(self, llm_config: dict) -> Runnable[dict, str]:
        """Dynamically creates an LLM chain based on the provided config."""
        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""
            You are an assistant for question-answering tasks.
            Use the following pieces of retrieved context to answer the question.
            If you don't know the answer, just say that you don't know.
            Use three sentences maximum and keep the answer concise.

            Context: {context}
            Question: {question}
            Answer:
            """
        )

        llm_type = llm_config.get("type", "openai")
        model_name = llm_config.get("model_name")
        api_key_env = llm_config.get("api_key_env")

        llm = None
        if llm_type == "openai":
            if not model_name:
                model_name = "gpt-3.5-turbo"
            llm = ChatOpenAI(model_name=model_name, api_key=os.getenv(api_key_env or "OPENAI_API_KEY"))
        elif llm_type == "anthropic":
            if not model_name:
                model_name = "claude-2"
            llm = ChatAnthropic(model_name=model_name, anthropic_api_key=os.getenv(api_key_env or "ANTHROPIC_API_KEY"))
        elif llm_type == "ollama":
            if not model_name:
                model_name = "llama2"
            llm = Ollama(model=model_name, base_url=llm_config.get("api_endpoint", "http://localhost:11434"))
        elif llm_type == "together":
            if not model_name:
                model_name = "mistralai/Mixtral-8x7B-Instruct-v0.1"
            llm = Together(
                model_name=model_name,
                together_api_key=os.getenv(api_key_env or "TOGETHER_API_KEY"),
            )
        else:
            raise ValueError(f"Unsupported LLM type: {llm_type}")

        llm_chain = LLMChain(llm=llm, prompt=prompt_template)
        return llm_chain


    def process_document(self, document_id: int, document_text: str):
        """
        Processes a document, splits it into chunks, embeds them, and stores them in the vector store.

        Args:
            document_id (int): The unique ID of the document.
            document_text (str): The text content of the document.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(document_text)

        metadatas = [{"document_id": str(document_id)} for _ in chunks]

        chunk_ids = [f"{document_id}_{i}" for i, _ in enumerate(chunks)]

        self.collection.add(
            ids=chunk_ids,
            documents=chunks,
            metadatas=metadatas
        )

    def query(self, question: str, document_ids: list[int], llm_config: dict) -> str:
        """
        Performs a RAG query using a dynamically configured LLM chain.
        """
        where_filter = {"document_id": {"$in": [str(doc_id) for doc_id in document_ids]}}
        results = self.collection.query(
            query_texts=[question],
            n_results=5,
            where=where_filter
        )
        retrieved_docs = results['documents'][0]
        if not retrieved_docs:
            return "I could not find any relevant information in the selected documents."
        context = "\n\n---\n\n".join(retrieved_docs)

        try:
            llm_chain = self._get_llm_chain(llm_config)
            answer = llm_chain.invoke({"context": context, "question": question})
            return answer['text']
        except Exception as e:
            return f"Error during LLM query: {e}"

    def delete_document(self, document_id: int):
        """
        Deletes all chunks associated with a document from the vector store.

        Args:
            document_id (int): The ID of the document to delete.
        """
        self.collection.delete(where={"document_id": str(document_id)})

# Example Usage (for testing)
if __name__ == '__main__':
    rag_system = RAGSystem()

    openai_llm_config = {"type": "openai", "model_name": "gpt-3.5-turbo", "api_key_env": "OPENAI_API_KEY"}

    doc1_text = "The sky is blue. The grass is green."
    doc2_text = "Photosynthesis is the process by which green plants use sunlight to synthesize foods."
    rag_system.process_document(document_id=1, document_text=doc1_text)
    rag_system.process_document(document_id=2, document_text=doc2_text)

    query1 = "What color is the sky?"
    answer1 = rag_system.query(question=query1, document_ids=[1], llm_config=openai_llm_config)
    print(f"Question: {query1}\nAnswer: {answer1}\n")

    query2 = "What is photosynthesis?"
    answer2 = rag_system.query(question=query2, document_ids=[2], llm_config=openai_llm_config)
    print(f"Question: {query2}\nAnswer: {answer2}\n")

    query3 = "What is photosynthesis?"
    answer3 = rag_system.query(question=query3, document_ids=[1], llm_config=openai_llm_config)
    print(f"Question: {query3} (from wrong doc)\nAnswer: {answer3}\n")

    rag_system.delete_document(document_id=1)
    answer4 = rag_system.query(question=query1, document_ids=[1], llm_config=openai_llm_config)
    print(f"Question: {query1} (after deletion)\nAnswer: {answer4}\n")
