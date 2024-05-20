import os
from flask import Flask, render_template, request, redirect, url_for
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

if os.path.exists("env.py"):
    import env

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/resume")
def resume():
    return render_template("resume.html")

@app.route("/my_projects")
def my_projects():
    return render_template("my_projects.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        projectsummary = request.form['projectsummary']

        message = Mail(
            from_email=email,
            to_emails='mawadda.kadi@gmail.com',
            subject='New Project Request',
            plain_text_content=f"Name: {name}\nEmail: {email}\n\nProject Description:\n{projectsummary}"
        )

        try:
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(message)
            return redirect(url_for('success'))
        except Exception as e:
            print(str(e))

    return render_template('contact.html')

@app.route('/success')
def success():
    return 'Your message has been sent!'

if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)
