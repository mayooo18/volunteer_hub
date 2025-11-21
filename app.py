from flask import Flask, render_template, request, redirect, url_for, abort
from flask_mail import Mail, Message
from config import Config
from models import db, Event, RSVP
from datetime import datetime
import os

app = Flask(__name__)

# secret key for session management
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")

# database configuration by render
database_url = os.environ.get("DATABASE_URL")

# fallback
if not database_url:
    database_url = "sqlite:///volunteer.db"

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# mail config
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "mendezmario2018@gmail.com")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER", app.config["MAIL_USERNAME"])

mail = Mail(app)

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    category = request.args.get('category')

    if category and category.strip() != '':
        events = Event.query.filter_by(category=category).order_by(Event.date).all()
    else:
        events = Event.query.order_by(Event.date).all()
    return render_template('index.html', events=events, selected_category=category)


@app.route('/add-event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        title = request.form.get('title')
        organization = request.form.get('organization')
        category = request.form.get('category')
        location = request.form.get('location')
        date_str = request.form.get('date')
        description = request.form.get('description')

        event_datetime = datetime.fromisoformat(date_str)
        event_date = event_datetime.date()

        new_event = Event(
            title=title,
            organization=organization,
            category=category,
            location=location,
            date=event_date,
            description=description
        )
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('add_event.html')


@app.route('/event/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    success = request.args.get('success')
    return render_template('event_detail.html', event=event, success=success)


@app.route('/event/<int:event_id>/rsvp', methods=['POST'])
def rsvp_event(event_id):
    event = Event.query.get_or_404(event_id)

    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')

    if not name or not email:
        abort(400, description="Name and email are required for RSVP.")

    new_rsvp = RSVP(
        event_id=event.id,
        name=name,
        email=email,
        phone=phone
    )

    db.session.add(new_rsvp)
    db.session.commit()

    subject = f"RSVP Confirmation for {event.title}"
    msg = Message(
        subject=subject,
        recipients=[email],
        sender=app.config.get("MAIL_DEFAULT_SENDER")
    )

    msg.body = f"""Hi {name},

Thank you for signing up to volunteer at "{event.title}".

Date: {event.date.strftime('%B %d, %Y')}
Location: {event.location}

We appreciate your support!

Volunteer Hub
"""

    mail.send(msg)

    return redirect(url_for('event_detail', event_id=event.id, success=1))


if __name__ == '__main__':
    app.run(debug=True)
