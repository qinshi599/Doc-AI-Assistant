// 🎯 简化版 langchainController.js

import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Ask question with LangChain
async function askQuestion(question) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    
    const pythonProcess = spawn('python3', ['scripts/langchain_rag.py', question], {
      cwd: path.join(__dirname, '../../..'),
      env: { ...process.env }
    });

    let output = '';

    pythonProcess.stdout.on('data', (data) => {
      output += data.toString();
    });

    pythonProcess.on('close', (code) => {
      const processingTime = Date.now() - startTime;
      
      if (code !== 0) {
        reject(new Error('Python process failed'));
        return;
      }

      try {
        const lines = output.trim().split('\n');
        const jsonLine = lines[lines.length - 1];
        const result = JSON.parse(jsonLine);
        
        console.log(`✅ AI answered in ${processingTime}ms`);
        resolve(result);
      } catch (error) {
        reject(new Error('Failed to parse AI response'));
      }
    });
  });
}

// API endpoint
const askQuestionWithLangChain = async (req, res) => {
  try {
    const { question } = req.body;
    
    if (!question) {
      return res.status(400).json({ error: 'Question is required' });
    }

    const result = await askQuestion(question);
    res.json({
      ...result,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('❌ Error:', error.message);
    res.status(500).json({ 
      error: 'Internal server error',
      message: error.message 
    });
  }
};

// Simplified health check
const healthCheck = (req, res) => {
  res.json({
    status: 'OK',
    system: 'LangChain RAG',
    timestamp: new Date().toISOString()
  });
};

export { askQuestionWithLangChain, healthCheck };
