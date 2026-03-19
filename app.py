from flask import Flask, render_template, request, redirect, url_for, abort
from models import db, Event, RSVP
from datetime import datetime
import requests
import os

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///volunteer.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Resend email config
app.config["RESEND_API_KEY"]    = os.getenv("RESEND_API_KEY", "")
app.config["RESEND_FROM_EMAIL"] = os.getenv("RESEND_FROM_EMAIL", "Volunteer Hub <noreply@volunteerhub.us>")
app.config["GMAIL_REPLY_TO"]    = os.getenv("GMAIL_REPLY_TO", "")

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    category = request.args.get("category", "").strip()
    if category:
        events = Event.query.filter_by(category=category).order_by(Event.date).all()
    else:
        events = Event.query.order_by(Event.date).all()
    return render_template("index.html", events=events, selected_category=category)


@app.route("/add-event", methods=["GET", "POST"])
def add_event():
    if request.method == "POST":
        title        = request.form.get("title", "").strip()
        organization = request.form.get("organization", "").strip()
        category     = request.form.get("category", "").strip()
        location     = request.form.get("location", "").strip()
        date_str     = request.form.get("date", "")
        description  = request.form.get("description", "").strip()

        event_date = datetime.fromisoformat(date_str).date()

        new_event = Event(
            title=title,
            organization=organization,
            category=category,
            location=location,
            date=event_date,
            description=description,
        )
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for("home"))

    return render_template("add_event.html")


@app.route("/event/<int:event_id>")
def event_detail(event_id):
    event   = Event.query.get_or_404(event_id)
    success = request.args.get("success")
    return render_template("event_detail.html", event=event, success=success)


@app.route("/event/<int:event_id>/rsvp", methods=["POST"])
def rsvp_event(event_id):
    event = Event.query.get_or_404(event_id)

    name  = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()

    if not name or not email:
        abort(400, description="Name and email are required.")

    new_rsvp = RSVP(event_id=event.id, name=name, email=email, phone=phone or None)
    db.session.add(new_rsvp)
    db.session.commit()

    # Send confirmation email
    api_key = app.config.get("RESEND_API_KEY")
    if api_key:
        try:
            requests.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "from":     app.config["RESEND_FROM_EMAIL"],
                    "to":       [email],
                    "subject":  f"RSVP Confirmation for {event.title}",
                    "text":     f"Hi {name},\n\nThanks for signing up for \"{event.title}\".\n\nDate: {event.date.strftime('%B %d, %Y')}\nLocation: {event.location}\n\n— Volunteer Hub",
                    "reply_to": [app.config["GMAIL_REPLY_TO"]] if app.config["GMAIL_REPLY_TO"] else [],
                },
                timeout=10,
            )
        except Exception as exc:
            app.logger.error(f"Email send failed: {exc}")

    return redirect(url_for("event_detail", event_id=event.id, success=1))


if __name__ == "__main__":
    app.run(debug=True)