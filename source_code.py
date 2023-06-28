from flask import Flask, request, render_template
import os
import shutil
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'repositoryArchive' not in request.files:
        return 'No file uploaded', 400

    file = request.files['repositoryArchive']
    if file.filename == '':
        return 'No selected file', 400

    # Create a temporary directory to store the uploaded file
    temp_dir = 'temp'
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    file.save(file_path)

    # Extract the repository archive
    extract_dir = os.path.splitext(file.filename)[0]
    shutil.unpack_archive(file_path, extract_dir)

    # Change the working directory to the extracted repository directory
    os.chdir(extract_dir)

    try:
        # Access the commit history
        commit_history = subprocess.check_output(['git', 'log']).decode('utf-8')

        # Parse the commit history and generate release notes
        release_notes = parse_commit_history(commit_history)

        # Clean up temporary files and directory
        os.chdir('..')
        shutil.rmtree(temp_dir)

        return render_template('release_notes.html', form_data=release_notes)
    except subprocess.CalledProcessError:
        return render_template('index2.html')

def parse_commit_history(commit_history):
    commits = commit_history.split('\n\n')
    release_notes = []
    for commit in commits:
        commit_data = {}
        lines = commit.strip().split('\n')
        for line in lines:
            if line.startswith('Author'):
                author_parts = line.split(':',1)
                if len(author_parts) > 1:
                    commit_data['Author'] = author_parts[1].strip()
            elif line.startswith('Date'):
                    date_parts = line.split(':',1)
                    if len(date_parts) > 1:
                        commit_data['Date'] = date_parts[1].strip()
            else:
                if 'Message' in commit_data:
                    commit_data['Message'] += '\n' + line.strip()
                else:
                    commit_data['Message'] = line.strip()
        if commit_data:
            release_notes.append(commit_data)
    return release_notes
if __name__ == '__main__':
    app.run()
