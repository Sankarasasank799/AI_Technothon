from flask import Flask, render_template, request, redirect, url_for
from git import Repo
from fpdf import FPDF
import os
from google.cloud import storage
from getpass import getpass

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        git_username = request.form['git_username']
        generate_release_notes(git_username)
        return redirect(url_for('download_release_notes'))
    if request.method == 'GET':
        git_username = input("Enter your GitHub Username : ")
        # git_password = getpass("Password")
        generate_release_notes(git_username)
        download_to_bucket()
    return render_template('web_page.html')


def generate_release_notes(git_username):
    # Fetch the Git repository for the specified username
    repo = Repo.clone_from(f'https://github.com/{git_username}/AI_Technothon',"temp_repo",branch='main')

    # Access the commits and generate release notes
    commits = list(repo.iter_commits())
    release_notes = ""
    for commit in commits:
        release_notes += f"Commit ID: {commit.hexsha}\n"
        release_notes += f"Author: {commit.author.name}\n"
        release_notes += f"Date: {commit.authored_datetime}\n"
        release_notes += f"Message: {commit.message}\n\n"

    # Create a PDF file with the release notes
    pdf = ""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=release_notes, ln=1)
    pdf.output("release_notes.pdf")

def download_to_bucket():
    storage_client = storage.Client()
    temp_bucket = storage_client.bucket("bucket_for_ai_technothon")
    temp_bolb = temp_bucket.blob("release_notes.pdf")

    temp_bolb.upload_from_filename("/home/hemanthpusala531/AI_Technothon/templates/release_notes.pdf")

@app.route('/download')
def download_release_notes():
    return redirect(url_for('static', filename='release_notes.pdf'))

if __name__ == '__main__':
    port= int(os.environ.get('PORT',8003))
    app.run(debug=True,host='0.0.0.0',port=port)
