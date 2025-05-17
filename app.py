from flask import Flask, render_template, request, jsonify
import pandas as pd
import plotly.express as px
import plotly.utils
import json
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Read the file into a pandas DataFrame
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:  # Excel file
                df = pd.read_excel(filepath)
            
            # Get column names for filtering options
            columns = df.columns.tolist()
            
            # Create a sample visualization
            if len(df.columns) >= 2:
                fig = px.scatter(df, x=df.columns[0], y=df.columns[1])
                plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                return jsonify({
                    'success': True,
                    'columns': columns,
                    'plot': plot_json
                })
            
            return jsonify({
                'success': True,
                'columns': columns,
                'error': 'Not enough columns for visualization'
            })
            
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'})
        
    return jsonify({'error': 'Invalid file type'})

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx', 'xls'}

if __name__ == '__main__':
    app.run(debug=True)