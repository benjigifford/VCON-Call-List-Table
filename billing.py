import streamlit as st
from pymongo import MongoClient
import pandas as pd
import openai
import json
from fpdf import FPDF

# Set up Streamlit app title and intro
st.title("Ben's Call Logs")
st.write("Displaying call logs with pagination and summaries.")

# Set your OpenAI API key
openai.api_key = st.secrets["openai_api_key"]

def generate_summary(vcon_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a summarization assistant."},
                {"role": "user", "content": f"Summarize this VCON: {vcon_text}"}
            ],
            max_tokens=50
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Error generating summary: {e}"

# MongoDB connection (replace with your secret values)
mongo_url = st.secrets["mongo_url"]
mongo_db = st.secrets["mongo_db"]
mongo_collection = st.secrets["mongo_collection"]

client = MongoClient(mongo_url)
db = client[mongo_db]
collection = db[mongo_collection]

# Query MongoDB for all call logs (no filtering by date)
results = collection.find()

# Process results for display
call_logs = []
for result in results:
    # Convert ObjectId to string to avoid serialization issues
    result['_id'] = str(result['_id'])
    
    # For debugging, uncomment the next line to print each JSON to the Streamlit app
    # st.write(result)
    
    created_at = pd.to_datetime(result["created_at"]).strftime("%Y-%m-%d")
    to_name = result["parties"][0]["name"]
    from_name = result["parties"][1]["name"]
    
    # Calculate total call duration in minutes
    total_seconds = sum(dialog.get("duration", 0) for dialog in result["dialog"])
    minute_duration = round(total_seconds / 60, 2)
    
    # Generate a summary using OpenAI for the dialog content
    dialog_text = json.dumps(result)  # Convert JSON to a string
    summary = generate_summary(dialog_text)

    # Append data to call logs with pricing calculation
    call_logs.append({
        "When": created_at,
        "To": to_name,
        "From": from_name,
        "Duration (minutes)": minute_duration,
        "Summary": summary,
       "Price": f"${minute_duration * 0.50:.2f}"  # Calculate price at $0.50/minute
    })


# Convert to DataFrame
df = pd.DataFrame(call_logs)

# Pagination and display setup
page_size = 25
total_pages = max(1, len(df) // page_size + (1 if len(df) % page_size != 0 else 0))

if "page" not in st.session_state:
    st.session_state.page = 1

start = (st.session_state.page - 1) * page_size
end = start + page_size
df_page = df.iloc[start:end]
df_page.index = range(start + 1, start + len(df_page) + 1)
st.write(df_page)

col1, col2, _ = st.columns([1, 1, 8])
with col1:
    if st.button("Previous") and st.session_state.page > 1:
        st.session_state.page -= 1
with col2:
    if st.button("Next") and st.session_state.page < total_pages:
        st.session_state.page += 1

st.write(f"Page {st.session_state.page} of {total_pages}")

def export_to_pdf(df):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Call Logs", ln=True, align='C')

    # Table header
    pdf.set_font("Arial", size=10)
    col_widths = [30, 30, 30, 30, 30, 70]  # Adjusted widths to allocate more space for the Summary column
    headers = ["When", "To", "From", "Duration (minutes)", "Price", "Summary"]
    for header, width in zip(headers, col_widths):
        pdf.cell(width, 10, header, 1, 0, 'C')
    pdf.ln()

    # Table rows
    for _, row in df.iterrows():
        pdf.cell(col_widths[0], 10, row["When"], 1)
        pdf.cell(col_widths[1], 10, row["To"], 1)
        pdf.cell(col_widths[2], 10, row["From"], 1)
        pdf.cell(col_widths[3], 10, str(row["Duration (minutes)"]), 1)
        pdf.cell(col_widths[4], 10, row["Price"], 1)

        # Wrap text for Summary column
        summary = row["Summary"]
        x, y = pdf.get_x(), pdf.get_y()
        pdf.multi_cell(col_widths[5], 10, summary, 1)  # Dynamically adjusts height based on text length
        pdf.set_xy(x + col_widths[5], y)  # Move to the next row start position
        pdf.ln()

    return pdf

# Export to PDF Button
if st.button("Export to PDF"):
    pdf = export_to_pdf(df)
    pdf_output = "call_logs.pdf"
    pdf.output(pdf_output)
    
    with open(pdf_output, "rb") as f:
        st.download_button("Download PDF", f, file_name="call_logs.pdf", mime="application/pdf")

# See Diary Button
if st.button("See Diary"):
    st.write("### Summaries of VCONs")
    for idx, summary in enumerate(df["Summary"], start=1):
        st.markdown(f"- **{idx}:** {summary}")
