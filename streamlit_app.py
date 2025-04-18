import streamlit as st
import pandas as pd
import plotly.express as px
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="Fund Misuse Detection", layout="wide")

# -------------------- FILE UPLOADER -------------------- #
st.sidebar.header(" Upload your CSV")
uploaded_file = st.sidebar.file_uploader("Upload CSV File", type=["csv"])

# Check if file is uploaded
if uploaded_file is None:
    st.warning("📂 Please upload a CSV file to proceed.")
    st.stop()

# -------------------- DATA PREPROCESSING -------------------- #
df = None  # Initialize df variable to avoid NameError

try:
    df = pd.read_csv(uploaded_file)
    df.dropna(inplace=True)  # Drop rows with missing values
except Exception as e:
    st.error(f"❌ Failed to read uploaded file: {e}")
    st.stop()

# -------------------- SIDEBAR OPTIONS -------------------- #
if df is not None:  # Ensure df is loaded
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

    if not numeric_columns:
        st.warning("No numeric columns found in the dataset.")
        st.stop()

    selected_columns = st.sidebar.multiselect("Select numeric columns", numeric_columns, default=numeric_columns)
    sensitivity = st.sidebar.slider(" Sensitivity", 0.01, 1.0, 0.5)

    if not selected_columns:
        st.warning("Please select at least one numeric column.")
        st.stop()
else:
    st.warning("Data not loaded properly.")

# -------------------- ANOMALY DETECTION -------------------- #
def detect_anomalies(df, selected_columns, sensitivity):
    df['AnomalyScore'] = abs(df[selected_columns] - df[selected_columns].mean()).sum(axis=1)
    threshold = df['AnomalyScore'].quantile(1 - sensitivity)
    anomalies = df[df['AnomalyScore'] > threshold]
    return anomalies

# -------------------- ONLY PROCESS IF df IS AVAILABLE -------------------- #
if df is not None and selected_columns:
    anomalies = detect_anomalies(df, selected_columns, sensitivity)
else:
    anomalies = pd.DataFrame()  # Initialize empty DataFrame if no anomalies detected

# -------------------- EMAIL FUNCTION -------------------- #
def send_email_alert(receiver_email, anomaly_count):
    sender_email = "asthasingh00442@gmail.com"
    password = "tayb uzra jqsw fcaw"  # Use app password or ENV variable

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🚨 Fund Misuse Alert"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    html = f"""
    <html><body>
        <h3>⚠ Alert: {anomaly_count} anomalies detected in fund usage data.</h3>
        <p>Please review your dashboard immediately.</p>
    </body></html>
    """
    msg.attach(MIMEText(html, "html"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        st.success("Email alert sent successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# -------------------- MAIN UI -------------------- #
st.title("Fund Misuse Detection Dashboard")
st.markdown("An AI-driven tool to identify anomalies in fund allocation and utilization.")

# -------------------- CHECK IF ANOMALIES EXIST -------------------- #
if df is not None and anomalies is not None:
    st.subheader("Anomaly Detection Table")
    if anomalies.empty:
        st.warning("No anomalies detected.")
    else:
        st.dataframe(anomalies, use_container_width=True)

    # -------------------- PLOTS -------------------- #
    if 'Department' in df.columns and not anomalies.empty:
        dept_count = anomalies['Department'].value_counts().reset_index()
        dept_count.columns = ['Department', 'Count']
        fig = px.bar(
            dept_count,
            x='Department',
            y='Count',
            title="Anomalies by Department",
            color='Count',
            color_continuous_scale='reds',
        )
        st.plotly_chart(fig, use_container_width=True)

    # -------------------- EMAIL FORM -------------------- #
    st.subheader(" Send Email Alert")
    receiver_email = st.text_input("Recipient Email")
    if st.button("Send Alert"):
        if receiver_email:
            send_email_alert(receiver_email, anomalies.shape[0])
        else:
            st.warning("Please enter a recipient email.")
else:
    st.warning("No anomalies detected yet.")
