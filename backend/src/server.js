import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import langchainRoutes from './routes/langchainRoutes.js';

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Request logging middleware
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// Routes
app.use('/api', langchainRoutes);

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    message: 'ITDoc AI Assistant API is running',
    timestamp: new Date().toISOString()
  });
});

// Root path
app.get('/', (req, res) => {
  res.json({
    message: 'ITDoc AI Assistant API',
    version: '1.0.0',
    endpoints: {
      health: '/health',
      'ask-langchain': '/api/ask-langchain'
    }
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('❌ Server error:', err);
  res.status(500).json({ 
    error: 'Internal server error',
    message: err.message 
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(` ITDoc AI Assistant API ready`);
  console.log(`Health check: http://localhost:${PORT}/health`);
});