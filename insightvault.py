#!/usr/bin/env python3
"""
InsightVault Comprehensive Launcher
A unified script for starting, diagnosing, and managing InsightVault services.
"""

import subprocess
import sys
import os
import time
import signal
import threading
import platform
import argparse
import requests
import socket
import json
from pathlib import Path
from typing import Dict, List, Optional

class InsightVaultLauncher:
    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        self.running = True
        self.backend_process = None
        self.frontend_process = None
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        
        # Service health tracking
        self.service_status = {
            'backend': {'status': 'unknown', 'last_check': None, 'startup_time': None},
            'frontend': {'status': 'unknown', 'last_check': None, 'startup_time': None}
        }
        
        # Configuration
        self.config = {
            'max_startup_attempts': 3,
            'health_check_timeout': 10,
            'startup_timeout': 30,
            'auto_restart_failed_services': True,
            'enable_detailed_logging': True
        }

    def log(self, message: str, level: str = "INFO", service: str | None = None):
        """Enhanced logging with service context and timestamps."""
        timestamp = time.strftime("%H:%M:%S")
        service_prefix = f"[{service}] " if service else ""
        level_emoji = {
            "INFO": "ℹ️",
            "SUCCESS": "✅", 
            "WARNING": "⚠️",
            "ERROR": "❌",
            "DEBUG": "🔍"
        }.get(level, "ℹ️")
        
        print(f"[{timestamp}] {level}: {service_prefix}{message}")

    def check_requirements(self) -> bool:
        """Check system requirements."""
        self.log("Checking system requirements...", "INFO", "SYSTEM")
        
        requirements_met = True
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            self.log(f"Python 3.8+ required, found {python_version.major}.{python_version.minor}", "ERROR", "SYSTEM")
            requirements_met = False
        else:
            self.log(f"Python {python_version.major}.{python_version.minor}.{python_version.micro} ✓", "SUCCESS", "SYSTEM")
        
        # Check Node.js
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                node_version = result.stdout.strip()
                self.log(f"Node.js {node_version} ✓", "SUCCESS", "SYSTEM")
            else:
                self.log("Node.js not found", "ERROR", "SYSTEM")
                requirements_met = False
        except FileNotFoundError:
            self.log("Node.js not found", "ERROR", "SYSTEM")
            requirements_met = False
        
        # Check npm
        npm_found = self.check_npm()
        if not npm_found:
            requirements_met = False
        
        # Check port availability
        if self.check_port_in_use(8000):
            self.log("Port 8000 is already in use", "WARNING", "SYSTEM")
        if self.check_port_in_use(3000):
            self.log("Port 3000 is already in use", "WARNING", "SYSTEM")
        
        return requirements_met

    def check_npm(self) -> bool:
        """Check npm availability with PATH fixing."""
        try:
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                npm_version = result.stdout.strip()
                self.log(f"npm {npm_version} ✓", "SUCCESS", "SYSTEM")
                return True
        except FileNotFoundError:
            pass
        
        # Try to find npm in common locations
        npm_paths = [
            r"C:\Program Files\nodejs\npm.cmd",
            r"C:\Program Files (x86)\nodejs\npm.cmd",
            "/usr/local/bin/npm",
            "/usr/bin/npm"
        ]
        
        for npm_path in npm_paths:
            if os.path.exists(npm_path):
                self.log(f"npm found at: {npm_path}", "INFO", "SYSTEM")
                if self.is_windows:
                    # Add to PATH for current session
                    current_path = os.environ.get('PATH', '')
                    nodejs_dir = os.path.dirname(npm_path)
                    if nodejs_dir not in current_path:
                        os.environ['PATH'] = f"{nodejs_dir};{current_path}"
                        self.log("npm PATH fixed automatically", "SUCCESS", "SYSTEM")
                        
                        # Verify npm now works
                        try:
                            result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
                            if result.returncode == 0:
                                self.log(f"npm verification successful: {result.stdout.strip()}", "SUCCESS", "SYSTEM")
                                return True
                        except:
                            pass
                        
                        self.log("npm PATH fixed but still not accessible", "ERROR", "SYSTEM")
                        return False
                    else:
                        # npm is in PATH but not working, try using full path
                        try:
                            result = subprocess.run([npm_path, "--version"], capture_output=True, text=True)
                            if result.returncode == 0:
                                self.log(f"npm working with full path: {result.stdout.strip()}", "SUCCESS", "SYSTEM")
                                return True
                        except:
                            pass
                break
        
        self.log("npm not found or not accessible", "ERROR", "SYSTEM")
        return False

    def check_port_in_use(self, port: int) -> bool:
        """Check if a port is in use."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                return result == 0
        except:
            return False

    def cleanup_ports(self):
        """Clean up ports that might be in use."""
        self.log("Cleaning up ports...", "INFO", "SYSTEM")
        
        for port in [8000, 3000]:
            if self.check_port_in_use(port):
                self.log(f"Port {port} is in use, attempting to free it...", "INFO", "SYSTEM")
                if self.kill_process_on_port(port):
                    self.log(f"Port {port} freed successfully", "SUCCESS", "SYSTEM")
                else:
                    self.log(f"Could not free port {port}", "WARNING", "SYSTEM")

    def kill_process_on_port(self, port: int) -> bool:
        """Kill process using a specific port (Windows only)."""
        if not self.is_windows:
            return False
        
        try:
            # Find process using the port
            result = subprocess.run(
                f'netstat -ano | findstr :{port}',
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if f':{port}' in line and 'LISTENING' in line:
                        # Extract PID
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            self.log(f"Found process {pid} using port {port}", "INFO", "SYSTEM")
                            
                            # Check if process actually exists
                            check_result = subprocess.run(
                                f'tasklist /FI "PID eq {pid}"',
                                shell=True,
                                capture_output=True,
                                text=True
                            )
                            
                            if check_result.returncode == 0 and pid in check_result.stdout:
                                # Process exists, kill it
                                kill_result = subprocess.run(
                                    f'taskkill /PID {pid} /F',
                                    shell=True,
                                    capture_output=True,
                                    text=True
                                )
                                
                                if kill_result.returncode == 0:
                                    self.log(f"Killed process {pid} on port {port}", "SUCCESS", "SYSTEM")
                                    time.sleep(2)  # Wait for port to be released
                                    return True
                                else:
                                    self.log(f"Failed to kill process {pid}: {kill_result.stderr}", "ERROR", "SYSTEM")
                            else:
                                # Process doesn't exist, port might be stale
                                self.log(f"Process {pid} not found, port {port} may be stale", "WARNING", "SYSTEM")
                                # Try to force release the port
                                try:
                                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                                    sock.bind(('localhost', port))
                                    sock.close()
                                    self.log(f"Port {port} released successfully", "SUCCESS", "SYSTEM")
                                    return True
                                except:
                                    pass
            else:
                # No process found, port might be available
                self.log(f"No process found using port {port}", "INFO", "SYSTEM")
                return True
            
            return False
            
        except Exception as e:
            self.log(f"Error killing process on port {port}: {e}", "ERROR", "SYSTEM")
            return False

    def run_diagnostics(self) -> Dict:
        """Run comprehensive diagnostics."""
        self.log("Running diagnostics...", "INFO", "SYSTEM")
        
        results = {
            'timestamp': time.time(),
            'system_info': {},
            'backend': {},
            'frontend': {},
            'network': {},
            'recommendations': []
        }
        
        # System info
        import platform
        results['system_info'] = {
            'platform': platform.system(),
            'platform_version': platform.release(),
            'python_version': sys.version,
            'architecture': platform.architecture()[0],
            'processor': platform.processor()
        }
        
        # Backend diagnostics
        backend_results = self.diagnose_backend()
        results['backend'] = backend_results
        
        # Frontend diagnostics
        frontend_results = self.diagnose_frontend()
        results['frontend'] = frontend_results
        
        # Network diagnostics
        network_results = self.diagnose_network()
        results['network'] = network_results
        
        # Generate recommendations
        results['recommendations'] = self.generate_recommendations(results)
        
        return results

    def diagnose_backend(self) -> Dict:
        """Diagnose backend issues."""
        results = {
            'status': 'unknown',
            'tests': [],
            'issues': []
        }
        
        # Test 1: Directory structure
        if os.path.exists("backend"):
            results['tests'].append({'name': 'Directory exists', 'status': 'pass'})
        else:
            results['tests'].append({'name': 'Directory exists', 'status': 'fail', 'error': 'Backend directory not found'})
            results['issues'].append("Backend directory missing")
        
        # Test 2: Key files
        key_files = [
            "backend/app/main.py",
            "backend/app/database.py", 
            "backend/app/models.py",
            "backend/requirements.txt"
        ]
        
        for file_path in key_files:
            if os.path.exists(file_path):
                results['tests'].append({'name': f'File exists: {file_path}', 'status': 'pass'})
            else:
                results['tests'].append({'name': f'File exists: {file_path}', 'status': 'fail', 'error': f'{file_path} not found'})
                results['issues'].append(f"Missing file: {file_path}")
        
        # Test 3: Python dependencies
        try:
            import fastapi
            results['tests'].append({'name': 'FastAPI installed', 'status': 'pass'})
        except ImportError:
            results['tests'].append({'name': 'FastAPI installed', 'status': 'fail', 'error': 'FastAPI not installed'})
            results['issues'].append("FastAPI not installed")
        
        try:
            import uvicorn
            results['tests'].append({'name': 'Uvicorn installed', 'status': 'pass'})
        except ImportError:
            results['tests'].append({'name': 'Uvicorn installed', 'status': 'fail', 'error': 'Uvicorn not installed'})
            results['issues'].append("Uvicorn not installed")
        
        # Determine status
        failed_tests = [t for t in results['tests'] if t['status'] == 'fail']
        if failed_tests:
            results['status'] = 'failed'
        else:
            results['status'] = 'healthy'
        
        return results

    def diagnose_frontend(self) -> Dict:
        """Diagnose frontend issues."""
        results = {
            'status': 'unknown',
            'tests': [],
            'issues': []
        }
        
        # Test 1: Directory structure
        if os.path.exists("frontend"):
            results['tests'].append({'name': 'Directory exists', 'status': 'pass'})
        else:
            results['tests'].append({'name': 'Directory exists', 'status': 'fail', 'error': 'Frontend directory not found'})
            results['issues'].append("Frontend directory missing")
        
        # Test 2: Key files
        key_files = [
            "frontend/package.json",
            "frontend/next.config.js",
            "frontend/src/app/page.tsx"
        ]
        
        for file_path in key_files:
            if os.path.exists(file_path):
                results['tests'].append({'name': f'File exists: {file_path}', 'status': 'pass'})
            else:
                results['tests'].append({'name': f'File exists: {file_path}', 'status': 'fail', 'error': f'{file_path} not found'})
                results['issues'].append(f"Missing file: {file_path}")
        
        # Test 3: Node.js
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                results['tests'].append({'name': 'Node.js installed', 'status': 'pass', 'version': result.stdout.strip()})
            else:
                results['tests'].append({'name': 'Node.js installed', 'status': 'fail', 'error': 'Node.js not found'})
                results['issues'].append("Node.js not installed")
        except FileNotFoundError:
            results['tests'].append({'name': 'Node.js installed', 'status': 'fail', 'error': 'Node.js not found'})
            results['issues'].append("Node.js not installed")
        
        # Test 4: npm
        try:
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                results['tests'].append({'name': 'npm installed', 'status': 'pass', 'version': result.stdout.strip()})
            else:
                results['tests'].append({'name': 'npm installed', 'status': 'fail', 'error': 'npm not found'})
                results['issues'].append("npm not installed")
        except FileNotFoundError:
            results['tests'].append({'name': 'npm installed', 'status': 'fail', 'error': 'npm not found'})
            results['issues'].append("npm not installed")
        
        # Test 5: node_modules
        if os.path.exists("frontend/node_modules"):
            results['tests'].append({'name': 'Dependencies installed', 'status': 'pass'})
        else:
            results['tests'].append({'name': 'Dependencies installed', 'status': 'fail', 'error': 'node_modules not found'})
            results['issues'].append("Frontend dependencies not installed")
        
        # Determine status
        failed_tests = [t for t in results['tests'] if t['status'] == 'fail']
        if failed_tests:
            results['status'] = 'failed'
        else:
            results['status'] = 'healthy'
        
        return results

    def diagnose_network(self) -> Dict:
        """Diagnose network issues."""
        results = {
            'tests': [],
            'issues': []
        }
        
        # Test 1: Port 8000 availability
        if self.check_port_in_use(8000):
            results['tests'].append({'name': 'Port 8000 available', 'status': 'fail', 'error': 'Port 8000 is in use'})
            results['issues'].append("Port 8000 is already in use")
        else:
            results['tests'].append({'name': 'Port 8000 available', 'status': 'pass'})
        
        # Test 2: Port 3000 availability
        if self.check_port_in_use(3000):
            results['tests'].append({'name': 'Port 3000 available', 'status': 'fail', 'error': 'Port 3000 is in use'})
            results['issues'].append("Port 3000 is already in use")
        else:
            results['tests'].append({'name': 'Port 3000 available', 'status': 'pass'})
        
        # Test 3: Localhost connectivity
        try:
            response = requests.get("http://localhost:8000", timeout=2)
            results['tests'].append({'name': 'Backend responding', 'status': 'pass'})
        except:
            results['tests'].append({'name': 'Backend responding', 'status': 'fail', 'error': 'Backend not responding'})
        
        try:
            response = requests.get("http://localhost:3000", timeout=2)
            results['tests'].append({'name': 'Frontend responding', 'status': 'pass'})
        except:
            results['tests'].append({'name': 'Frontend responding', 'status': 'fail', 'error': 'Frontend not responding'})
        
        return results

    def generate_recommendations(self, results: Dict) -> List[str]:
        """Generate recommendations based on diagnostic results."""
        recommendations = []
        
        # Backend recommendations
        backend_issues = results['backend'].get('issues', [])
        for issue in backend_issues:
            if "FastAPI not installed" in issue:
                recommendations.append("Run: pip install fastapi uvicorn")
            elif "Missing file" in issue:
                recommendations.append("Ensure all required backend files are present")
        
        # Frontend recommendations
        frontend_issues = results['frontend'].get('issues', [])
        for issue in frontend_issues:
            if "Node.js not installed" in issue:
                recommendations.append("Install Node.js from https://nodejs.org/")
            elif "npm not installed" in issue:
                recommendations.append("Install npm or check PATH configuration")
            elif "Dependencies not installed" in issue:
                recommendations.append("Run: cd frontend && npm install")
            elif "Missing file" in issue:
                recommendations.append("Ensure all required frontend files are present")
        
        # Network recommendations
        network_issues = results['network'].get('issues', [])
        for issue in network_issues:
            if "Port 8000 is already in use" in issue:
                recommendations.append("Stop other services using port 8000 or change backend port")
            elif "Port 3000 is already in use" in issue:
                recommendations.append("Stop other services using port 3000 or change frontend port")
        
        return recommendations

    def install_dependencies(self, minimal: bool = False):
        """Install dependencies for both services."""
        self.log("Installing dependencies...", "INFO", "SYSTEM")
        
        # Backend dependencies
        self.log("Installing backend dependencies...", "INFO", "BACKEND")
        try:
            requirements_file = "requirements-minimal.txt" if minimal else "requirements.txt"
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", requirements_file],
                cwd="backend",
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.log("Backend dependencies installed successfully", "SUCCESS", "BACKEND")
            else:
                self.log(f"Failed to install backend dependencies: {result.stderr}", "ERROR", "BACKEND")
        except Exception as e:
            self.log(f"Error installing backend dependencies: {e}", "ERROR", "BACKEND")
        
        # Frontend dependencies
        self.log("Installing frontend dependencies...", "INFO", "FRONTEND")
        try:
            result = subprocess.run(
                "npm install", 
                cwd="frontend", 
                shell=True, 
                capture_output=True, 
                text=True
            )
            if result.returncode == 0:
                self.log("Frontend dependencies installed successfully", "SUCCESS", "FRONTEND")
            else:
                self.log(f"Failed to install frontend dependencies: {result.stderr}", "ERROR", "FRONTEND")
        except Exception as e:
            self.log(f"Error installing frontend dependencies: {e}", "ERROR", "FRONTEND")

    def start_backend(self) -> bool:
        """Start backend server."""
        self.log("Starting backend server...", "INFO", "BACKEND")
        
        try:
            # Initialize database if needed
            self.log("Checking database initialization...", "INFO", "BACKEND")
            try:
                if self.is_windows:
                    init_cmd = f"{sys.executable} init_db.py"
                    result = subprocess.run(init_cmd, cwd="backend", shell=True, capture_output=True, text=True, timeout=30)
                else:
                    init_cmd = ["python3", "init_db.py"]
                    result = subprocess.run(init_cmd, cwd="backend", capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    self.log("Database initialized successfully", "SUCCESS", "BACKEND")
                else:
                    self.log(f"Database initialization warning: {result.stderr}", "WARNING", "BACKEND")
            except Exception as e:
                self.log(f"Database initialization check failed: {e}", "WARNING", "BACKEND")
            
            if self.is_windows:
                cmd = f"{sys.executable} -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
                self.backend_process = subprocess.Popen(
                    cmd, 
                    cwd="backend", 
                    shell=True,
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True
                )
            else:
                cmd = ["python3", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]
                self.backend_process = subprocess.Popen(
                    cmd, 
                    cwd="backend", 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True
                )
            
            # Wait for startup
            time.sleep(3)
            
            if self.backend_process.poll() is None:
                self.log("Backend server started successfully", "SUCCESS", "BACKEND")
                self.service_status['backend']['startup_time'] = time.time()
                return True
            else:
                stdout, stderr = self.backend_process.communicate()
                self.log(f"Backend process crashed!", "ERROR", "BACKEND")
                if stdout:
                    self.log(f"Backend STDOUT: {stdout}", "ERROR", "BACKEND")
                if stderr:
                    self.log(f"Backend STDERR: {stderr}", "ERROR", "BACKEND")
                return False
            
        except Exception as e:
            self.log(f"Failed to start backend: {e}", "ERROR", "BACKEND")
            return False

    def start_frontend(self) -> bool:
        """Start frontend server."""
        self.log("Starting frontend server...", "INFO", "FRONTEND")
        
        try:
            if self.is_windows:
                # Use full npm path if needed
                npm_cmd = "npm run dev"
                try:
                    result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
                    if result.returncode != 0:
                        npm_paths = [
                            r"C:\Program Files\nodejs\npm.cmd",
                            r"C:\Program Files (x86)\nodejs\npm.cmd"
                        ]
                        for npm_path in npm_paths:
                            if os.path.exists(npm_path):
                                npm_cmd = f'"{npm_path}" run dev'
                                break
                except:
                    pass
                
                self.frontend_process = subprocess.Popen(
                    npm_cmd, 
                    cwd="frontend", 
                    shell=True,
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True
                )
            else:
                self.frontend_process = subprocess.Popen(
                    ["npm", "run", "dev"], 
                    cwd="frontend", 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True
                )
            
            # Wait for startup
            time.sleep(5)
            
            if self.frontend_process.poll() is None:
                self.log("Frontend server started successfully", "SUCCESS", "FRONTEND")
                self.service_status['frontend']['startup_time'] = time.time()
                return True
            else:
                stdout, stderr = self.frontend_process.communicate()
                self.log(f"Frontend process crashed!", "ERROR", "FRONTEND")
                if stdout:
                    self.log(f"Frontend STDOUT: {stdout}", "ERROR", "FRONTEND")
                if stderr:
                    self.log(f"Frontend STDERR: {stderr}", "ERROR", "FRONTEND")
                return False
            
        except Exception as e:
            self.log(f"Failed to start frontend: {e}", "ERROR", "FRONTEND")
            return False

    def verify_service_health(self, service: str) -> bool:
        """Verify that a service is actually responding."""
        url = self.backend_url if service == 'backend' else self.frontend_url
        timeout = 10 if service == 'frontend' else 5  # Frontend takes longer to start
        
        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except:
            return False

    def start_services(self, auto_install: bool = False, minimal: bool = False) -> bool:
        """Start both services with optional dependency installation."""
        self.log("🚀 Starting InsightVault services...", "INFO", "SYSTEM")
        
        # Check requirements
        if not self.check_requirements():
            self.log("Requirements check failed", "ERROR", "SYSTEM")
            return False
        
        # Install dependencies if requested
        if auto_install:
            self.install_dependencies(minimal=minimal)
        
        # Start backend
        if not self.start_backend():
            self.log("Failed to start backend", "ERROR", "SYSTEM")
            return False
        
        # Start frontend
        if not self.start_frontend():
            self.log("Failed to start frontend", "ERROR", "SYSTEM")
            self.cleanup()
            return False
        
        # Verify services are responding
        backend_ok = self.verify_service_health('backend')
        frontend_ok = self.verify_service_health('frontend')
        
        if backend_ok and frontend_ok:
            self.log("🎉 InsightVault is ready!", "SUCCESS", "SYSTEM")
            self.log(f"Frontend: {self.frontend_url}", "INFO", "SYSTEM")
            self.log(f"Backend: {self.backend_url}", "INFO", "SYSTEM")
            self.log("Press Ctrl+C to stop all services", "INFO", "SYSTEM")
            return True
        else:
            if not backend_ok:
                self.log("Backend is not responding", "ERROR", "SYSTEM")
            if not frontend_ok:
                self.log("Frontend is not responding", "ERROR", "SYSTEM")
            return False

    def monitor_services(self):
        """Monitor services for crashes."""
        while self.running:
            if self.backend_process and self.backend_process.poll() is not None:
                self.log("Backend process has stopped", "ERROR", "SYSTEM")
                break
            
            if self.frontend_process and self.frontend_process.poll() is not None:
                self.log("Frontend process has stopped", "ERROR", "SYSTEM")
                break
            
            time.sleep(5)

    def cleanup(self):
        """Clean up processes."""
        if self.backend_process:
            self.log("Stopping backend...", "INFO", "SYSTEM")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        if self.frontend_process:
            self.log("Stopping frontend...", "INFO", "SYSTEM")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
        
        self.log("Cleanup complete", "INFO", "SYSTEM")

    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.log("Shutting down...", "INFO", "SYSTEM")
        self.running = False
        self.cleanup()
        sys.exit(0)

    def run_interactive(self):
        """Run in interactive mode with monitoring."""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Start monitoring
        monitor_thread = threading.Thread(target=self.monitor_services, daemon=True)
        monitor_thread.start()
        
        # Keep running until shutdown
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
        self.cleanup()

def print_help():
    """Print comprehensive help information."""
    help_text = """
