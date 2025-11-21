from flask import Flask, render_template, request, redirect, url_for, abort
from config import Config
from models import db, Event, RSVP
from datetime import datetime

import os


app = Flask(__name__)

#secet key for session management
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
#database configuration by render
database_url = os.environ.get("DATABASE_URL")

#fallback
if not database_url:
    database_url = "sqlite:///volunteer.db"

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)



@app.route('/')
def home():
    events = Event.query.order_by(Event.date).all()
    return render_template('index.html', events= events )

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
            date= event_date,
            description=description
        )
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('add_event.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()    
    app.run(debug=True)


