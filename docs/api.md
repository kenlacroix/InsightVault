# 🔌 API Reference

This document provides detailed information about the InsightVault backend API endpoints, request/response formats, and authentication.

## 🔐 Authentication

InsightVault uses API key authentication for securing endpoints.

### API Key Setup

1. **Generate API Key**: Create a secure API key for your application
2. **Include in Headers**: Add the key to all API requests
3. **Environment Variable**: Store the key in `backend/.env`

```bash
# In backend/.env
API_KEY=your-secure-api-key-here
```

### Request Headers

Include the API key in all requests:

```http
X-API-Key: your-secure-api-key-here
Content-Type: application/json
```

## 📡 Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## 🔗 Endpoints

### File Management

#### Upload File

Upload ChatGPT conversation files for processing.

```http
POST /api/files/upload
```

**Request:**

- **Content-Type**: `multipart/form-data`
- **Body**: Form data with file field

```bash
curl -X POST "http://localhost:8000/api/files/upload" \
  -H "X-API-Key: your-api-key" \
  -F "file=@conversations.json"
```

**Response:**

```json
{
  "success": true,
  "file_id": "uuid-string",
  "filename": "conversations.json",
  "size": 1024000,
  "message": "File uploaded successfully"
}
```

#### List Files

Get a list of uploaded files.

```http
GET /api/files/list
```

**Response:**

```json
{
  "files": [
    {
      "id": "uuid-string",
      "filename": "conversations.json",
      "size": 1024000,
      "uploaded_at": "2024-01-15T10:30:00Z",
      "status": "uploaded"
    }
  ]
}
```

#### Delete File

Remove a file from the system.

```http
DELETE /api/files/{file_id}
```

**Response:**

```json
{
  "success": true,
  "message": "File deleted successfully"
}
```

### Conversation Processing

#### Process Conversations

Parse and process uploaded conversation files.

```http
POST /api/chat/process
```

**Request:**

```json
{
  "file_id": "uuid-string",
  "options": {
    "generate_summaries": true,
    "extract_tags": true,
    "analyze_sentiment": true
  }
}
```

**Response:**

```json
{
  "success": true,
  "conversations_processed": 25,
  "processing_time": 45.2,
  "message": "Conversations processed successfully"
}
```

#### List Conversations

Get all processed conversations with optional filtering.

```http
GET /api/chat/conversations
```

**Query Parameters:**

- `limit` (int): Number of conversations to return (default: 50)
- `offset` (int): Number of conversations to skip (default: 0)
- `search` (string): Search term for conversation content
- `tags` (string): Comma-separated list of tags to filter by
- `date_from` (string): Start date (ISO format)
- `date_to` (string): End date (ISO format)

**Response:**

```json
{
  "conversations": [
    {
      "id": "uuid-string",
      "title": "Discussion about anxiety and mindfulness",
      "summary": "A deep conversation about managing anxiety through mindfulness practices...",
      "tags": ["anxiety", "mindfulness", "mental-health"],
      "created_at": "2024-01-10T14:30:00Z",
      "message_count": 15,
      "sentiment_score": 0.7
    }
  ],
  "total": 25,
  "limit": 50,
  "offset": 0
}
```

#### Get Conversation Details

Get detailed information about a specific conversation.

```http
GET /api/chat/conversations/{conversation_id}
```

**Response:**

```json
{
  "id": "uuid-string",
  "title": "Discussion about anxiety and mindfulness",
  "summary": "A deep conversation about managing anxiety through mindfulness practices...",
  "tags": ["anxiety", "mindfulness", "mental-health"],
  "created_at": "2024-01-10T14:30:00Z",
  "messages": [
    {
      "id": "msg-1",
      "role": "user",
      "content": "I've been feeling really anxious lately...",
      "timestamp": "2024-01-10T14:30:00Z"
    },
    {
      "id": "msg-2",
      "role": "assistant",
      "content": "I understand you're going through a difficult time...",
      "timestamp": "2024-01-10T14:31:00Z"
    }
  ],
  "metadata": {
    "message_count": 15,
    "sentiment_score": 0.7,
    "topics": ["anxiety", "mindfulness", "breathing"],
    "emotions": ["concern", "hope", "relief"]
  }
}
```

### AI Analysis

#### Generate Summaries

Generate AI-powered summaries for conversations.

```http
POST /api/chat/summarize
```

**Request:**

```json
{
  "conversation_ids": ["uuid-1", "uuid-2"],
  "options": {
    "include_tags": true,
    "include_sentiment": true,
    "summary_length": "medium"
  }
}
```

