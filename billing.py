import streamlit as st
from pymongo import MongoClient
import pandas as pd

# Set up Streamlit app title and intro
st.title("Ben's Call Logs")
st.write("Displaying call logs with pagination.")

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
    created_at = pd.to_datetime(result["created_at"]).strftime("%Y-%m-%d")
    to_name = result["parties"][0]["name"]
    from_name = result["parties"][1]["name"]
    
    # Calculate total call duration in minutes
    total_seconds = sum(dialog.get("duration", 0) for dialog in result["dialog"])
    minute_duration = round(total_seconds / 60, 2)
    
    # Add a summary from the dialog (assuming 'summary' field exists)
    summary = result.get("summary", "No summary provided")
    
    # Append data to call logs
    call_logs.append({
        "When": created_at,
        "To": to_name,
        "From": from_name,
        "Duration (minutes)": minute_duration,
        "Summary": summary
    })

# Convert to DataFrame
df = pd.DataFrame(call_logs)

# Assuming 'df' is already populated with the call log data
page_size = 25
total_pages = max(1, len(df) // page_size + (1 if len(df) % page_size != 0 else 0))

# Initialize session state for the page number
if "page" not in st.session_state:
    st.session_state.page = 1

# Display the current page of the table
start = (st.session_state.page - 1) * page_size
end = start + page_size
df_page = df.iloc[start:end]

# Adjust row indices to start from 1
df_page.index = range(start + 1, start + len(df_page) + 1)

# Display the page with updated indices
st.write(df_page)

# Create "Previous" and "Next" buttons for pagination
col1, col2, _ = st.columns([1, 1, 8])
with col1:
    if st.button("Previous") and st.session_state.page > 1:
        st.session_state.page -= 1
with col2:
    if st.button("Next") and st.session_state.page < total_pages:
        st.session_state.page += 1

# Display current page number
st.write(f"Page {st.session_state.page} of {total_pages}")
