#!/usr/bin/env python3
"""
LangChain-based RAG System for ITDoc AI Assistant
Advanced RAG implementation with conversation memory and custom prompts
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional
import logging
from dotenv import load_dotenv

# LangChain imports
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.messages import HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LangChainRAGSystem:
    def __init__(self, index_name: str = None, model_name: str = "gpt-3.5-turbo"):
        """
        Initialize LangChain RAG system
        
        Args:
            index_name: Pinecone index name
            model_name: OpenAI model to use
        """
        self.index_name = index_name or os.getenv('PINECONE_INDEX_NAME')
        self.model_name = model_name
        
        # Allowed documents for filtering
        self.allowed_docs = [
            "troubleshoot-azure-virtual-machines-windows",
            "windows-server-identity", 
            "security-operations",
            "troubleshoot-microsoft-365-admintoc"
        ]
        
        # Initialize components
        self._init_embeddings()
        self._init_llm()
        self._init_vectorstore()
        self._init_prompts()
        self._init_memory()
        self._build_rag_chain()
        
        logger.info("✅ LangChain RAG System initialized")

    def _init_embeddings(self):
        """Initialize OpenAI embeddings"""
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large",
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        logger.info("🧠 Embeddings initialized")

    def _init_llm(self):
        """Initialize ChatOpenAI LLM"""
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=0.3,
            max_tokens=800,
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        logger.info(f"🤖 LLM initialized: {self.model_name}")

    def _init_vectorstore(self):
        """Initialize Pinecone vectorstore"""
        try:
            self.vectorstore = PineconeVectorStore(
                index_name=self.index_name,
                embedding=self.embeddings
            )
            
            # Create retriever with filtering
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={
                    "k": 10, # number of documents to retrieve
                    "filter": {"doc_name": {"$in": self.allowed_docs}}
                }
            )
            logger.info(f"🗄️ Vectorstore connected: {self.index_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to vectorstore: {e}")
            raise

    def _init_prompts(self):
        """Initialize custom prompts"""
        # System prompt for RAG
        self.system_prompt = """You are a professional IT documentation assistant. Answer questions strictly based on the provided context. 
        If information is insufficient, reply "No relevant documentation found. Do not make up information."

**Rules**:
1. All answers must be based on the provided context, do not fabricate information
2. Reply in English, maintain technical accuracy but be user-friendly
3. Provide detailed operational steps and practical examples
4. Format your answer clearly with proper line breaks and structure
5. Use numbered lists for step-by-step instructions
6. Use bullet points for additional details under each step

**Context**:
{context}

