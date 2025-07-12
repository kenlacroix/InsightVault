"""
Advanced Interactive Dashboard for InsightVault
Unified Web Interface - Beautiful, Clutter-Free Design

Provides comprehensive dashboard with modern UI, file upload, conversation browsing,
and advanced analytics in a single, intuitive interface.
"""

import os
import json
import webbrowser
import base64
import io
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
from collections import defaultdict, Counter
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from wordcloud import WordCloud
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import umap

from chat_parser import Conversation, ChatParser
from analytics_engine import AnalyticsEngine, AnalyticsData
from insight_engine import SAMPLE_QUESTIONS


class UnifiedDashboard:
    """Unified, beautiful web dashboard for InsightVault"""
    
    def __init__(self, config_path: str = 'config.json'):
        self.config_path = config_path
        self.analytics_engine = AnalyticsEngine(config_path)
        self.chat_parser = ChatParser()
        self.conversations: List[Conversation] = []
        self.analytics_data: Optional[AnalyticsData] = None
        
        # Dashboard state
        self.app: Optional[dash.Dash] = None
        self.server_running = False
        self.current_tab = "analytics"
        self.current_page = 0
        self.items_per_page = 10
        self.dark_mode = False
        
        # Enhanced color palettes
        self.light_colors = {
            'primary': '#6366f1',      # Indigo
            'secondary': '#10b981',    # Emerald
            'accent': '#f59e0b',       # Amber
            'success': '#059669',      # Green
            'warning': '#d97706',      # Orange
            'danger': '#dc2626',       # Red
            'info': '#0891b2',         # Cyan
            'light': '#f8fafc',        # Slate 50
            'dark': '#1e293b',         # Slate 800
            'muted': '#64748b',        # Slate 500
            'border': '#e2e8f0',       # Slate 200
            'background': '#ffffff',   # White
            'surface': '#f1f5f9',      # Slate 100
            'text': '#1e293b',         # Slate 800
            'text-muted': '#64748b'    # Slate 500
        }
        
        self.dark_colors = {
            'primary': '#818cf8',      # Indigo 400
            'secondary': '#34d399',    # Emerald 400
            'accent': '#fbbf24',       # Amber 400
            'success': '#10b981',      # Emerald 500
            'warning': '#f59e0b',      # Amber 500
            'danger': '#ef4444',       # Red 500
            'info': '#06b6d4',         # Cyan 500
            'light': '#1e293b',        # Slate 800
            'dark': '#f8fafc',         # Slate 50
            'muted': '#94a3b8',        # Slate 400
            'border': '#334155',       # Slate 700
            'background': '#0f172a',   # Slate 900
            'surface': '#1e293b',      # Slate 800
            'text': '#f8fafc',         # Slate 50
            'text-muted': '#94a3b8'    # Slate 400
        }
        
        self.colors = self.light_colors
        
        # Plotly templates
        self.light_template = "plotly_white"
        self.dark_template = "plotly_dark"
        self.plotly_template = self.light_template
        
        # Initialize components
        self._initialize_dashboard()
    
    def _initialize_dashboard(self):
        """Initialize the Dash application with enhanced styling"""
        self.app = dash.Dash(
            __name__,
            external_stylesheets=[
                dbc.themes.BOOTSTRAP,
                dbc.icons.FONT_AWESOME,
                "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap",
                "https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"
            ],
            suppress_callback_exceptions=True
        )
        
        self.app.title = "InsightVault - Personal Growth Analytics"
        
        # Enhanced CSS for modern design with dark mode support
        self.app.index_string = '''
        <!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>{%title%}</title>
                {%favicon%}
                {%css%}
                <style>
                    :root {
                        --transition-speed: 0.3s;
                        --border-radius: 16px;
                        --shadow-light: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                        --shadow-medium: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
                        --shadow-heavy: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
                    }
                    
                    * {
                        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                        transition: all var(--transition-speed) ease;
                    }
                    
                    body {
                        margin: 0;
                        padding: 0;
                        overflow-x: hidden;
                    }
                    
                    .dashboard-container {
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        padding: 0;
                        position: relative;
                    }
                    
                    .dashboard-container.dark-mode {
                        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                    }
                    
                    .main-content {
                        background: #ffffff;
                        border-radius: 20px 20px 0 0;
                        margin-top: 20px;
                        min-height: calc(100vh - 40px);
                        box-shadow: var(--shadow-heavy);
                        position: relative;
                        overflow: hidden;
                    }
                    
                    .main-content.dark-mode {
                        background: #0f172a;
                        color: #f8fafc;
                    }
                    
                    .main-content::before {
                        content: '';
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        height: 4px;
                        background: linear-gradient(90deg, #6366f1, #10b981, #f59e0b, #ef4444);
                        z-index: 1;
                    }
                    
                    .nav-tabs {
                        border: none;
                        background: transparent;
                        padding: 0 2rem;
                        margin-top: 1rem;
                    }
                    
                    .nav-tabs .nav-link {
                        border: none;
                        color: #64748b;
                        font-weight: 500;
                        padding: 1rem 1.5rem;
                        border-radius: 12px 12px 0 0;
                        margin-right: 0.5rem;
                        transition: all var(--transition-speed) ease;
                        position: relative;
                        overflow: hidden;
                    }
                    
                    .nav-tabs .nav-link::before {
                        content: '';
                        position: absolute;
                        top: 0;
                        left: -100%;
                        width: 100%;
                        height: 100%;
                        background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.1), transparent);
                        transition: left 0.5s ease;
                    }
                    
                    .nav-tabs .nav-link:hover::before {
                        left: 100%;
                    }
                    
                    .nav-tabs .nav-link.active {
                        background: #ffffff;
                        color: #6366f1;
                        border-bottom: 3px solid #6366f1;
                        transform: translateY(-2px);
                        box-shadow: var(--shadow-light);
                    }
                    
                    .nav-tabs .nav-link:hover {
                        background: rgba(99, 102, 241, 0.1);
                        color: #6366f1;
                        transform: translateY(-1px);
                    }
                    
                    .dark-mode .nav-tabs .nav-link.active {
                        background: #1e293b;
                        color: #818cf8;
                        border-bottom-color: #818cf8;
                    }
                    
                    .dark-mode .nav-tabs .nav-link:hover {
                        background: rgba(129, 140, 248, 0.1);
                        color: #818cf8;
                    }
                    
                    .card {
                        border: none;
                        border-radius: var(--border-radius);
                        box-shadow: var(--shadow-light);
                        transition: all var(--transition-speed) ease;
                        background: #ffffff;
                        overflow: hidden;
                    }
                    
                    .dark-mode .card {
                        background: #1e293b;
                        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
                    }
                    
                    .card:hover {
                        box-shadow: var(--shadow-medium);
                        transform: translateY(-4px);
                    }
                    
                    .card-header {
                        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                        border-bottom: 1px solid #e2e8f0;
                        padding: 1.25rem 1.5rem;
                    }
                    
                    .dark-mode .card-header {
                        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                        border-bottom-color: #334155;
                    }
                    
                    .btn-primary {
                        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                        border: none;
                        border-radius: 12px;
                        font-weight: 600;
                        padding: 0.75rem 1.5rem;
                        transition: all var(--transition-speed) ease;
                        position: relative;
                        overflow: hidden;
                    }
                    
                    .btn-primary::before {
                        content: '';
                        position: absolute;
                        top: 0;
                        left: -100%;
                        width: 100%;
                        height: 100%;
                        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
                        transition: left 0.5s ease;
                    }
                    
                    .btn-primary:hover::before {
                        left: 100%;
                    }
                    
                    .btn-primary:hover {
                        transform: translateY(-2px);
                        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
                    }
                    
                    .upload-area {
                        border: 2px dashed #e2e8f0;
                        border-radius: var(--border-radius);
                        padding: 3rem 2rem;
                        text-align: center;
                        background: #f8fafc;
                        transition: all var(--transition-speed) ease;
                        cursor: pointer;
                        position: relative;
                        overflow: hidden;
                    }
                    
                    .dark-mode .upload-area {
                        border-color: #334155;
                        background: #1e293b;
                    }
                    
                    .upload-area::before {
                        content: '';
                        position: absolute;
                        top: 0;
                        left: -100%;
                        width: 100%;
                        height: 100%;
                        background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.1), transparent);
                        transition: left 0.5s ease;
                    }
                    
                    .upload-area:hover::before {
                        left: 100%;
                    }
                    
                    .upload-area:hover {
                        border-color: #6366f1;
                        background: rgba(99, 102, 241, 0.05);
                        transform: translateY(-2px);
                    }
                    
                    .stat-card {
                        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                        border-left: 4px solid #6366f1;
                        position: relative;
                        overflow: hidden;
                    }
                    
                    .dark-mode .stat-card {
                        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                        border-left-color: #818cf8;
                    }
                    
                    .stat-card::before {
                        content: '';
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        height: 2px;
                        background: linear-gradient(90deg, #6366f1, #10b981, #f59e0b);
                        transform: scaleX(0);
                        transition: transform 0.5s ease;
                    }
                    
                    .stat-card:hover::before {
                        transform: scaleX(1);
                    }
                    
                    .conversation-item {
                        padding: 1rem;
                        border-radius: 12px;
                        border: 1px solid #e2e8f0;
                        margin-bottom: 0.5rem;
                        cursor: pointer;
                        transition: all var(--transition-speed) ease;
                        background: #ffffff;
                        position: relative;
                        overflow: hidden;
                    }
                    
                    .dark-mode .conversation-item {
                        border-color: #334155;
                        background: #1e293b;
                    }
                    
                    .conversation-item::before {
                        content: '';
                        position: absolute;
                        top: 0;
                        left: -100%;
                        width: 100%;
                        height: 100%;
                        background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.05), transparent);
                        transition: left 0.5s ease;
                    }
                    
                    .conversation-item:hover::before {
                        left: 100%;
                    }
                    
                    .conversation-item:hover {
                        border-color: #6366f1;
                        background: rgba(99, 102, 241, 0.05);
                        transform: translateX(4px);
                    }
                    
                    .conversation-item.selected {
                        border-color: #6366f1;
                        background: rgba(99, 102, 241, 0.1);
                        box-shadow: var(--shadow-light);
                    }
                    
                    .insight-card {
                        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                        border-left: 4px solid #f59e0b;
                    }
                    
                    .dark-mode .insight-card {
                        background: linear-gradient(135deg, #451a03 0%, #78350f 100%);
                        border-left-color: #fbbf24;
                    }
                    
                    .loading-spinner {
                        display: inline-block;
                        width: 20px;
                        height: 20px;
                        border: 3px solid #f3f3f3;
                        border-top: 3px solid #6366f1;
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                    }
                    
                    .dark-mode .loading-spinner {
                        border-color: #334155;
                        border-top-color: #818cf8;
                    }
                    
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                    
                    .fade-in {
                        animation: fadeIn 0.5s ease-in;
                    }
                    
                    @keyframes fadeIn {
                        from { opacity: 0; transform: translateY(20px); }
                        to { opacity: 1; transform: translateY(0); }
                    }
                    
                    .slide-in {
                        animation: slideIn 0.5s ease-out;
                    }
                    
                    @keyframes slideIn {
                        from { transform: translateX(-100%); }
                        to { transform: translateX(0); }
                    }
                    
                    .pulse {
                        animation: pulse 2s infinite;
                    }
                    
                    @keyframes pulse {
                        0% { transform: scale(1); }
                        50% { transform: scale(1.05); }
                        100% { transform: scale(1); }
                    }
                    
                    .theme-toggle {
                        background: rgba(255, 255, 255, 0.2);
                        border: 2px solid rgba(255, 255, 255, 0.3);
                        border-radius: 50px;
                        padding: 0.5rem;
                        cursor: pointer;
                        transition: all var(--transition-speed) ease;
                        position: relative;
                        overflow: hidden;
                    }
                    
                    .theme-toggle:hover {
                        background: rgba(255, 255, 255, 0.3);
                        transform: scale(1.1);
                    }
                    
                    .theme-toggle::before {
                        content: '';
                        position: absolute;
                        top: 0;
                        left: -100%;
                        width: 100%;
                        height: 100%;
                        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
                        transition: left 0.5s ease;
                    }
                    
                    .theme-toggle:hover::before {
                        left: 100%;
                    }
                    
                    .badge {
                        border-radius: 20px;
                        padding: 0.5rem 1rem;
                        font-weight: 500;
                        transition: all var(--transition-speed) ease;
                    }
                    
                    .badge:hover {
                        transform: scale(1.05);
                    }
                    
                    .alert {
                        border-radius: var(--border-radius);
                        border: none;
                        box-shadow: var(--shadow-light);
                    }
                    
                    .dark-mode .alert {
                        background: #1e293b;
                        color: #f8fafc;
                    }
                    
                    .form-control {
                        border-radius: 12px;
                        border: 2px solid #e2e8f0;
                        transition: all var(--transition-speed) ease;
                    }
                    
                    .dark-mode .form-control {
                        background: #1e293b;
                        border-color: #334155;
                        color: #f8fafc;
                    }
                    
                    .form-control:focus {
                        border-color: #6366f1;
                        box-shadow: 0 0 0 0.2rem rgba(99, 102, 241, 0.25);
                    }
                    
                    .dropdown-menu {
                        border-radius: var(--border-radius);
                        border: none;
                        box-shadow: var(--shadow-medium);
                    }
                    
                    .dark-mode .dropdown-menu {
                        background: #1e293b;
                        border: 1px solid #334155;
                    }
                    
                    .pagination {
                        border-radius: var(--border-radius);
                    }
                    
                    .page-link {
                        border-radius: 8px;
                        margin: 0 0.25rem;
                        transition: all var(--transition-speed) ease;
                    }
                    
                    .page-link:hover {
                        transform: translateY(-1px);
                    }
                    
                    .dark-mode .page-link {
                        background: #1e293b;
                        border-color: #334155;
                        color: #f8fafc;
                    }
                    
                    .dark-mode .page-item.active .page-link {
                        background: #6366f1;
                        border-color: #6366f1;
                    }
                </style>
            </head>
            <body>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    {%renderer%}
                </footer>
            </body>
        </html>
        '''
        
        # Setup callbacks
        self._setup_callbacks()
    
    def create_layout(self) -> html.Div:
        """Create the main dashboard layout with enhanced design"""
        return html.Div([
            # Store components for data management
            dcc.Store(id='conversation-data'),
            dcc.Store(id='analytics-data'),
            dcc.Store(id='current-tab'),
            dcc.Store(id='current-page'),
            dcc.Store(id='dark-mode', data=False),
            
            # Main container
            html.Div([
                # Header
                self._create_header(),
                
                # Main content area
                html.Div([
                    # Navigation tabs
                    self._create_navigation(),
                    
                    # Tab content
                    html.Div(id='tab-content', className='p-4 fade-in')
                    
                ], className='main-content', id='main-content')
                
            ], className='dashboard-container', id='dashboard-container')
        ])
    
    def _create_header(self) -> html.Div:
        """Create enhanced header with theme toggle and upload functionality"""
        return html.Div([
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H1("🧠 InsightVault", className="text-white mb-0", 
                                   style={'fontWeight': '800', 'fontSize': '2.5rem'}),
                            html.P("Personal Growth Analytics", className="text-white-50 mb-0",
                                   style={'fontSize': '1.1rem', 'fontWeight': '300'})
                        ])
                    ], width=6),
                    dbc.Col([
                        html.Div([
                            # File upload
                            dcc.Upload(
                                id='upload-data',
                                children=html.Div([
                                    html.I(className="fas fa-cloud-upload-alt me-2"),
                                    "Upload Conversations"
                                ]),
                                style={
                                    'display': 'inline-block',
                                    'padding': '12px 24px',
                                    'backgroundColor': 'rgba(255,255,255,0.2)',
                                    'borderRadius': '12px',
                                    'color': 'white',
                                    'cursor': 'pointer',
                                    'border': '2px dashed rgba(255,255,255,0.3)',
                                    'transition': 'all 0.3s ease',
                                    'fontWeight': '500'
                                },
                                multiple=False
                            ),
                            # Theme toggle
                            html.Button([
                                html.I(className="fas fa-moon", id="theme-icon")
                            ], id='theme-toggle', className='theme-toggle ms-3'),
                            # Settings button
                            html.Button([
                                html.I(className="fas fa-cog")
                            ], id='settings-btn', className='btn btn-outline-light ms-3',
                               style={'borderRadius': '12px', 'padding': '12px 16px'})
                        ], className='text-end')
                    ], width=6)
                ], align='center', className='py-4')
            ], fluid=True)
        ])
    
    def _create_navigation(self) -> html.Div:
        """Create modern tab navigation"""
        return html.Div([
            dbc.Nav([
                dbc.NavItem([
                    dbc.NavLink([
                        html.I(className="fas fa-chart-line me-2"),
                        "Analytics"
                    ], id='analytics-tab', active=True, className='nav-link')
                ]),
                dbc.NavItem([
                    dbc.NavLink([
                        html.I(className="fas fa-comments me-2"),
                        "Conversations"
                    ], id='conversations-tab', className='nav-link')
                ]),
                dbc.NavItem([
                    dbc.NavLink([
                        html.I(className="fas fa-robot me-2"),
                        "AI Features"
                    ], id='ai-tab', className='nav-link')
                ]),
                dbc.NavItem([
                    dbc.NavLink([
                        html.I(className="fas fa-file-alt me-2"),
                        "Reports"
                    ], id='reports-tab', className='nav-link')
                ])
            ], className='nav-tabs border-0 px-4 pt-4')
        ])
    
    def _create_analytics_tab(self) -> html.Div:
        """Create analytics dashboard tab with enhanced animations"""
        if not self.analytics_data:
            return self._create_empty_analytics_state()
        
        return html.Div([
            # Overview cards with staggered animation
            html.Div([
                self._create_overview_cards()
            ], style={'animationDelay': '0.1s'}),
            
            html.Hr(className='my-4'),
            
            # Charts grid with enhanced animations
            dbc.Row([
                dbc.Col([
                    self._create_sentiment_timeline_card()
                ], width=12, className='mb-4 fade-in')
            ], style={'animationDelay': '0.2s'}),
            
            dbc.Row([
                dbc.Col([
                    self._create_emotional_patterns_card()
                ], width=6, className='mb-4 fade-in'),
                dbc.Col([
                    self._create_growth_metrics_card()
                ], width=6, className='mb-4 fade-in')
            ], style={'animationDelay': '0.3s'}),
            
            dbc.Row([
                dbc.Col([
                    self._create_topic_analysis_card()
                ], width=6, className='mb-4 fade-in'),
                dbc.Col([
                    self._create_breakthrough_moments_card()
                ], width=6, className='mb-4 fade-in')
            ], style={'animationDelay': '0.4s'}),
            
            dbc.Row([
                dbc.Col([
                    self._create_writing_style_card()
                ], width=6, className='mb-4 fade-in'),
                dbc.Col([
                    self._create_goal_achievement_card()
                ], width=6, className='mb-4 fade-in')
            ], style={'animationDelay': '0.5s'})
        ])
    
    def _create_conversations_tab(self) -> html.Div:
        """Create conversations browsing tab"""
        if not self.conversations:
            return self._create_empty_conversations_state()
        
        return html.Div([
            dbc.Row([
                # Search and filters
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Search & Filter", className="card-title mb-3"),
                            dbc.InputGroup([
                                dbc.InputGroupText(html.I(className="fas fa-search")),
                                dbc.Input(id="search-input", placeholder="Search conversations...", 
                                         type="text", className="form-control")
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Date Range"),
                                    dcc.DatePickerRange(
                                        id='date-range',
                                        display_format='MMM DD, YYYY',
                                        className='w-100'
                                    )
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("Tags"),
                                    dcc.Dropdown(
                                        id='tag-filter',
                                        options=[{'label': tag, 'value': tag} for tag in self._get_all_tags()],
                                        placeholder="Filter by tags...",
                                        multi=True
                                    )
                                ], width=6)
                            ])
                        ])
                    ])
                ], width=4),
                
                # Conversation list
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Conversations", className="card-title mb-3"),
                            html.Div(id="conversation-list"),
                                        # Pagination
            dbc.Pagination(
                id="pagination",
                max_value=max(1, len(self.conversations) // self.items_per_page),
                active_page=1,
                className="mt-3"
            )
                        ])
                    ])
                ], width=8)
            ]),
            
            # Selected conversation details
            html.Div(id="conversation-details", className="mt-4")
        ])
    
    def _create_ai_tab(self) -> html.Div:
        """Create AI features tab"""
        return html.Div([
            dbc.Row([
                # Insight generation
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Generate Insights", className="mb-0"),
                            html.I(className="fas fa-lightbulb text-warning")
                        ]),
                        dbc.CardBody([
                            dcc.Dropdown(
                                id="question-dropdown",
                                options=[{'label': q, 'value': q} for q in SAMPLE_QUESTIONS],
                                placeholder="Ask a reflective question...",
                                className="mb-3"
                            ),
                            dbc.Button([
                                html.I(className="fas fa-magic me-2"),
                                "Generate Insight"
                            ], id="generate-insight-btn", color="primary", className="mb-3"),
                            html.Div(id="insight-result")
                        ])
                    ])
                ], width=6),
                
                # Summarization
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Summarize Conversations", className="mb-0"),
                            html.I(className="fas fa-file-text text-info")
                        ]),
                        dbc.CardBody([
                            dbc.Button([
                                html.I(className="fas fa-magic me-2"),
                                "Summarize All"
                            ], id="summarize-all-btn", color="success", className="mb-2"),
                            html.Br(),
                            dbc.Button([
                                html.I(className="fas fa-download me-2"),
                                "Export Summaries"
                            ], id="export-summaries-btn", color="info"),
                            html.Div(id="summarization-status", className="mt-3")
                        ])
                    ])
                ], width=6)
            ])
        ])
    
    def _create_reports_tab(self) -> html.Div:
        """Create reports and export tab"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Export Reports", className="mb-0"),
                            html.I(className="fas fa-file-export text-primary")
                        ]),
                        dbc.CardBody([
                            dbc.ButtonGroup([
                                dbc.Button([
                                    html.I(className="fas fa-file-pdf me-2"),
                                    "PDF Report"
                                ], id="export-pdf-btn", color="danger"),
                                dbc.Button([
                                    html.I(className="fas fa-file-excel me-2"),
                                    "Excel Report"
                                ], id="export-excel-btn", color="success"),
                                dbc.Button([
                                    html.I(className="fas fa-file-code me-2"),
                                    "JSON Data"
                                ], id="export-json-btn", color="info")
                            ], className="mb-3"),
                            html.Div(id="export-status")
                        ])
                    ])
                ], width=12)
            ])
        ])
    
    def _create_empty_analytics_state(self) -> html.Div:
        """Create enhanced empty state for analytics tab"""
        return html.Div([
            dbc.Alert([
                html.H4("📊 Welcome to Analytics", className="alert-heading fw-bold"),
                html.P("Upload your ChatGPT conversations to see beautiful analytics and insights."),
                html.Hr(),
                html.P("Drag and drop your conversations.json file in the header above to get started.", 
                       className="mb-0"),
                html.Div([
                    html.I(className="fas fa-arrow-up fa-2x text-primary mt-3 pulse")
                ], className="text-center")
            ], color="info", className="text-center animate__animated animate__fadeIn")
        ], className="text-center py-5")
    
    def _create_empty_conversations_state(self) -> html.Div:
        """Create enhanced empty state for conversations tab"""
        return html.Div([
            dbc.Alert([
                html.H4("💬 No Conversations Loaded", className="alert-heading fw-bold"),
                html.P("Upload your ChatGPT conversations to browse and search through them."),
                html.Hr(),
                html.P("Use the upload button in the header to load your data.", 
                       className="mb-0"),
                html.Div([
                    html.I(className="fas fa-cloud-upload-alt fa-2x text-primary mt-3 pulse")
                ], className="text-center")
            ], color="info", className="text-center animate__animated animate__fadeIn")
        ], className="text-center py-5")
    
    def _create_overview_cards(self) -> dbc.Row:
        """Create modern overview statistics cards with animations"""
        if not self.analytics_data:
            return dbc.Row()
        
        cards = [
            self._create_stat_card(
                "Total Conversations", 
                self.analytics_data.conversation_count,
                "fas fa-comments",
                "primary"
            ),
            self._create_stat_card(
                "Total Messages",
                self.analytics_data.total_messages,
                "fas fa-envelope",
                "success"
            ),
            self._create_stat_card(
                "Date Range",
                f"{self.analytics_data.date_range[0].strftime('%b %Y')} - {self.analytics_data.date_range[1].strftime('%b %Y')}",
                "fas fa-calendar",
                "info"
            ),
            self._create_stat_card(
                "Unique Themes",
                len(self.analytics_data.top_tags),
                "fas fa-tags",
                "warning"
            )
        ]
        
        return dbc.Row([
            dbc.Col(card, width=3, className="fade-in") for card in cards
        ], className="mb-4")
    
    def _create_stat_card(self, title: str, value: Any, icon: str, color: str) -> dbc.Card:
        """Create a modern statistics card"""
        return dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H3(str(value), className="card-title mb-1", 
                               style={'fontWeight': '700', 'color': self.colors[color]}),
                        html.P(title, className="card-text text-muted mb-0")
                    ], width=8),
                    dbc.Col([
                        html.I(className=f"{icon} fa-2x", 
                              style={'color': self.colors[color], 'opacity': '0.8'})
                    ], width=4, className="text-center d-flex align-items-center")
                ], align="center")
            ])
        ], className="stat-card h-100")
    
    def _get_all_tags(self) -> List[str]:
        """Get all unique tags from conversations"""
        all_tags = set()
        for conv in self.conversations:
            all_tags.update(conv.tags)
        return sorted(list(all_tags))
    
    def _setup_callbacks(self):
        """Setup all dashboard callbacks with enhanced functionality"""
        if not self.app:
            return
        
        # Theme toggle callback
        @self.app.callback(
            [Output('dark-mode', 'data'),
             Output('dashboard-container', 'className'),
             Output('main-content', 'className'),
             Output('theme-icon', 'className')],
            Input('theme-toggle', 'n_clicks'),
            State('dark-mode', 'data'),
            prevent_initial_call=True
        )
        def toggle_theme(n_clicks, current_dark_mode):
            if n_clicks:
                new_dark_mode = not current_dark_mode
                self.dark_mode = new_dark_mode
                
                # Update colors and template
                if new_dark_mode:
                    self.colors = self.dark_colors
                    self.plotly_template = self.dark_template
                else:
                    self.colors = self.light_colors
                    self.plotly_template = self.light_template
                
                # Update CSS classes
                container_class = 'dashboard-container dark-mode' if new_dark_mode else 'dashboard-container'
                content_class = 'main-content dark-mode p-4 fade-in' if new_dark_mode else 'main-content p-4 fade-in'
                icon_class = 'fas fa-sun' if new_dark_mode else 'fas fa-moon'
                
                return new_dark_mode, container_class, content_class, icon_class
            
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        # Tab switching callback with animations
        @self.app.callback(
            Output('tab-content', 'children'),
            [Input('analytics-tab', 'n_clicks'),
             Input('conversations-tab', 'n_clicks'),
             Input('ai-tab', 'n_clicks'),
             Input('reports-tab', 'n_clicks')],
            prevent_initial_call=True
        )
        def switch_tab(analytics_clicks, conversations_clicks, ai_clicks, reports_clicks):
            ctx = callback_context
            if not ctx.triggered:
                return self._create_analytics_tab()
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if button_id == 'analytics-tab':
                return self._create_analytics_tab()
            elif button_id == 'conversations-tab':
                return self._create_conversations_tab()
            elif button_id == 'ai-tab':
                return self._create_ai_tab()
            elif button_id == 'reports-tab':
                return self._create_reports_tab()
            
            return self._create_analytics_tab()
        
        # File upload callback with loading state
        @self.app.callback(
            [Output('conversation-data', 'data'),
             Output('analytics-data', 'data'),
             Output('upload-data', 'children')],
            Input('upload-data', 'contents'),
            State('upload-data', 'filename'),
            prevent_initial_call=True
        )
        def handle_file_upload(contents, filename):
            if contents is None:
                return dash.no_update, dash.no_update, dash.no_update
            
            # Show loading state
            loading_children = html.Div([
                html.I(className="fas fa-spinner fa-spin me-2"),
                "Processing..."
            ])
            
            try:
                # Decode uploaded file
                content_type, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)
                
                # Parse conversations from JSON data
                try:
                    # Parse the JSON data
                    json_data = json.loads(decoded.decode('utf-8'))
                    
                    # Create temporary file to use existing parser
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                        json.dump(json_data, temp_file)
                        temp_file_path = temp_file.name
                    
                    # Load conversations using existing parser
                    if self.chat_parser.load_conversations(temp_file_path):
                        self.conversations = self.chat_parser.conversations
                        self.analytics_data = self.analytics_engine.analyze_conversations(self.conversations)
                        
                        # Clean up temp file
                        os.unlink(temp_file_path)
                        
                        # Success state
                        success_children = html.Div([
                            html.I(className="fas fa-check me-2"),
                            f"Loaded {len(self.conversations)} conversations"
                        ])
                        
                        return len(self.conversations), "loaded", success_children
                    
                    # Clean up temp file if loading failed
                    os.unlink(temp_file_path)
                except Exception as e:
                    print(f"Error parsing uploaded file: {e}")
                
            except Exception as e:
                print(f"Error uploading file: {e}")
            
            # Error state
            error_children = html.Div([
                html.I(className="fas fa-exclamation-triangle me-2"),
                "Upload failed"
            ])
            
            return dash.no_update, dash.no_update, error_children
        
        # Search callback with enhanced filtering
        @self.app.callback(
            Output('conversation-list', 'children'),
            [Input('search-input', 'value'),
             Input('date-range', 'start_date'),
             Input('date-range', 'end_date'),
             Input('tag-filter', 'value'),
             Input('pagination', 'active_page')],
            prevent_initial_call=False
        )
        def update_conversation_list(search_query, start_date, end_date, tags, page):
            if not self.conversations:
                return []
            
            # Filter conversations
            filtered = self.conversations
            
            if search_query:
                filtered = [c for c in filtered if search_query.lower() in c.title.lower() or 
                           search_query.lower() in c.get_full_text().lower()]
            
            if tags:
                filtered = [c for c in filtered if any(tag in c.tags for tag in tags)]
            
            # Date filtering
            if start_date or end_date:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00')) if start_date else None
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00')) if end_date else None
                
                filtered = [c for c in filtered if 
                           (not start_dt or c.create_date >= start_dt) and
                           (not end_dt or c.create_date <= end_dt)]
            
            # Paginate
            page = page or 1
            start_idx = (page - 1) * self.items_per_page
            end_idx = start_idx + self.items_per_page
            page_conversations = filtered[start_idx:end_idx]
            
            # Create conversation items with enhanced styling
            items = []
            for i, conv in enumerate(page_conversations):
                item = html.Div([
                    html.H6(conv.title, className="mb-1 fw-bold"),
                    html.Small(f"📅 {conv.create_date.strftime('%b %d, %Y')} • "
                              f"💬 {len(conv.messages)} messages", 
                              className="text-muted"),
                    html.Div([
                        dbc.Badge(tag, color="primary", className="me-1 pulse") 
                        for tag in conv.tags[:3]
                    ], className="mt-2")
                ], className="conversation-item slide-in", 
                   style={'animationDelay': f'{i * 0.1}s'},
                   id=f"conv-{conv.id}")
                items.append(item)
            
            return items
        
        # Initial content
        @self.app.callback(
            Output('tab-content', 'children', allow_duplicate=True),
            Input('_', 'children'),
            prevent_initial_call=True
        )
        def initial_content(_):
            return self._create_analytics_tab()
    
    def load_conversations(self, conversations: List[Conversation]) -> bool:
        """Load conversations into the dashboard"""
        try:
            self.conversations = conversations
            self.analytics_data = self.analytics_engine.analyze_conversations(conversations)
            return True
        except Exception as e:
            print(f"Error loading conversations: {e}")
            return False
    
    def run_server(self, host: str = '127.0.0.1', port: int = 8050, debug: bool = False) -> str:
        """Run the unified dashboard server"""
        if not self.app:
            print("Dashboard not initialized properly.")
            return ""
        
        # Set layout
        self.app.layout = self.create_layout()
        
        try:
            print(f"🚀 Starting InsightVault Unified Dashboard...")
            print(f"🌐 Dashboard URL: http://{host}:{port}")
            
            # Open browser automatically
            dashboard_url = f"http://{host}:{port}"
            
            if not debug:
                import threading
                threading.Timer(1.5, lambda: webbrowser.open(dashboard_url)).start()
            
            self.server_running = True
            self.app.run(host=host, port=port, debug=debug)
            
            return dashboard_url
            
        except Exception as e:
            print(f"Error running dashboard server: {e}")
            return ""

    def _create_sentiment_timeline_card(self) -> dbc.Card:
        """Create sentiment timeline visualization card"""
        return dbc.Card([
            dbc.CardHeader([
                html.H5("Emotional Journey Timeline", className="mb-0"),
                dbc.Badge("Interactive", color="primary", className="ms-2")
            ]),
            dbc.CardBody([
                dcc.Graph(
                    id="sentiment-timeline",
                    figure=self._create_sentiment_timeline_figure()
                )
            ])
        ])
    
    def _create_emotional_patterns_card(self) -> dbc.Card:
        """Create emotional patterns visualization card"""
        return dbc.Card([
            dbc.CardHeader([
                html.H5("Emotional Patterns", className="mb-0")
            ]),
            dbc.CardBody([
                dcc.Graph(
                    id="emotional-patterns",
                    figure=self._create_emotional_patterns_figure()
                )
            ])
        ])
    
    def _create_growth_metrics_card(self) -> dbc.Card:
        """Create growth metrics visualization card"""
        return dbc.Card([
            dbc.CardHeader([
                html.H5("Personal Growth Metrics", className="mb-0")
            ]),
            dbc.CardBody([
                dcc.Graph(
                    id="growth-metrics",
                    figure=self._create_growth_metrics_figure()
                )
            ])
        ])
    
    def _create_topic_analysis_card(self) -> dbc.Card:
        """Create topic analysis visualization card"""
        return dbc.Card([
            dbc.CardHeader([
                html.H5("Topic Analysis & Clustering", className="mb-0")
            ]),
            dbc.CardBody([
                dcc.Graph(
                    id="topic-clusters",
                    figure=self._create_topic_clusters_figure()
                )
            ])
        ])
    
    def _create_breakthrough_moments_card(self) -> dbc.Card:
        """Create breakthrough moments visualization card"""
        return dbc.Card([
            dbc.CardHeader([
                html.H5("Breakthrough Moments", className="mb-0"),
                dbc.Badge("AI Detected", color="success", className="ms-2")
            ]),
            dbc.CardBody([
                html.Div(id="breakthrough-content")
            ])
        ])
    
    def _create_writing_style_card(self) -> dbc.Card:
        """Create writing style evolution visualization card"""
        return dbc.Card([
            dbc.CardHeader([
                html.H5("Writing Style Evolution", className="mb-0")
            ]),
            dbc.CardBody([
                dcc.Graph(
                    id="writing-style-evolution",
                    figure=self._create_writing_style_figure()
                )
            ])
        ])
    
    def _create_goal_achievement_card(self) -> dbc.Card:
        """Create goal achievement visualization card"""
        return dbc.Card([
            dbc.CardHeader([
                html.H5("Goal Achievement Tracking", className="mb-0")
            ]),
            dbc.CardBody([
                dcc.Graph(
                    id="goal-achievement",
                    figure=self._create_goal_achievement_figure()
                )
            ])
        ])
    
    def _create_sentiment_timeline_figure(self) -> go.Figure:
        """Create sentiment timeline visualization"""
        if not self.analytics_data or not self.analytics_data.sentiment_trends:
            return go.Figure().add_annotation(text="No sentiment data available", showarrow=False)
        
        sentiment_trends = self.analytics_data.sentiment_trends
        months = sorted(sentiment_trends.keys())
        
        # Handle the sentiment trends data structure properly
        sentiments = []
        counts = []
        for month in months:
            month_data = sentiment_trends[month]
            if isinstance(month_data, dict):
                sentiments.append(month_data.get('avg_sentiment', 0))
                counts.append(month_data.get('conversation_count', 0))
            else:
                sentiments.append(0)
                counts.append(0)
        
        # Create subplot
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Sentiment Trend', 'Activity Level'),
            vertical_spacing=0.1,
            row_heights=[0.7, 0.3]
        )
        
        # Sentiment line
        fig.add_trace(
            go.Scatter(
                x=months,
                y=sentiments,
                mode='lines+markers',
                name='Average Sentiment',
                line=dict(color=self.colors['primary'], width=3),
                marker=dict(size=8),
                hovertemplate='<b>%{x}</b><br>Sentiment: %{y:.2f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Add sentiment zones
        fig.add_hline(y=0, line_dash="dash", line_color="gray", row="1", col="1")
        fig.add_hrect(y0=0.1, y1=1, fillcolor="rgba(16, 185, 129, 0.1)", line_width=0, row="1", col="1")
        fig.add_hrect(y0=-1, y1=-0.1, fillcolor="rgba(220, 38, 38, 0.1)", line_width=0, row="1", col="1")
        
        # Activity bars
        fig.add_trace(
            go.Bar(
                x=months,
                y=counts,
                name='Conversations',
                marker_color=self.colors['secondary'],
                opacity=0.7,
                hovertemplate='<b>%{x}</b><br>Conversations: %{y}<extra></extra>'
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title="Emotional Journey Over Time",
            height=500,
            showlegend=False,
            template=self.plotly_template
        )
        
        fig.update_yaxes(title_text="Sentiment Score", row=1, col=1)
        fig.update_yaxes(title_text="Activity", row=2, col=1)
        
        return fig
    
    def _create_emotional_patterns_figure(self) -> go.Figure:
        """Create emotional patterns visualization"""
        if not self.analytics_data or not self.analytics_data.emotional_patterns:
            return go.Figure().add_annotation(text="No emotional pattern data available", showarrow=False)
        
        patterns = self.analytics_data.emotional_patterns
        overall_dist = patterns.get('overall_emotional_distribution', {})
        
        if not overall_dist:
            return go.Figure().add_annotation(text="No emotional data available", showarrow=False)
        
        # Create pie chart for overall distribution
        labels = list(overall_dist.keys())
        values = list(overall_dist.values())
        colors_map = {'positive': self.colors['success'], 'negative': self.colors['danger'], 'neutral': self.colors['info']}
        pie_colors = [colors_map.get(label, self.colors['primary']) for label in labels]
        
        fig = go.Figure(data=[
            go.Pie(
                labels=[label.title() for label in labels],
                values=values,
                hole=0.4,
                marker_colors=pie_colors,
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title="Overall Emotional Distribution",
            height=400,
            template=self.plotly_template
        )
        
        return fig
    
    def _create_growth_metrics_figure(self) -> go.Figure:
        """Create growth metrics visualization"""
        if not self.analytics_data or not self.analytics_data.growth_metrics:
            return go.Figure().add_annotation(text="No growth metrics available", showarrow=False)
        
        growth_metrics = self.analytics_data.growth_metrics
        metrics = list(growth_metrics.keys())
        values = list(growth_metrics.values())
        
        # Color coding: positive = green, negative = red
        colors = [self.colors['success'] if v >= 0 else self.colors['danger'] for v in values]
        
        fig = go.Figure(data=[
            go.Bar(
                x=[metric.replace('_', ' ').title() for metric in metrics],
                y=values,
                marker_color=colors,
                text=[f'{v:.1%}' for v in values],
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Growth Rate: %{y:.1%}<extra></extra>'
            )
        ])
        
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        
        fig.update_layout(
            title="Personal Growth Metrics",
            yaxis_title="Growth Rate",
            height=400,
            template=self.plotly_template
        )
        
        fig.update_yaxes(tickformat='.0%')
        
        return fig
    
    def _create_topic_clusters_figure(self) -> go.Figure:
        """Create topic clustering visualization"""
        if not self.analytics_data or not self.analytics_data.concept_relationships:
            return self._create_empty_figure("No concept relationship data available")
        
        concept_data = self.analytics_data.concept_relationships
        
        # Create network graph for concept relationships
        fig = go.Figure()
        
        # Add concept nodes
        concepts = concept_data.get('top_concepts', [])[:15]  # Top 15 concepts
        
        for i, concept in enumerate(concepts):
            fig.add_trace(go.Scatter(
                x=[i % 5],  # Simple grid layout
                y=[i // 5],
                mode='markers+text',
                marker=dict(size=20, color=self.colors['primary']),
                text=[concept],
                textposition="middle center",
                name=concept,
                showlegend=False
            ))
        
        fig.update_layout(
            title="Concept Relationship Map",
            xaxis=dict(showgrid=False, showticklabels=False, range=[-0.5, 4.5]),
            yaxis=dict(showgrid=False, showticklabels=False, range=[-0.5, 2.5]),
            template=self.plotly_template,
            height=400
        )
        
        return fig
    
    def _create_writing_style_figure(self) -> go.Figure:
        """Create writing style evolution visualization"""
        if not self.analytics_data or not self.analytics_data.writing_style_evolution:
            return self._create_empty_figure("No writing style data available")
        
        style_data = self.analytics_data.writing_style_evolution
        periods = list(style_data.keys())
        
        # Create radar chart for writing style dimensions
        fig = go.Figure()
        
        # Get style dimensions (excluding technical metrics)
        style_dimensions = ['complexity', 'emotional_depth', 'analytical', 'reflective', 'concrete', 'abstract']
        
        for period in periods:
            if period in style_data:
                values = [style_data[period].get(dim, 0) for dim in style_dimensions]
                # Normalize values for better visualization
                max_val = max(values) if values else 1
                normalized_values = [v / max_val for v in values]
                
                fig.add_trace(go.Scatterpolar(
                    r=normalized_values,
                    theta=style_dimensions,
                    fill='toself',
                    name=period.capitalize(),
                    line_color=self.colors.get(period, self.colors['primary'])
                ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=True,
            title="Writing Style Evolution",
            template=self.plotly_template,
            height=400
        )
        
        return fig
    
    def _create_goal_achievement_figure(self) -> go.Figure:
        """Create goal achievement tracking visualization"""
        if not self.analytics_data or not self.analytics_data.goal_achievement:
            return self._create_empty_figure("No goal achievement data available")
        
        goal_data = self.analytics_data.goal_achievement
        
        # Create timeline chart
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Goal Mentions Timeline', 'Achievement Rate'),
            vertical_spacing=0.1
        )
        
        # Goal mentions timeline
        if goal_data.get('goal_mentions'):
            goal_dates = [gm['date'] for gm in goal_data['goal_mentions']]
            goal_counts = [gm['goal_mentions'] for gm in goal_data['goal_mentions']]
            
            fig.add_trace(
                go.Scatter(
                    x=goal_dates,
                    y=goal_counts,
                    mode='lines+markers',
                    name='Goal Mentions',
                    line=dict(color=self.colors['primary'], width=2),
                    marker=dict(size=8)
                ),
                row=1, col=1
            )
        
        # Achievement rate bar
        achievement_rate = goal_data.get('achievement_rate', 0)
        fig.add_trace(
            go.Bar(
                x=['Achievement Rate'],
                y=[achievement_rate],
                name='Success Rate',
                marker_color=self.colors['success'] if achievement_rate > 0.5 else self.colors['warning']
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title="Goal Achievement Tracking",
            template=self.plotly_template,
            height=500,
            showlegend=False
        )
        
        fig.update_yaxes(title_text="Goal Mentions", row=1, col=1)
        fig.update_yaxes(title_text="Achievement Rate", row=2, col=1)
        
        return fig
    
    def _create_empty_figure(self, message: str) -> go.Figure:
        """Create an empty figure with a message"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False),
            template=self.plotly_template,
            height=400
        )
        return fig


# Legacy compatibility - keep the old class name for existing code
class AdvancedDashboard(UnifiedDashboard):
    """Legacy class name for backward compatibility"""
    pass


def main():
    """Test the unified dashboard with sample data"""
    from chat_parser import ChatParser
    
    dashboard = UnifiedDashboard()
    
    # Load sample conversations
    parser = ChatParser()
    if parser.load_conversations('data/sample_conversations.json'):
        dashboard.load_conversations(parser.conversations)
        
        # Run the dashboard
        print("Starting Unified Dashboard...")
        dashboard.run_server(debug=True)
    else:
        print("Could not load sample conversations")


if __name__ == '__main__':
    main()