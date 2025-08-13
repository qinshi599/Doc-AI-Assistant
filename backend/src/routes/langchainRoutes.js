import express from 'express';
import { askQuestionWithLangChain, healthCheck } from '../controllers/langchainController.js';

const router = express.Router();

// LangChain-powered Q&A endpoint
router.post('/ask-langchain', askQuestionWithLangChain);

// Health check for LangChain system
router.get('/health-langchain', healthCheck);

export default router;
