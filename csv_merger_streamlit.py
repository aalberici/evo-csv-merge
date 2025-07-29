import streamlit as st
import pandas as pd
import numpy as np
import io
from typing import List, Tuple, Optional, Dict, Any
import difflib

# Page configuration
st.set_page_config(
    page_title="CSV Merger Tool - NimbleSET Style",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
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
    
    .error-message {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .venn-diagram {
        text-align: center;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .join-button {
        width: 100%;
        margin: 0.25rem 0;
    }
</style>
""", unsafe_allow_html=True)

class CSVMerger:
    """Main class for handling CSV merge operations"""
    
    def __init__(self):
        self.left_df: Optional[pd.DataFrame] = None
        self.right_df: Optional[pd.DataFrame] = None
        self.merged_df: Optional[pd.DataFrame] = None
        
    def load_csv(self, uploaded_file, file_side: str) -> bool:
        """Load CSV file and return success status"""
        try:
            if uploaded_file is not None:
                df = pd.read_csv(uploaded_file)
                if file_side == "left":
                    self.left_df = df
                else:
                    self.right_df = df
                return True
        except Exception as e:
            st.error(f"Error loading {file_side} CSV: {str(e)}")
            return False
        return False
    
    def get_column_names(self, side: str) -> List[str]:
        """Get column names for specified side"""
        df = self.left_df if side == "left" else self.right_df
        return list(df.columns) if df is not None else []
    
    def auto_detect_keys(self) -> Tuple[Optional[str], Optional[str]]:
        """Automatically detect the best matching key columns"""
        if self.left_df is None or self.right_df is None:
            return None, None
            
        left_cols = set(self.left_df.columns)
        right_cols = set(self.right_df.columns)
        
        # Find exact matches
        exact_matches = left_cols.intersection(right_cols)
        
        if exact_matches:
            # Prioritize common key names
            priority_keys = ['id', 'ID', 'key', 'Key', 'code', 'Code', 'name', 'Name']
            for key in priority_keys:
                if key in exact_matches:
                    return key, key
            # Return first exact match
            best_match = list(exact_matches)[0]
            return best_match, best_match
        
        # Look for similar column names using fuzzy matching
        best_match = None
        best_ratio = 0.6  # Minimum similarity threshold
        
        for left_col in left_cols:
            for right_col in right_cols:
                ratio = difflib.SequenceMatcher(None, left_col.lower(), right_col.lower()).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = (left_col, right_col)
        
        return best_match if best_match else (None, None)
    
    def perform_join(self, left_key: str, right_key: str, join_type: str) -> bool:
        """Perform the specified join operation"""
        if self.left_df is None or self.right_df is None:
            st.error("Please upload both CSV files")
            return False
            
        if not left_key or not right_key:
            st.error("Please select join keys for both files")
            return False
        
        try:
            left_df = self.left_df.copy()
            right_df = self.right_df.copy()
            
            # Rename right key to match left key for joining if they're different
            if left_key != right_key:
                right_df = right_df.rename(columns={right_key: left_key})
            
            if join_type == "inner":
                self.merged_df = pd.merge(left_df, right_df, on=left_key, how='inner', suffixes=('_left', '_right'))
            elif join_type == "left":
                self.merged_df = pd.merge(left_df, right_df, on=left_key, how='left', suffixes=('_left', '_right'))
            elif join_type == "right":
                self.merged_df = pd.merge(left_df, right_df, on=left_key, how='right', suffixes=('_left', '_right'))
            elif join_type == "outer":
                self.merged_df = pd.merge(left_df, right_df, on=left_key, how='outer', suffixes=('_left', '_right'))
            elif join_type == "union":
                # For union, we need to align columns first
                all_cols = list(set(left_df.columns) | set(right_df.columns))
                left_aligned = left_df.reindex(columns=all_cols, fill_value='')
                right_aligned = right_df.reindex(columns=all_cols, fill_value='')
                self.merged_df = pd.concat([left_aligned, right_aligned], ignore_index=True)
            
            return True
            
        except Exception as e:
            st.error(f"Join operation failed: {str(e)}")
            return False
    
    def get_join_stats(self) -> Dict[str, int]:
        """Get statistics about the join operation"""
        stats = {
            "left_records": len(self.left_df) if self.left_df is not None else 0,
            "right_records": len(self.right_df) if self.right_df is not None else 0,
            "result_records": len(self.merged_df) if self.merged_df is not None else 0,
            "result_columns": len(self.merged_df.columns) if self.merged_df is not None else 0
        }
        return stats

def create_venn_diagram():
    """Create a text-based Venn diagram representation"""
    st.markdown("""
    <div class="venn-diagram">
        <h4>📊 Data Relationship Visualization</h4>
        <div style="display: flex; justify-content: center; align-items: center; gap: 20px;">
            <div style="background: #4facfe; color: white; padding: 20px; border-radius: 50%; width: 100px; height: 100px; display: flex; align-items: center; justify-content: center; opacity: 0.8;">
                <strong>LEFT<br>ONLY</strong>
            </div>
            <div style="background: linear-gradient(45deg, #4facfe, #00f2fe); color: white; padding: 20px; border-radius: 20px; width: 80px; height: 80px; display: flex; align-items: center; justify-content: center;">
                <strong>BOTH</strong>
            </div>
            <div style="background: #00f2fe; color: white; padding: 20px; border-radius: 50%; width: 100px; height: 100px; display: flex; align-items: center; justify-content: center; opacity: 0.8;">
                <strong>RIGHT<br>ONLY</strong>
            </div>
        </div>
        <p style="margin-top: 10px; color: #666;">The intersection represents records that match on the selected key</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔗 CSV Merger Tool</h1>
        <p>Merge CSV files with automatic key detection and advanced join operations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'merger' not in st.session_state:
        st.session_state.merger = CSVMerger()
    
    merger = st.session_state.merger
    
    # Sidebar for controls
    with st.sidebar:
        st.header("🎛️ Controls")
        
        # File uploads
        st.subheader("📁 Upload CSV Files")
        
        left_file = st.file_uploader(
            "Choose LEFT CSV file",
            type=['csv'],
            key="left_file"
        )
        
        right_file = st.file_uploader(
            "Choose RIGHT CSV file", 
            type=['csv'],
            key="right_file"
        )
        
        # Load files
        left_loaded = merger.load_csv(left_file, "left")
        right_loaded = merger.load_csv(right_file, "right")
        
        # Show file info
        if left_loaded and merger.left_df is not None:
            st.success(f"✅ Left file: {len(merger.left_df)} rows, {len(merger.left_df.columns)} columns")
        
        if right_loaded and merger.right_df is not None:
            st.success(f"✅ Right file: {len(merger.right_df)} rows, {len(merger.right_df.columns)} columns")
        
        st.divider()
        
        # Key selection
        if merger.left_df is not None and merger.right_df is not None:
            st.subheader("🔑 Join Configuration")
            
            # Auto-detect button
            if st.button("🔍 Auto-detect Keys", use_container_width=True):
                left_key, right_key = merger.auto_detect_keys()
                if left_key and right_key:
                    st.session_state.left_key = left_key
                    st.session_state.right_key = right_key
                    st.success(f"Auto-detected: {left_key} ↔ {right_key}")
                else:
                    st.warning("No matching keys found. Please select manually.")
            
            # Key selection dropdowns
            left_cols = merger.get_column_names("left")
            right_cols = merger.get_column_names("right")
            
            left_key = st.selectbox(
                "Left file join key:",
                options=[""] + left_cols,
                index=left_cols.index(st.session_state.get('left_key', '')) + 1 if st.session_state.get('left_key', '') in left_cols else 0
            )
            
            right_key = st.selectbox(
                "Right file join key:",
                options=[""] + right_cols,
                index=right_cols.index(st.session_state.get('right_key', '')) + 1 if st.session_state.get('right_key', '') in right_cols else 0
            )
            
            st.divider()
            
            # Join type selection
            st.subheader("⚙️ Join Operations")
            
            join_type = st.selectbox(
                "Select join type:",
                options=["inner", "left", "right", "outer", "union"],
                format_func=lambda x: {
                    "inner": "🎯 Inner Join (Intersection)",
                    "left": "⬅️ Left Join", 
                    "right": "➡️ Right Join",
                    "outer": "🔄 Full Outer Join",
                    "union": "➕ Union (All Records)"
                }[x]
            )
            
            # Quick join buttons
            st.subheader("🚀 Quick Actions")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("⬅️ Left Join", use_container_width=True):
                    if merger.perform_join(left_key, right_key, "left"):
                        st.rerun()
                
                if st.button("🎯 Inner Join", use_container_width=True):
                    if merger.perform_join(left_key, right_key, "inner"):
                        st.rerun()
                
                if st.button("➕ Union", use_container_width=True):
                    if merger.perform_join(left_key, right_key, "union"):
                        st.rerun()
            
            with col2:
                if st.button("➡️ Right Join", use_container_width=True):
                    if merger.perform_join(left_key, right_key, "right"):
                        st.rerun()
                
                if st.button("🔄 Full Outer", use_container_width=True):
                    if merger.perform_join(left_key, right_key, "outer"):
                        st.rerun()
                
                if st.button("⚡ Intersection", use_container_width=True):
                    if merger.perform_join(left_key, right_key, "inner"):
                        st.rerun()
            
            # Main join button
            if st.button(f"🔗 Perform {join_type.title()} Join", type="primary", use_container_width=True):
                if merger.perform_join(left_key, right_key, join_type):
                    st.rerun()
    
    # Main content area
    if merger.left_df is None or merger.right_df is None:
        st.info("👆 Please upload both CSV files using the sidebar to get started")
        
        # Show example Venn diagram
        create_venn_diagram()
        
        # Instructions
        st.markdown("""
        ## 📖 How to Use This Tool
        
        1. **Upload Files**: Use the sidebar to upload your LEFT and RIGHT CSV files
        2. **Auto-detect Keys**: Click "Auto-detect Keys" to find matching columns automatically
        3. **Choose Join Type**: Select from various join operations:
           - **Inner Join**: Only matching records (intersection)
           - **Left Join**: All left records + matching right records
           - **Right Join**: All right records + matching left records
           - **Full Outer**: All records from both files
           - **Union**: Simple combination of all records
        4. **Select Columns**: Choose which columns to include in results
        5. **Download**: Export your merged data
        
        ## 🎯 Join Types Explained
        
        - **Left Only**: Records that exist only in the left file
        - **Right Only**: Records that exist only in the right file  
        - **Both (Intersection)**: Records that match between both files
        - **Union**: All records combined from both files
        """)
    
    else:
        # Show file previews
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Left File Preview")
            st.dataframe(merger.left_df.head(), use_container_width=True)
        
        with col2:
            st.subheader("📋 Right File Preview") 
            st.dataframe(merger.right_df.head(), use_container_width=True)
        
        # Show Venn diagram
        create_venn_diagram()
        
        # Results section
        if merger.merged_df is not None:
            st.header("📊 Merge Results")
            
            # Statistics
            stats = merger.get_join_stats()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Left Records", stats["left_records"])
            
            with col2:
                st.metric("Right Records", stats["right_records"])
            
            with col3:
                st.metric("Result Records", stats["result_records"])
            
            with col4:
                st.metric("Result Columns", stats["result_columns"])
            
            # Column selection
            st.subheader("📋 Select Columns to Display")
            
            all_columns = list(merger.merged_df.columns)
            
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.button("Select All"):
                    st.session_state.selected_columns = all_columns
            
            with col2:
                if st.button("Deselect All"):
                    st.session_state.selected_columns = []
            
            # Initialize selected columns if not exists
            if 'selected_columns' not in st.session_state:
                st.session_state.selected_columns = all_columns
            
            selected_columns = st.multiselect(
                "Choose columns:",
                options=all_columns,
                default=st.session_state.selected_columns,
                key="column_selector"
            )
            
            # Update session state
            st.session_state.selected_columns = selected_columns
            
            # Display filtered results
            if selected_columns:
                st.subheader("🔍 Results Preview")
                filtered_df = merger.merged_df[selected_columns]
                
                # Show preview (first 1000 rows)
                preview_df = filtered_df.head(1000)
                st.dataframe(preview_df, use_container_width=True)
                
                if len(filtered_df) > 1000:
                    st.info(f"Showing first 1000 rows. Total rows: {len(filtered_df)}")
                
                # Download button
                st.subheader("💾 Download Results")
                
                # Prepare CSV for download
                csv_buffer = io.StringIO()
                filtered_df.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()
                
                st.download_button(
                    label="📥 Download Merged CSV",
                    data=csv_data,
                    file_name="merged_data.csv",
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )
                
                # Additional download options
                col1, col2 = st.columns(2)
                
                with col1:
                    # Excel download
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        filtered_df.to_excel(writer, sheet_name='Merged Data', index=False)
                    excel_data = excel_buffer.getvalue()
                    
                    st.download_button(
                        label="📊 Download as Excel",
                        data=excel_data,
                        file_name="merged_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                
                with col2:
                    # JSON download
                    json_data = filtered_df.to_json(orient='records', indent=2)
                    
                    st.download_button(
                        label="🔄 Download as JSON",
                        data=json_data,
                        file_name="merged_data.json",
                        mime="application/json",
                        use_container_width=True
                    )
            
            else:
                st.warning("Please select at least one column to display results.")

if __name__ == "__main__":
    main()