**Question**: {question}"""

        # Create chat prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{question}")
        ])
        
        logger.info("📝 Prompts initialized")

    # Initialize conversation memory
    def _init_memory(self):
        """Initialize conversation memory"""
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        logger.info("Memory initialized")

    def _build_rag_chain(self):
        """Build the RAG chain using LangChain LCEL"""
        # Create context retrieval chain
        def format_docs(docs):
            """Format retrieved documents for context"""
            formatted = []
            for doc in docs:
                doc_name = doc.metadata.get('doc_name', 'Unknown Document')
                page = doc.metadata.get('page_number', 'Unknown Page')
                doc_url = doc.metadata.get('doc_url', '')
                content = doc.page_content
                
                formatted.append(f"[Document]: {doc_name}\n[Page]: {page}\n[URL]: {doc_url}\n[Content]: {content}")
            
            return "\n\n---\n\n".join(formatted)

        # Build the RAG chain
        self.rag_chain = (
            RunnableParallel({
                "context": self.retriever | format_docs,
                "question": RunnablePassthrough(),
                "chat_history": lambda x: self.memory.chat_memory.messages
            })
            | self.prompt_template
            | self.llm
            | StrOutputParser()
        )
        
        logger.info("⛓️ RAG chain built")

    def ask_question(self, question: str) -> Dict[str, Any]:
        """
        Ask a question and get an answer from the RAG system
        
        Args:
            question: User question
            
        Returns:
            Dictionary with answer and metadata
        """
        logger.info(f"Processing question: {question}")
        
        try:
            # Get relevant documents first for metadata
            docs = self.retriever.invoke(question)
            
            if not docs:
                return {
                    "question": question,
                    "answer": "No relevant documentation found",
                    "sources": [],
                    "confidence": "0%"
                }
            
            # Generate answer using RAG chain
            answer = self.rag_chain.invoke(question)
            
            # Update memory
            self.memory.chat_memory.add_user_message(question)
            self.memory.chat_memory.add_ai_message(answer)
            
            # Format sources
            document_titles = {
                "troubleshoot-azure-virtual-machines-windows": "Azure Virtual Machine Troubleshooting Guide",
                "windows-server-identity": "Windows Server Identity & Authentication",
                "security-operations": "Microsoft Security Operations Guide", 
                "troubleshoot-microsoft-365-admintoc": "Microsoft 365 Administration Guide"
            }

            references = []
            seen_urls = set()

            for doc in docs[:3]:  # Top 3 sources
                url = doc.metadata.get('doc_url', '')
                doc_name = doc.metadata.get('doc_name', 'Unknown Document')
                
                # Only keep unique URLs
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    title = document_titles.get(doc_name, "Microsoft Technical Documentation")
                    references.append({
                        "title": title,
                        "url": url
                    })

            result = {
                "question": question,
                "answer": answer,
                "references": references 
            }
            
            logger.info("✅ Answer generated successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to process question: {e}")
            return {
                "question": question,
                "answer": f"Error processing question: {str(e)}",
                "sources": [],
                "confidence": "0%"
            }

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        history = []
        messages = self.memory.chat_memory.messages
        
        for i in range(0, len(messages), 2):
            if i + 1 < len(messages):
                history.append({
                    "question": messages[i].content,
                    "answer": messages[i + 1].content
                })
        
        return history

    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()
        logger.info("🧹 Memory cleared")

    def test_retrieval(self, query: str = "How to troubleshoot Azure VM startup failures?", k: int = 3):
        """Test document retrieval"""
        logger.info(f"🔍 Testing retrieval with: '{query}'")
        
        try:
            docs = self.retriever.invoke(query)
            
            print(f"\n🔍 Retrieval Results (Found {len(docs)} documents):")
            print("=" * 60)
            
            for i, doc in enumerate(docs[:k]):
                print(f"\n📄 Document {i+1}:")
                print(f"  📖 Name: {doc.metadata.get('doc_name', 'Unknown')}")
                print(f"  📄 Page: {doc.metadata.get('page_number', 'Unknown')}")
                print(f"  🔗 URL: {doc.metadata.get('doc_url', 'Unknown')}")
                print(f"  📝 Preview: {doc.page_content[:150]}...")
            
            return docs
            
        except Exception as e:
            logger.error(f"❌ Retrieval test failed: {e}")
            return []

def main():
    """Main function for testing RAG system"""
    print("🚀 LangChain RAG System Test")
    print("=" * 50)
    
    try:
        # Initialize RAG system
        rag = LangChainRAGSystem()
        
        # Test retrieval
        print("\n1.Testing Document Retrieval:")
        rag.test_retrieval()
        
        # Test Q&A
        print("\n2. Testing Q&A System:")
        test_questions = [
            "How to troubleshoot Azure VM startup failures?",
            "How to configure Windows domain authentication?",
            "How can M365 administrators reset user passwords?"
        ]
        
        for question in test_questions:
            print(f"\n❓ Question: {question}")
            result = rag.ask_question(question)
            print(f"💬 Answer: {result['answer'][:200]}...")
            print(f"🎯 Confidence: {result['confidence']}")
            print(f"📚 Source Count: {len(result['sources'])}")
        
        # Show conversation history
        print("\n3.Conversation History:")
        history = rag.get_conversation_history()
        print(f"📝 Conversation Rounds: {len(history)}")
        
        print("\n🎉 RAG System Test Complete!")
        
    except Exception as e:
        print(f"❌ Test Failed: {e}")
        return 1
    
    return 0

def api_mode():
    """API mode for Node.js integration"""
    import sys
    
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: python langchain_rag.py '<question>'"}, ensure_ascii=False))
        return 1
    
    question = sys.argv[1]
    
    try:
        # Initialize RAG system
        rag = LangChainRAGSystem()
        
        # Get answer
        result = rag.ask_question(question)
        
        # Output as JSON
        print(json.dumps(result, ensure_ascii=False))
        return 0
        
    except Exception as e:
        error_result = {
            "question": question,
            "answer": f"Error processing question: {str(e)}",
            "sources": [],
            "confidence": "0%"
        }
        print(json.dumps(error_result, ensure_ascii=False))
        return 1

if __name__ == "__main__":
    # Check if running in API mode (with command line argument)
    if len(sys.argv) == 2:
        exit(api_mode())
    else:
        # Run test mode
        exit(main())
