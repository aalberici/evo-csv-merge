import streamlit as st
import pandas as pd
import numpy as np
import io
from typing import List, Tuple, Optional, Dict, Any
import difflib
import base64
from datetime import datetime
import json
import os
import uuid

def get_eye_icon_base64():
    """Get base64 encoded eye icon"""
    try:
        with open("icons/lucide--eye.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        # Fallback to text if icon not found
        return None

def eye_icon_html(size: int = 16) -> str:
    """Generate eye icon HTML"""
    icon_b64 = get_eye_icon_base64()
    if icon_b64:
        return f'<img src="data:image/png;base64,{icon_b64}" style="width: {size}px; height: {size}px; vertical-align: middle; margin-right: 4px;">'
    else:
        return "▶"  # Fallback to text

def lucide_icon(name: str, size: int = 16, color: str = "currentColor") -> str:
    """Generate Lucide icon HTML"""
    return f'<i data-lucide="{name}" style="width: {size}px; height: {size}px; color: {color};"></i>'

def init_lucide_icons():
    """Initialize Lucide icons after page load"""
    st.markdown("""
    <script>
    // Function to initialize Lucide icons
    function initLucideIcons() {
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        } else {
            // If lucide is not loaded yet, try again after a short delay
            setTimeout(initLucideIcons, 100);
        }
    }
    
    // Initialize icons when the page loads
    document.addEventListener('DOMContentLoaded', initLucideIcons);
    
    // Also initialize icons periodically for dynamic content
    setInterval(initLucideIcons, 1000);
    
    // Initialize immediately in case DOM is already loaded
    initLucideIcons();
    </script>
    """, unsafe_allow_html=True)

# Page configuration
st.set_page_config(
    page_title="CSV Data Processing Suite",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Lucide icons
init_lucide_icons()

def check_authentication():
    """Check if user is authenticated"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown("""
        <div class="main-header">
            <h1>Login Required</h1>
            <p>Please enter your credentials to access the CSV Processing Suite</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                username = st.text_input("Username", placeholder="Enter username")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                
                submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
                
                if submitted:
                    # Get password from secrets
                    try:
                        stored_password = st.secrets["auth"]["password"]
                        
                        if username == "evolutivo" and password == stored_password:
                            st.session_state.authenticated = True
                            st.success("✅ Login successful! Redirecting...")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")
                    except KeyError:
                        st.error("❌ Authentication configuration error. Please contact administrator.")
        
        st.markdown("""
        <div style="text-align: center; margin-top: 2rem; color: #666;">
            <p>This application requires authentication to access</p>
        </div>
        """, unsafe_allow_html=True)
        
        return False
    
    return True

# Modern CSS Design System
st.markdown("""
<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Lucide Icon Styling */
    .lucide-icon {
        width: 16px;
        height: 16px;
        display: inline-block;
        vertical-align: middle;
        margin-right: 4px;
        stroke: currentColor;
        stroke-width: 2;
        fill: none;
    }
    
    /* Icon Button Styling */
    .icon-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        padding: 0.5rem;
        border: none;
        border-radius: var(--radius-md);
        background: white;
        color: var(--neutral-600);
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--neutral-200);
        min-width: 40px;
        height: 40px;
    }
    
    .icon-button:hover {
        background: var(--primary-50);
        color: var(--primary-600);
        border-color: var(--primary-200);
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
    
    .icon-button.danger:hover {
        background: var(--error-50);
        color: var(--error-600);
        border-color: var(--error-200);
    }
    
    .icon-button.primary {
        background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
        color: white;
        border-color: var(--primary-500);
    }
    
    .icon-button.primary:hover {
        background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 100%);
        color: white;
        border-color: var(--primary-600);
    }
    
    /* CSS Variables for Design System */
    :root {
        --primary-50: #f0f9ff;
        --primary-100: #e0f2fe;
        --primary-200: #bae6fd;
        --primary-300: #7dd3fc;
        --primary-400: #38bdf8;
        --primary-500: #0ea5e9;
        --primary-600: #0284c7;
        --primary-700: #0369a1;
        --primary-800: #075985;
        --primary-900: #0c4a6e;
        
        --secondary-50: #fafaf9;
        --secondary-100: #f5f5f4;
        --secondary-200: #e7e5e4;
        --secondary-300: #d6d3d1;
        --secondary-400: #a8a29e;
        --secondary-500: #78716c;
        --secondary-600: #57534e;
        --secondary-700: #44403c;
        --secondary-800: #292524;
        --secondary-900: #1c1917;
        
        --success-50: #f0fdf4;
        --success-500: #22c55e;
        --success-600: #16a34a;
        
        --warning-50: #fffbeb;
        --warning-500: #f59e0b;
        --warning-600: #d97706;
        
        --error-50: #fef2f2;
        --error-500: #ef4444;
        --error-600: #dc2626;
        
        --neutral-50: #fafafa;
        --neutral-100: #f5f5f5;
        --neutral-200: #e5e5e5;
        --neutral-300: #d4d4d4;
        --neutral-400: #a3a3a3;
        --neutral-500: #737373;
        --neutral-600: #525252;
        --neutral-700: #404040;
        --neutral-800: #262626;
        --neutral-900: #171717;
        
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
        
        --radius-sm: 0.375rem;
        --radius-md: 0.5rem;
        --radius-lg: 0.75rem;
        --radius-xl: 1rem;
        --radius-2xl: 1.5rem;
    }
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background: linear-gradient(135deg, var(--neutral-50) 0%, var(--primary-50) 100%);
        color: var(--neutral-800);
        line-height: 1.6;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-weight: 600;
        letter-spacing: -0.025em;
        color: var(--neutral-900);
    }
    
    h1 { font-size: 2.25rem; line-height: 2.5rem; }
    h2 { font-size: 1.875rem; line-height: 2.25rem; }
    h3 { font-size: 1.5rem; line-height: 2rem; }
    
    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 50%, var(--primary-800) 100%);
        padding: 3rem 2rem;
        border-radius: var(--radius-2xl);
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-xl);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        opacity: 0.3;
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.125rem;
        margin-bottom: 0;
        position: relative;
        z-index: 1;
    }
    
    /* Cards */
    .modern-card {
        background: white;
        border-radius: var(--radius-xl);
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--neutral-200);
        transition: all 0.3s ease;
    }
    
    .modern-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
        border-color: var(--primary-200);
    }
    
    .artifact-card {
        background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
        color: white;
        border-radius: var(--radius-xl);
        padding: 1.5rem;
        margin: 0.75rem 0;
        box-shadow: var(--shadow-lg);
        border: none;
        transition: all 0.3s ease;
    }
    
    .artifact-card:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-xl);
    }
    
    .tool-card {
        background: white;
        padding: 2rem;
        border-radius: var(--radius-xl);
        border-left: 4px solid var(--primary-500);
        margin: 1.5rem 0;
        box-shadow: var(--shadow-md);
        transition: all 0.3s ease;
    }
    
    .tool-card:hover {
        border-left-color: var(--primary-600);
        box-shadow: var(--shadow-lg);
        transform: translateX(4px);
    }
    
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: var(--radius-lg);
        border-left: 4px solid var(--primary-400);
        margin: 0.75rem 0;
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        box-shadow: var(--shadow-md);
        border-left-color: var(--primary-500);
    }
    
    /* Status Messages */
    .success-message {
        background: var(--success-50);
        border: 1px solid var(--success-500);
        color: var(--success-600);
        padding: 1rem 1.5rem;
        border-radius: var(--radius-lg);
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .warning-message {
        background: var(--warning-50);
        border: 1px solid var(--warning-500);
        color: var(--warning-600);
        padding: 1rem 1.5rem;
        border-radius: var(--radius-lg);
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .error-message {
        background: var(--error-50);
        border: 1px solid var(--error-500);
        color: var(--error-600);
        padding: 1rem 1.5rem;
        border-radius: var(--radius-lg);
        margin: 1rem 0;
        font-weight: 500;
    }
    
    /* Artifact Manager */
    .artifact-manager {
        background: white;
        padding: 2rem;
        border-radius: var(--radius-xl);
        border: 2px dashed var(--primary-300);
        margin: 1.5rem 0;
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
    }
    
    .artifact-manager:hover {
        border-color: var(--primary-400);
        box-shadow: var(--shadow-md);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
        color: white;
        border: none;
        border-radius: var(--radius-lg);
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-size: 0.875rem;
        letter-spacing: 0.025em;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-sm);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 100%);
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: var(--shadow-sm);
    }
    
    /* Form Elements */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border: 2px solid var(--neutral-200);
        border-radius: var(--radius-lg);
        padding: 0.75rem 1rem;
        font-size: 0.875rem;
        transition: all 0.3s ease;
        background: white;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--primary-500);
        box-shadow: 0 0 0 3px var(--primary-100);
        outline: none;
    }
    
    /* Multiselect */
    .stMultiSelect > div > div {
        border: 2px solid var(--neutral-200);
        border-radius: var(--radius-lg);
        background: white;
    }
    
    .stMultiSelect > div > div:focus-within {
        border-color: var(--primary-500);
        box-shadow: 0 0 0 3px var(--primary-100);
    }
    
    /* Checkboxes */
    .stCheckbox > label {
        font-weight: 500;
        color: var(--neutral-700);
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: var(--neutral-50);
        border-radius: var(--radius-lg);
        border: 1px solid var(--neutral-200);
        font-weight: 600;
        color: var(--neutral-800);
    }
    
    .streamlit-expanderContent {
        background: white;
        border: 1px solid var(--neutral-200);
        border-top: none;
        border-radius: 0 0 var(--radius-lg) var(--radius-lg);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: var(--neutral-100);
        padding: 0.25rem;
        border-radius: var(--radius-lg);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: var(--radius-md);
        color: var(--neutral-600);
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        color: var(--primary-600);
        box-shadow: var(--shadow-sm);
    }
    
    /* Metrics */
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid var(--neutral-200);
        padding: 1.5rem;
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        box-shadow: var(--shadow-md);
        border-color: var(--primary-200);
    }
    
    /* DataFrames */
    .stDataFrame {
        border-radius: var(--radius-lg);
        overflow: hidden;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--neutral-200);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--neutral-50) 0%, var(--neutral-100) 100%);
        border-right: 1px solid var(--neutral-200);
    }
    
    /* File Uploader */
    .stFileUploader > div {
        border: 2px dashed var(--primary-300);
        border-radius: var(--radius-lg);
        background: var(--primary-50);
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:hover {
        border-color: var(--primary-400);
        background: var(--primary-100);
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--primary-500) 0%, var(--primary-600) 100%);
        border-radius: var(--radius-sm);
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: var(--primary-500);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 3rem 2rem;
        color: var(--neutral-500);
        font-size: 0.875rem;
        border-top: 1px solid var(--neutral-200);
        margin-top: 4rem;
        background: var(--neutral-50);
        border-radius: var(--radius-xl) var(--radius-xl) 0 0;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--neutral-100);
        border-radius: var(--radius-sm);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--neutral-300);
        border-radius: var(--radius-sm);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--neutral-400);
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-10px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    .slide-in {
        animation: slideIn 0.3s ease-out;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            padding: 2rem 1rem;
        }
        
        .main-header h1 {
            font-size: 2rem;
        }
        
        .modern-card,
        .tool-card {
            padding: 1rem;
        }
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        :root {
            --neutral-50: #171717;
            --neutral-100: #262626;
            --neutral-200: #404040;
            --neutral-800: #f5f5f5;
            --neutral-900: #fafafa;
        }
    }
</style>
""", unsafe_allow_html=True)

class DataArtifact:
    """Class to represent a data artifact with metadata"""
    
    def __init__(self, name: str, dataframe: pd.DataFrame, source: str, created_at: datetime = None):
        self.name = name
        self.dataframe = dataframe.copy()
        self.source = source  # 'cleaning', 'merging', 'upload'
        self.created_at = created_at or datetime.now()
        self.rows = len(dataframe)
        self.columns = len(dataframe.columns)
        self.memory_mb = dataframe.memory_usage(deep=True).sum() / 1024 / 1024
    
    def get_summary(self) -> str:
        return f"{self.name} | {self.rows:,} rows × {self.columns} cols | {self.memory_mb:.1f}MB | {self.source}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert artifact to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'dataframe': self.dataframe.to_json(orient='records'),
            'source': self.source,
            'created_at': self.created_at.isoformat(),
            'rows': self.rows,
            'columns': self.columns,
            'memory_mb': self.memory_mb
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataArtifact':
        """Create artifact from dictionary"""
        df = pd.read_json(data['dataframe'], orient='records')
        artifact = cls(
            name=data['name'],
            dataframe=df,
            source=data['source'],
            created_at=datetime.fromisoformat(data['created_at'])
        )
        return artifact

class ArtifactManager:
    """Manages data artifacts across the application with persistent storage"""
    
    def __init__(self):
        self.artifacts_dir = "artifacts"
        self.artifacts_file = os.path.join(self.artifacts_dir, "artifacts.json")
        
        # Create artifacts directory if it doesn't exist
        if not os.path.exists(self.artifacts_dir):
            os.makedirs(self.artifacts_dir)
        
        # Load artifacts from disk
        self._load_artifacts()
    
    def _load_artifacts(self):
        """Load artifacts from persistent storage"""
        try:
            if os.path.exists(self.artifacts_file):
                with open(self.artifacts_file, 'r', encoding='utf-8') as f:
                    artifacts_data = json.load(f)
                    artifacts = {}
                    for name, data in artifacts_data.items():
                        artifacts[name] = DataArtifact.from_dict(data)
                    st.session_state.artifacts = artifacts
            else:
                st.session_state.artifacts = {}
        except Exception as e:
            st.error(f"Failed to load artifacts: {str(e)}")
            st.session_state.artifacts = {}
    
    def _save_artifacts_to_disk(self):
        """Save artifacts to persistent storage"""
        try:
            artifacts_data = {}
            for name, artifact in st.session_state.artifacts.items():
                artifacts_data[name] = artifact.to_dict()
            
            with open(self.artifacts_file, 'w', encoding='utf-8') as f:
                json.dump(artifacts_data, f, indent=2)
            return True
        except Exception as e:
            st.error(f"Failed to save artifacts to disk: {str(e)}")
            return False
    
    def save_artifact(self, artifact: DataArtifact) -> bool:
        """Save an artifact to session state and persistent storage"""
        try:
            st.session_state.artifacts[artifact.name] = artifact
            return self._save_artifacts_to_disk()
        except Exception as e:
            st.error(f"Failed to save artifact: {str(e)}")
            return False
    
    def get_artifact(self, name: str) -> Optional[DataArtifact]:
        """Retrieve an artifact by name"""
        return st.session_state.artifacts.get(name)
    
    def list_artifacts(self) -> List[str]:
        """Get list of all artifact names"""
        return list(st.session_state.artifacts.keys())
    
    def delete_artifact(self, name: str) -> bool:
        """Delete an artifact from session state and persistent storage"""
        if name in st.session_state.artifacts:
            del st.session_state.artifacts[name]
            return self._save_artifacts_to_disk()
        return False
    
    def get_artifacts_by_source(self, source: str) -> List[DataArtifact]:
        """Get artifacts filtered by source"""
        return [artifact for artifact in st.session_state.artifacts.values() if artifact.source == source]
    
    def clear_all_artifacts(self) -> bool:
        """Clear all artifacts from memory and disk"""
        try:
            st.session_state.artifacts = {}
            if os.path.exists(self.artifacts_file):
                os.remove(self.artifacts_file)
            return True
        except Exception as e:
            st.error(f"Failed to clear artifacts: {str(e)}")
            return False

class DataProcessor:
    """Main class for handling all data processing operations"""
    
    def __init__(self, artifact_manager: ArtifactManager):
        self.artifact_manager = artifact_manager
        self.dataframes: List[pd.DataFrame] = []
        self.file_names: List[str] = []
        self.merged_df: Optional[pd.DataFrame] = None
        self.cleaned_df: Optional[pd.DataFrame] = None
        
    def load_files(self, uploaded_files) -> bool:
        """Load multiple CSV files"""
        try:
            self.dataframes = []
            self.file_names = []
            
            for file in uploaded_files:
                try:
                    df = pd.read_csv(file, encoding='utf-8')
                except UnicodeDecodeError:
                    file.seek(0)
                    df = pd.read_csv(file, encoding='latin1')
                
                df.columns = df.columns.str.strip()
                self.dataframes.append(df)
                self.file_names.append(file.name)
                
            return True
        except Exception as e:
            st.error(f"Error loading files: {str(e)}")
            return False
    
    def load_artifact_as_dataframe(self, artifact_name: str, position: int = 0) -> bool:
        """Load an artifact as a dataframe for processing"""
        artifact = self.artifact_manager.get_artifact(artifact_name)
        if artifact:
            if position >= len(self.dataframes):
                self.dataframes.extend([None] * (position - len(self.dataframes) + 1))
                self.file_names.extend([''] * (position - len(self.file_names) + 1))
            
            self.dataframes[position] = artifact.dataframe.copy()
            self.file_names[position] = f"Artifact: {artifact_name}"
            return True
        return False
    
    def load_pasted_text(self, text_data: str, position: int = 0, name: str = "Pasted Data") -> bool:
        """Load CSV data from pasted text"""
        try:
            if not text_data.strip():
                st.error("No data provided")
                return False
            
            from io import StringIO
            text_data = text_data.strip()
            
            # Check if it's markdown table format
            if self._is_markdown_table(text_data):
                df = self._parse_markdown_table(text_data)
                if df is not None:
                    st.info("✅ Detected and parsed markdown table format")
                else:
                    st.error("Failed to parse markdown table format")
                    return False
            else:
                # Try different CSV separators with better detection
                separators = [
                    (',', 'comma'),
                    (';', 'semicolon'), 
                    ('\t', 'tab'),
                    ('|', 'pipe')
                ]
                
                df = None
                detected_sep = None
                
                for sep, sep_name in separators:
                    try:
                        csv_buffer = StringIO(text_data)
                        test_df = pd.read_csv(csv_buffer, sep=sep, nrows=5)  # Test with first 5 rows
                        
                        # Better validation: check if we have multiple columns AND reasonable data
                        if (len(test_df.columns) > 1 and 
                            not test_df.empty and 
                            not all(col.startswith('Unnamed:') for col in test_df.columns)):
                            
                            # Parse the full data
                            csv_buffer = StringIO(text_data)
                            df = pd.read_csv(csv_buffer, sep=sep)
                            detected_sep = sep_name
                            break
                            
                    except Exception as e:
                        continue
                
                if df is None:
                    # Fallback: try comma separator with more lenient parsing
                    try:
                        csv_buffer = StringIO(text_data)
                        df = pd.read_csv(csv_buffer, sep=',', skipinitialspace=True)
                        detected_sep = 'comma (fallback)'
                    except:
                        pass
                
                if df is None or df.empty:
                    st.error("Could not parse the pasted data. Supported formats: CSV (comma, semicolon, tab, pipe separated) and Markdown tables.")
                    return False
                
                st.info(f"✅ Detected {detected_sep}-separated format")
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Remove any completely empty columns that might have been created
            df = df.dropna(axis=1, how='all')
            
            # Ensure we have enough space in the dataframes list
            if position >= len(self.dataframes):
                self.dataframes.extend([None] * (position - len(self.dataframes) + 1))
                self.file_names.extend([''] * (position - len(self.file_names) + 1))
            
            self.dataframes[position] = df
            self.file_names[position] = name
            
            return True
            
        except Exception as e:
            st.error(f"Error parsing pasted data: {str(e)}")
            return False
    
    def _is_markdown_table(self, text: str) -> bool:
        """Check if text appears to be a markdown table"""
        lines = text.strip().split('\n')
        if len(lines) < 2:
            return False
        
        # Look for markdown table pattern: header row followed by separator row
        first_line = lines[0].strip()
        second_line = lines[1].strip() if len(lines) > 1 else ""
        
        # Check if first line has pipes and second line has dashes/pipes
        has_pipes_first = '|' in first_line
        has_separator_second = bool(second_line and 
                                  '|' in second_line and 
                                  ('-' in second_line or ':' in second_line))
        
        return has_pipes_first and has_separator_second
    
    def _parse_markdown_table(self, text: str) -> pd.DataFrame:
        """Parse markdown table format"""
        try:
            lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
            
            if len(lines) < 2:
                return None
            
            # Extract header row (first line)
            header_line = lines[0]
            if header_line.startswith('|'):
                header_line = header_line[1:]
            if header_line.endswith('|'):
                header_line = header_line[:-1]
            
            headers = [col.strip() for col in header_line.split('|')]
            
            # Skip separator row (second line) and process data rows
            data_rows = []
            for line in lines[2:]:  # Skip header and separator
                if not line:
                    continue
                    
                # Remove leading/trailing pipes
                if line.startswith('|'):
                    line = line[1:]
                if line.endswith('|'):
                    line = line[:-1]
                
                row_data = [cell.strip() for cell in line.split('|')]
                
                # Pad or truncate row to match header length
                while len(row_data) < len(headers):
                    row_data.append('')
                row_data = row_data[:len(headers)]
                
                data_rows.append(row_data)
            
            if not data_rows:
                return None
            
            # Create DataFrame
            df = pd.DataFrame(data_rows, columns=headers)
            return df
            
        except Exception as e:
            st.error(f"Error parsing markdown table: {str(e)}")
            return None
    
    def get_column_names(self, df_index: int = 0) -> List[str]:
        """Get column names for specified dataframe"""
        if df_index < len(self.dataframes) and self.dataframes[df_index] is not None:
            return list(self.dataframes[df_index].columns)
        return []
    
    def add_new_column(self, df: pd.DataFrame, col_name: str, col_type: str, **kwargs) -> pd.DataFrame:
        """Add a new column to the DataFrame based on specified rules."""
        if col_name in df.columns:
            st.warning(f"Column '{col_name}' already exists. Overwriting.")

        if col_type == "Autonumber":
            start = kwargs.get('autonum_start', 1)
            df[col_name] = range(start, start + len(df))
        elif col_type == "Fixed Value":
            fixed_value = kwargs.get('fixed_value', '')
            df[col_name] = fixed_value
        elif col_type == "Random Integer":
            min_val = kwargs.get('random_int_min', 0)
            max_val = kwargs.get('random_int_max', 100)
            df[col_name] = np.random.randint(min_val, max_val + 1, size=len(df))
        elif col_type == "Random Float":
            min_val = kwargs.get('random_float_min', 0.0)
            max_val = kwargs.get('random_float_max', 1.0)
            df[col_name] = np.random.uniform(min_val, max_val, size=len(df))
        elif col_type == "UUID7":
            df[col_name] = [str(uuid.uuid4()) for _ in range(len(df))]
        elif col_type == "Increment Existing":
            source_col = kwargs.get('source_column')
            increment_by = kwargs.get('increment_by', 1)
            if source_col and source_col in df.columns:
                if pd.api.types.is_numeric_dtype(df[source_col]):
                    df[col_name] = df[source_col] + increment_by
                else:
                    st.error(f"Source column '{source_col}' is not numeric for 'Increment Existing'.")
                    return df
            else:
                st.error(f"Source column '{source_col}' not found for 'Increment Existing'.")
                return df
        else:
            st.error("Invalid column type specified.")
            return df
        return df
    
    def auto_detect_keys(self, left_idx: int = 0, right_idx: int = 1) -> Tuple[Optional[str], Optional[str]]:
        """Automatically detect matching key columns between two dataframes"""
        if (len(self.dataframes) < 2 or left_idx >= len(self.dataframes) or 
            right_idx >= len(self.dataframes) or 
            self.dataframes[left_idx] is None or self.dataframes[right_idx] is None):
            return None, None
            
        left_cols = set(self.dataframes[left_idx].columns)
        right_cols = set(self.dataframes[right_idx].columns)
        
        # Find exact matches
        exact_matches = left_cols.intersection(right_cols)
        
        if exact_matches:
            priority_keys = ['id', 'ID', 'key', 'Key', 'code', 'Code', 'name', 'Name', 'email', 'Email']
            for key in priority_keys:
                if key in exact_matches:
                    return key, key
            best_match = list(exact_matches)[0]
            return best_match, best_match
        
        # Fuzzy matching
        best_match = None
        best_ratio = 0.6
        
        for left_col in left_cols:
            for right_col in right_cols:
                ratio = difflib.SequenceMatcher(None, left_col.lower(), right_col.lower()).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = (left_col, right_col)
        
        return best_match if best_match else (None, None)
    
    def merge_dataframes(self, left_idx: int, right_idx: int, left_key: str, right_key: str, join_type: str) -> bool:
        """Merge two dataframes"""
        try:
            if (left_idx >= len(self.dataframes) or right_idx >= len(self.dataframes) or
                self.dataframes[left_idx] is None or self.dataframes[right_idx] is None):
                st.error("Invalid dataframe indices or missing dataframes")
                return False
                
            left_df = self.dataframes[left_idx].copy()
            right_df = self.dataframes[right_idx].copy()
            
            if left_key != right_key:
                left_df['_join_key'] = left_df[left_key]
                right_df['_join_key'] = right_df[right_key]
                join_on = '_join_key'
            else:
                join_on = left_key
            
            if join_type == "union":
                all_cols = list(set(left_df.columns) | set(right_df.columns))
                left_aligned = left_df.reindex(columns=all_cols, fill_value='')
                right_aligned = right_df.reindex(columns=all_cols, fill_value='')
                self.merged_df = pd.concat([left_aligned, right_aligned], ignore_index=True)
            else:
                self.merged_df = pd.merge(left_df, right_df, on=join_on, how=join_type, suffixes=('_left', '_right'))
            
            if left_key != right_key and '_join_key' in self.merged_df.columns:
                self.merged_df = self.merged_df.drop('_join_key', axis=1)
            
            return True
        except Exception as e:
            st.error(f"Merge operation failed: {str(e)}")
            return False
    
    def to_camel_case(self, text: str) -> str:
        """Convert text to camelCase"""
        # Remove special characters and split by spaces, underscores, hyphens
        import re
        words = re.split(r'[_\-\s]+', text.strip())
        if not words:
            return text
        
        # First word lowercase, rest title case
        camel_case = words[0].lower()
        for word in words[1:]:
            if word:
                camel_case += word.capitalize()
        
        return camel_case
    
    def remove_spaces_from_text(self, text: str) -> str:
        """Remove spaces and replace with underscores"""
        return text.strip().replace(' ', '_')
    
    def apply_column_renaming(self, df: pd.DataFrame, rename_options: Dict[str, Any]) -> pd.DataFrame:
        """Apply column renaming based on options"""
        if not rename_options.get('enable_column_renaming', False):
            return df
        
        new_columns = {}
        
        for col in df.columns:
            new_name = col
            
            # Apply automatic transformations
            if rename_options.get('remove_spaces', False):
                new_name = self.remove_spaces_from_text(new_name)
            
            if rename_options.get('to_camel_case', False):
                new_name = self.to_camel_case(new_name)
            
            # Apply manual renames (takes precedence)
            manual_renames = rename_options.get('manual_renames', {})
            if col in manual_renames and manual_renames[col].strip():
                new_name = manual_renames[col].strip()
            
            if new_name != col:
                new_columns[col] = new_name
        
        if new_columns:
            df = df.rename(columns=new_columns)
            st.success(f"✅ Renamed {len(new_columns)} columns: {', '.join([f'{old} → {new}' for old, new in new_columns.items()])}")
        
        return df
    
    def clean_data(self, options: Dict[str, Any]) -> bool:
        """Clean data based on provided options"""
        try:
            if options.get('merge_files', False) and len(self.dataframes) > 1:
                # Merge multiple files
                valid_dfs = [df for df in self.dataframes if df is not None]
                if len(valid_dfs) < 2:
                    st.error("Need at least 2 valid dataframes to merge")
                    return False
                
                if options.get('keep_first_header_only', True):
                    for i in range(1, len(valid_dfs)):
                        common_cols = valid_dfs[0].columns.intersection(valid_dfs[i].columns)
                        valid_dfs[i] = valid_dfs[i][common_cols]
                
                self.cleaned_df = pd.concat(valid_dfs, ignore_index=True, join='outer')
            else:
                # Work with first valid dataframe if no merge
                valid_df = next((df for df in self.dataframes if df is not None), None)
                self.cleaned_df = valid_df.copy() if valid_df is not None else None
            
            if self.cleaned_df is not None:
                # Apply column renaming FIRST (before column selection)
                self.cleaned_df = self.apply_column_renaming(self.cleaned_df, options.get('column_rename_options', {}))
                # Apply column keeping/removal *after* renaming, as it affects columns
                columns_to_keep = options.get('columns_to_keep')
                if columns_to_keep is not None and len(columns_to_keep) > 0:
                    # Map original column names to renamed columns if renaming was applied
                    rename_options = options.get('column_rename_options', {})
                    if rename_options.get('enable_column_renaming', False):
                        # Create mapping from old names to new names
                        old_to_new = {}
                        manual_renames = rename_options.get('manual_renames', {})
                        
                        for old_col in columns_to_keep:
                            new_col = old_col
                            
                            # Apply automatic transformations
                            if rename_options.get('remove_spaces', False):
                                new_col = self.remove_spaces_from_text(new_col)
                            if rename_options.get('to_camel_case', False):
                                new_col = self.to_camel_case(new_col)
                            
                            # Apply manual renames (takes precedence)
                            if old_col in manual_renames and manual_renames[old_col].strip():
                                new_col = manual_renames[old_col].strip()
                            
                            old_to_new[old_col] = new_col
                        
                        # Update columns_to_keep with renamed columns
                        columns_to_keep = [old_to_new.get(col, col) for col in columns_to_keep]
                    
                    # Ensure all columns to keep actually exist in the DataFrame
                    existing_cols = self.cleaned_df.columns.tolist()
                    cols_to_select = [col for col in columns_to_keep if col in existing_cols]
                    
                    if cols_to_select:  # Only filter if we have valid columns to keep
                        original_col_count = len(self.cleaned_df.columns)
                        self.cleaned_df = self.cleaned_df[cols_to_select]
                        removed_count = original_col_count - len(cols_to_select)
                        st.success(f"✅ Column filtering applied: Kept {len(cols_to_select)} columns, removed {removed_count} columns")
                        
                        # Show which columns were kept and removed
                        removed_cols = set(existing_cols) - set(cols_to_select)
                        if removed_cols:
                            st.info(f"🗑️ Removed columns: {', '.join(sorted(removed_cols))}")
                        st.info(f"✅ Kept columns: {', '.join(cols_to_select)}")
                    else:
                        st.warning("⚠️ None of the selected columns exist in the dataset. All columns retained.")
                    
                    # Warn if some selected columns were not found
                    missing_cols = set(columns_to_keep) - set(existing_cols)
                    if missing_cols:
                        st.warning(f"⚠️ Selected columns not found in dataset: {', '.join(sorted(missing_cols))}")
                else:
                    st.info("ℹ️ No column filtering applied - all columns retained.")

                # Apply other cleaning operations
                if options.get('remove_duplicates', False):
                    self.cleaned_df.drop_duplicates(inplace=True)
                
                if options.get('remove_empty_rows', True):
                    self.cleaned_df.dropna(how='all', inplace=True)
                
                if options.get('remove_empty_columns', False):
                    self.cleaned_df.dropna(axis=1, how='all', inplace=True)
                
                if options.get('strip_whitespace', True):
                    for col in self.cleaned_df.select_dtypes(include=['object']).columns:
                        self.cleaned_df[col] = self.cleaned_df[col].astype(str).str.strip()
                
                if options.get('standardize_case', False):
                    case_option = options.get('case_type', 'lower')
                    for col in self.cleaned_df.select_dtypes(include=['object']).columns:
                        if case_option == 'lower':
                            self.cleaned_df[col] = self.cleaned_df[col].astype(str).str.lower()
                        elif case_option == 'upper':
                            self.cleaned_df[col] = self.cleaned_df[col].astype(str).str.upper()
                        elif case_option == 'title':
                            self.cleaned_df[col] = self.cleaned_df[col].astype(str).str.title()
            
            return True
        except Exception as e:
            st.error(f"Data cleaning failed: {str(e)}")
            return False

def render_artifact_manager(artifact_manager: ArtifactManager):
    """Render the artifact management interface"""
    artifacts = artifact_manager.list_artifacts()
    
    # Header with modern styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 100%); 
                padding: 1rem; border-radius: var(--radius-lg); margin-bottom: 1rem; 
                box-shadow: var(--shadow-md); position: relative; overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; 
                    background: url('data:image/svg+xml,%3Csvg width=\'40\' height=\'40\' viewBox=\'0 0 40 40\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'%23ffffff\' fill-opacity=\'0.1\'%3E%3Ccircle cx=\'20\' cy=\'20\' r=\'1\'/%3E%3C/g%3E%3C/svg%3E'); 
                    opacity: 0.3;"></div>
        <h4 style="color: white; margin: 0; font-size: 1rem; font-weight: 600; position: relative; z-index: 1;">
            Data Artifacts
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    if artifacts:
        # Bulk actions
        with st.expander("Bulk Actions", expanded=False):
            if st.button("Clear All", type="secondary", use_container_width=True):
                if st.session_state.get('confirm_clear_all', False):
                    if artifact_manager.clear_all_artifacts():
                        st.success("✅ All cleared!")
                        st.session_state.confirm_clear_all = False
                        st.rerun()
                else:
                    st.session_state.confirm_clear_all = True
                    st.warning("⚠️ Click again to confirm")
                    st.rerun()
        
        # Artifacts list with improved UX
        for artifact_name in artifacts:
            artifact = artifact_manager.get_artifact(artifact_name)
            
            # Container for each artifact with modern styling
            with st.container():
                st.markdown(f"""
                <div class="modern-card slide-in" style="border-left: 4px solid var(--primary-500); margin: 1rem 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: var(--neutral-900); font-size: 1rem; font-weight: 600;">
                                {artifact.name}
                            </strong><br>
                            <div style="margin: 0.5rem 0; color: var(--neutral-600); font-size: 0.875rem;">
                                <span style="background: var(--primary-100); color: var(--primary-700); 
                                           padding: 0.25rem 0.5rem; border-radius: var(--radius-sm); 
                                           font-weight: 500; margin-right: 0.5rem;">
                                    {artifact.rows:,} rows
                                </span>
                                <span style="background: var(--secondary-100); color: var(--secondary-700); 
                                           padding: 0.25rem 0.5rem; border-radius: var(--radius-sm); 
                                           font-weight: 500; margin-right: 0.5rem;">
                                    {artifact.columns} cols
                                </span>
                                <span style="background: var(--neutral-100); color: var(--neutral-700); 
                                           padding: 0.25rem 0.5rem; border-radius: var(--radius-sm); 
                                           font-weight: 500;">
                                    {artifact.memory_mb:.1f}MB
                                </span>
                            </div>
                            <small style="color: var(--neutral-500); font-size: 0.75rem;">
                                {artifact.source} • {artifact.created_at.strftime('%m/%d %H:%M')}
                            </small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Action buttons in a compact row
                col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
                
                with col1:
                    # Create custom button with eye icon inside
                    eye_icon = eye_icon_html(20)
                    if eye_icon and eye_icon.startswith('<img'):
                        st.markdown(f"""
                        <div style="margin-bottom: 0.5rem;">
                            <button onclick="document.querySelector('[data-testid*=\"baseButton\"][key*=\"view_{artifact_name}\"]').click()" 
                                    style="width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 0.5rem; 
                                           background: white; cursor: pointer; display: flex; align-items: center; 
                                           justify-content: center; transition: all 0.3s ease;"
                                    onmouseover="this.style.background='#f0f9ff'; this.style.borderColor='#0ea5e9';"
                                    onmouseout="this.style.background='white'; this.style.borderColor='#ddd';"
                                    title="Preview data">
                                {eye_icon}
                            </button>
                        </div>
                        """, unsafe_allow_html=True)
                        # Hidden button for functionality
                        if st.button("", key=f"view_{artifact_name}", help="Preview data"):
                            st.session_state[f"show_popup_{artifact_name}"] = True
                    else:
                        # Fallback to emoji if icon not found
                        if st.button("👁", key=f"view_{artifact_name}", 
                                   help="Preview data", use_container_width=True):
                            st.session_state[f"show_popup_{artifact_name}"] = True
                
                with col2:
                    if st.button("✏ Rename", key=f"rename_{artifact_name}", 
                               help="Rename artifact", use_container_width=True):
                        st.session_state[f"rename_mode_{artifact_name}"] = True
                        st.rerun()
                
                with col3:
                    if st.button("📋 Copy", key=f"copy_{artifact_name}", 
                               help="Duplicate artifact", use_container_width=True):
                        # Create a copy with timestamp
                        new_name = f"{artifact_name}_copy_{datetime.now().strftime('%H%M%S')}"
                        new_artifact = DataArtifact(
                            name=new_name,
                            dataframe=artifact.dataframe.copy(),
                            source=artifact.source
                        )
                        if artifact_manager.save_artifact(new_artifact):
                            st.success(f"✅ Copied as {new_name}")
                            st.rerun()
                
                with col4:
                    if st.button("🗑 Delete", key=f"delete_{artifact_name}", 
                               help="Delete artifact", use_container_width=True):
                        if st.session_state.get(f'confirm_delete_{artifact_name}', False):
                            if artifact_manager.delete_artifact(artifact_name):
                                st.success(f"✅ Deleted")
                                st.session_state[f'confirm_delete_{artifact_name}'] = False
                                st.rerun()
                        else:
                            st.session_state[f'confirm_delete_{artifact_name}'] = True
                            st.warning("⚠️ Click again to confirm")
                            st.rerun()
                
                # Rename dialog
                if st.session_state.get(f"rename_mode_{artifact_name}", False):
                    @st.dialog(f"✏️ Rename: {artifact_name}")
                    def show_rename_dialog():
                        new_name = st.text_input("New name:", value=artifact_name, key=f"new_name_{artifact_name}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Save", key="save_rename", type="primary", use_container_width=True):
                                if new_name.strip() and new_name.strip() != artifact_name:
                                    if new_name.strip() not in artifact_manager.list_artifacts():
                                        # Create new artifact with new name
                                        new_artifact = DataArtifact(
                                            name=new_name.strip(),
                                            dataframe=artifact.dataframe.copy(),
                                            source=artifact.source,
                                            created_at=artifact.created_at
                                        )
                                        if artifact_manager.save_artifact(new_artifact):
                                            # Delete old artifact
                                            artifact_manager.delete_artifact(artifact_name)
                                            st.success(f"✅ Renamed to {new_name.strip()}")
                                            st.session_state[f"rename_mode_{artifact_name}"] = False
                                            st.rerun()
                                    else:
                                        st.error("❌ Name already exists")
                                else:
                                    st.error("❌ Enter a valid new name")
                        
                        with col2:
                            if st.button("❌ Cancel", key="cancel_rename", use_container_width=True):
                                st.session_state[f"rename_mode_{artifact_name}"] = False
                                st.rerun()
                    
                    show_rename_dialog()
                
                # Preview dialog
                if st.session_state.get(f"show_popup_{artifact_name}", False):
                    @st.dialog(f"📊 {artifact_name}")
                    def show_artifact_preview():
                        # Metrics in columns
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Rows", f"{artifact.rows:,}")
                        with col2:
                            st.metric("Columns", artifact.columns)
                        with col3:
                            st.metric("Size", f"{artifact.memory_mb:.1f}MB")
                        
                        st.markdown(f"""
                        **Source:** {artifact.source} | **Created:** {artifact.created_at.strftime('%Y-%m-%d %H:%M:%S')}
                        """)
                        
                        st.markdown("**Data Preview:**")
                        st.dataframe(artifact.dataframe.head(20), use_container_width=True)
                        
                        if st.button("✅ Close", key="close_preview", type="primary", use_container_width=True):
                            st.session_state[f"show_popup_{artifact_name}"] = False
                            st.rerun()
                    
                    show_artifact_preview()
                
                st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid #eee;'>", 
                           unsafe_allow_html=True)
    
    else:
        st.markdown("""
        <div style="text-align: center; padding: 3rem 2rem; color: var(--neutral-500); 
                   background: white; border-radius: var(--radius-xl); 
                   border: 2px dashed var(--neutral-300); box-shadow: var(--shadow-sm);">
            <h4 style="color: var(--neutral-600); font-weight: 600; margin-bottom: 0.5rem;">
                No Artifacts Yet
            </h4>
            <p style="margin: 0; color: var(--neutral-500);">
                Create some in the Data Cleaning tool to get started!
            </p>
        </div>
        """, unsafe_allow_html=True)

@st.cache_data
def convert_df_to_csv(df):
    """Convert DataFrame to CSV string with caching"""
    return df.to_csv(index=False)

@st.cache_data
def convert_df_to_excel(df):
    """Convert DataFrame to Excel bytes with caching"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Processed Data', index=False)
    return output.getvalue()

def render_data_cleaning_tool(processor: DataProcessor, artifact_manager: ArtifactManager):
    """Render the data cleaning interface"""
    st.header("Data Cleaning Tool")
    
    # Data source selection
    st.subheader("Select Data Source")
    
    data_source = st.radio(
        "Choose your data source:",
        ["Upload Files", "Use Artifacts", "Paste Text"],
        key="cleaning_data_source",
        horizontal=True
    )
    
    if data_source == "Upload Files":
        # File upload
        uploaded_files = st.file_uploader(
            "Choose CSV files",
            type="csv",
            accept_multiple_files=True,
            help="Upload one or multiple CSV files for cleaning",
            key="cleaning_uploader"
        )
        
        files_loaded = False
        if uploaded_files:
            if processor.load_files(uploaded_files):
                st.success(f"✅ Loaded {len(processor.dataframes)} file(s)")
                files_loaded = True
    
    elif data_source == "Use Artifacts":
        artifacts = artifact_manager.list_artifacts()
        if artifacts:
            st.info("Select one or more artifacts to load for cleaning. Multiple artifacts will be treated as separate files.")
            
            selected_artifacts = st.multiselect(
                "Select artifacts to load:",
                options=artifacts,
                help="Choose artifacts to load for cleaning",
                key="cleaning_artifacts_select"
            )
            
            files_loaded = False
            if selected_artifacts:
                # Clear existing dataframes
                processor.dataframes = []
                processor.file_names = []
                
                # Load selected artifacts
                for artifact_name in selected_artifacts:
                    artifact = artifact_manager.get_artifact(artifact_name)
                    if artifact:
                        processor.dataframes.append(artifact.dataframe.copy())
                        processor.file_names.append(f"Artifact: {artifact_name}")
                
                if processor.dataframes:
                    st.success(f"✅ Loaded {len(processor.dataframes)} artifact(s)")
                    files_loaded = True
        else:
            st.info("No artifacts available. Create some first by uploading files and saving them as artifacts!")
            files_loaded = False
    
    else:  # Paste Text
        st.info("Paste your data below. Supports CSV (comma, semicolon, tab, pipe-separated) and Markdown table formats.")
        
        pasted_text = st.text_area(
            "Paste CSV data here:",
            height=200,
            placeholder="CSV: name,age,city\nJohn,25,New York\n\nMarkdown: | name | age | city |\n|------|-----|------|\n| John | 25  | NYC  |",
            help="Paste CSV data or Markdown table with headers. The system will auto-detect the format.",
            key="cleaning_pasted_text"
        )
        
        files_loaded = False
        if pasted_text.strip():
            if st.button("Parse Pasted Data", type="secondary"):
                # Clear existing dataframes
                processor.dataframes = []
                processor.file_names = []
                
                if processor.load_pasted_text(pasted_text, 0, "Pasted CSV Data"):
                    st.success("✅ Successfully parsed pasted data!")
                    files_loaded = True
                    st.rerun()
        
        # Check if we already have parsed data
        if len(processor.dataframes) > 0 and processor.dataframes[0] is not None:
            files_loaded = True
    
    if files_loaded:
        # Cleaning options
            st.subheader("Cleaning Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                merge_files = st.checkbox("Merge uploaded CSV files", value=len(processor.dataframes) > 1)
                remove_duplicates = st.checkbox("Remove duplicate rows", value=False)
                remove_empty_rows = st.checkbox("Remove empty rows", value=True)
                remove_empty_columns = st.checkbox("Remove empty columns", value=False)
            
            with col2:
                keep_first_header_only = st.checkbox("Keep only first file's header structure", value=True)
                strip_whitespace = st.checkbox("Strip whitespace from text", value=True)
                standardize_case = st.checkbox("Standardize text case", value=False)
                
                if standardize_case:
                    case_type = st.selectbox("Case type", ["lower", "upper", "title"])
                else:
                    case_type = "lower"

            # Calculate columns available for selection based on merge preference
            current_columns_for_selection = []
            if merge_files and len(processor.dataframes) > 1:
                # Calculate the union of columns across all dataframes if merging is active
                all_cols_set = set()
                for df in processor.dataframes:
                    if df is not None:
                        all_cols_set.update(df.columns)
                current_columns_for_selection = sorted(list(all_cols_set))
            elif len(processor.dataframes) > 0 and processor.dataframes[0] is not None:
                # Use columns from the first dataframe if no merge
                current_columns_for_selection = list(processor.dataframes[0].columns)

            # NEW: Column Renaming section (before column management)
            with st.expander("Column Renaming", expanded=False):
                st.info("Rename columns to improve data quality and consistency.")
                
                enable_column_renaming = st.checkbox("Enable column renaming", key="enable_column_renaming")
                
                if enable_column_renaming:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Automatic Transformations:**")
                        remove_spaces = st.checkbox("Remove spaces (replace with underscores)", key="remove_spaces_cols")
                        to_camel_case = st.checkbox("Convert to camelCase", key="to_camel_case_cols")
                        
                        if remove_spaces and to_camel_case:
                            st.warning("⚠️ Both options selected: camelCase will be applied after removing spaces")
                    
                    with col2:
                        st.markdown("**Preview of automatic changes:**")
                        if current_columns_for_selection:
                            preview_cols = current_columns_for_selection[:3]  # Show first 3 as examples
                            for col in preview_cols:
                                original = col
                                transformed = col
                                
                                if remove_spaces:
                                    transformed = processor.remove_spaces_from_text(transformed)
                                if to_camel_case:
                                    transformed = processor.to_camel_case(transformed)
                                
                                if transformed != original:
                                    st.text(f"{original} → {transformed}")
                            
                            if len(current_columns_for_selection) > 3:
                                st.caption(f"... and {len(current_columns_for_selection) - 3} more columns")
                        else:
                            st.caption("No columns to preview")
                    
                    # Manual column renaming
                    st.markdown("**Manual Column Renaming:**")
                    st.info("Specify custom names for individual columns (overrides automatic transformations)")
                    
                    if current_columns_for_selection:
                        # Create a form for manual renames
                        manual_renames = {}
                        
                        # Show in a more compact format
                        cols_per_row = 2
                        for i in range(0, len(current_columns_for_selection), cols_per_row):
                            row_cols = current_columns_for_selection[i:i+cols_per_row]
                            form_cols = st.columns(len(row_cols))
                            
                            for j, col_name in enumerate(row_cols):
                                with form_cols[j]:
                                    new_name = st.text_input(
                                        f"Rename '{col_name}':",
                                        value="",
                                        placeholder=f"Leave empty to keep '{col_name}'",
                                        key=f"manual_rename_{col_name}",
                                        help=f"Enter new name for column '{col_name}' or leave empty"
                                    )
                                    if new_name.strip():
                                        manual_renames[col_name] = new_name.strip()
                        
                        if manual_renames:
                            st.success(f"✅ {len(manual_renames)} manual renames configured")
                    else:
                        st.warning("No columns available for renaming")

            # NEW: Column Management section (first step - select columns to keep)
            with st.expander("Column Management", expanded=False):

                columns_to_keep = []
                if current_columns_for_selection:
                    st.info("Select columns to KEEP. Unselected columns will be removed after cleaning.")
                    
                    # Handle newly added columns while preserving user's previous selection
                    if 'new_columns_to_add' in st.session_state:
                        # Get current selection if it exists, otherwise start with empty list
                        current_selection = st.session_state.get("cols_to_keep_clean", [])
                        # Add new columns to the existing selection
                        for new_col in st.session_state['new_columns_to_add']:
                            if new_col in current_columns_for_selection and new_col not in current_selection:
                                current_selection.append(new_col)
                        # Filter to only include columns that exist in current dataset
                        default_selection = [col for col in current_selection if col in current_columns_for_selection]
                        # Clear the new columns list
                        del st.session_state['new_columns_to_add']
                    else:
                        # Use existing selection or default to all columns only on first load
                        existing_selection = st.session_state.get("cols_to_keep_clean", current_columns_for_selection)
                        # Filter to only include columns that exist in current dataset
                        default_selection = [col for col in existing_selection if col in current_columns_for_selection]
                        # If no valid columns from previous selection, default to all current columns
                        if not default_selection and current_columns_for_selection:
                            default_selection = current_columns_for_selection
                    
                    columns_to_keep = st.multiselect(
                        "Select columns to keep:",
                        options=current_columns_for_selection,
                        default=default_selection,
                        key="cols_to_keep_clean"
                    )
                else:
                    st.warning("No columns to display. Please upload files first.")
                    columns_to_keep = [] # Ensure it's an empty list if no columns

            # NEW: Add New Columns section (after column selection, before cleaning)
            with st.expander("Add New Columns", expanded=False):
                st.info("Add new columns to your data. These will be included in the final cleaned dataset.")
                
                # Get the working dataframe for adding columns
                working_df = None
                if merge_files and len(processor.dataframes) > 1:
                    # If merging, work with a temporary merged version
                    valid_dfs = [df for df in processor.dataframes if df is not None]
                    if len(valid_dfs) >= 2:
                        if keep_first_header_only:
                            for i in range(1, len(valid_dfs)):
                                common_cols = valid_dfs[0].columns.intersection(valid_dfs[i].columns)
                                valid_dfs[i] = valid_dfs[i][common_cols]
                        working_df = pd.concat(valid_dfs, ignore_index=True, join='outer')
                elif len(processor.dataframes) > 0 and processor.dataframes[0] is not None:
                    working_df = processor.dataframes[0].copy()
                
                if working_df is not None:
                    counter = st.session_state.get('add_column_counter', 0)
                    new_col_name = st.text_input("New Column Name:", key=f"new_col_name_pre_clean_{counter}")
                    col_type = st.selectbox(
                        "Select Column Value Type:",
                        ["Autonumber", "Fixed Value", "Random Integer", "Random Float", "UUID7", "Increment Existing"],
                        key="new_col_type_pre_clean"
                    )

                    col_kwargs = {}

                    if col_type == "Autonumber":
                        col_kwargs['autonum_start'] = st.number_input("Start Number:", min_value=1, value=1, step=1, key="autonum_start_pre_clean")
                    elif col_type == "Fixed Value":
                        col_kwargs['fixed_value'] = st.text_input("Fixed Value:", key="fixed_value_pre_clean")
                    elif col_type == "Random Integer":
                        col_kwargs['random_int_min'] = st.number_input("Minimum Value:", min_value=0, value=0, step=1, key="rand_int_min_pre_clean")
                        col_kwargs['random_int_max'] = st.number_input("Maximum Value:", min_value=0, value=100, step=1, key="rand_int_max_pre_clean")
                    elif col_type == "Random Float":
                        col_kwargs['random_float_min'] = st.number_input("Minimum Value:", value=0.0, key="rand_float_min_pre_clean")
                        col_kwargs['random_float_max'] = st.number_input("Maximum Value:", value=1.0, key="rand_float_max_pre_clean")
                    elif col_type == "UUID7":
                        st.info("UUID7 will generate unique identifiers for each row")
                    elif col_type == "Increment Existing":
                        numeric_cols = working_df.select_dtypes(include=np.number).columns.tolist()
                        if numeric_cols:
                            col_kwargs['source_column'] = st.selectbox("Select Numeric Source Column:", [""] + numeric_cols, key="source_col_increment_pre_clean")
                            col_kwargs['increment_by'] = st.number_input("Increment By:", value=1, step=1, key="increment_by_pre_clean")
                        else:
                            st.warning("No numeric columns available for increment operation.")

                    if st.button("Add Column", type="secondary", use_container_width=True, key="add_new_column_pre_clean"):
                        if new_col_name.strip():
                            # Add column to all relevant dataframes
                            if merge_files and len(processor.dataframes) > 1:
                                for i, df in enumerate(processor.dataframes):
                                    if df is not None:
                                        processor.dataframes[i] = processor.add_new_column(
                                            df, new_col_name.strip(), col_type, **col_kwargs
                                        )
                            elif len(processor.dataframes) > 0 and processor.dataframes[0] is not None:
                                processor.dataframes[0] = processor.add_new_column(
                                    processor.dataframes[0], new_col_name.strip(), col_type, **col_kwargs
                                )
                            
                            # Store the new column name to be added after rerun
                            if 'new_columns_to_add' not in st.session_state:
                                st.session_state['new_columns_to_add'] = []
                            st.session_state['new_columns_to_add'].append(new_col_name.strip())
                            
                            # Clear the text input by updating its key
                            if 'add_column_counter' not in st.session_state:
                                st.session_state['add_column_counter'] = 0
                            st.session_state['add_column_counter'] += 1
                            
                            st.success(f"✅ Column '{new_col_name.strip()}' added and will be selected for cleaning!")
                            st.rerun()
                        else:
                            st.error("Please enter a name for the new column.")
                else:
                    st.warning("No data available. Please upload files first.")

            # NEW: Column Selection Preview Panel
            if current_columns_for_selection:
                with st.expander("Current Column Selection Preview", expanded=True):
                    selected_cols = st.session_state.get("cols_to_keep_clean", [])
                    
                    if selected_cols:
                        st.success(f"✅ **{len(selected_cols)} columns selected** for cleaning:")
                        
                        # Show selected columns in a nice format
                        cols_per_row = 4
                        for i in range(0, len(selected_cols), cols_per_row):
                            row_cols = selected_cols[i:i+cols_per_row]
                            col_containers = st.columns(len(row_cols))
                            for j, col_name in enumerate(row_cols):
                                with col_containers[j]:
                                    st.markdown(f"🔹 `{col_name}`")
                        
                        # Show what will be removed
                        all_available = set(current_columns_for_selection)
                        selected_set = set(selected_cols)
                        removed_cols = all_available - selected_set
                        
                        if removed_cols:
                            st.warning(f"⚠️ **{len(removed_cols)} columns will be removed:** {', '.join(sorted(removed_cols))}")
                        else:
                            st.info("ℹ️ All available columns are selected")
                    else:
                        st.error("❌ **No columns selected!** All columns will be retained.")
            
            # Preview original data
            show_original = st.checkbox("Show original data", value=True)
            if show_original:
                for i, df in enumerate(processor.dataframes):
                    if df is not None:
                        with st.expander(f"📄 {processor.file_names[i]} ({len(df):,} rows, {len(df.columns)} columns)"):
                            st.dataframe(df.head(10), use_container_width=True)
            
            # Process data
            if st.button("Clean Data", type="primary", use_container_width=True):
                # Collect manual renames from session state
                manual_renames = {}
                if current_columns_for_selection:
                    for col_name in current_columns_for_selection:
                        rename_key = f"manual_rename_{col_name}"
                        if rename_key in st.session_state and st.session_state[rename_key].strip():
                            manual_renames[col_name] = st.session_state[rename_key].strip()
                
                cleaning_options = {
                    'merge_files': merge_files,
                    'keep_first_header_only': keep_first_header_only,
                    'remove_duplicates': remove_duplicates,
                    'remove_empty_rows': remove_empty_rows,
                    'remove_empty_columns': remove_empty_columns,
                    'strip_whitespace': strip_whitespace,
                    'standardize_case': standardize_case,
                    'case_type': case_type,
                    'columns_to_keep': columns_to_keep, # Pass selected columns to keep
                    'column_rename_options': {
                        'enable_column_renaming': st.session_state.get('enable_column_renaming', False),
                        'remove_spaces': st.session_state.get('remove_spaces_cols', False),
                        'to_camel_case': st.session_state.get('to_camel_case_cols', False),
                        'manual_renames': manual_renames
                    }
                }
                
                if processor.clean_data(cleaning_options):
                    st.success("✅ Data cleaning completed!")
                    st.rerun()
            
            # Show cleaned results
            if processor.cleaned_df is not None:
                st.subheader("Cleaned Data Results")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Rows", f"{len(processor.cleaned_df):,}")
                with col2:
                    st.metric("Columns", len(processor.cleaned_df.columns))
                with col3:
                    memory_mb = processor.cleaned_df.memory_usage(deep=True).sum() / 1024 / 1024
                    st.metric("Memory", f"{memory_mb:.2f} MB")
                
                # Preview cleaned data
                st.dataframe(processor.cleaned_df.head(20), use_container_width=True)
                
                # Save as artifact
                st.subheader("Save & Download")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    artifact_name = st.text_input(
                        "Artifact name (to reuse in CSV Merger):",
                        value=f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        help="Give this cleaned dataset a name to use it in the CSV Merger tool"
                    )
                
                with col2:
                    if st.button("Save as Artifact", type="primary", use_container_width=True):
                        if artifact_name.strip():
                            # Use the cleaned dataframe which already has column selection applied
                            artifact = DataArtifact(
                                name=artifact_name.strip(),
                                dataframe=processor.cleaned_df.copy(),  # Ensure we copy the cleaned data
                                source="cleaning"
                            )
                            if artifact_manager.save_artifact(artifact):
                                st.success(f"✅ Saved as artifact: {artifact_name} with {len(processor.cleaned_df.columns)} columns")
                                st.rerun()
                        else:
                            st.error("Please enter an artifact name")
                
                # Download options
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    csv_data = convert_df_to_csv(processor.cleaned_df)
                    st.download_button(
                        "📄 Download CSV",
                        data=csv_data,
                        file_name="cleaned_data.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col2:
                    excel_data = convert_df_to_excel(processor.cleaned_df)
                    st.download_button(
                        "📊 Download Excel",
                        data=excel_data,
                        file_name="cleaned_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                
                with col3:
                    json_data = processor.cleaned_df.to_json(orient='records', indent=2)
                    st.download_button(
                        "🔗 Download JSON",
                        data=json_data,
                        file_name="cleaned_data.json",
                        mime="application/json",
                        use_container_width=True
                    )


def render_csv_merger_tool(processor: DataProcessor, artifact_manager: ArtifactManager):
    """Render the CSV merger interface"""
    st.header("CSV Merger Tool")
    
    # Data source selection
    st.subheader("Select Data Sources")
    
    col1, col2 = st.columns(2)
    
    # LEFT data source
    with col1:
        st.markdown("**LEFT Dataset**")
        left_source = st.radio(
            "Choose left data source:",
            ["Upload File", "Use Artifact", "Paste Text"],
            key="left_source",
            horizontal=True
        )
        
        if left_source == "Upload File":
            left_file = st.file_uploader("Choose LEFT CSV file", type=['csv'], key="merger_left")
            if left_file:
                if processor.load_files([left_file]):
                    st.success(f"✅ Loaded: {left_file.name}")
        elif left_source == "Use Artifact":
            artifacts = artifact_manager.list_artifacts()
            if artifacts:
                left_artifact = st.selectbox("Select left artifact:", [""] + artifacts, key="left_artifact")
                if left_artifact:
                    if processor.load_artifact_as_dataframe(left_artifact, 0):
                        st.success(f"✅ Loaded artifact: {left_artifact}")
            else:
                st.info("No artifacts available. Create some in the Data Cleaning tool first!")
        else:  # Paste Text
            st.info("Paste your LEFT dataset (CSV or Markdown table format)")
            left_pasted_text = st.text_area(
                "Paste LEFT CSV data:",
                height=150,
                placeholder="CSV: id,name,value\n1,Item A,100\n\nMarkdown: | id | name | value |\n|----|----- |-------|",
                key="left_pasted_text"
            )
            
            if left_pasted_text.strip():
                if st.button("Parse LEFT Data", type="secondary", key="parse_left"):
                    if processor.load_pasted_text(left_pasted_text, 0, "Left Pasted Data"):
                        st.success("✅ Successfully parsed LEFT data!")
                        st.rerun()
    
    # RIGHT data source
    with col2:
        st.markdown("**RIGHT Dataset**")
        right_source = st.radio(
            "Choose right data source:",
            ["Upload File", "Use Artifact", "Paste Text"],
            key="right_source",
            horizontal=True
        )
        
        if right_source == "Upload File":
            right_file = st.file_uploader("Choose RIGHT CSV file", type=['csv'], key="merger_right")
            if right_file:
                # Ensure we have space for the right file
                if len(processor.dataframes) < 2:
                    processor.dataframes.append(None)
                    processor.file_names.append("")
                
                try:
                    df = pd.read_csv(right_file, encoding='utf-8')
                except UnicodeDecodeError:
                    right_file.seek(0)
                    df = pd.read_csv(right_file, encoding='latin1')
                
                df.columns = df.columns.str.strip()
                processor.dataframes[1] = df
                processor.file_names[1] = right_file.name
                st.success(f"✅ Loaded: {right_file.name}")
        elif right_source == "Use Artifact":
            artifacts = artifact_manager.list_artifacts()
            if artifacts:
                right_artifact = st.selectbox("Select right artifact:", [""] + artifacts, key="right_artifact")
                if right_artifact:
                    if processor.load_artifact_as_dataframe(right_artifact, 1):
                        st.success(f"✅ Loaded artifact: {right_artifact}")
            else:
                st.info("No artifacts available. Create some in the Data Cleaning tool first!")
        else:  # Paste Text
            st.info("Paste your RIGHT dataset (CSV or Markdown table format)")
            right_pasted_text = st.text_area(
                "Paste RIGHT CSV data:",
                height=150,
                placeholder="CSV: id,description,category\n1,Product A,Electronics\n\nMarkdown: | id | description | category |",
                key="right_pasted_text"
            )
            
            if right_pasted_text.strip():
                if st.button("Parse RIGHT Data", type="secondary", key="parse_right"):
                    if processor.load_pasted_text(right_pasted_text, 1, "Right Pasted Data"):
                        st.success("✅ Successfully parsed RIGHT data!")
                        st.rerun()
    
    # Check if we have both datasets
    if (len(processor.dataframes) >= 2 and 
        processor.dataframes[0] is not None and 
        processor.dataframes[1] is not None):
        
        # Show file previews
        st.subheader("Data Preview")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Left Dataset Preview**")
            st.dataframe(processor.dataframes[0].head(5), use_container_width=True)
            st.caption(f"{len(processor.dataframes[0]):,} rows, {len(processor.dataframes[0].columns)} columns")
        
        with col2:
            st.markdown("**Right Dataset Preview**")
            st.dataframe(processor.dataframes[1].head(5), use_container_width=True)
            st.caption(f"{len(processor.dataframes[1]):,} rows, {len(processor.dataframes[1].columns)} columns")
        
        # Key selection
        st.subheader("Join Configuration")
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            left_cols = processor.get_column_names(0)
            left_key = st.selectbox("Left dataset join key:", [""] + left_cols, key="left_key_select")
        
        with col2:
            right_cols = processor.get_column_names(1)
            right_key = st.selectbox("Right dataset join key:", [""] + right_cols, key="right_key_select")
        
        with col3:
            if st.button("Auto-detect", use_container_width=True):
                auto_left, auto_right = processor.auto_detect_keys(0, 1)
                if auto_left and auto_right:
                    st.success(f"Found: {auto_left} ↔ {auto_right}")
                    # Store in session state to update selectboxes
                    st.session_state.suggested_left_key = auto_left
                    st.session_state.suggested_right_key = auto_right
                else:
                    st.warning("No matching keys found")
        
        # Use suggested keys if available
        if 'suggested_left_key' in st.session_state and not left_key:
            left_key = st.session_state.suggested_left_key
        if 'suggested_right_key' in st.session_state and not right_key:
            right_key = st.session_state.suggested_right_key
        
        # Join type selection
        join_type = st.selectbox(
            "Select join type:",
            ["inner", "left", "right", "outer", "union"],
            format_func=lambda x: {
                "inner": "Inner Join (Intersection)",
                "left": "Left Join",
                "right": "Right Join", 
                "outer": "Full Outer Join",
                "union": "Union (All Records)"
            }[x]
        )
        
        # Perform merge
        if st.button("Perform Merge", type="primary", use_container_width=True):
            if left_key and right_key:
                if processor.merge_dataframes(0, 1, left_key, right_key, join_type):
                    st.success("✅ Merge completed successfully!")
                    st.rerun()
            else:
                st.error("Please select join keys for both datasets")
        
        # Show merge results
        if processor.merged_df is not None:
            st.subheader("Merge Results")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Left Records", f"{len(processor.dataframes[0]):,}")
            with col2:
                st.metric("Right Records", f"{len(processor.dataframes[1]):,}")
            with col3:
                st.metric("Result Records", f"{len(processor.merged_df):,}")
            
            st.dataframe(processor.merged_df.head(20), use_container_width=True)
            
            # Save merged result as artifact
            st.subheader("Save & Download")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                merge_artifact_name = st.text_input(
                    "Save merged result as artifact:",
                    value=f"merged_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    help="Save this merged dataset to reuse later"
                )
            
            with col2:
                if st.button("Save Merge Result", type="primary", use_container_width=True):
                    if merge_artifact_name.strip():
                        artifact = DataArtifact(
                            name=merge_artifact_name.strip(),
                            dataframe=processor.merged_df,
                            source="merging"
                        )
                        if artifact_manager.save_artifact(artifact):
                            st.success(f"✅ Saved as artifact: {merge_artifact_name}")
                            st.rerun()
                    else:
                        st.error("Please enter an artifact name")
            
            # Download merged data
            col1, col2, col3 = st.columns(3)
            
            with col1:
                csv_data = convert_df_to_csv(processor.merged_df)
                st.download_button(
                    "📄 Download CSV",
                    data=csv_data,
                    file_name="merged_data.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                excel_data = convert_df_to_excel(processor.merged_df)
                st.download_button(
                    "📊 Download Excel",
                    data=excel_data,
                    file_name="merged_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            with col3:
                json_data = processor.merged_df.to_json(orient='records', indent=2)
                st.download_button(
                    "🔗 Download JSON",
                    data=json_data,
                    file_name="merged_data.json",
                    mime="application/json",
                    use_container_width=True
                )
    else:
        st.info("Please select both left and right datasets to proceed with merging")

def main():
    """Main application function"""
    # Check authentication first
    if not check_authentication():
        return
    
    # Initialize managers
    if 'artifact_manager' not in st.session_state:
        st.session_state.artifact_manager = ArtifactManager()
    
    artifact_manager = st.session_state.artifact_manager
    
    # Add logout button and artifact manager in sidebar
    with st.sidebar:
        if st.button("Logout", key="logout_btn"):
            st.session_state.authenticated = False
            st.rerun()
        
        st.divider()
        
        # Artifact manager in sidebar
        render_artifact_manager(artifact_manager)
    
    # Logo and title
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("evo-logo.png", width=120)
    with col2:
        st.title("CSV Data Processing Suite")
        st.caption("Complete toolkit for CSV data cleaning, merging, and analysis")
    
    # Initialize processor
    if 'processor' not in st.session_state:
        st.session_state.processor = DataProcessor(artifact_manager)
    
    processor = st.session_state.processor
    
    # Navigation tabs
    tab1, tab2 = st.tabs(["Data Cleaning", "CSV Merger"])
    
    with tab1:
        render_data_cleaning_tool(processor, artifact_manager)
    
    with tab2:
        render_csv_merger_tool(processor, artifact_manager)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>Built with Streamlit | Professional CSV Data Processing Suite</p>
        <p><strong>Workflow:</strong> Clean Data → Save as Artifact → Use in Merger → Export Results</p>
    </div>
    """, unsafe_allow_html=True)
    

if __name__ == "__main__":
    main()
