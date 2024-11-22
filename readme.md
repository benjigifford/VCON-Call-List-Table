# Streamlit Paged Table Application

This Streamlit application connects to a MongoDB database to display call logs with pagination, making it easy to browse through call records.

## Features

- Displays call logs with pagination (25 logs per page)
- Shows call details including date, recipient, sender, duration, and a summary
- "Previous" and "Next" buttons for navigation through pages
- Automatically calculates call duration in minutes
  
## Requirements

- Python 3.12 or later
- Required packages: `streamlit`, `pandas`, `pymongo`, `fpdf`

## Installation

Install dependencies using pip:
```bash
pip install streamlit pandas pymongo fpdf
```
## Usage

Configure MongoDB credentials in secrets.toml:

```
mongo_url = "<your_mongodb_url>"
mongo_db = "<your_database_name>"
mongo_collection = "<your_collection_name>"
openai_api_key = "<your_api_key>"
```

To run the application, simply execute the following command:

```bash
streamlit run app.py
```

## Configuration

The page size (number of logs per page) is set to 25 but can be modified in the code.
MongoDB query filters can be added to retrieve specific data ranges if desired.

## Contributing

Contributions are welcome! If you'd like to contribute to this project, please fork the repository and submit a pull request.

## File Overview

- billing.py: Main application script to load data, process, and display it with pagination.
- secrets.toml: Stores MongoDB connection details for secure access.

## License

This application is licensed under the MIT License.
