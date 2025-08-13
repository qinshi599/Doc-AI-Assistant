# 🤖 ITDoc AI Assistant

Hey there, this is Nora! 👋 So this is my AI chatbot that I built to answer IT questions. The questions you're gonna ask depend on the docs you feed into it, and yes, it will not be like a general chatbot that gives you vague answers!

You can imagine it as an expert in a specific field. Eventually, I want to use it as a company internal chatbot to service the staff, saving their time from searching through heaps of docs and guides! 

**Use Case 1:** 
You are an IT support newbie and you still need to learn a lot of new things. There are always some problems you can help your customers with, but you may not be able to find the answer in the docs quickly - here we are!

**Use Case 2:** 
You just joined a big company, and you went on a business trip. You have no idea what the process is to get reimbursed, or you want to know what the benefits for employees are - here we are! 

**Use Case 3:** 
Want to become a trivia master? I'll build a comprehensive knowledge base where all your questions can get authoritative answers! 

## What does it do?

It's pretty simple - you ask it questions about IT stuff (limited to Azure, Windows Server, M365, Security in this demo), and it gives you answers based on actual Microsoft documentation. No more "have you tried turning it off and on again?" responses! 😅

https://github.com/qinshi599/Doc-AI-Assistant/blob/main/demo.mov
## 🛠️ Tech Stack

I went with:
- **LangChain** for the RAG (Retrieval Augmented Generation) magic
- **OpenAI API** for the actual AI brains
- **Pinecone** to store document vectors (fancy database for AI)
- **Node.js** for the backend API
- **Simple HTML/CSS/JS** for the frontend (keeping it real!)

## 🚀 Quick Start

### 1. Clone this bad boy
```bash
git clone https://github.com/yourusername/itdoc-ai-assistant.git
cd itdoc-ai-assistant
```

### 2. Set up your API keys
```bash
# Copy the example file
cp env_example.txt .env

# Edit .env and add your keys:
# - OpenAI API key (get from https://openai.com)
# - Pinecone API key (get from https://pinecone.io)
```

### 3. Run the setup (this might take a few minutes)
```bash
# This will process documents and start the server
./run_demo.sh --setup
```

### 4. Test it out!
Open `frontend/index.html` in your browser, or test the API:

```bash
curl -X POST http://localhost:3001/api/ask-langchain \
  -H "Content-Type: application/json" \
  -d '{"question": "How to troubleshoot Azure VM startup failures?"}'
```

## 📁 What's in here?

```
itdoc-ai-assistant/
├── backend/               # Node.js API server
├── frontend/              # Simple chat interface
├── scripts/               # Python AI magic
│   ├── langchain_rag.py      # The main AI brain
│   └── setup_vectorstore.py  # Document processor
├── data/demo_docs/        # Microsoft IT PDFs
├── run_demo.sh           # One-click startup
└── requirements.txt      # Python dependencies
```

I tried to keep it simple - no overcomplicated folder structures here!

## 💬 What can you ask it?

Try these:
- "How to troubleshoot Azure VM startup failures?"
- "How to reset M365 user password?"
- "What are best practices for M365 security?"
- "How to configure Windows domain authentication?"

It knows about:
- 🔵 Azure Virtual Machines
- 🪟 Windows Server stuff
- 🛡️ Microsoft Security
- 📧 Microsoft 365 administration

## 🎨 Features

- **Clean interface**
- **Source citations** - tells you where the info comes from
- **Fast responses** - usually under 3 seconds
- **Real documentation** - no more made-up answers!

## 🧠 How it works

1. **Document Processing**: I fed it 4 Microsoft IT guides (~1000 pages)
2. **Vector Magic**: It breaks everything into chunks and creates "embeddings"
3. **Smart Search**: When you ask something, it finds relevant chunks
4. **AI Generation**: GPT reads those chunks and gives you a proper answer
5. **Citations**: It shows you exactly where the info came from

Pretty neat, right?

## 🚧 Known Issues

- Sometimes it might not find info if you ask in a weird way
- The document processing takes a while the first time
- It's focused on Microsoft stuff only (by design)

## 🔮 Future ideas

If I get motivated:
- [ ] Add more document types
- [ ] Real-time streaming responses
- [ ] Better mobile interface
- [ ] Document upload feature
- [ ] Maybe a proper React frontend?

## 🤝 Contributing

Found a bug? Have an idea? Feel free to open an issue or PR. I'm pretty responsive (usually).

## 📝 License

MIT - do whatever you want with it!

## 🙏 Thanks

- OpenAI for making this stuff accessible
- LangChain team for the awesome framework
- Microsoft for the comprehensive docs (even if they're hard to search)

---

**P.S.** If you're using this for work, maybe don't tell your boss how much time you're saving 😉
