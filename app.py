import streamlit as st
import matplotlib.pyplot as plt
from collections import Counter
from io import BytesIO
import plotly.express as px
import pandas as pd
import json
import os
import glob

# Dynamically load tags and file sources from all JSONL files in a batch
all_tags = []
file_sources = []
entry_log = []
dataset_files = st.file_uploader("Upload one or more JSONL dataset files", type="jsonl", accept_multiple_files=True)

if dataset_files:
    for uploaded_file in dataset_files:
        filename = uploaded_file.name
        lines = uploaded_file.read().decode("utf-8").splitlines()
        for line in lines:
            try:
                entry = json.loads(line)
                if "tag" in entry:
                    all_tags.append(entry["tag"])
                    file_sources.append(filename)
                    entry_log.append({"File": filename, "Tag": entry["tag"]})
            except:
                continue

# Preview uploaded tags by file
tab1, tab2 = st.tabs(["📄 Chart", "📊 Preview Uploaded Data"])
with tab2:
    if entry_log:
        st.subheader("Uploaded Tags by File")
        df_log = pd.DataFrame(entry_log)
        st.dataframe(df_log)

        # Per-file summary
        st.subheader("Summary: Tag Counts by File")
        file_summary = df_log.groupby(["File", "Tag"]).size().reset_index(name="Count")

        # Optional filter by tag or file
        selected_tag = st.selectbox("Filter by tag (optional):", options=["All"] + sorted(df_log["Tag"].unique().tolist()))
        selected_file = st.selectbox("Filter by file (optional):", options=["All"] + sorted(df_log["File"].unique().tolist()))

        filtered_summary = file_summary.copy()
        if selected_tag != "All":
            filtered_summary = filtered_summary[filtered_summary["Tag"] == selected_tag]
        if selected_file != "All":
            filtered_summary = filtered_summary[filtered_summary["File"] == selected_file]

        st.dataframe(filtered_summary)

        # Summary chart
        if not filtered_summary.empty:
            st.subheader("Chart: Tag Counts by File")
            chart = px.bar(filtered_summary, x="Tag", y="Count", color="File", barmode="group",
                           title="Filtered Tag Counts by File", text="Count")
            st.plotly_chart(chart)

            # Export as PNG
            chart_png = BytesIO()
            chart.write_image(chart_png, format="png")
            st.download_button("Download Chart as PNG", chart_png.getvalue(), file_name="filtered_tag_chart.png", mime="image/png")

            # Export as PDF
            chart_pdf = BytesIO()
            chart.write_image(chart_pdf, format="pdf")

            # Add a custom header/footer in export section
            logo_path = "logo.png"
            if os.path.exists(logo_path):
                st.image(logo_path, width=120)
            else:
                st.markdown("### 🧠 Mental Health Dataset Creator")

            st.markdown("### 📄 Export Options with Report Style")
            user_id_display = st.session_state.get('user_id', 'anonymous')
            export_datetime = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            st.markdown(f"**Generated by:** `{user_id_display}`  ")
            st.markdown(f"**Generated on:** `{export_datetime}`  ")
            st.markdown("This PDF is generated from the current chart, including custom header info. Future versions may include headers, metadata, and page numbers."))

            st.download_button("Download Chart as PDF", chart_pdf.getvalue(), file_name=f"filtered_tag_chart_{user_id_display}.pdf", mime="application/pdf"), file_name="filtered_tag_chart.pdf", mime="application/pdf"), file_name="filtered_tag_chart.pdf", mime="application/pdf")
        csv = filtered_summary.to_csv(index=False).encode('utf-8')
        st.download_button("Download Summary as CSV", csv, file_name="tag_summary_by_file.csv", mime="text/csv")

# The rest of the app continues unchanged...
