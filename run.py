import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash,  make_response, g
from flask_babel import Babel, lazy_gettext as _
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from dotenv import load_dotenv


if os.path.exists("env.py"):
    import env

app = Flask(__name__)

load_dotenv()

# Secret Keys
app.secret_key = os.getenv("SECRET_KEY")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

# Configurations for Flask-Babel
app.config['BABEL_DEFAULT_LOCALE'] = 'de'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
app.config['BABEL_SUPPORTED_LOCALES'] = ['de', 'en']

babel = Babel(app)

logging.basicConfig(level=logging.DEBUG)


def get_locale():
    lang = request.cookies.get('lang')
    if not lang:
        lang = request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES'])
    return lang

babel.init_app(app, locale_selector=get_locale)

@app.before_request
def before_request():
    lang = request.cookies.get('lang')
    if not lang:
        lang = request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES'])
        response = make_response(redirect(request.url))
        response.set_cookie('lang', lang)
        return response
    g.current_lang = lang
    logging.debug(f"Current language set to: {lang}")



@app.route("/")
def index():
    return render_template("index.html")


@app.route('/switch_language/<language>')
def switch_language(language=None):
    response = make_response(redirect(request.referrer))
    response.set_cookie('lang', language)
    logging.debug(f"Switching language to: {language}")
    return response


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

        from_email = Email('mawadda.kadi@gmail.com')
        to_email = To('mawadda.kadi@gmail.com')
        subject = 'New Project Request'
        content = Content('text/plain', f"Name: {name}\nEmail: {email}\n\nProject Description:\n{projectsummary}")

        message = Mail(from_email, to_email, subject, content)
        message.reply_to = Email(email)

        try:
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(message)
            print(f"Response status code: {response.status_code}")
            print(f"Response body: {response.body}")
            print(f"Response headers: {response.headers}")
            flash('Your message has been sent!', 'success')
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            flash('An error occurred while sending your message. Please try again.', 'danger')

    return render_template('contact.html')


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=False)
