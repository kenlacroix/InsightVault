"""
Chat Interface for InsightVault
Provides a simple chat interface for ChatGPT-powered conversation analysis
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from typing import List, Optional, Callable
from chat_parser import Conversation
from chatgpt_integration import ChatGPTIntegration, create_chatgpt_integration
from datetime import datetime


class ChatInterface:
    """Simple chat interface for ChatGPT integration"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.chatgpt = None
        self.conversations = []
        self.on_message_callback = None
        
        # Initialize ChatGPT integration
        self._initialize_chatgpt()
        
        if parent:
            self.create_widgets(parent)
    
    def _initialize_chatgpt(self):
        """Initialize ChatGPT integration"""
        self.chatgpt = create_chatgpt_integration()
        if not self.chatgpt:
            print("ChatGPT integration not available - API key needed")
    
    def set_conversations(self, conversations: List[Conversation]):
        """Set conversations for analysis"""
        self.conversations = conversations
    
    def set_message_callback(self, callback: Callable[[str], None]):
        """Set callback for when messages are received"""
        self.on_message_callback = callback
    
    def create_widgets(self, parent):
        """Create the chat interface widgets"""
        # Main frame
        self.frame = ttk.Frame(parent)
        
        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(
            self.frame, 
            width=60, 
            height=20, 
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Input area
        input_frame = ttk.Frame(self.frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.message_input = ttk.Entry(input_frame)
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.message_input.bind('<Return>', self._send_message)
        
        self.send_button = ttk.Button(input_frame, text="Send", command=self._send_message)
        self.send_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Quick action buttons
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Analyze Conversations", 
                  command=self._analyze_conversations).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Programming Analysis", 
                  command=self._programming_analysis).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Growth Analysis", 
                  command=self._growth_analysis).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear Chat", 
                  command=self._clear_chat).pack(side=tk.RIGHT)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_label = ttk.Label(self.frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
    
    def _send_message(self, event=None):
        """Send a message to ChatGPT"""
        message = self.message_input.get().strip()
        if not message:
            return
        
        # Clear input
        self.message_input.delete(0, tk.END)
        
        # Display user message
        self._add_message("You", message)
        
        # Check if ChatGPT is available
        if not self.chatgpt:
            self._add_message("System", "ChatGPT is not available. Please configure your API key in Settings.")
            return
        
        # Check if conversations are loaded
        if not self.conversations:
            self._add_message("System", "No conversations loaded. Please load conversations first.")
            return
        
        # Generate response in background
        self.status_var.set("Generating response...")
        self.send_button.config(state=tk.DISABLED)
        
        def generate_response():
            try:
                response = self.chatgpt.generate_ai_response(message, self.conversations)
                self.frame.after(0, lambda: self._add_message("AI", response))
                self.frame.after(0, lambda: self.status_var.set("Ready"))
                self.frame.after(0, lambda: self.send_button.config(state=tk.NORMAL))
                
                # Call callback if set
                if self.on_message_callback:
                    self.on_message_callback(response)
                    
            except Exception as e:
                error_msg = f"Error generating response: {str(e)}"
                self.frame.after(0, lambda: self._add_message("System", error_msg))
                self.frame.after(0, lambda: self.status_var.set("Error"))
                self.frame.after(0, lambda: self.send_button.config(state=tk.NORMAL))
        
        threading.Thread(target=generate_response, daemon=True).start()
    
    def _analyze_conversations(self):
        """Analyze all conversations"""
        if not self.chatgpt:
            self._add_message("System", "ChatGPT is not available. Please configure your API key.")
            return
        
        if not self.conversations:
            self._add_message("System", "No conversations loaded.")
            return
        
        self.status_var.set("Analyzing conversations...")
        
        def analyze():
            try:
                analysis = self.chatgpt.analyze_conversations(self.conversations, "general")
                if "error" in analysis:
                    self.frame.after(0, lambda: self._add_message("System", analysis["error"]))
                else:
                    response = analysis["analysis"]["raw_response"]
                    self.frame.after(0, lambda: self._add_message("AI", f"Conversation Analysis:\n\n{response}"))
                
                self.frame.after(0, lambda: self.status_var.set("Ready"))
                
            except Exception as e:
                error_msg = f"Error analyzing conversations: {str(e)}"
                self.frame.after(0, lambda: self._add_message("System", error_msg))
                self.frame.after(0, lambda: self.status_var.set("Error"))
        
        threading.Thread(target=analyze, daemon=True).start()
    
    def _programming_analysis(self):
        """Analyze programming patterns"""
        if not self.chatgpt:
            self._add_message("System", "ChatGPT is not available. Please configure your API key.")
            return
        
        if not self.conversations:
            self._add_message("System", "No conversations loaded.")
            return
        
        self.status_var.set("Analyzing programming patterns...")
        
        def analyze():
            try:
                # Get programming patterns
                patterns = self.chatgpt.detect_programming_patterns(self.conversations)
                
                # Generate AI analysis
                analysis = self.chatgpt.analyze_conversations(self.conversations, "programming")
                
                if "error" in analysis:
                    self.frame.after(0, lambda: self._add_message("System", analysis["error"]))
                else:
                    response = analysis["analysis"]["raw_response"]
                    patterns_summary = f"""
Programming Patterns Detected:
- Languages: {', '.join(patterns['languages_detected']) or 'None'}
- Technologies: {', '.join(patterns['technologies_detected']) or 'None'}
- Concepts: {', '.join(patterns['concepts_detected']) or 'None'}
- Programming conversations: {patterns['programming_conversations_count']} out of {patterns['total_conversations']}

AI Analysis:
{response}
"""
                    self.frame.after(0, lambda: self._add_message("AI", patterns_summary))
                
                self.frame.after(0, lambda: self.status_var.set("Ready"))
                
            except Exception as e:
                error_msg = f"Error analyzing programming patterns: {str(e)}"
                self.frame.after(0, lambda: self._add_message("System", error_msg))
                self.frame.after(0, lambda: self.status_var.set("Error"))
        
        threading.Thread(target=analyze, daemon=True).start()
    
    def _growth_analysis(self):
        """Analyze growth patterns"""
        if not self.chatgpt:
            self._add_message("System", "ChatGPT is not available. Please configure your API key.")
            return
        
        if not self.conversations:
            self._add_message("System", "No conversations loaded.")
            return
        
        self.status_var.set("Analyzing growth patterns...")
        
        def analyze():
            try:
                analysis = self.chatgpt.analyze_conversations(self.conversations, "growth")
                if "error" in analysis:
                    self.frame.after(0, lambda: self._add_message("System", analysis["error"]))
                else:
                    response = analysis["analysis"]["raw_response"]
                    self.frame.after(0, lambda: self._add_message("AI", f"Growth Analysis:\n\n{response}"))
                
                self.frame.after(0, lambda: self.status_var.set("Ready"))
                
            except Exception as e:
                error_msg = f"Error analyzing growth patterns: {str(e)}"
                self.frame.after(0, lambda: self._add_message("System", error_msg))
                self.frame.after(0, lambda: self.status_var.set("Error"))
        
        threading.Thread(target=analyze, daemon=True).start()
    
    def _add_message(self, sender: str, message: str):
        """Add a message to the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M")
        
        # Format message
        formatted_message = f"[{timestamp}] {sender}: {message}\n\n"
        
        # Add to display
        self.chat_display.insert(tk.END, formatted_message)
        self.chat_display.see(tk.END)
        
        self.chat_display.config(state=tk.DISABLED)
    
    def _clear_chat(self):
        """Clear the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self._add_message("System", "Chat cleared.")
    
    def pack(self, **kwargs):
        """Pack the chat interface"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the chat interface"""
        self.frame.grid(**kwargs)


# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("InsightVault Chat Interface")
    root.geometry("600x500")
    
    chat = ChatInterface()
    chat.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Add welcome message
    chat._add_message("System", "Welcome to InsightVault Chat! Load conversations and start chatting with AI.")
    
    root.mainloop() 