InsightVault Comprehensive Launcher
===================================

A unified script for starting, diagnosing, and managing InsightVault services.

USAGE:
    python insightvault.py [COMMAND] [OPTIONS]

COMMANDS:
    start           Start InsightVault services
    quick           Quick start (skip dependency installation)
    diagnose        Run comprehensive diagnostics
    cleanup         Clean up ports and processes
    install         Install dependencies only
    help            Show this help message

OPTIONS:
    --auto-install  Automatically install dependencies before starting
    --minimal       Use minimal requirements (avoid Rust compilation)
    --no-monitor    Don't monitor services (exit after starting)
    --save-report   Save diagnostic report to file
    --verbose       Enable verbose logging

EXAMPLES:
    # Quick start (recommended for development)
    python insightvault.py quick

    # Start with automatic dependency installation
    python insightvault.py start --auto-install

    # Start with minimal dependencies (avoid Rust issues)
    python insightvault.py start --auto-install --minimal

    # Run diagnostics only
    python insightvault.py diagnose

    # Clean up ports and processes
    python insightvault.py cleanup

    # Install dependencies only
    python insightvault.py install --minimal

FEATURES:
    ✅ Automatic port cleanup
    ✅ npm PATH fixing for Windows
    ✅ Comprehensive diagnostics
    ✅ Service monitoring
    ✅ Graceful shutdown
    ✅ Unicode issue detection
    ✅ Dependency management
    ✅ Health checking

