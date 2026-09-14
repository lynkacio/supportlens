'use client';

import { useState, type FormEvent } from 'react';
import PageContainer from "@/components/PageContainer";
import { API_BASE_URL } from "../../lib/api";

export default function QueryPage() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setAnswer('');

    try {
      const res = await fetch(`${API_BASE_URL}/api/tickets/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setAnswer(data.answer);
    } catch (err) {
      setAnswer('AI query request failed, please check the backend service.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main>
      <PageContainer>
        <h1 className="text-3xl font-bold mb-2">Ask AI</h1>
        <p className="text-gray-500 mb-8">
          Ask the AI questions in natural language to quickly retrieve and analyze ticket data.
        </p>

        <form onSubmit={handleSubmit} className="mb-8 flex gap-4">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g. What are the recent high-priority billing issues?"
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Thinking...' : 'Send'}
          </button>
        </form>

        {answer && (
          <div className="bg-white p-6 rounded-xl shadow border border-gray-100">
            <h3 className="font-semibold text-gray-700 mb-2">AI Answer</h3>
            <p className="text-gray-800 whitespace-pre-wrap">{answer}</p>
          </div>
        )}
      </PageContainer>
    </main>
  );
}