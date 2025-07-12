# System Architecture

## 🏗️ High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Query    │───▶│  Query Parser   │───▶│ Semantic Search │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Insight Gen    │◀───│ Holistic Analyzer│◀───│ Context Extractor│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Core Components

### 1. Natural Language Query Engine

**Purpose**: Understand user intent and extract key concepts from natural language queries.

**Components**:

- **Intent Recognition**: Classify query type (learning, relationships, goals, etc.)
- **Entity Extraction**: Identify key concepts, people, emotions, time periods
- **Query Expansion**: Generate related terms and synonyms
- **Context Understanding**: Consider user's history and preferences

**Example**:

```
Input: "What have I learned about my relationships and boundaries?"
Output: {
  intent: "learning_analysis",
  entities: ["relationships", "boundaries", "learning"],
  time_context: "all_time",
  focus_areas: ["personal_growth", "interpersonal_skills"]
}
```

### 2. Semantic Search & Matching

**Purpose**: Find relevant conversations using semantic similarity.

**Technology Stack**:

- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Vector Database**: FAISS or Pinecone for similarity search
- **Indexing**: Conversation-level and message-level embeddings
- **Ranking**: Relevance scoring with recency and importance weights

**Process**:

1. Generate embeddings for all conversations
2. Index embeddings in vector database
3. Query expansion for better recall
4. Semantic similarity search
5. Re-rank results by relevance and recency

### 3. Contextual Analysis Pipeline

**Purpose**: Deep analysis of patterns, evolution, and insights across conversations.

**Analysis Layers**:

#### A. Topic Clustering

- Group related conversations by semantic similarity
- Identify emerging themes and topics
- Track topic evolution over time

#### B. Sentiment Evolution

- Track emotional changes over time
- Identify emotional triggers and patterns
- Map sentiment to life events

#### C. Belief System Mapping

- Extract core beliefs and values
- Track how beliefs have evolved
- Identify belief conflicts and resolutions

#### D. Learning Pattern Recognition

- Find "aha moments" and breakthroughs
- Identify gradual learning patterns
- Map learning to specific life areas

#### E. Cross-Reference Synthesis

- Connect insights across different life areas
- Identify interdependencies between topics
- Generate holistic understanding

### 4. Holistic Insight Generation

**Purpose**: Synthesize insights into actionable, personalized recommendations.

**Output Structure**:

```json
{
  "summary": "Your understanding of boundaries has evolved significantly...",
  "key_learnings": [
    "You've identified 3 toxic relationship patterns",
    "Your communication style has become more direct",
    "You're setting boundaries in 40% more situations"
  ],
  "evolution_timeline": {
    "month_1_2": "Recognizing boundary violations",
    "month_3_4": "Learning to say 'no' without guilt",
    "month_5_6": "Proactively setting healthy boundaries"
  },
  "breakthrough_moments": [
    {
      "conversation_id": 47,
      "date": "2024-01-15",
      "insight": "I realized I don't owe anyone my time or energy",
      "impact_score": 0.9
    }
  ],
  "actionable_next_steps": [
    "Practice boundary-setting in low-stakes situations",
    "Journal about your boundary journey weekly",
    "Consider therapy to deepen this work"
  ],
  "confidence_score": 0.85
}
```

## 🗄️ Data Architecture

### Conversation Storage

```json
{
  "conversation_id": "uuid",
  "title": "string",
  "create_date": "datetime",
  "messages": [
    {
      "role": "user|assistant",
      "content": "string",
      "timestamp": "datetime",
      "sentiment": "float",
      "topics": ["array"],
      "entities": ["array"]
    }
  ],
  "metadata": {
    "embedding": "vector",
    "summary": "string",
    "key_themes": ["array"],
    "sentiment_trend": "float",
    "importance_score": "float"
  }
}
```

### User Profile

```json
{
  "user_id": "uuid",
  "preferences": {
    "insight_depth": "basic|detailed|comprehensive",
    "focus_areas": ["array"],
    "learning_goals": ["array"]
  },
  "interaction_history": [
    {
      "query": "string",
      "timestamp": "datetime",
      "insight_rating": "int",
      "action_taken": "string"
    }
  ]
}
```

## 🔄 Processing Pipeline

### 1. Data Ingestion

1. Parse ChatGPT export JSON
2. Extract conversations and messages
3. Generate embeddings for each conversation
4. Store in vector database
5. Index for fast retrieval

### 2. Query Processing

1. Parse natural language query
2. Extract intent and entities
3. Expand query with synonyms
4. Search vector database
5. Rank results by relevance

### 3. Analysis Generation

1. Cluster relevant conversations
2. Extract patterns and themes
3. Track evolution over time
4. Identify breakthrough moments
5. Generate actionable insights

### 4. Response Synthesis

1. Structure insights logically
2. Add confidence scores
3. Include supporting evidence
4. Generate next steps
5. Format for user consumption

## 🛠️ Technology Stack

### Backend

- **Framework**: FastAPI or Flask
- **Database**: PostgreSQL + Redis
- **Vector Database**: FAISS, Pinecone, or Weaviate
- **NLP**: spaCy, sentence-transformers
- **LLM**: OpenAI GPT-4 or Anthropic Claude

### Frontend

- **Framework**: React or Vue.js
- **UI Library**: Material-UI or Ant Design
- **Charts**: D3.js or Chart.js
- **State Management**: Redux or Vuex

### Infrastructure

- **Deployment**: Docker + Kubernetes
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack
- **Caching**: Redis

## 📊 Performance Considerations

### Scalability

- **Horizontal Scaling**: Stateless API design
- **Caching**: Redis for frequently accessed data
- **CDN**: Static assets and embeddings
- **Database**: Read replicas for analytics

### Latency

- **Vector Search**: Optimized indexing
- **Caching**: Query result caching
- **Async Processing**: Background analysis tasks
- **CDN**: Global content delivery

### Accuracy

- **Embedding Quality**: Fine-tuned models
- **Query Expansion**: Comprehensive synonym sets
- **Relevance Scoring**: Multi-factor ranking
- **User Feedback**: Continuous improvement loop

## 🔒 Security & Privacy

### Data Protection

- **Encryption**: At rest and in transit
- **Access Control**: Role-based permissions
- **Data Minimization**: Only necessary data collection
- **User Control**: Data export and deletion

### Privacy

- **Local Processing**: Sensitive data stays local
- **Anonymization**: Remove personal identifiers
- **Consent Management**: Clear user consent
- **Audit Trail**: Track data access and usage
