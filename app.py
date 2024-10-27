import os
from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

app = Flask(__name__)

# Upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(request.url)

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        data = pd.read_csv(file_path)
        
        columns = data.columns.tolist()
        return render_template('select_column.html', columns=columns, file_name=file.filename)

@app.route('/show_bar_chart', methods=['POST'])
def show_bar_chart():
    column_name = request.form['column']
    file_name = request.form['file_name']

    # Read the CSV file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    data = pd.read_csv(file_path)

    # Filter the column data
    filtered_data = data[column_name].value_counts()

    # Get the current date
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Plot the bar chart
    plt.figure(figsize=(10, 6))  # Adjust the figure size
    colors = plt.cm.Paired.colors  # Use a set of distinct colors

    bar_plot = filtered_data.plot(kind='bar', color=colors)

    # Add text labels on the bars
    for i in range(len(filtered_data)):
        bar_plot.text(i, filtered_data[i], str(filtered_data[i]), ha='center', va='bottom', fontsize=10)

    # Title with the current date
    plt.title(f"Distribution of {column_name} - {current_date}", fontsize=16)
    plt.xlabel(column_name, fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.xticks(rotation=45, ha='right')  # Rotate the x-axis labels for better readability

    # Save the plot to a bytes buffer for display on the webpage
    img = io.BytesIO()
    plt.tight_layout()  # Adjust layout to prevent clipping
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')

    # Save the plot to a file for download
    download_path = os.path.join(app.config['UPLOAD_FOLDER'], 'bar_chart.png')
    plt.savefig(download_path)

    return render_template('bar_chart.html', plot_url=plot_url, file_name='bar_chart.png')

@app.route('/download/<file_name>')
def download_file(file_name):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], file_name), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
