#!/usr/bin/env python3

import os
import logging
from typing import List
from dotenv import load_dotenv

# LangChain imports
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

# Load environment and configure logging
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Simplified document processor with essential functionality only"""
    
    def __init__(self, max_pages: int = 50, chunk_size: int = 500, chunk_overlap: int = 50):
        self.max_pages = max_pages
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Document URL mapping for citations
        self.doc_urls = {
            "troubleshoot-azure-virtual-machines-windows": "https://learn.microsoft.com/azure/virtual-machines/troubleshooting",
            "windows-server-identity": "https://learn.microsoft.com/windows-server/identity", 
            "security-operations": "https://learn.microsoft.com/security/operations",
            "troubleshoot-microsoft-365-admintoc": "https://learn.microsoft.com/microsoft-365/admin"
        }
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", "!", "?", ";", ":", " ", ""]
        )
        
        logger.info("✅ Document processor initialized")

    def _classify_doc_type(self, doc_name: str) -> str:
        """Classify document type based on filename"""
        name = doc_name.lower()
        if "troubleshoot" in name: return "Troubleshooting"
        elif "identity" in name: return "Authentication"
        elif "security" in name: return "Security"
        elif "admin" in name: return "Administration"
        else: return "General"

    def process_pdf(self, pdf_path: str) -> List[Document]:
        """Process single PDF file into chunks"""
        doc_name = os.path.basename(pdf_path).replace(".pdf", "")
        
        # Load PDF
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        
        # Limit pages for demo
        if len(pages) > self.max_pages:
            pages = pages[:self.max_pages]
            logger.info(f"📄 Limited to first {self.max_pages} pages")
        
        # Split into chunks
        chunks = self.text_splitter.split_documents(pages)
        
        # Add metadata for each chunk
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                'doc_name': doc_name,
                'doc_type': self._classify_doc_type(doc_name),
                'doc_url': self.doc_urls.get(doc_name, ""),
                'page_number': chunk.metadata.get('page', 0) + 1,
                'chunk_id': i
            })
        return chunks

    def process_all_documents(self, docs_dir: str = "data/demo_docs") -> List[Document]:
        """Process all PDF files in directory"""
        logger.info(f"📂 Processing documents in: {docs_dir}")
        
        if not os.path.exists(docs_dir):
            raise FileNotFoundError(f"Directory not found: {docs_dir}")
        
        pdf_files = [f for f in os.listdir(docs_dir) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            raise FileNotFoundError(f"No PDF files found in {docs_dir}")
        
        logger.info(f"📄 Found {len(pdf_files)} PDF files")
        
        all_chunks = []
        for pdf_file in pdf_files:
            pdf_path = os.path.join(docs_dir, pdf_file)
            chunks = self.process_pdf(pdf_path)
            all_chunks.extend(chunks)
        
        logger.info(f"🎉 Total processed: {len(all_chunks)} chunks from {len(pdf_files)} documents")
        return all_chunks

def setup_vectorstore():
    """Main setup function - process documents and create vector store"""
    logger.info("🚀 Starting ITDoc AI Assistant setup")
    
    try:
        # 1. Initialize processor
        processor = DocumentProcessor(max_pages=50)
        
        # 2. Process all documents
        all_chunks = processor.process_all_documents("data/demo_docs")
        
        # 3. Initialize embeddings
        logger.info("Initializing embeddings...")
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large",
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # 4. Create vector store
        index_name = os.getenv('PINECONE_INDEX_NAME')
        logger.info(f"🔄 Creating vector store with {len(all_chunks)} chunks...")
        
        vectorstore = PineconeVectorStore.from_documents(
            documents=all_chunks,
            embedding=embeddings,
            index_name=index_name
        )
        
        logger.info(f"✅ Vector store created successfully!")
        logger.info(f"📊 Summary:")
        logger.info(f"  - Documents processed: {len(set(chunk.metadata['doc_name'] for chunk in all_chunks))}")
        logger.info(f"  - Total chunks: {len(all_chunks)}")
        logger.info(f"  - Pinecone index: {index_name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return False

def main():
    """Main function"""
    print("🚀 ITDoc AI Assistant - Vector Store Setup")
    print("=" * 50)
    
    # Check environment
    required_vars = ['OPENAI_API_KEY', 'PINECONE_API_KEY', 'PINECONE_INDEX_NAME']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
        return 1
    
    # Run setup
    success = setup_vectorstore()
    
    if success:
        print("\n🎉 Setup complete!")
        print("✅ Now you can test the RAG system:")
        print("   python3 scripts/langchain_rag.py")
        return 0
    else:
        print("\n❌ Setup failed!")
        return 1

if __name__ == "__main__":
    exit(main())
