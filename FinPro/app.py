import streamlit as st
import plotly.express as px
import pandas as pd
from financial_analyzer import FinancialReportAnalyzer
import google.generativeai as genai
import os

# Set your Gemini API key
GENAI_API_KEY = "***"
genai.configure(api_key=GENAI_API_KEY)

def get_gemini_summary(text):
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        response = model.generate_content(f"Summarize this executive message without altering the tone or meaning:\n\n{text}")
        return response.text
    except Exception as e:
        return f"Gemini Error: {str(e)}"

def process_report(file, label):
    with open(f"temp_{label}.pdf", "wb") as f:
        f.write(file.getvalue())
    analyzer = FinancialReportAnalyzer()
    text = analyzer.read_document(f"temp_{label}.pdf")
    metrics = analyzer.extract_financial_metrics(text)
    summary = analyzer.summarize_text(text)
    gemini_summary = get_gemini_summary(summary)
    return metrics, text, gemini_summary

def visualize_comparison(metrics1, metrics2, label1, label2):
    keys = set(metrics1.keys()) | set(metrics2.keys())
    data = {
        "Metric": [],
        label1: [],
        label2: []
    }

    for key in keys:
        data["Metric"].append(key.replace("_", " ").title())
        data[label1].append(metrics1.get(key, 0) or 0)
        data[label2].append(metrics2.get(key, 0) or 0)

    df = pd.DataFrame(data)

    st.subheader("Metric Comparison Table")
    st.dataframe(df)

    fig = px.bar(df, x="Metric", y=[label1, label2],
                 barmode="group", title="Year-wise Financial Metric Comparison",
                 labels={"value": "Value (USD)"})
    st.plotly_chart(fig, use_container_width=True)

def main():
    st.set_page_config(page_title="FinPro – AI Financial Report Analyzer", layout="wide")
    st.title("📊 FinPro: AI-Powered Financial Report Analyzer")

    st.write("Upload **two annual reports** of the same company to compare their key financial metrics.")

    col1, col2 = st.columns(2)
    with col1:
        file1 = st.file_uploader("Upload Year 1 Report", type=["pdf", "txt"], key="file1")
    with col2:
        file2 = st.file_uploader("Upload Year 2 Report", type=["pdf", "txt"], key="file2")

    if file1 and file2:
        year1 = st.text_input("Label for Year 1 (e.g., 2022)", "Year 1")
        year2 = st.text_input("Label for Year 2 (e.g., 2023)", "Year 2")

        with st.spinner("Processing both reports..."):
            metrics1, text1, gemini_summary1 = process_report(file1, "year1")
            metrics2, text2, gemini_summary2 = process_report(file2, "year2")

            st.header("Executive Summary Comparison")
            st.subheader(f"{year1} Summary")
            st.write(gemini_summary1)

            st.subheader(f"{year2} Summary")
            st.write(gemini_summary2)

            st.header("Financial Metrics Comparison")
            visualize_comparison(metrics1, metrics2, year1, year2)

    elif file1 or file2:
        st.info("Please upload both reports to compare.")

if __name__ == "__main__":
    main()

