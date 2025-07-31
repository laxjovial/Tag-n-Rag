import os
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.chains import LLMChain

class RAGSystem:
    def __init__(self, config=None):
        """
        Initializes the RAG system.

        Args:
            config (dict): A dictionary with configuration options.
                           For now, this is a placeholder.
        """
        self.config = config or {}

        # 1. Initialize the embedding model
        self.embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

        # 2. Initialize the vector store (ChromaDB)
        # Using a local, in-memory instance for now.
        # For persistence, you can run a ChromaDB server and use:
        # self.client = chromadb.HttpClient(host='localhost', port=8000)
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(name="rag_documents")

        # 3. Initialize Langchain components (placeholders for now)
        # In a real scenario, the model would be loaded based on the user's selection
        self.llm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo") # Placeholder

        self.prompt_template = PromptTemplate(
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

        self.llm_chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

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

        # Create metadata for each chunk
        metadatas = [{"document_id": str(document_id)} for _ in chunks]

        # Generate unique IDs for each chunk
        chunk_ids = [f"{document_id}_{i}" for i, _ in enumerate(chunks)]

        # Add chunks to the collection
        self.collection.add(
            ids=chunk_ids,
            documents=chunks,
            metadatas=metadatas
        )

    def query(self, question: str, document_ids: list[int]):
        """
        Performs a RAG query on a set of documents.

        Args:
            question (str): The user's question.
            document_ids (list[int]): A list of document IDs to search within.

        Returns:
            str: The generated answer.
        """
        # 1. Retrieve relevant document chunks
        # ChromaDB filters on metadata. We'll filter by the document_ids.
        where_filter = {"document_id": {"$in": [str(doc_id) for doc_id in document_ids]}}

        results = self.collection.query(
            query_texts=[question],
            n_results=5, # Get the top 5 most relevant chunks
            where=where_filter
        )

        retrieved_docs = results['documents'][0]

        if not retrieved_docs:
            return "I could not find any relevant information in the selected documents."

        context = "\n\n---\n\n".join(retrieved_docs)

        # 2. Generate an answer using the LLM
        answer = self.llm_chain.run({"context": context, "question": question})

        return answer

    def delete_document(self, document_id: int):
        """
        Deletes all chunks associated with a document from the vector store.

        Args:
            document_id (int): The ID of the document to delete.
        """
        self.collection.delete(where={"document_id": str(document_id)})

# Example Usage (for testing)
if __name__ == '__main__':
    # This part will not run when imported, but is useful for direct testing.
    rag_system = RAGSystem()

    # 1. Process a couple of documents
    doc1_text = "The sky is blue. The grass is green."
    doc2_text = "Photosynthesis is the process by which green plants use sunlight to synthesize foods."
    rag_system.process_document(document_id=1, document_text=doc1_text)
    rag_system.process_document(document_id=2, document_text=doc2_text)

    # 2. Query the documents
    query1 = "What color is the sky?"
    answer1 = rag_system.query(question=query1, document_ids=[1])
    print(f"Question: {query1}\nAnswer: {answer1}\n")

    query2 = "What is photosynthesis?"
    answer2 = rag_system.query(question=query2, document_ids=[2])
    print(f"Question: {query2}\nAnswer: {answer2}\n")

    query3 = "What is photosynthesis?"
    answer3 = rag_system.query(question=query3, document_ids=[1]) # Querying the wrong doc
    print(f"Question: {query3} (from wrong doc)\nAnswer: {answer3}\n")

    # 3. Delete a document
    rag_system.delete_document(document_id=1)
    answer4 = rag_system.query(question=query1, document_ids=[1])
    print(f"Question: {query1} (after deletion)\nAnswer: {answer4}\n")
