# Data Visualization Dashboard

A simple and interactive data visualization dashboard built with Streamlit that allows users to upload CSV or Excel files and create various types of visualizations.

## Features

- File upload support for CSV and Excel files
- Multiple chart types (Scatter Plot, Line Chart, Bar Chart, Histogram)
- Interactive data preview
- Dynamic axis selection
- Responsive visualizations

## Installation

1. First, ensure Python 3.11 is installed on your system. You can download it from the [official Python website](https://www.python.org/downloads/).

2. After installing Python, open a terminal and verify the installation:
   ```
   python --version
   ```

3. Install the required packages using pip:
   ```
   pip install streamlit pandas plotly openpyxl
   ```

## Running the Dashboard

1. Navigate to the project directory:
   ```
   cd "path/to/Data Visualization"
   ```

2. Start the Streamlit server:
   ```
   streamlit run app_streamlit.py
   ```

3. The dashboard will open automatically in your default web browser.

## Usage

1. Upload your data file (CSV or Excel) using the file uploader
2. Preview your data in the table view
3. Select your desired chart type
4. Choose the variables for X and Y axes
5. The visualization will update automatically

## Troubleshooting

If you encounter any issues with Python or pip not being recognized:

1. Make sure Python is added to your system's PATH
2. Try using `python -m pip` instead of just `pip`
3. For Windows users, you might need to use `py` instead of `python`