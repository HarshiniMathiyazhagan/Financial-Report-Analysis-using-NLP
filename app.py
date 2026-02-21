import streamlit as st
import plotly.express as px
import pandas as pd
from financial_analyzer import FinancialReportAnalyzer

st.set_page_config(page_title="Financial Report Analyzer", layout="wide")

def main():
    st.title("Financial Report Analyzer")
    st.write("""
    Upload your financial report (PDF or text format) to extract and analyze key financial metrics.
    The system uses advanced NLP techniques to identify important financial information.
    """)

    # File upload
    uploaded_file = st.file_uploader("Choose a financial report", type=["pdf", "txt"])

    if uploaded_file is not None:
        with open("temp_report.pdf", "wb") as f:
            f.write(uploaded_file.getvalue())

        try:
            analyzer = FinancialReportAnalyzer()

            # Extract text
            text = analyzer.read_document("temp_report.pdf")

            # Show extracted text preview
            with st.expander("Show extracted text"):
                st.text_area("Extracted Text Preview", text[:3000], height=300)

            # Extract metrics
            metrics = analyzer.extract_financial_metrics(text)

            # Generate and display summary
            summary = analyzer.summarize_text(text)
            st.header("Document Summary")
            st.write(summary)

            # Display metrics
            st.header("Extracted Financial Metrics")
            cols = st.columns(3)
            for idx, (metric, value) in enumerate(metrics.items()):
                with cols[idx % 3]:
                    if value is not None:
                        st.metric(
                            label=metric.replace('_', ' ').title(),
                            value=f"${value:,.2f}"
                        )
                    else:
                        st.metric(
                            label=metric.replace('_', ' ').title(),
                            value="Not found"
                        )

            # Visualize metrics
            st.header("Financial Metrics Visualization")
            valid_metrics = {k: v for k, v in metrics.items() if v is not None}

            if valid_metrics:
                df = pd.DataFrame({
                    'Metric': list(valid_metrics.keys()),
                    'Value': list(valid_metrics.values())
                })

                fig_bar = px.bar(
                    df,
                    x='Metric',
                    y='Value',
                    title='Financial Metrics Overview (Bar Chart)',
                    labels={'Value': 'Value (USD)'},
                    template='plotly_white'
                )
                fig_bar.update_layout(height=500)

                fig_line = px.line(
                    df,
                    x='Metric',
                    y='Value',
                    title='Financial Metrics Trend (Line Plot)',
                    labels={'Value': 'Value (USD)'},
                    template='plotly_white'
                )
                fig_line.update_layout(height=500)

                st.plotly_chart(fig_bar, use_container_width=True)
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.warning("No metrics available for visualization.")

        except Exception as e:
            st.error(f"Error processing document: {str(e)}")

if __name__ == '__main__':
    main()
