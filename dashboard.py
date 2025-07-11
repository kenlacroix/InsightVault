"""
Advanced Interactive Dashboard for InsightVault
Phase 3: Advanced Analytics & Visualization

Provides comprehensive dashboard with Plotly/Dash for real-time conversation analytics,
interactive charts, and export capabilities.
"""

import os
import json
import webbrowser
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
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

from chat_parser import Conversation
from analytics_engine import AnalyticsEngine, AnalyticsData


class AdvancedDashboard:
    """Advanced interactive dashboard for InsightVault analytics"""
    
    def __init__(self, config_path: str = 'config.json'):
        self.config_path = config_path
        self.analytics_engine = AnalyticsEngine(config_path)
        self.conversations: List[Conversation] = []
        self.analytics_data: Optional[AnalyticsData] = None
        
        # Dashboard state
        self.app = None
        self.server_running = False
        
        # Color themes
        self.colors = {
            'primary': '#3498db',
            'secondary': '#2ecc71', 
            'danger': '#e74c3c',
            'warning': '#f39c12',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'success': '#28a745'
        }
        
        # Initialize components
        self._initialize_dashboard()
    
    def _initialize_dashboard(self):
        """Initialize the Dash application"""
        self.app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
            suppress_callback_exceptions=True
        )
        
        self.app.title = "InsightVault - Advanced Analytics Dashboard"
        
        # Setup callbacks
        self._setup_callbacks()
    
    def load_conversations(self, conversations: List[Conversation]) -> bool:
        """Load conversations into the dashboard"""
        try:
            self.conversations = conversations
            self.analytics_data = self.analytics_engine.analyze_conversations(conversations)
            return True
        except Exception as e:
            print(f"Error loading conversations: {e}")
            return False
    
    def create_layout(self) -> html.Div:
        """Create the main dashboard layout"""
        if not self.analytics_data:
            return self._create_empty_state()
        
        return html.Div([
            dcc.Store(id='conversation-data'),
            dcc.Store(id='analytics-data'),
            
            # Header
            self._create_header(),
            
            # Main content
            dbc.Container([
                # Overview cards
                self._create_overview_cards(),
                
                html.Hr(),
                
                # Main charts row
                dbc.Row([
                    dbc.Col([
                        self._create_sentiment_timeline_card()
                    ], width=12)
                ], className="mb-4"),
                
                # Second row
                dbc.Row([
                    dbc.Col([
                        self._create_emotional_patterns_card()
                    ], width=6),
                    dbc.Col([
                        self._create_growth_metrics_card()
                    ], width=6)
                ], className="mb-4"),
                
                # Third row
                dbc.Row([
                    dbc.Col([
                        self._create_topic_analysis_card()
                    ], width=6),
                    dbc.Col([
                        self._create_conversation_insights_card()
                    ], width=6)
                ], className="mb-4"),
                
                # Fourth row - New Phase 3 features
                dbc.Row([
                    dbc.Col([
                        self._create_breakthrough_moments_card()
                    ], width=6),
                    dbc.Col([
                        self._create_writing_style_card()
                    ], width=6)
                ], className="mb-4"),
                
                # Fifth row - Goal achievement
                dbc.Row([
                    dbc.Col([
                        self._create_goal_achievement_card()
                    ], width=12)
                ], className="mb-4"),
                
                # Export section
                self._create_export_section(),
                
            ], fluid=True)
        ])
    
    def _create_empty_state(self) -> html.Div:
        """Create layout when no data is loaded"""
        return dbc.Container([
            dbc.Alert([
                html.H4("Welcome to InsightVault Advanced Dashboard", className="alert-heading"),
                html.P("No conversation data loaded. Please load conversations to begin analysis."),
                html.Hr(),
                html.P("Use the main application to load your ChatGPT conversations and then access this dashboard.", className="mb-0")
            ], color="info", className="mt-5")
        ])
    
    def _create_header(self) -> dbc.Navbar:
        """Create dashboard header"""
        return dbc.Navbar(
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.Img(src="/assets/logo.png", height="30px", className="me-2") if os.path.exists("assets/logo.png") else None,
                        dbc.NavbarBrand("InsightVault - Advanced Analytics", className="ms-2")
                    ], width="auto"),
                    dbc.Col([
                        dbc.Nav([
                            dbc.NavItem(dbc.Button("Refresh Data", id="refresh-btn", color="outline-light", size="sm")),
                            dbc.NavItem(dbc.Button("Export Dashboard", id="export-btn", color="outline-light", size="sm", className="ms-2"))
                        ], navbar=True)
                    ], width="auto")
                ], align="center", className="g-0 w-100", justify="between")
            ], fluid=True),
            color="primary",
            dark=True,
            className="mb-4"
        )
    
    def _create_overview_cards(self) -> dbc.Row:
        """Create overview statistics cards"""
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
                "Top Themes",
                len(self.analytics_data.top_tags),
                "fas fa-tags",
                "warning"
            )
        ]
        
        return dbc.Row([
            dbc.Col(card, width=3) for card in cards
        ], className="mb-4")
    
    def _create_stat_card(self, title: str, value: Any, icon: str, color: str) -> dbc.Card:
        """Create a statistics card"""
        return dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H4(str(value), className="card-title mb-0"),
                        html.P(title, className="card-text text-muted")
                    ], width=8),
                    dbc.Col([
                        html.I(className=f"{icon} fa-2x text-{color}")
                    ], width=4, className="text-center")
                ], align="center")
            ])
        ], className="h-100")
    
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
    
    def _create_conversation_insights_card(self) -> dbc.Card:
        """Create conversation insights and patterns card"""
        return dbc.Card([
            dbc.CardHeader([
                html.H5("Conversation Insights", className="mb-0")
            ]),
            dbc.CardBody([
                self._create_insights_content()
            ])
        ])
    
    def _create_export_section(self) -> dbc.Card:
        """Create export options section"""
        return dbc.Card([
            dbc.CardHeader([
                html.H5("Export & Reports", className="mb-0")
            ]),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.ButtonGroup([
                            dbc.Button("Export PDF Report", id="export-pdf-btn", color="primary"),
                            dbc.Button("Export Excel", id="export-excel-btn", color="success"),
                            dbc.Button("Export JSON", id="export-json-btn", color="info")
                        ], className="me-2"),
                        dbc.ButtonGroup([
                            dbc.Button("Share Dashboard", id="share-btn", color="secondary"),
                            dbc.Button("Schedule Report", id="schedule-btn", color="warning")
                        ])
                    ], width=12)
                ]),
                html.Hr(),
                html.Div(id="export-status", className="mt-2")
            ])
        ], className="mt-4")
    
    def _create_sentiment_timeline_figure(self) -> go.Figure:
        """Create sentiment timeline visualization"""
        if not self.analytics_data or not self.analytics_data.sentiment_trends:
            return go.Figure().add_annotation(text="No sentiment data available", showarrow=False)
        
        sentiment_trends = self.analytics_data.sentiment_trends
        months = sorted(sentiment_trends.keys())
        sentiments = [sentiment_trends[month]['avg_sentiment'] for month in months]
        counts = [sentiment_trends[month]['conversation_count'] for month in months]
        
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
        fig.add_hline(y=0, line_dash="dash", line_color="gray", row=1, col=1)
        fig.add_hrect(y0=0.1, y1=1, fillcolor="rgba(46, 204, 113, 0.1)", line_width=0, row=1, col=1)
        fig.add_hrect(y0=-1, y1=-0.1, fillcolor="rgba(231, 76, 60, 0.1)", line_width=0, row=1, col=1)
        
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
            showlegend=False
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
            height=400
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
            height=400
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
    
    def _create_breakthrough_content(self) -> html.Div:
        """Create breakthrough moments content display"""
        if not self.analytics_data or not self.analytics_data.breakthrough_moments:
            return html.Div([
                html.P("No breakthrough moments detected in your conversations.", 
                       className="text-muted text-center")
            ])
        
        breakthroughs = self.analytics_data.breakthrough_moments[:5]  # Show top 5
        
        breakthrough_cards = []
        for breakthrough in breakthroughs:
            card = dbc.Card([
                dbc.CardBody([
                    html.H6(breakthrough['title'], className="card-title"),
                    html.P(f"Date: {breakthrough['date'][:10]}", className="text-muted small"),
                    html.P(f"Score: {breakthrough['breakthrough_score']:.1f}", 
                           className="text-success small"),
                    html.P(breakthrough['summary'], className="card-text small"),
                    html.Div([
                        dbc.Badge(kw, color="info", className="me-1") 
                        for kw in breakthrough['detected_keywords'][:3]
                    ])
                ])
            ], className="mb-2")
            breakthrough_cards.append(card)
        
        return html.Div(breakthrough_cards)
    
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
    
    def _create_wordcloud(self) -> html.Div:
        """Create word cloud visualization"""
        if not self.conversations:
            return html.Div("No conversation data available for word cloud")
        
        try:
            # Combine all conversation text
            all_text = ' '.join([conv.get_full_text() for conv in self.conversations])
            
            # Generate word cloud
            wordcloud = WordCloud(
                width=500, 
                height=300,
                background_color='white',
                max_words=100,
                colormap='viridis'
            ).generate(all_text)
            
            # Save word cloud as image
            os.makedirs('assets', exist_ok=True)
            wordcloud_path = 'assets/wordcloud.png'
            wordcloud.to_file(wordcloud_path)
            
            return html.Div([
                html.Img(
                    src='/assets/wordcloud.png',
                    style={'width': '100%', 'height': 'auto'}
                )
            ])
            
        except Exception as e:
            return html.Div(f"Error generating word cloud: {str(e)}")
    
    def _create_insights_content(self) -> html.Div:
        """Create insights content section"""
        if not self.analytics_data:
            return html.Div("No analytics data available")
        
        insights = []
        
        # Conversation frequency insight
        if self.analytics_data.conversation_count > 0:
            date_range = self.analytics_data.date_range
            days_span = (date_range[1] - date_range[0]).days
            if days_span > 0:
                freq = self.analytics_data.conversation_count / (days_span / 30)  # per month
                insights.append(
                    dbc.Alert([
                        html.H6("Conversation Frequency", className="alert-heading"),
                        html.P(f"You have {freq:.1f} conversations per month on average.")
                    ], color="info")
                )
        
        # Growth insight
        if self.analytics_data.growth_metrics:
            positive_growth = sum(1 for v in self.analytics_data.growth_metrics.values() if v > 0)
            total_metrics = len(self.analytics_data.growth_metrics)
            if total_metrics > 0:
                growth_percentage = (positive_growth / total_metrics) * 100
                color = "success" if growth_percentage > 50 else "warning"
                insights.append(
                    dbc.Alert([
                        html.H6("Growth Progress", className="alert-heading"),
                        html.P(f"{growth_percentage:.0f}% of your growth metrics show positive trends.")
                    ], color=color)
                )
        
        # Top themes insight
        if self.analytics_data.top_tags:
            top_tag = self.analytics_data.top_tags[0]
            insights.append(
                dbc.Alert([
                    html.H6("Most Frequent Theme", className="alert-heading"),
                    html.P(f"'{top_tag[0]}' appears in {top_tag[1]} conversations.")
                ], color="primary")
            )
        
        return html.Div(insights) if insights else html.Div("No insights available")
    
    def _setup_callbacks(self):
        """Setup dashboard callbacks"""
        
        @self.app.callback(
            Output('conversation-data', 'data'),
            Output('analytics-data', 'data'),
            Input('refresh-btn', 'n_clicks'),
            prevent_initial_call=True
        )
        def refresh_data(n_clicks):
            if n_clicks and self.conversations:
                self.analytics_data = self.analytics_engine.analyze_conversations(self.conversations)
                return len(self.conversations), "refreshed"
            return dash.no_update, dash.no_update
        
        @self.app.callback(
            Output('export-status', 'children'),
            [Input('export-pdf-btn', 'n_clicks'),
             Input('export-excel-btn', 'n_clicks'),
             Input('export-json-btn', 'n_clicks')],
            prevent_initial_call=True
        )
        def handle_exports(pdf_clicks, excel_clicks, json_clicks):
            ctx = callback_context
            if not ctx.triggered:
                return ""
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                if button_id == 'export-pdf-btn':
                    path = self.export_pdf_report(f"output/dashboard_report_{timestamp}.pdf")
                    return dbc.Alert(f"PDF report exported to {path}", color="success", dismissable=True)
                
                elif button_id == 'export-excel-btn':
                    path = self.export_excel_report(f"output/dashboard_data_{timestamp}.xlsx")
                    return dbc.Alert(f"Excel report exported to {path}", color="success", dismissable=True)
                
                elif button_id == 'export-json-btn':
                    path = self.export_json_data(f"output/dashboard_data_{timestamp}.json")
                    return dbc.Alert(f"JSON data exported to {path}", color="success", dismissable=True)
                    
            except Exception as e:
                return dbc.Alert(f"Export failed: {str(e)}", color="danger", dismissable=True)
            
            return ""
        
        @self.app.callback(
            Output('breakthrough-content', 'children'),
            [Input('refresh-btn', 'n_clicks')],
            prevent_initial_call=False
        )
        def update_breakthrough_content(n_clicks):
            return self._create_breakthrough_content()
    
    def export_pdf_report(self, output_path: str) -> str:
        """Export comprehensive PDF report"""
        try:
            from fpdf import FPDF
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'InsightVault - Advanced Analytics Report', ln=True, align='C')
            
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', ln=True)
            pdf.ln(10)
            
            if self.analytics_data:
                # Summary statistics
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, 'Summary Statistics', ln=True)
                pdf.set_font('Arial', '', 10)
                
                stats = [
                    f"Total Conversations: {self.analytics_data.conversation_count}",
                    f"Total Messages: {self.analytics_data.total_messages}",
                    f"Date Range: {self.analytics_data.date_range[0].strftime('%Y-%m-%d')} to {self.analytics_data.date_range[1].strftime('%Y-%m-%d')}",
                    f"Top Themes: {len(self.analytics_data.top_tags)}"
                ]
                
                for stat in stats:
                    pdf.cell(0, 8, stat, ln=True)
                
                pdf.ln(10)
                
                # Top tags
                if self.analytics_data.top_tags:
                    pdf.set_font('Arial', 'B', 14)
                    pdf.cell(0, 10, 'Most Frequent Themes', ln=True)
                    pdf.set_font('Arial', '', 10)
                    
                    for tag, count in self.analytics_data.top_tags[:10]:
                        pdf.cell(0, 6, f"• {tag}: {count} occurrences", ln=True)
            
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            pdf.output(output_path)
            return output_path
            
        except Exception as e:
            print(f"Error creating PDF report: {e}")
            return ""
    
    def export_excel_report(self, output_path: str) -> str:
        """Export comprehensive Excel report with multiple sheets"""
        try:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Summary sheet
                if self.analytics_data:
                    summary_data = {
                        'Metric': ['Total Conversations', 'Total Messages', 'Start Date', 'End Date'],
                        'Value': [
                            self.analytics_data.conversation_count,
                            self.analytics_data.total_messages,
                            self.analytics_data.date_range[0].strftime('%Y-%m-%d'),
                            self.analytics_data.date_range[1].strftime('%Y-%m-%d')
                        ]
                    }
                    pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                    
                    # Tags sheet
                    if self.analytics_data.top_tags:
                        tags_data = pd.DataFrame(self.analytics_data.top_tags, columns=['Tag', 'Count'])
                        tags_data.to_excel(writer, sheet_name='Tags', index=False)
                    
                    # Growth metrics sheet
                    if self.analytics_data.growth_metrics:
                        growth_data = pd.DataFrame([
                            {'Metric': k, 'Growth_Rate': v} 
                            for k, v in self.analytics_data.growth_metrics.items()
                        ])
                        growth_data.to_excel(writer, sheet_name='Growth_Metrics', index=False)
                
                # Conversations sheet
                if self.conversations:
                    conv_data = []
                    for conv in self.conversations:
                        conv_data.append({
                            'Title': conv.title,
                            'Date': conv.create_date.strftime('%Y-%m-%d'),
                            'Message_Count': len(conv.messages),
                            'Character_Count': len(conv.get_full_text()),
                            'Tags': ', '.join(conv.tags)
                        })
                    
                    pd.DataFrame(conv_data).to_excel(writer, sheet_name='Conversations', index=False)
            
            return output_path
            
        except Exception as e:
            print(f"Error creating Excel report: {e}")
            return ""
    
    def export_json_data(self, output_path: str) -> str:
        """Export analytics data as JSON"""
        try:
            data = {
                'generated_at': datetime.now().isoformat(),
                'conversations_count': len(self.conversations),
                'analytics': {}
            }
            
            if self.analytics_data:
                data['analytics'] = {
                    'conversation_count': self.analytics_data.conversation_count,
                    'total_messages': self.analytics_data.total_messages,
                    'date_range': [
                        self.analytics_data.date_range[0].isoformat(),
                        self.analytics_data.date_range[1].isoformat()
                    ],
                    'top_tags': self.analytics_data.top_tags,
                    'emotional_patterns': self.analytics_data.emotional_patterns,
                    'growth_metrics': self.analytics_data.growth_metrics,
                    'engagement_stats': self.analytics_data.engagement_stats
                }
            
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            return output_path
            
        except Exception as e:
            print(f"Error exporting JSON data: {e}")
            return ""
    
    def run_server(self, host: str = '127.0.0.1', port: int = 8050, debug: bool = False) -> str:
        """Run the dashboard server"""
        if not self.conversations:
            print("No conversations loaded. Please load conversations first.")
            return ""
        
        # Set layout
        self.app.layout = self.create_layout()
        
        try:
            print(f"🚀 Starting InsightVault Advanced Dashboard...")
            print(f"📊 Dashboard URL: http://{host}:{port}")
            print(f"📈 Loaded {len(self.conversations)} conversations")
            
            # Open browser automatically
            dashboard_url = f"http://{host}:{port}"
            
            if not debug:
                import threading
                threading.Timer(1.5, lambda: webbrowser.open(dashboard_url)).start()
            
            self.server_running = True
            self.app.run_server(host=host, port=port, debug=debug)
            
            return dashboard_url
            
        except Exception as e:
            print(f"Error running dashboard server: {e}")
            return ""
    
    def create_static_dashboard(self, output_path: str = None) -> str:
        """Create a static HTML dashboard file"""
        if not output_path:
            output_path = f"output/static_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        try:
            # Create figures
            sentiment_fig = self._create_sentiment_timeline_figure()
            emotional_fig = self._create_emotional_patterns_figure()
            growth_fig = self._create_growth_metrics_figure()
            topic_fig = self._create_topic_clusters_figure()
            
            # Generate HTML
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>InsightVault - Advanced Analytics Dashboard</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
                    .dashboard-header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem 0; }}
                    .stat-card {{ border-left: 4px solid #007bff; }}
                </style>
            </head>
            <body>
                <div class="dashboard-header">
                    <div class="container">
                        <h1>InsightVault - Advanced Analytics Dashboard</h1>
                        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                </div>
                
                <div class="container mt-4">
                    <div class="row mb-4">
                        <div class="col-md-3">
                            <div class="card stat-card">
                                <div class="card-body">
                                    <h5>{self.analytics_data.conversation_count if self.analytics_data else 0}</h5>
                                    <p class="text-muted">Total Conversations</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card stat-card">
                                <div class="card-body">
                                    <h5>{self.analytics_data.total_messages if self.analytics_data else 0}</h5>
                                    <p class="text-muted">Total Messages</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card stat-card">
                                <div class="card-body">
                                    <h5>{len(self.analytics_data.top_tags) if self.analytics_data else 0}</h5>
                                    <p class="text-muted">Unique Themes</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card stat-card">
                                <div class="card-body">
                                    <h5>{len(self.conversations)}</h5>
                                    <p class="text-muted">Data Points</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-12 mb-4">
                            <div class="card">
                                <div class="card-header">
                                    <h5>Emotional Journey Timeline</h5>
                                </div>
                                <div class="card-body">
                                    <div id="sentiment-chart"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6 mb-4">
                            <div class="card">
                                <div class="card-header">
                                    <h5>Emotional Patterns</h5>
                                </div>
                                <div class="card-body">
                                    <div id="emotional-chart"></div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6 mb-4">
                            <div class="card">
                                <div class="card-header">
                                    <h5>Growth Metrics</h5>
                                </div>
                                <div class="card-body">
                                    <div id="growth-chart"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-12 mb-4">
                            <div class="card">
                                <div class="card-header">
                                    <h5>Topic Analysis</h5>
                                </div>
                                <div class="card-body">
                                    <div id="topic-chart"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <script>
                    Plotly.newPlot('sentiment-chart', {sentiment_fig.to_json()});
                    Plotly.newPlot('emotional-chart', {emotional_fig.to_json()});
                    Plotly.newPlot('growth-chart', {growth_fig.to_json()});
                    Plotly.newPlot('topic-chart', {topic_fig.to_json()});
                </script>
            </body>
            </html>
            """
            
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return output_path
            
        except Exception as e:
            print(f"Error creating static dashboard: {e}")
            return ""


def main():
    """Test the dashboard with sample data"""
    from chat_parser import ChatParser
    
    dashboard = AdvancedDashboard()
    
    # Load sample conversations
    parser = ChatParser()
    if parser.load_conversations('data/sample_conversations.json'):
        dashboard.load_conversations(parser.conversations)
        
        # Run the dashboard
        print("Starting Advanced Dashboard...")
        dashboard.run_server(debug=True)
    else:
        print("Could not load sample conversations")


if __name__ == '__main__':
    main()