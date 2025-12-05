# AI Interview Bot - REST API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints

### 1. Start Interview
**POST** `/api/interview/start`

Start a new interview session.

**Request Body:**
```json
{
  "mode": "role",
  "content": "Senior Python Developer",
  "session_id": "optional-custom-id"
}
```

**Response:**
```json
{
  "session_id": "session_1234567890",
  "first_question": "Tell me about yourself",
  "message": "Interview started successfully"
}
```

---

### 2. Submit Answer
**POST** `/api/interview/answer`

Submit an answer and receive feedback + next question.

**Request Body:**
```json
{
  "session_id": "session_1234567890",
  "answer": "I have 5 years of experience in Python development..."
}
```

**Response:**
```json
{
  "feedback": "Good answer! You demonstrated...",
  "next_question": "Can you explain decorators in Python?",
  "is_followup": false,
  "interview_complete": false,
  "final_feedback": null
}
```

---

### 3. Transcribe Audio
**POST** `/api/interview/transcribe`

Upload audio file and get transcription.

**Request:**
- Content-Type: `multipart/form-data`
- Field: `audio` (file upload)

**Response:**
```json
{
  "transcription": "I have experience with Python and Django..."
}
```

---

### 4. Get Session Status
**GET** `/api/interview/status/{session_id}`

Get current interview session information.

**Response:**
```json
{
  "session_id": "session_1234567890",
  "mode": "role",
  "question_count": 3,
  "total_exchanges": 5,
  "current_question": "Explain async/await in Python",
  "interview_active": true
}
```

---

### 5. End Interview
**DELETE** `/api/interview/end/{session_id}`

End interview and get final feedback.

**Response:**
```json
{
  "message": "Interview ended",
  "final_feedback": "Overall, you demonstrated strong...",
  "total_questions": 10
}
```

---

## Installation & Running

### 1. Install Dependencies
```bash
pip install -r requirements_api.txt
```

### 2. Set Environment Variables
Create `.env` file:
```
GEMINI_API_KEY=your-api-key-here
```

### 3. Run Server
```bash
python api_server.py
```

Or with uvicorn:
```bash
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Frontend Integration Example

### JavaScript/React Example

```javascript
// Start interview
const startInterview = async () => {
  const response = await fetch('http://localhost:8000/api/interview/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      mode: 'role',
      content: 'Senior Python Developer'
    })
  });
  const data = await response.json();
  console.log(data.first_question);
  return data.session_id;
};

// Submit answer
const submitAnswer = async (sessionId, answer) => {
  const response = await fetch('http://localhost:8000/api/interview/answer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      answer: answer
    })
  });
  return await response.json();
};

// Transcribe audio
const transcribeAudio = async (audioBlob) => {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.wav');
  
  const response = await fetch('http://localhost:8000/api/interview/transcribe', {
    method: 'POST',
    body: formData
  });
  return await response.json();
};
```

---

## Production Deployment

### Security Considerations
1. Update CORS origins to your frontend domain
2. Add authentication/authorization
3. Use HTTPS
4. Rate limiting
5. Use database instead of in-memory sessions

### Recommended Stack
- **Database**: PostgreSQL/MongoDB for session storage
- **Cache**: Redis for session management
- **Deployment**: Docker + AWS/GCP/Azure
- **Load Balancer**: Nginx

---

## Error Responses

All errors follow this format:
```json
{
  "detail": "Error message here"
}
```

**Common Status Codes:**
- `200` - Success
- `400` - Bad Request
- `404` - Session Not Found
- `500` - Internal Server Error
