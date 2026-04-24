import axios from 'axios';

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});

export async function sendMessage(sessionId, message) {
  const { data } = await client.post('/api/chat', {
    session_id: sessionId,
    message,
  });
  return data;
}