**Response:**

```json
{
  "summaries": [
    {
      "conversation_id": "uuid-1",
      "title": "AI-generated title",
      "summary": "AI-generated summary...",
      "tags": ["tag1", "tag2"],
      "sentiment": "positive",
      "confidence": 0.85
    }
  ],
  "processing_time": 12.5
}
```

#### Generate Insights

Generate deep insights from conversations based on user questions.

```http
POST /api/chat/insights
```

**Request:**

```json
{
  "question": "How have I grown spiritually over time?",
  "conversation_ids": ["uuid-1", "uuid-2", "uuid-3"],
  "options": {
    "include_quotes": true,
    "include_timeline": true,
    "analysis_depth": "deep"
  }
}
```

**Response:**

```json
{
  "insight": {
    "question": "How have I grown spiritually over time?",
    "analysis": "Based on your conversations, I can see a clear evolution in your spiritual journey...",
    "key_insights": [
      "You've developed a consistent meditation practice",
      "Your understanding of mindfulness has deepened",
      "You've become more comfortable with uncertainty"
    ],
    "quotes": [
      {
        "text": "I've learned that meditation isn't about clearing my mind...",
        "conversation_id": "uuid-1",
        "timestamp": "2024-01-10T14:30:00Z"
      }
    ],
    "timeline": [
      {
        "period": "Early 2023",
        "insight": "Beginning of spiritual exploration",
        "conversations": ["uuid-1"]
      }
    ],
    "recommendations": [
      "Continue your daily meditation practice",
      "Explore different spiritual traditions",
      "Document your spiritual insights regularly"
    ]
  },
  "processing_time": 25.3,
  "conversations_analyzed": 3
}
```

#### Search Conversations

Search conversations using semantic and keyword search.

```http
GET /api/chat/search
```

**Query Parameters:**

- `q` (string): Search query (required)
- `type` (string): Search type - "semantic" or "keyword" (default: "semantic")
- `limit` (int): Number of results (default: 20)
- `offset` (int): Number of results to skip (default: 0)
- `include_content` (boolean): Include message content in results (default: false)

**Response:**

```json
{
  "results": [
    {
      "conversation_id": "uuid-string",
      "title": "Discussion about anxiety and mindfulness",
      "relevance_score": 0.95,
      "matched_messages": [
        {
          "id": "msg-1",
          "content": "I've been feeling really anxious lately...",
          "highlight": "feeling really <em>anxious</em> lately"
        }
      ],
      "tags": ["anxiety", "mindfulness"],
      "created_at": "2024-01-10T14:30:00Z"
    }
  ],
  "total": 5,
  "query": "anxiety management",
  "search_type": "semantic"
}
```

### Chat Interface

#### Send Message

Send a message to the AI assistant for real-time conversation.

```http
POST /api/chat/send
```

**Request:**

```json
{
  "message": "How have I grown spiritually over time?",
  "context": {
    "conversation_ids": ["uuid-1", "uuid-2"],
    "include_history": true
  }
}
```

**Response:**

```json
{
  "response": "Based on your conversations, I can see a clear evolution in your spiritual journey...",
  "conversation_id": "chat-uuid",
  "timestamp": "2024-01-15T10:30:00Z",
  "processing_time": 3.2
}
```

#### Stream Chat Response

Get streaming responses for real-time chat experience.

```http
POST /api/chat/send-stream
```

**Request:** Same as `/api/chat/send`

**Response:** Server-Sent Events (SSE) stream

```
data: {"type": "status", "message": "Processing your question..."}
data: {"type": "status", "message": "Analyzing conversations..."}
data: {"type": "response", "content": "Based on your conversations..."}
data: {"type": "complete", "conversation_id": "chat-uuid"}
```

### Analytics

#### Get Analytics

Get analytics and insights about your conversations.

```http
GET /api/analytics/overview
```

**Query Parameters:**

- `date_from` (string): Start date (ISO format)
- `date_to` (string): End date (ISO format)
- `group_by` (string): Grouping - "day", "week", "month" (default: "month")

**Response:**

```json
{
  "total_conversations": 150,
  "total_messages": 2500,
  "date_range": {
    "from": "2023-01-01",
    "to": "2024-01-15"
  },
  "conversations_over_time": [
    {
      "date": "2024-01",
      "count": 25,
      "messages": 400
    }
  ],
  "top_tags": [
    { "tag": "anxiety", "count": 45 },
    { "tag": "mindfulness", "count": 38 }
  ],
  "sentiment_distribution": {
    "positive": 60,
    "neutral": 25,
    "negative": 15
  }
}
```

