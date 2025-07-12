// User Types
export interface User {
  id: string;
  email: string;
  created_at: string;
  updated_at: string;
}

export interface UserProfile {
  id: string;
  user_id: string;
  focus_areas: string[];
  learning_goals: string[];
  preferences: Record<string, any>;
  created_at: string;
  updated_at: string;
}

// Conversation Types
export interface Conversation {
  id: string;
  user_id: string;
  title: string;
  content: Message[];
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

// Insight Types
export interface Insight {
  id: string;
  user_id: string;
  conversation_id?: string;
  query: string;
  response: InsightResponse;
  confidence_score: number;
  created_at: string;
}

export interface InsightResponse {
  key_learnings: string[];
  next_steps: string[];
  themes: string[];
  summary: string;
  model_used: string;
}

// Analytics Types
export interface AnalyticsData {
  id: string;
  user_id: string;
  data_type: string;
  data: Record<string, any>;
  created_at: string;
}

export interface TrendAnalysis {
  trends: Trend[];
  patterns: Pattern[];
  recommendations: Recommendation[];
}

export interface Trend {
  name: string;
  direction: "increasing" | "decreasing" | "stable";
  confidence: number;
  description: string;
}

export interface Pattern {
  name: string;
  frequency: number;
  description: string;
  impact: "positive" | "negative" | "neutral";
}

export interface Recommendation {
  type: string;
  title: string;
  description: string;
  priority: "high" | "medium" | "low";
  action_items: string[];
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Auth Types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  confirm_password: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// File Upload Types
export interface FileUploadResponse {
  file_id: string;
  filename: string;
  size: number;
  status: "processing" | "completed" | "failed";
  message?: string;
}

// Chat Types
export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  conversation_id?: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  context?: Record<string, any>;
}

export interface ChatResponse {
  message: ChatMessage;
  insights?: InsightResponse;
  suggestions?: string[];
}