TROUBLESHOOTING:
    If you encounter issues:
    1. Run: python insightvault.py diagnose
    2. Check the recommendations
    3. Try: python insightvault.py cleanup
    4. Use --minimal flag to avoid Rust compilation issues
    """
    print(help_text)

def main():
    """Main entry point with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="InsightVault Comprehensive Launcher",
        add_help=False
    )
    
    parser.add_argument('command', nargs='?', default='help',
                       choices=['start', 'quick', 'diagnose', 'cleanup', 'install', 'help'],
                       help='Command to execute')
    
    parser.add_argument('--auto-install', action='store_true',
                       help='Automatically install dependencies before starting')
    parser.add_argument('--minimal', action='store_true',
                       help='Use minimal requirements (avoid Rust compilation)')
    parser.add_argument('--no-monitor', action='store_true',
                       help='Don\'t monitor services (exit after starting)')
    parser.add_argument('--save-report', action='store_true',
                       help='Save diagnostic report to file')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('-h', '--help', action='store_true',
                       help='Show help message')
    
    args = parser.parse_args()
    
    # Show help if requested
    if args.help or args.command == 'help':
        print_help()
        return
    
    # Create launcher instance
    launcher = InsightVaultLauncher()
    
    # Execute command
    if args.command == 'start':
        success = launcher.start_services(auto_install=args.auto_install, minimal=args.minimal)
        if success and not args.no_monitor:
            launcher.run_interactive()
        elif not success:
            sys.exit(1)
    
    elif args.command == 'quick':
        success = launcher.start_services(auto_install=False, minimal=False)
        if success and not args.no_monitor:
            launcher.run_interactive()
        elif not success:
            sys.exit(1)
    
    elif args.command == 'diagnose':
        print("=" * 60)
        print("InsightVault Diagnostic Report")
        print("=" * 60)
        
        results = launcher.run_diagnostics()
        
        # Print summary
        print(f"\nBackend Status: {results['backend']['status']}")
        print(f"Frontend Status: {results['frontend']['status']}")
        
        total_issues = (
            len(results['backend'].get('issues', [])) +
            len(results['frontend'].get('issues', [])) +
            len(results['network'].get('issues', []))
        )
        
        if total_issues == 0:
            print("🎉 All systems are healthy!")
        else:
            print(f"⚠️ Found {total_issues} issues that need attention")
        
        if results['recommendations']:
            print(f"\n📋 Recommendations:")
            for i, rec in enumerate(results['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        # Save report if requested
        if args.save_report:
            filename = f"insightvault_diagnostic_{int(time.time())}.json"
            try:
                with open(filename, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
                print(f"\n💾 Report saved to {filename}")
            except Exception as e:
                print(f"\n❌ Failed to save report: {e}")
        
        if total_issues > 0:
            sys.exit(1)
    
    elif args.command == 'cleanup':
        print("=" * 50)
        print("InsightVault Port Cleanup")
        print("=" * 50)
        launcher.cleanup_ports()
        print("✅ Cleanup complete")
    
    elif args.command == 'install':
        print("=" * 50)
        print("InsightVault Dependency Installation")
        print("=" * 50)
        launcher.install_dependencies(minimal=args.minimal)
        print("✅ Installation complete")

if __name__ == "__main__":
    main() 