#### Get Tag Analytics

Get detailed analytics for specific tags.

```http
GET /api/analytics/tags/{tag}
```

**Response:**

```json
{
  "tag": "anxiety",
  "total_mentions": 45,
  "conversations": 30,
  "trend_over_time": [
    {
      "date": "2024-01",
      "mentions": 8,
      "conversations": 6
    }
  ],
  "related_tags": [
    { "tag": "mindfulness", "correlation": 0.8 },
    { "tag": "therapy", "correlation": 0.6 }
  ],
  "sentiment_breakdown": {
    "positive": 20,
    "neutral": 15,
    "negative": 10
  }
}
```

### Settings

#### Get Settings

Get current application settings.

```http
GET /api/settings
```

**Response:**

```json
{
  "ai_model": "gpt-4",
  "max_tokens": 1500,
  "temperature": 0.7,
  "cache_enabled": true,
  "privacy_settings": {
    "data_retention_days": 365,
    "anonymize_exports": false
  }
}
```

#### Update Settings

Update application settings.

```http
PUT /api/settings
```

**Request:**

```json
{
  "ai_model": "gpt-4",
  "max_tokens": 2000,
  "temperature": 0.8,
  "privacy_settings": {
    "data_retention_days": 180
  }
}
```

**Response:**

```json
{
  "success": true,
  "message": "Settings updated successfully"
}
```

## 📊 Error Responses

All endpoints return consistent error responses:

### 400 Bad Request

```json
{
  "error": "validation_error",
  "message": "Invalid request parameters",
  "details": {
    "field": "file_id",
    "issue": "File ID is required"
  }
}
```

### 401 Unauthorized

```json
{
  "error": "authentication_error",
  "message": "Invalid or missing API key"
}
```

### 404 Not Found

```json
{
  "error": "not_found",
  "message": "Resource not found",
  "resource": "conversation",
  "id": "uuid-string"
}
```

### 500 Internal Server Error

```json
{
  "error": "internal_error",
  "message": "An unexpected error occurred",
  "request_id": "req-uuid"
}
```

## 🔄 Rate Limiting

API requests are rate-limited to prevent abuse:

- **Standard**: 100 requests per minute
- **File Upload**: 10 uploads per minute
- **AI Analysis**: 20 requests per minute

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248600
```

## 📝 Data Types

### Conversation Object

```json
{
  "id": "string (UUID)",
  "title": "string",
  "summary": "string",
  "tags": ["string"],
  "created_at": "string (ISO 8601)",
  "message_count": "integer",
  "sentiment_score": "float (-1.0 to 1.0)"
}
```

### Message Object

```json
{
  "id": "string",
  "role": "string (user|assistant)",
  "content": "string",
  "timestamp": "string (ISO 8601)"
}
```

### Insight Object

```json
{
  "question": "string",
  "analysis": "string",
  "key_insights": ["string"],
  "quotes": [
    {
      "text": "string",
      "conversation_id": "string (UUID)",
      "timestamp": "string (ISO 8601)"
    }
  ],
  "recommendations": ["string"]
}
```

## 🧪 Testing the API

### Using curl

```bash
# Test authentication
curl -X GET "http://localhost:8000/api/files/list" \
  -H "X-API-Key: your-api-key"

# Upload a file
curl -X POST "http://localhost:8000/api/files/upload" \
  -H "X-API-Key: your-api-key" \
  -F "file=@conversations.json"

# Generate insights
curl -X POST "http://localhost:8000/api/chat/insights" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How have I grown spiritually?",
    "conversation_ids": ["uuid-1"]
  }'
```

### Using Python

```python
import requests

# Base configuration
base_url = "http://localhost:8000"
headers = {"X-API-Key": "your-api-key"}

# List files
response = requests.get(f"{base_url}/api/files/list", headers=headers)
files = response.json()

# Upload file
with open("conversations.json", "rb") as f:
    files = {"file": f}
    response = requests.post(f"{base_url}/api/files/upload",
                           headers=headers, files=files)
    result = response.json()
```

## 📚 Additional Resources

- **[Interactive API Docs](http://localhost:8000/docs)** - Swagger UI documentation
- **[OpenAPI Schema](http://localhost:8000/openapi.json)** - OpenAPI specification
- **[Development Guide](development.md)** - Backend development information

---

_For more information, check the [development guide](development.md) or open an issue on GitHub._
