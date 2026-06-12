import sys
import os
import streamlit as st

# Force Python to locate local modules correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from batch_processor import process_code_directory

# 1. Page Configuration Set Up
st.set_page_config(page_title="AI Agentic Co-Refactoring Dashboard", layout="wide")
st.title("🛠️ AI Agentic Co-Refactoring Dashboard")

# 2. Sidebar Configurations: Input/Output Paths and Run Control
st.sidebar.header("📁 Pipeline Configuration")
input_folder = st.sidebar.text_input("Input Legacy Folder Path:", value="./legacy_code")
output_folder = st.sidebar.text_input("Output Optimized Folder Path:", value="./optimized_code")

# Execution Action Button
if st.sidebar.button("🚀 Run Refactoring Engine", use_container_width=True):
    if not os.path.exists(input_folder):
        st.sidebar.error(f"Input path '{input_folder}' does not exist!")
    else:
        with st.spinner("Agents processing files... Please check Docker activity."):
            try:
                # Trigger your pre-built multi-language batch execution engine
                process_code_directory(input_folder, output_folder)
                st.sidebar.success("Job completed successfully!")
            except Exception as e:
                st.sidebar.error(f"Execution failed: {str(e)}")

# 3. Sidebar File Selector: Monitor files in the input directory
st.sidebar.header("📄 Source Files Explorer")
if os.path.exists(input_folder):
    # Retrieve all applicable source items inside the target directory
    source_files = [
        f for f in os.listdir(input_folder)
        if f.endswith(".py") or f.endswith(".ipynb") or f.endswith(".sql")
    ]
    
    if source_files:
        selected_file = st.sidebar.selectbox("Select a file to inspect:", source_files)
    else:
        st.sidebar.info("No active .py, .ipynb, or .sql files found in input directory.")
        selected_file = None
else:
    st.sidebar.warning("Provide a valid input folder path to display files.")
    selected_file = None

# 4. Main Application Workspace: Side-by-Side Comparison Panels
if selected_file:
    file_root, file_ext = os.path.splitext(selected_file)
    
    # Resolve exact execution paths
    legacy_file_path = os.path.join(input_folder, selected_file)
    out_ext = ".sql" if file_ext.lower() == ".sql" else ".py"
    optimized_file_name = f"optimized_{file_root}{out_ext}"
    optimized_file_path = os.path.join(output_folder, optimized_file_name)
    report_file_path = os.path.join(output_folder, f"report_{file_root}.md")

    # Layout Definition: Split workspace into columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"🔴 Legacy Source: `{selected_file}`")
        try:
            with open(legacy_file_path, "r", encoding="utf-8") as f:
                legacy_content = f.read()
            st.code(legacy_content, language="python" if file_ext != ".sql" else "sql", line_numbers=True)
        except Exception as e:
            st.error(f"Could not load legacy file content: {str(e)}")

    with col2:
        st.subheader(f"🟢 Optimized Agent Code: `{optimized_file_name}`")
        if os.path.exists(optimized_file_path):
            try:
                with open(optimized_file_path, "r", encoding="utf-8") as f:
                    optimized_content = f.read()
                st.code(optimized_content, language="python" if out_ext != ".sql" else "sql", line_numbers=True)
            except Exception as e:
                st.error(f"Could not load optimized file content: {str(e)}")
        else:
            st.info("Optimized file code will appear here once the job finishes processing successfully.")

    # 5. Full-Width Section: Analytics Scorecard and Diagnostic Markdown Reports
    st.divider()
    st.subheader("📋 Agentic Diagnostic & Change Impact Report")
    if os.path.exists(report_file_path):
        try:
            with open(report_file_path, "r", encoding="utf-8") as f:
                report_markdown = f.read()
            # Render the report with markdown syntax highlighting directly on screen
            st.markdown(report_markdown)
        except Exception as e:
            st.error(f"Could not load diagnostic report file: {str(e)}")
    else:
        st.info("The Markdown evaluation metrics and code diff breakdown report will display here after execution.")
else:
    st.info("👋 Welcome! Configure your workspace directories on the sidebar and run the engine or select a file to begin code code analysis.")
