import streamlit as st
import pandas as pd
import numpy as np
import io
from typing import List, Tuple, Optional, Dict, Any
import difflib
import base64
from datetime import datetime
import pickle
import os

# Page configuration
st.set_page_config(
    page_title="CSV Data Processing Suite",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

def check_authentication():
    """Check if user is authenticated"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown("""
        <div class="main-header">
            <h1>🔐 Login Required</h1>
            <p>Please enter your credentials to access the CSV Processing Suite</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                username = st.text_input("Username", placeholder="Enter username")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                
                submitted = st.form_submit_button("🔓 Login", use_container_width=True, type="primary")
                
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
            <p>🔒 This application requires authentication to access</p>
        </div>
        """, unsafe_allow_html=True)
        
        return False
    
    return True

# Enhanced CSS for multi-purpose app
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .artifact-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .tool-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stat-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4facfe;
        margin: 0.5rem 0;
    }
    
    .success-message {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .artifact-manager {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border: 2px dashed #667eea;
        margin: 1rem 0;
    }
    
    .footer {
        text-align: center;
        padding: 2rem;
        color: #666;
        font-size: 0.9em;
        border-top: 1px solid #eee;
        margin-top: 3rem;
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

class ArtifactManager:
    """Manages data artifacts across the application with persistent storage"""
    
    def __init__(self):
        self.artifacts_dir = "artifacts"
        self.artifacts_file = os.path.join(self.artifacts_dir, "artifacts.pkl")
        
        # Create artifacts directory if it doesn't exist
        if not os.path.exists(self.artifacts_dir):
            os.makedirs(self.artifacts_dir)
        
        # Load artifacts from disk
        self._load_artifacts()
    
    def _load_artifacts(self):
        """Load artifacts from persistent storage"""
        try:
            if os.path.exists(self.artifacts_file):
                with open(self.artifacts_file, 'rb') as f:
                    artifacts = pickle.load(f)
                    st.session_state.artifacts = artifacts
            else:
                st.session_state.artifacts = {}
        except Exception as e:
            st.error(f"Failed to load artifacts: {str(e)}")
            st.session_state.artifacts = {}
    
    def _save_artifacts_to_disk(self):
        """Save artifacts to persistent storage"""
        try:
            with open(self.artifacts_file, 'wb') as f:
                pickle.dump(st.session_state.artifacts, f)
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
                # Apply column keeping/removal *before* other operations, as it affects columns
                columns_to_keep = options.get('columns_to_keep')
                if columns_to_keep is not None:
                    # Ensure all columns to keep actually exist in the DataFrame
                    existing_cols = self.cleaned_df.columns.tolist()
                    cols_to_select = [col for col in columns_to_keep if col in existing_cols]
                    self.cleaned_df = self.cleaned_df[cols_to_select]
                    # Warn if some selected columns were not found
                    removed_missing_cols = set(columns_to_keep) - set(cols_to_select)
                    if removed_missing_cols:
                        st.warning(f"Columns not found in the dataset and therefore removed: {', '.join(removed_missing_cols)}")

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
    
    if artifacts:
        st.markdown("""
        <div class="artifact-manager">
            <h4>📦 Data Artifacts (Persistent)</h4>
            <p>Saved datasets that persist across sessions and can be reused across tools</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add clear all button
        if st.button("🗑️ Clear All Artifacts", type="secondary", use_container_width=True):
            if st.session_state.get('confirm_clear_all', False):
                if artifact_manager.clear_all_artifacts():
                    st.success("✅ All artifacts cleared!")
                    st.session_state.confirm_clear_all = False
                    st.rerun()
            else:
                st.session_state.confirm_clear_all = True
                st.warning("⚠️ Click again to confirm clearing ALL artifacts")
                st.rerun()
        
        st.divider()
        
        for artifact_name in artifacts:
            artifact = artifact_manager.get_artifact(artifact_name)
            
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"""
                <div class="artifact-card">
                    <strong>{artifact.name}</strong><br>
                    <small>{artifact.get_summary()}</small><br>
                    <small>Created: {artifact.created_at.strftime('%Y-%m-%d %H:%M')}</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("👁️ View", key=f"view_{artifact_name}", use_container_width=True):
                    st.session_state[f"show_popup_{artifact_name}"] = True
                
                # Show popup dialog if triggered
                if st.session_state.get(f"show_popup_{artifact_name}", False):
                    @st.dialog(f"📊 Preview: {artifact_name}")
                    def show_artifact_preview():
                        st.markdown(f"""
                        **Dataset Information:**
                        - **Rows:** {artifact.rows:,}
                        - **Columns:** {artifact.columns}
                        - **Size:** {artifact.memory_mb:.1f} MB
                        - **Source:** {artifact.source}
                        - **Created:** {artifact.created_at.strftime('%Y-%m-%d %H:%M:%S')}
                        """)
                        
                        st.markdown("**Data Preview (first 20 rows):**")
                        st.dataframe(artifact.dataframe.head(20), use_container_width=True)
                        
                        if st.button("Close", type="primary", use_container_width=True):
                            st.session_state[f"show_popup_{artifact_name}"] = False
                            st.rerun()
                    
                    show_artifact_preview()
            
            with col3:
                if st.button("🗑️ Delete", key=f"delete_{artifact_name}", use_container_width=True):
                    if artifact_manager.delete_artifact(artifact_name):
                        st.success(f"Deleted {artifact_name}")
                        st.rerun()
    else:
        st.info("📦 No artifacts saved yet. Create some in the Data Cleaning section!")

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
    st.header("🧹 Data Cleaning Tool")
    
    # File upload
    uploaded_files = st.file_uploader(
        "Choose CSV files",
        type="csv",
        accept_multiple_files=True,
        help="Upload one or multiple CSV files for cleaning",
        key="cleaning_uploader"
    )
    
    if uploaded_files:
        if processor.load_files(uploaded_files):
            st.success(f"✅ Loaded {len(processor.dataframes)} file(s)")
            
            # Cleaning options
            st.subheader("🔧 Cleaning Options")
            
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

            # NEW: Column Management section
            with st.expander("🛠️ Column Management", expanded=False):
                current_columns_for_selection = []
                # Determine columns available for selection based on merge preference
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

                columns_to_keep = []
                if current_columns_for_selection:
                    st.info("Select columns to KEEP. Unselected columns will be removed after cleaning.")
                    columns_to_keep = st.multiselect(
                        "Select columns to keep:",
                        options=current_columns_for_selection,
                        default=current_columns_for_selection, # All selected by default
                        key="cols_to_keep_clean"
                    )
                else:
                    st.warning("No columns to display. Please upload files first.")
                    columns_to_keep = [] # Ensure it's an empty list if no columns

            # NEW: Add New Columns section (before cleaning)
            with st.expander("➕ Add New Columns", expanded=False):
                st.info("Add new columns to your data before cleaning. These will be applied to the source data.")
                
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
                    new_col_name = st.text_input("New Column Name:", key="new_col_name_pre_clean")
                    col_type = st.selectbox(
                        "Select Column Value Type:",
                        ["Autonumber", "Fixed Value", "Random Integer", "Random Float", "Increment Existing"],
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
                    elif col_type == "Increment Existing":
                        numeric_cols = working_df.select_dtypes(include=np.number).columns.tolist()
                        if numeric_cols:
                            col_kwargs['source_column'] = st.selectbox("Select Numeric Source Column:", [""] + numeric_cols, key="source_col_increment_pre_clean")
                            col_kwargs['increment_by'] = st.number_input("Increment By:", value=1, step=1, key="increment_by_pre_clean")
                        else:
                            st.warning("No numeric columns available for increment operation.")

                    if st.button("➕ Add Column to Source Data", type="secondary", use_container_width=True, key="add_new_column_pre_clean"):
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
                            
                            st.success(f"✅ Column '{new_col_name.strip()}' added to source data!")
                            st.rerun()
                        else:
                            st.error("Please enter a name for the new column.")
                else:
                    st.warning("No data available. Please upload files first.")
            
            # Preview original data
            show_original = st.checkbox("Show original data", value=True)
            if show_original:
                for i, df in enumerate(processor.dataframes):
                    if df is not None:
                        with st.expander(f"📄 {processor.file_names[i]} ({len(df):,} rows, {len(df.columns)} columns)"):
                            st.dataframe(df.head(10), use_container_width=True)
            
            # Process data
            if st.button("🚀 Clean Data", type="primary", use_container_width=True):
                cleaning_options = {
                    'merge_files': merge_files,
                    'keep_first_header_only': keep_first_header_only,
                    'remove_duplicates': remove_duplicates,
                    'remove_empty_rows': remove_empty_rows,
                    'remove_empty_columns': remove_empty_columns,
                    'strip_whitespace': strip_whitespace,
                    'standardize_case': standardize_case,
                    'case_type': case_type,
                    'columns_to_keep': columns_to_keep # Pass selected columns to keep
                }
                
                if processor.clean_data(cleaning_options):
                    st.success("✅ Data cleaning completed!")
                    st.rerun()
            
            # Show cleaned results
            if processor.cleaned_df is not None:
                st.subheader("📊 Cleaned Data Results")
                
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
                st.subheader("💾 Save & Download")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    artifact_name = st.text_input(
                        "Artifact name (to reuse in CSV Merger):",
                        value=f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        help="Give this cleaned dataset a name to use it in the CSV Merger tool"
                    )
                
                with col2:
                    if st.button("💾 Save as Artifact", type="primary", use_container_width=True):
                        if artifact_name.strip():
                            artifact = DataArtifact(
                                name=artifact_name.strip(),
                                dataframe=processor.cleaned_df,
                                source="cleaning"
                            )
                            if artifact_manager.save_artifact(artifact):
                                st.success(f"✅ Saved as artifact: {artifact_name}")
                                st.rerun()
                        else:
                            st.error("Please enter an artifact name")
                
                # Download options
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    csv_data = convert_df_to_csv(processor.cleaned_df)
                    st.download_button(
                        "📥 Download CSV",
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
                        "🔄 Download JSON",
                        data=json_data,
                        file_name="cleaned_data.json",
                        mime="application/json",
                        use_container_width=True
                    )


def render_csv_merger_tool(processor: DataProcessor, artifact_manager: ArtifactManager):
    """Render the CSV merger interface"""
    st.header("🔗 CSV Merger Tool")
    
    # Data source selection
    st.subheader("📂 Select Data Sources")
    
    col1, col2 = st.columns(2)
    
    # LEFT data source
    with col1:
        st.markdown("**LEFT Dataset**")
        left_source = st.radio(
            "Choose left data source:",
            ["Upload File", "Use Artifact"],
            key="left_source",
            horizontal=True
        )
        
        if left_source == "Upload File":
            left_file = st.file_uploader("Choose LEFT CSV file", type=['csv'], key="merger_left")
            if left_file:
                if processor.load_files([left_file]):
                    st.success(f"✅ Loaded: {left_file.name}")
        else:
            artifacts = artifact_manager.list_artifacts()
            if artifacts:
                left_artifact = st.selectbox("Select left artifact:", [""] + artifacts, key="left_artifact")
                if left_artifact:
                    if processor.load_artifact_as_dataframe(left_artifact, 0):
                        st.success(f"✅ Loaded artifact: {left_artifact}")
            else:
                st.info("No artifacts available. Create some in the Data Cleaning tool first!")
    
    # RIGHT data source
    with col2:
        st.markdown("**RIGHT Dataset**")
        right_source = st.radio(
            "Choose right data source:",
            ["Upload File", "Use Artifact"],
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
        else:
            artifacts = artifact_manager.list_artifacts()
            if artifacts:
                right_artifact = st.selectbox("Select right artifact:", [""] + artifacts, key="right_artifact")
                if right_artifact:
                    if processor.load_artifact_as_dataframe(right_artifact, 1):
                        st.success(f"✅ Loaded artifact: {right_artifact}")
            else:
                st.info("No artifacts available. Create some in the Data Cleaning tool first!")
    
    # Check if we have both datasets
    if (len(processor.dataframes) >= 2 and 
        processor.dataframes[0] is not None and 
        processor.dataframes[1] is not None):
        
        # Show file previews
        st.subheader("📋 Data Preview")
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
        st.subheader("🔑 Join Configuration")
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            left_cols = processor.get_column_names(0)
            left_key = st.selectbox("Left dataset join key:", [""] + left_cols, key="left_key_select")
        
        with col2:
            right_cols = processor.get_column_names(1)
            right_key = st.selectbox("Right dataset join key:", [""] + right_cols, key="right_key_select")
        
        with col3:
            if st.button("🔍 Auto-detect", use_container_width=True):
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
                "inner": "🎯 Inner Join (Intersection)",
                "left": "⬅️ Left Join",
                "right": "➡️ Right Join", 
                "outer": "🔄 Full Outer Join",
                "union": "➕ Union (All Records)"
            }[x]
        )
        
        # Perform merge
        if st.button("🔗 Perform Merge", type="primary", use_container_width=True):
            if left_key and right_key:
                if processor.merge_dataframes(0, 1, left_key, right_key, join_type):
                    st.success("✅ Merge completed successfully!")
                    st.rerun()
            else:
                st.error("Please select join keys for both datasets")
        
        # Show merge results
        if processor.merged_df is not None:
            st.subheader("📊 Merge Results")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Left Records", f"{len(processor.dataframes[0]):,}")
            with col2:
                st.metric("Right Records", f"{len(processor.dataframes[1]):,}")
            with col3:
                st.metric("Result Records", f"{len(processor.merged_df):,}")
            
            st.dataframe(processor.merged_df.head(20), use_container_width=True)
            
            # Save merged result as artifact
            st.subheader("💾 Save & Download")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                merge_artifact_name = st.text_input(
                    "Save merged result as artifact:",
                    value=f"merged_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    help="Save this merged dataset to reuse later"
                )
            
            with col2:
                if st.button("💾 Save Merge Result", type="primary", use_container_width=True):
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
                    "📥 Download CSV",
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
                    "🔄 Download JSON",
                    data=json_data,
                    file_name="merged_data.json",
                    mime="application/json",
                    use_container_width=True
                )
    else:
        st.info("👆 Please select both left and right datasets to proceed with merging")

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
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
        
        st.divider()
        
        # Artifact manager in sidebar
        render_artifact_manager(artifact_manager)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔧 CSV Data Processing Suite</h1>
        <p>Complete toolkit for CSV data cleaning, merging, and analysis</p>
        <p style="font-size: 0.9em; opacity: 0.8;">Create artifacts in Data Cleaning, then reuse them in CSV Merger</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize processor
    if 'processor' not in st.session_state:
        st.session_state.processor = DataProcessor(artifact_manager)
    
    processor = st.session_state.processor
    
    # Navigation tabs
    tab1, tab2 = st.tabs(["🧹 Data Cleaning", "🔗 CSV Merger"])
    
    with tab1:
        render_data_cleaning_tool(processor, artifact_manager)
    
    with tab2:
        render_csv_merger_tool(processor, artifact_manager)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>Built with ❤️ using Streamlit | Professional CSV Data Processing Suite</p>
        <p>🔧 <strong>Workflow:</strong> Clean Data → Save as Artifact → Use in Merger → Export Results</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
