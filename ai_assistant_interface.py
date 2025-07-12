"""
AI Assistant Interface for InsightVault
Phase 1: Chat-like Interface Integration

Provides a conversational interface for the AI assistant that integrates with the existing dashboard.
Features:
- Chat-like query interface
- Real-time insight generation
- Conversation history
- Quick question suggestions
- Integration with existing dashboard
"""

import os
import json
import webbrowser
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

from ai_assistant import AIAssistant, GeneratedInsight


class AIAssistantInterface:
    """Chat-like interface for the AI assistant"""
    
    def __init__(self, config_path: str = 'config.json'):
        self.config_path = config_path
        self.ai_assistant = AIAssistant(config_path)
        self.app: Optional[dash.Dash] = None
        self.conversation_history: List[Dict[str, Any]] = []
        self.quick_questions = self._initialize_quick_questions()
        
        # Initialize the interface
        self._initialize_interface()
    
    def _initialize_quick_questions(self) -> List[Dict[str, Any]]:
        """Initialize quick question suggestions"""
        return [
            {
                'category': 'Learning & Growth',
                'questions': [
                    "What have I learned about my relationships and boundaries?",
                    "How has my understanding of productivity evolved?",
                    "What patterns do you see in my learning journey?",
                    "When did I have breakthrough moments about self-care?"
                ]
            },
            {
                'category': 'Relationships & Social',
                'questions': [
                    "What patterns do you see in my friendships and social connections?",
                    "How has my communication style changed over time?",
                    "What have I learned about setting healthy boundaries?",
                    "What relationship dynamics do I keep repeating?"
                ]
            },
            {
                'category': 'Personal Development',
                'questions': [
                    "What goals have I been working on and how am I progressing?",
                    "What habits have I successfully built or broken?",
                    "How has my self-confidence evolved?",
                    "What limiting beliefs have I overcome?"
                ]
            },
            {
                'category': 'Emotional & Mental Health',
                'questions': [
                    "How has my emotional well-being changed over time?",
                    "What triggers my stress and how do I handle it?",
                    "What coping mechanisms have been most effective?",
                    "How has my self-compassion grown?"
                ]
            }
        ]
    
    def _initialize_interface(self):
        """Initialize the Dash application"""
        self.app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
            suppress_callback_exceptions=True
        )
        
        self.app.title = "InsightVault - AI Personal Growth Assistant"
        
        # Setup callbacks
        self._setup_callbacks()
    
    def create_layout(self) -> html.Div:
        """Create the main interface layout"""
        return html.Div([
            dcc.Store(id='conversation-history'),
            dcc.Store(id='ai-assistant-state'),
            
            # Header
            self._create_header(),
            
            # Main content
            dbc.Container([
                dbc.Row([
                    # Chat interface
                    dbc.Col([
                        self._create_chat_interface()
                    ], width=8),
                    
                    # Quick questions sidebar
                    dbc.Col([
                        self._create_quick_questions_sidebar()
                    ], width=4)
                ], className="mb-4"),
                
                # Status and controls
                dbc.Row([
                    dbc.Col([
                        self._create_status_section()
                    ], width=12)
                ])
                
            ], fluid=True)
        ])
    
    def _create_header(self) -> dbc.Navbar:
        """Create the interface header"""
        return dbc.Navbar(
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.I(className="fas fa-brain me-2"),
                        dbc.NavbarBrand("InsightVault AI Assistant", className="ms-2")
                    ], width="auto"),
                    dbc.Col([
                        dbc.Nav([
                            dbc.NavItem(dbc.Button("Load Conversations", id="load-conversations-btn", 
                                                  color="outline-light", size="sm")),
                            dbc.NavItem(dbc.Button("Clear History", id="clear-history-btn", 
                                                  color="outline-light", size="sm", className="ms-2")),
                            dbc.NavItem(dbc.Button("Export Insights", id="export-insights-btn", 
                                                  color="outline-light", size="sm", className="ms-2"))
                        ], navbar=True)
                    ], width="auto")
                ], align="center", className="g-0 w-100", justify="between")
            ], fluid=True),
            color="primary",
            dark=True,
            className="mb-4"
        )
    
    def _create_chat_interface(self) -> dbc.Card:
        """Create the main chat interface"""
        return dbc.Card([
            dbc.CardHeader([
                html.H5("💬 Ask me anything about your personal growth journey", className="mb-0")
            ]),
            dbc.CardBody([
                # Chat messages area
                html.Div(id="chat-messages", className="chat-messages mb-3"),
                
                # Input area
                dbc.InputGroup([
                    dbc.Textarea(
                        id="query-input",
                        placeholder="What have you learned about yourself? Ask me anything...",
                        rows=3,
                        className="form-control"
                    ),
                    dbc.InputGroupText([
                        dbc.Button("Send", id="send-query-btn", color="primary", className="btn-sm")
                    ])
                ])
            ])
        ], className="h-100")
    
    def _create_quick_questions_sidebar(self) -> dbc.Card:
        """Create the quick questions sidebar"""
        return dbc.Card([
            dbc.CardHeader([
                html.H5("💡 Quick Questions", className="mb-0")
            ]),
            dbc.CardBody([
                html.Div(id="quick-questions-content")
            ])
        ])
    
    def _create_status_section(self) -> dbc.Card:
        """Create the status and controls section"""
        return dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Div(id="status-indicator", className="text-muted")
                    ], width=6),
                    dbc.Col([
                        html.Div(id="export-status", className="text-muted")
                    ], width=6)
                ])
            ])
        ])
    
    def _create_quick_questions_content(self) -> html.Div:
        """Create the content for quick questions"""
        content = []
        
        for category in self.quick_questions:
            # Category header
            content.append(html.H6(category['category'], className="mt-3 mb-2"))
            
            # Questions
            for question in category['questions']:
                content.append(
                    dbc.Button(
                        question,
                        id=f"quick-question-{hash(question)}",
                        color="outline-primary",
                        size="sm",
                        className="w-100 mb-2 text-start",
                        style={"textAlign": "left", "whiteSpace": "normal", "height": "auto"}
                    )
                )
        
        return html.Div(content)
    
    def _setup_callbacks(self):
        """Setup Dash callbacks"""
        
        @self.app.callback(
            Output("quick-questions-content", "children"),
            Input("load-conversations-btn", "n_clicks"),
            prevent_initial_call=True
        )
        def update_quick_questions(n_clicks):
            return self._create_quick_questions_content()
        
        @self.app.callback(
            [Output("chat-messages", "children"),
             Output("query-input", "value"),
             Output("conversation-history", "data")],
            [Input("send-query-btn", "n_clicks"),
             Input("query-input", "n_submit")] +
            [Input(f"quick-question-{hash(q)}", "n_clicks") 
             for category in self.quick_questions 
             for q in category['questions']],
            [State("query-input", "value"),
             State("conversation-history", "data")],
            prevent_initial_call=True
        )
        def handle_query(send_clicks, submit_clicks, *quick_clicks):
            ctx = callback_context
            if not ctx.triggered:
                raise PreventUpdate
            
            # Get the query
            query = None
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if trigger_id == "send-query-btn" or trigger_id == "query-input":
                query = ctx.inputs["query-input.value"]
            else:
                # Quick question was clicked
                for category in self.quick_questions:
                    for question in category['questions']:
                        if trigger_id == f"quick-question-{hash(question)}":
                            query = question
                            break
                    if query:
                        break
            
            if not query or not query.strip():
                raise PreventUpdate
            
            # Process the query
            try:
                insight = self.ai_assistant.process_query(query.strip())
                response = self.ai_assistant.format_insight_response(insight)
                
                # Add to conversation history
                history = ctx.states["conversation-history.data"] or []
                history.append({
                    'query': query,
                    'response': response,
                    'timestamp': datetime.now().isoformat(),
                    'confidence': insight.confidence_score,
                    'insight_data': {
                        'summary': insight.summary,
                        'key_learnings': insight.key_learnings,
                        'breakthrough_moments': insight.breakthrough_moments,
                        'next_steps': insight.actionable_next_steps
                    }
                })
                
                # Create chat messages
                messages = self._create_chat_messages(history)
                
                return messages, "", history
                
            except Exception as e:
                error_message = f"Error processing query: {str(e)}"
                history = ctx.states["conversation-history.data"] or []
                history.append({
                    'query': query,
                    'response': error_message,
                    'timestamp': datetime.now().isoformat(),
                    'confidence': 0.0,
                    'error': True
                })
                
                messages = self._create_chat_messages(history)
                return messages, "", history
        
        @self.app.callback(
            [Output("chat-messages", "children"),
             Output("conversation-history", "data")],
            Input("clear-history-btn", "n_clicks"),
            prevent_initial_call=True
        )
        def clear_history(n_clicks):
            if n_clicks:
                return [], []
            raise PreventUpdate
        
        @self.app.callback(
            Output("status-indicator", "children"),
            [Input("load-conversations-btn", "n_clicks")],
            prevent_initial_call=True
        )
        def update_status(n_clicks):
            if n_clicks:
                conv_count = len(self.ai_assistant.conversations)
                if conv_count > 0:
                    return f"✅ Loaded {conv_count} conversations"
                else:
                    return "⚠️ No conversations loaded. Please load your ChatGPT exports."
            return "Ready to analyze your personal growth journey"
        
        @self.app.callback(
            Output("export-status", "children"),
            Input("export-insights-btn", "n_clicks"),
            State("conversation-history", "data"),
            prevent_initial_call=True
        )
        def export_insights(n_clicks, history):
            if n_clicks and history:
                try:
                    self._export_insights(history)
                    return "✅ Insights exported successfully"
                except Exception as e:
                    return f"❌ Export failed: {str(e)}"
            return ""
    
    def _create_chat_messages(self, history: List[Dict[str, Any]]) -> List[html.Div]:
        """Create chat message components from history"""
        messages = []
        
        for entry in history:
            # User message
            messages.append(
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.Strong("You: "),
                            entry['query']
                        ], className="user-message")
                    ])
                ], className="mb-3", color="light")
            )
            
            # Assistant response
            if entry.get('error'):
                # Error message
                messages.append(
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.Strong("Assistant: "),
                                html.Span(entry['response'], className="text-danger")
                            ], className="assistant-message")
                        ])
                    ], className="mb-3", color="danger", outline=True)
                )
            else:
                # Insight response
                messages.append(
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.Strong("Assistant: "),
                                html.Div([
                                    html.Pre(entry['response'], className="insight-response mb-2"),
                                    html.Small(f"Confidence: {int(entry['confidence'] * 100)}%", 
                                             className="text-muted")
                                ])
                            ], className="assistant-message")
                        ])
                    ], className="mb-3", color="primary", outline=True)
                )
        
        return messages
    
    def _export_insights(self, history: List[Dict[str, Any]]):
        """Export insights to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"insights_export_{timestamp}.json"
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'total_insights': len(history),
            'conversations_analyzed': len(self.ai_assistant.conversations),
            'insights': history
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"Insights exported to {filename}")
    
    def load_conversations(self, file_path: str) -> bool:
        """Load conversations for the AI assistant"""
        return self.ai_assistant.load_conversations(file_path)
    
    def run_server(self, host: str = '127.0.0.1', port: int = 8051, debug: bool = False) -> str:
        """Run the AI assistant interface server"""
        if not self.app:
            raise RuntimeError("Interface not initialized")
        
        # Set the layout
        self.app.layout = self.create_layout()
        
        # Run the server
        url = f"http://{host}:{port}"
        print(f"Starting AI Assistant Interface at {url}")
        
        if not debug:
            # In production, we'd run this differently
            print("Note: In production, use uvicorn or gunicorn to run the server")
        
        self.app.run_server(host=host, port=port, debug=debug)
        return url


def main():
    """Main function to run the AI assistant interface"""
    interface = AIAssistantInterface()
    
    # Example: Load conversations if available
    # if os.path.exists('data/conversations.json'):
    #     interface.load_conversations('data/conversations.json')
    
    # Run the interface
    interface.run_server(debug=True)


if __name__ == "__main__":
    main()