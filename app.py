import base64
import datetime
import hashlib
import hmac
import json
import os
import secrets
import string
import time
from urllib.parse import urlencode
import uuid
from datetime import datetime, timedelta


from dotenv import load_dotenv
from flask import flash, jsonify, redirect, render_template, request, session, url_for
from flask import (
    Flask,
    flash,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from flask import flash, redirect, render_template, request, session, url_for
from flask_cors import CORS
from flask_mail import Mail
from flask_mail import Message
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from google.auth import default
from google_auth_oauthlib.flow import Flow
import requests
from sqlalchemy import or_
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from utils import gen_id, generate_token, verify_token, generate_otp
from mailer import  send_welcome_email, send_submission_email, send_welcome_email, send_suspension_email, send_follow_up_email, send_otp

load_dotenv()


from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "articles")

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", os.getenv('SK'))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "tunu_journal.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024
app.config['MAIL_SERVER'] = 'mail.tunujournal.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=72)

# app.config["SESSION_COOKIE_SECURE"] = True  #
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app.config['MAIL_USERNAME'] = 'support@tunujournal.com'
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASS_S')


INFO_EMAIL = "info@tunujournal.com"
SUPPORT_EMAIL = "support@tunujournal.com"
NOREPLY_EMAIL = "noreply@tunujournal.com"

app.config["UPLOAD_M_FOLDER"] = os.path.join(BASE_DIR, "static","uploads", "manuscripts")
os.makedirs(app.config["UPLOAD_M_FOLDER"], exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["MAIL_DEFAULT_SENDER"] = (
    "Tunu Journal",
     f'{SUPPORT_EMAIL}'
)

CORS(
    app,
    supports_credentials=True,
    origins=[
        "https://www.tunujournal.com",
        "https://www.submit.tunujournal.com",
        "https://tunujournal.com",
        "https://submit.tunujournal.com",
    ]
)

db = SQLAlchemy(app)
mail = Mail(app)
migrate = Migrate(app, db)


GOOGLE_CLIENT_SECRETS_FILE = "client_secret.json"

DELTA = 3

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

SECRET_KEY = "super-token-secret"

limiter = Limiter(
    key_func = get_remote_address,
    app=app,
    storage_uri = "memory://",
    default_limits=['200 per day', "5 per minute"]
)

OTHER_ROUTES = {
    "dashboard",
    "profile",
    "submit",
}

# MODELS

class Volume(db.Model):
    __tablename__ = "volumes"

    id = db.Column(db.Integer, primary_key=True)
    volume_number = db.Column(db.String(50), nullable=False)
    year = db.Column(db.String(4), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.Text, nullable=False)

    issues = db.relationship(
        "Issue",
        backref="volume",
        lazy=True,
        cascade="all, delete-orphan"
    )

class Issue(db.Model):
    __tablename__ = "issues"

    id = db.Column(db.Integer, primary_key=True)
    issue_number = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    volume_id = db.Column(db.Integer, db.ForeignKey("volumes.id"), nullable=False)

    articles = db.relationship(
        "Article",
        backref="issue",
        lazy=True,
        cascade="all, delete-orphan"
    )

class Article(db.Model):
    __tablename__ = "articles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    authors = db.Column(db.String(500), nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    doi = db.Column(db.String(150), nullable=True, unique=True)
    keywords_raw = db.Column(db.String(500), nullable=True)
    body_text = db.Column(db.Text, nullable=False)
    pdf_file = db.Column(db.String(300), nullable=True)
    published_date = db.Column(db.String(50), nullable=True)
    issue_id = db.Column(db.Integer, db.ForeignKey("issues.id"), nullable=False)

    references = db.relationship(
        "Reference",
        backref="article",
        lazy=True,
        cascade="all, delete-orphan"
    )

    @property
    def keywords(self):
        if not self.keywords_raw:
            return []
        return [keyword.strip() for keyword in self.keywords_raw.split(",") if keyword.strip()]

    @property
    def doi_url(self):
        if not self.doi:
            return None
        return f"https://doi.org/{self.doi}"

    @property
    def article_url(self):
        return url_for(
            "article_detail",
            volume_id=self.issue.volume_id,
            issue_id=self.issue.id,
            article_id=self.id
        )

class Reference(db.Model):
    __tablename__ = "references"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey("articles.id"), nullable=False)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(50), unique=True, index=True, default=lambda: gen_id("TJ", 6, True))
    google_id = db.Column(db.String(255), unique=True, index=True, nullable=True)
    email = db.Column(db.String(255), unique=True, index=True, nullable=False)
    password = db.Column(db.String(1012), nullable=True) 
    name = db.Column(db.String(255), nullable=False)
    tkv = db.Column(db.String(50), unique=True, index=True, default=lambda: gen_id("TK", 10))
    
    email_method = db.Column(db.Boolean, default=False, nullable=False)
    google_method = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_super_admin = db.Column(db.Boolean, default=False, nullable=True)

    role = db.Column(db.String(50), default='author', nullable=False) 
    institution = db.Column(db.String(255), nullable=True)
    orcid_id = db.Column(db.String(50), unique=True, index=True, nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)
    updated_by = db.Column(db.String, db.ForeignKey("users.id"), nullable=True)

class OTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10))
    user_id = db.Column(db.String, db.ForeignKey("users.id"), nullable=True)
    
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)
    is_used = db.Column(db.Boolean, default=False, nullable=False)
    
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10))
    level = db.Column(db.String(10))
    message = db.Column(db.String(1024))
    user_id = db.Column(db.String, db.ForeignKey("users.id"), nullable=False)
    accessed_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(410))
    last_login = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    last_logout = db.Column(db.DateTime, nullable=True)
    admin_id = db.Column(db.String, db.ForeignKey("users.id"), nullable=False)
    admin_uid = db.Column(db.String, db.ForeignKey("users.uid"), nullable=False)

class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.String(20), primary_key=True, default=lambda: gen_id("SUB", 10))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    title = db.Column(db.String(500))
    abstract = db.Column(db.Text)
    pdf_url = db.Column(db.String(500))
    status = db.Column(db.String(50), default="Pending")
    
    user = db.relationship("User", backref="submissions")

class EmailProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Integer, default=0)
    sent = db.Column(db.Integer, default=0)
    current = db.Column(db.String(255))
    p_type = db.Column(db.String(255), default="Auto")
    running = db.Column(db.Boolean, default=False)
    cancelled = db.Column(db.Boolean, default=False)
    initiated_at = db.Column(db.DateTime, default=datetime.utcnow() + timedelta(hours=DELTA), nullable=False)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(10), default=gen_id('NOTIF', 6))
    title = db.Column(db.String(556), nullable=False)
    category = db.Column(db.String(556), nullable=False, default="system")
    desc = db.Column(db.String(7890), nullable=False)
    icon = db.Column(db.String(), nullable=False, default='info-circle')
    created_at = db.Column(db.DateTime, default=datetime.utcnow() + timedelta(hours=DELTA), nullable=False)
    target_id = db.Column(db.String, db.ForeignKey("users.id"), nullable=True)
    by_id = db.Column(db.String, db.ForeignKey("users.id"), nullable=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    is_single = db.Column(db.Boolean, default=False, nullable=False)
        
    def to_dict(self):
            return {
                'id':self.id,
                'uid':self.uid,
                'title':self.title,
                'category':self.category,
                'desc':self.desc,
                'icon':self.icon,
                'created_at': self.created_at,
                'target_id': self.target_id,
                'is_read':self.is_read,
            }
        
 
# APP UTILS

def check_admin(id):
    admin = Admin.query.filter_by(admin_id=id).first()
    if admin:
        return True
    else:
        return False
    
def get_current_user():
    token = request.headers.get("Authorization")
    if not token:
        token = request.args.get('token')
        
    if not token:
        return None

    payload = verify_token(token)
    if not payload:
        return None

    user = User.query.get(payload["user_id"])
    if not user:
        return None

    if user.tkv != payload["tkv"]:
        return None

    return user

@limiter.limit('2 per 5 minutes')
def init_otp(user, resend):
    try:
        existing = OTP.query.filter_by(user_id=user.id).first()

        if existing:
            expiry = existing.created_at + timedelta(minutes=5)

            if datetime.utcnow() < expiry:
                return send_otp(mail, INFO_EMAIL, user, existing.code, resend)

            db.session.delete(existing)
            db.session.flush()

        otp = generate_otp()

        new_otp = OTP(
            user_id=user.id,
            code=otp
        )

        db.session.add(new_otp)

        if not send_otp(mail, INFO_EMAIL, user, otp, resend):
            db.session.rollback()
            return False

        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        print(e)
        return False
     
def push_system_log(uid, code, level, message):
    new_log = Log(code=code, level=level, message=message, user_id=uid)
    db.session.add(new_log)
    db.session.commit()
    
@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

    
@app.errorhandler(500)
def internal_server_error(error):
    flash("An internal server error occurred. Please try again later.", "error")
    return render_template("500.html"), 500


@app.errorhandler(413)
def file_too_large(error):
    flash("That PDF is too large. Maximum allowed size is 25MB.")
    return redirect(request.referrer or url_for("home"))

@app.before_request
def checkuser():
    protected = (
        request.path.startswith("/admin/") and not request.path.startswith("/admin/login")
        or request.endpoint in OTHER_ROUTES
    )

    if not protected:
        return

    user = User.query.get(session.get("user_id"))
    
    if  not user:
        session.clear()
        flash("Please login to continue", "error")
        return redirect(url_for("home", login='_'))

    if  not user.is_active:
        session.clear()
        flash("Your account has been deactivated. Please contact support", "error")
        send_suspension_email(user, mail)
        return redirect(url_for("home"))


@app.route("/")
def home():
    subjects = db.session.query(Volume.subject).distinct().all()
    categories = []

    for subject_row in subjects:
        subject = subject_row[0]

        latest_volume = (
            Volume.query
            .filter_by(subject=subject)
            .order_by(Volume.year.desc(), Volume.id.desc())
            .first()
        )

        current_issue = None

        if latest_volume:
            current_issue = (
                Issue.query
                .filter_by(volume_id=latest_volume.id)
                .order_by(Issue.id.desc())
                .first()
            )

        categories.append({
            "name": subject,
            "latest_volume": latest_volume,
            "current_issue": current_issue
        })

    latest_articles = (
        Article.query
        .join(Issue)
        .join(Volume)
        .order_by(Article.id.desc())
        .limit(6)
        .all()
    )

    return render_template(
        "home.html",
        categories=categories,
        latest_articles=latest_articles
    )

# AUTHENTICATION

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'All fields are required'}), 400
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'All fields are required'}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if user.google_method and not user.email_method or not user.password or user.google_id:
        return jsonify({'error': 'Invalid login method. Please login using Google.'}), 400
    
    if not check_password_hash(user.password, password):
        return jsonify({
            "error": "Invalid credentials"
        }), 401
    
    user.tkv = gen_id("TK", 10)
    db.session.commit()

    token = generate_token(user.id, user.tkv)

    session['user_id'] = user.id
    session['token'] = token
    session['user_name'] = user.name

    return jsonify({'status':'ok'}), 200  

@app.route('/api/register', methods=['GET', 'POST'])
def api_register():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        institution = request.form.get('institution')
        orcid_id = request.form.get('orcid_id')
        phone = request.form.get('phone')

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template('register.html')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with that email address already exists.", "error")
            return render_template('register.html')

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            institution=institution,
            orcid_id=orcid_id or None,
            phone=phone,
            role="scholar",
            tkv=gen_id("TKV", 8)
        )
        
        db.session.add(new_user)
        
        db.session.commit()
        session.clear()
        session['user_id'] = new_user.id
        session['user_name'] = new_user.name
        
        try:
            if init_otp(new_user, False):
                print('OTP sent')
        except Exception as e:
            print( f'Error occured: {str(e)}')
        

        flash("Registration successful. Please verify your account using the OTP sent to your email.", "success")
        return redirect(url_for('verify_otp'))

    return render_template('register.html')

@app.route("/google/login")
def login():
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for("callback", _external=True)
    )

    auth_url, _ = flow.authorization_url(prompt="consent")
    return redirect(auth_url)

@app.route("/google/callback")
def callback():
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for("callback", _external=True)
    )

    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    user_info = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {credentials.token}"}
    ).json()

    google_id = user_info["sub"]
    email = user_info["email"]
    name = user_info["name"]

    user = User.query.filter_by(google_id=google_id).first()
    
    if not user.is_active:
        flash('Your account has been suspended. Please contact support', 'error') 
        return redirect(url_for('home'))

    if not user:
        user = User(
            google_id=google_id,
            email=email,
            name=name,
            google_method=True,
            email_method=False,
            is_active=True,
            tkv=gen_id("TK", 10)
        )
        db.session.add(user)
        db.session.commit()

    user.tkv = gen_id("TK", 10)
    db.session.commit()

    token = generate_token(user.id, user.tkv)

    session['user_id'] = user.id
    session['token'] = token
    session['user_name'] = user.name
    
    flash('Logged in Successfully')
    return redirect(
        url_for('dashboard')
    )

# DEFAULT FILES

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    results = []

    if query:
        search_term = f"%{query}%"

        results = (
            Article.query
            .filter(
                or_(
                    Article.title.ilike(search_term),
                    Article.authors.ilike(search_term),
                    Article.abstract.ilike(search_term),
                    Article.keywords_raw.ilike(search_term),
                    Article.doi.ilike(search_term)
                )
            )
            .order_by(Article.id.desc())
            .all()
        )

    return render_template(
        "search.html",
        query=query,
        results=results
    )

@app.route("/faculty")
def faculty():
    faculty_members = [
        {
            "name": "Dr. Lina Akaka",
            "role": "-Loading...",
            "institution": "-Loading..."
        },
        {
            "name": "Prof. Tom Olali",
            "role": "-Loading...",
            "institution": "-Loading..."
        },
        {
            "name": "Dkt. Angela Sawe",
            "role": "-Loading...",
            "institution": "-Loading..."
        }
    ]

    return render_template(
        "faculty.html",
        faculty=faculty_members
    )

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/terms-of-use")
def terms():
    return render_template('terms_of_use.html')

@app.route("/privacy-policy")
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route("/submission-guidelines/kiswahili")
def submission_guidelines_swa():
    return render_template("submission_guidelines_kiswahili.html")

@app.route("/submission-guidelines/education")
def submission_guidelines_edu():
    return render_template("submission_guidelines_education.html")

@app.route("/submission-guidelines")
def submission_guidelines():
    return render_template("submission_guidelines_education.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route("/dashboard")
def dashboard():
    user = None
    
    token = request.args.get('token') or session.get('token')
    params = request.args.get('params')

    if params:
        try:
            decoded_data = json.loads(base64.urlsafe_b64decode(params.encode()).decode())
            token = decoded_data.get('token')
        except Exception:
            pass

    if token:
        payload = verify_token(token)
        if payload:
            user = User.query.get(payload["user_id"])
            if user and user.tkv == payload["tkv"]:
                session['user_id'] = user.id
                session['token'] = token

    if not user and 'user_id' in session:
        user = User.query.get(session['user_id'])

    if not user:
        flash("Please log in to access the dashboard.")
        return redirect(url_for('home'))

    if not user.is_verified:
        flash("Account not verified. Verify to continue.", 'error')
        return redirect(url_for('verify_otp'))


    submissions = Submission.query.filter_by(user_id=user.id).all()
    return render_template("dashboard.html", user=user, submissions=submissions)

# APP ROUTES

@app.route("/submit", methods=["POST"])
def submit():
    user = None
    token = session.get('token')

    if token:
        payload = verify_token(token)
        if payload:
            user = User.query.get(payload["user_id"])
            if user and user.tkv != payload["tkv"]:
                user = None

    if not user and 'user_id' in session:
        user = User.query.get(session['user_id'])

    if not user:
        flash("Authorization is required to submit a manuscript.")
        return redirect(url_for('home'))

    title = request.form.get("title")
    abstract = request.form.get("abstract")
    file = request.files.get("pdf")

    if not file or file.filename == '':
        flash("A PDF file is required for submission.")
        return redirect(url_for('dashboard'))

    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(gen_id('SUB', 20) + ".pdf")
        path = os.path.join(app.config["UPLOAD_M_FOLDER"], filename)
        file.save(path)

        submission = Submission(
            user_id=user.id,
            title=title,
            abstract=abstract,
            pdf_url=filename
        )
        db.session.add(submission)
        db.session.commit()
        flash("Manuscript submitted successfully.")
    else:
        flash("Invalid file format. Only PDF files are accepted.")

    return redirect(url_for('dashboard'))

@app.route("/submission/<string:submission_id>/download")
def download_submission_pdf(submission_id):
    user = None
    token = session.get('token')

    if token:
        payload = verify_token(token)
        if payload:
            user = User.query.get(payload["user_id"])
            if user and user.tkv != payload["tkv"]:
                user = None

    if not user and 'user_id' in session:
        user = User.query.get(session['user_id'])

    if not user:
        flash("Authorization is required to download this document.")
        return redirect(url_for('home'))

    submission = Submission.query.get_or_404(submission_id)
    
    if submission.user_id != user.id and not session.get('admin_logged_in'):
        flash("Unauthorized access to this submission.")
        return redirect(url_for('dashboard'))

    if not submission.pdf_url:
        flash("No PDF file associated with this submission.")
        return redirect(url_for('dashboard'))

    file_path = os.path.join(app.config["UPLOAD_M_FOLDER"], submission.pdf_url)

    if not os.path.exists(file_path):
        flash("The PDF file could not be found.")
        return redirect(url_for('dashboard'))

    return send_from_directory(
        app.config["UPLOAD_M_FOLDER"],
        submission.pdf_url,
        as_attachment=True,
        download_name=f"submission_{submission.id}.pdf"
    )

@app.route('/uploads/M/<filename>')
def get_file(filename):
    filename = secure_filename(filename)    
    return send_from_directory(app.config["UPLOAD_M_FOLDER"], filename)

@app.route("/volume/<volume_id>")
def volume_detail(volume_id):
    volume = Volume.query.get_or_404(volume_id)

    issues = (
        Issue.query
        .filter_by(volume_id=volume.id)
        .order_by(Issue.id.desc())
        .all()
    )

    return render_template(
        "volume.html",
        volume=volume,
        issues=issues
    )

@app.route("/volume/<int:volume_id>/issue/<int:issue_id>")
def issue_detail(volume_id, issue_id):
    volume = Volume.query.get_or_404(volume_id)

    issue = Issue.query.filter_by(
        id=issue_id,
        volume_id=volume.id
    ).first_or_404()

    articles = (
        Article.query
        .filter_by(issue_id=issue.id)
        .order_by(Article.id.desc())
        .all()
    )

    return render_template(
        "issue.html",
        volume=volume,
        issue=issue,
        articles=articles
    )

@app.route("/volume/<int:volume_id>/issue/<int:issue_id>/article/<int:article_id>")
def article_detail(volume_id, issue_id, article_id):
    volume = Volume.query.get_or_404(volume_id)

    issue = Issue.query.filter_by(
        id=issue_id,
        volume_id=volume.id
    ).first_or_404()

    article = Article.query.filter_by(
        id=article_id,
        issue_id=issue.id
    ).first_or_404()

    related_articles = (
        Article.query
        .filter(
            Article.issue_id == issue.id,
            Article.id != article.id
        )
        .limit(4)
        .all()
    )

    return render_template(
        "article.html",
        volume=volume,
        issue=issue,
        article=article,
        related_articles=related_articles
    )

@app.route("/article/<int:article_id>/download")
def download_pdf(article_id):
    article = Article.query.get_or_404(article_id)

    if not article.pdf_file:
        flash("The PDF for this article has not been uploaded yet.", 'error')
        return redirect(article.article_url)

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], article.pdf_file)

    if not os.path.exists(file_path):
        flash("The PDF file could not be found.", 'error')
        return redirect(article.article_url)

    flash("PDF downloaded successfully.", 'success')

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        article.pdf_file,
        as_attachment=True,
        download_name=f"tunu_journal_article_{article.id}.pdf"
    )

@app.route("/archives")
def archives():
    page = request.args.get("page", 1, type=int)
    per_page = 6

    pagination = (
        Volume.query
        .order_by(Volume.year.desc(), Volume.id.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return render_template(
        "archive.html",
        volumes=pagination.items,
        page=page,
        total_pages=pagination.pages,
        pagination=pagination
    )

# USER VERIFICATION

@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    user = User.query.get(session.get("user_id"))

    if not user:
        return redirect(url_for("home", login='_'))
    
    if user.is_verified:
        flash("Account already verified", "info")
        return redirect(url_for('dashboard'))
    
    if request.method == "POST":
        otp = request.form.get("otp", "").strip()

        user_otp = OTP.query.filter_by(
            user_id=user.id,
            is_used=False
        ).first()

        if not user_otp and not user.is_verified:
            flash("No valid OTP found. Please press 'Resend OTP' button below", "error")
            return redirect(url_for("verify_otp"))
        
        if user_otp.code != otp:
            flash("Invalid OTP.", "error")
            return redirect(url_for("verify_otp"))

        user.is_verified = True
        user_otp.is_used = True

        db.session.commit()
        session['user_id'] = user.id
        session['user_name'] = user.name
        
        send_welcome_email( user, mail)

        flash("OTP verified successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template("verify.html")

@app.route("/resend-otp")
@limiter.limit('2 per 5 minutes')
def resend_otp():
    user = User.query.filter_by(id=session.get('user_id')).first()
    if init_otp(user, True):
       flash('OTP resend successfully', 'success')
    else:
       flash('Failed to resend email. Please try again or contact support', 'error') 
    return render_template('verify.html')

# SEO ROUTES

@app.route("/robots.txt")
def robots():
    robots_text = f"User-agent: *\nAllow: /\n\nSitemap: {request.url_root}sitemap.xml\n"
    return app.response_class(
        robots_text,
        mimetype="text/plain"
    )

@app.route("/sitemap.xml")
def sitemap():
    pages = []

    static_routes = [
        "home",
        "archives",
        "faculty",
        "about"
    ]

    for route in static_routes:
        pages.append(url_for(route, _external=True))

    articles = Article.query.all()

    for article in articles:
        pages.append(url_for(
            "article_detail",
            volume_id=article.issue.volume_id,
            issue_id=article.issue.id,
            article_id=article.id,
            _external=True
        ))

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for page_url in pages:
        xml.append("<url>")
        xml.append(f"<loc>{page_url}</loc>")
        xml.append("</url>")

    xml.append("</urlset>")

    return app.response_class(
        "\n".join(xml),
        mimetype="application/xml"
    )


#ADMIN MANAGEMENT!!!
@app.route('/admin')
def admin_portal():
    volumes = Volume.query.all()
    return render_template('admin.html', volumes=volumes)

@app.route('/admin/login', methods=['POST'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    
    if username and password:
        user = User.query.filter_by(email=username).first()
        
        if not user.is_active:
            flash('Your account has been suspended. Please contact support', 'error') 
            return redirect(url_for('logout'))
        
        if user and check_password_hash(user.password, password):
            
            if user.is_admin:
                
                token = generate_token(user.id, user.tkv)
                
                session['admin_logged_in'] = True
                session['user_id'] = user.id
                session['admin_token'] = token
                session['user_name'] = user.name
                
                return redirect(url_for('admin_portal'))
            else:
                flash("You do not have enough permisions to view this page.", 'error')
                return redirect(url_for('admin_portal'))
        else:
            flash("Invalid administrative identification credentials.", 'error')
            return redirect(url_for('admin_portal'))
    else:
        flash("Invalid administrative identification credentials.", 'error')
        return redirect(url_for('admin_portal'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_portal'))

@app.route('/admin/structure')
def admin_structure():
    if not session.get('admin_logged_in'):
        flash("Authorization required.", 'error')
        return redirect(url_for('admin_portal'))
    volumes = Volume.query.all()
    return render_template('admin_structure.html', volumes=volumes)

@app.route('/admin/publish')
def admin_publish():
    if not session.get('admin_logged_in'):
        flash("Authorization required.", 'error')
        return redirect(url_for('admin_portal'))
    volumes = Volume.query.all()
    return render_template('admin_publish.html', volumes=volumes)

@app.route('/admin/add-volume', methods=['POST'])
def admin_add_volume():
    if not session.get('admin_logged_in'):
        flash("Authorization required.", 'error')
        return redirect(url_for('admin_portal'))
    
    vol = Volume(
        volume_number=request.form.get('volume_number'),
        year=request.form.get('year'),
        subject=request.form.get('subject'),
        title=request.form.get('title'),
        desc=request.form.get('desc')
    )
    db.session.add(vol)
    db.session.commit()
    return redirect(url_for('admin_portal'))

@app.route('/admin/add-issue', methods=['POST'])
def admin_add_issue():
    if not session.get('admin_logged_in'):
        flash("Authorization required.", 'error')
        return redirect(url_for('admin_portal'))
    
    iss = Issue(
        issue_number=request.form.get('issue_number'),
        title=request.form.get('title'),
        date=request.form.get('date'),
        volume_id=int(request.form.get('volume_id'))
    )
    db.session.add(iss)
    db.session.commit()
    return redirect(url_for('admin_portal'))

@app.route('/admin/add-article', methods=['POST'])
def admin_add_article():
    if not session.get('admin_logged_in'):
        flash("Authorization required.", 'error')
        return redirect(url_for('admin_portal'))
    
    pdf_file = request.files.get('pdf_file')
    filename_saved = None
    
    if pdf_file and pdf_file.filename.endswith('.pdf'):
        secure_name = secure_filename(pdf_file.filename)
        destination = os.path.join(app.config['UPLOAD_FOLDER'], secure_name)
        pdf_file.save(destination)
        filename_saved = secure_name
        
    art = Article(
        title=request.form.get('title'),
        authors=request.form.get('authors'),
        abstract=request.form.get('abstract'),
        doi=request.form.get('doi'),
        keywords_raw=request.form.get('keywords_raw'),
        body_text=request.form.get('body_text'),
        issue_id=int(request.form.get('issue_id')),
        pdf_file=filename_saved
    )
    db.session.add(art)
    db.session.commit()
    return redirect(url_for('admin_portal'))

@app.route('/admin/volume/edit/<int:volume_id>', methods=['GET'])
def admin_edit_volume(volume_id):
    if not session.get('admin_logged_in'):
        flash("Authorization required.", 'error')
        return redirect(url_for('admin_portal'))
    volume = Volume.query.get_or_404(volume_id)
    return render_template('admin_edit_volume.html', volume=volume)

@app.route('/admin/volume/update/<int:volume_id>', methods=['POST'])
def admin_update_volume(volume_id):
    if not session.get('admin_logged_in'):
        flash("Authorization required.", 'error')
        return redirect(url_for('admin_portal'))
    
    volume = Volume.query.get_or_404(volume_id)
    volume.volume_number = request.form.get('volume_number')
    volume.year = request.form.get('year')
    volume.subject = request.form.get('subject')
    volume.title = request.form.get('title')
    volume.desc = request.form.get('desc')
    db.session.commit()
    return redirect(url_for('admin_portal'))

@app.route('/admin/volume/delete/<int:volume_id>')
def admin_delete_volume(volume_id):
    if not session.get('admin_logged_in'):
        flash("Authorization required.", 'error')
        return redirect(url_for('admin_portal'))
    volume = Volume.query.get_or_404(volume_id)
    db.session.delete(volume)
    db.session.commit()
    return redirect(url_for('admin_portal'))

@app.route('/admin/issue/edit/<int:issue_id>', methods=['GET'])
def admin_edit_issue(issue_id):
    if not session.get('admin_logged_in'):
        flash("Authorization required.", 'error')
        return redirect(url_for('admin_portal'))
    issue = Issue.query.get_or_404(issue_id)
    volumes = Volume.query.all()
    return render_template('admin_edit_issue.html', issue=issue, volumes=volumes)

@app.route('/admin/issue/update/<int:issue_id>', methods=['POST'])
def admin_update_issue(issue_id):
    if not session.get('admin_logged_in'):
        flash("Authorization required.", 'error')
        return redirect(url_for('admin_portal'))
    issue = Issue.query.get_or_404(issue_id)
    issue.volume_id = int(request.form.get('volume_id'))
    issue.issue_number = request.form.get('issue_number')
    issue.date = request.form.get('date')
    issue.title = request.form.get('title')
    db.session.commit()
    return redirect(url_for('admin_portal'))

@app.route('/admin/issue/delete/<int:issue_id>')
def admin_delete_issue(issue_id):
    if not session.get('admin_logged_in'):
        flash("Authorization required.", 'error')
        return redirect(url_for('admin_portal'))
    issue = Issue.query.get_or_404(issue_id)
    db.session.delete(issue)
    db.session.commit()
    return redirect(url_for('admin_portal'))

@app.route('/admin/article/edit/<int:article_id>', methods=['GET'])
def admin_edit_article(article_id):
    if not session.get('admin_logged_in'):
        flash("Authorization required.", 'error')
        return redirect(url_for('admin_portal'))
    article = Article.query.get_or_404(article_id)
    volumes = Volume.query.all()
    return render_template('admin_edit_article.html', article=article, volumes=volumes)

@app.route('/admin/submissions', methods=['GET'])
def admin_submissions():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_portal'))
        
    submissions = Submission.query.order_by(Submission.id.desc()).all()
    return render_template('admin_submissions.html', submissions=submissions)

@app.route('/admin/submission/status/<submission_id>', methods=['POST'])
def update_submission_status(submission_id):
    if not session.get('admin_logged_in'):
        flash("Unauthorized administrative access attempt.", "error")
        return redirect(url_for('admin_portal'))
        
    submission = Submission.query.get_or_404(submission_id)
    user = User.query.filter_by(id=submission.user_id).first()
    
    if not user:
        flash("User to be edited is not found. Please reresh page", 'error')
        return redirect(url_for('admin_submissions'))
      
    new_status = request.form.get('status')
    
    valid_statuses = ['Pending', 'Under Review', 'Accepted', 'Rejected']
    if new_status in valid_statuses:
        submission.status = new_status
        db.session.commit()
        flash(f"Manuscript {submission_id} stage successfully and transitioned to '{new_status}'.", "success")
        if send_submission_email(mail,  new_status, user, submission ):
            print('EMAIL SENT')
        else:
            print('EMAIL AILED')
    else:
        flash("Invalid structural state modification requested.", "error")
        
    return redirect(url_for('admin_submissions'))

@app.route('/admin/article/update/<int:article_id>', methods=['POST'])
def admin_update_article(article_id):
    if not session.get('admin_logged_in'):
        flash("Authorization required.", 'error')
        return redirect(url_for('admin_portal'))
    article = Article.query.get_or_404(article_id)
    
    article.issue_id = int(request.form.get('issue_id'))
    article.title = request.form.get('title')
    article.doi = request.form.get('doi')
    article.authors = request.form.get('authors')
    article.keywords_raw = request.form.get('keywords_raw')
    article.abstract = request.form.get('abstract')
    article.body_text = request.form.get('body_text')

    pdf_file = request.files.get('pdf_file')
    if pdf_file and pdf_file.filename.endswith('.pdf'):
        secure_name = secure_filename(pdf_file.filename)
        destination = os.path.join(app.config['UPLOAD_FOLDER'], secure_name)
        pdf_file.save(destination)
        article.pdf_file = secure_name

    db.session.commit()
    return redirect(url_for('admin_portal'))

@app.route('/admin/article/delete/<int:article_id>')
def admin_delete_article(article_id):
    if not session.get('admin_logged_in'):
        flash("Authorization required.", 'error')
        return redirect(url_for('admin_portal'))
    article = Article.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    return redirect(url_for('admin_portal'))

@app.route('/admin/management', methods=['GET'])
def admin_management():
    if not session.get('admin_logged_in'):
        flash("Authorization required.", 'error')
        return redirect(url_for('admin_portal'))
    user = User.query.filter_by(id=session.get('user_id')).first()
    
    if not user.is_super_admin:
        flash('You do NOT have enough permissions to view this page', 'error')
        return redirect(url_for('admin_portal'))
    system_logs = Log.query.all()
    
    users = User.query.order_by(User.id.desc()).all()
    return render_template(
        'admin_management.html', 
        users=users, 
        logs=system_logs, 
        configs=[]
    )

@app.route('/admin/user/toggle/<int:user_id>', methods=['POST'])
def admin_toggle_user(user_id):
    if not session.get('admin_logged_in'):
        flash("Authorization required.", 'error')
        return redirect(url_for('admin_portal'))
    
    user = User.query.get_or_404(user_id)
    admin = User.query.get_or_404(session.get('user_id'))
    user.is_active = not user.is_active
    
    

    if not user.is_active:
        send_suspension_email(user, mail)
        user.tkv = '000000'
        
    db.session.commit()
    
    action = "activated" if user.is_active else "suspended"
    level = "INFO" if user.is_active else "WARNING"
    push_system_log(session.get('user_id'), '401', level, f"User account {user.email} was {action} by { admin.name}.")
    
    flash(f"Scholar status successfully updated to {action}.", 'success')
    return redirect(url_for('admin_management'))

@app.route('/admin/marketing/broadcast', methods=['POST'])
def admin_broadcast():
    if not session.get('admin_logged_in'):
        flash("Authorization required.", "error")
        return redirect(url_for("admin_portal"))

    channel = request.form.get("channel")
    target_role = request.form.get("target_role")
    subject = request.form.get("subject")
    template = request.form.get("message")

    query = User.query
    if target_role != "all":
        query = query.filter_by(role=target_role)

    recipients = query.all()

    progress = EmailProgress.query.filter_by(p_type="Broadcast").first()

    if progress is None:
        progress = EmailProgress(p_type="Broadcast")
        db.session.add(progress)
        db.session.commit()

    elif progress.running:
        progress = EmailProgress(p_type="Broadcast")
        db.session.add(progress)
        db.session.commit()

    progress.total = len(recipients)
    progress.sent = 0
    progress.current = ""
    progress.running = True
    db.session.commit()

    email_success = 0
    sms_success = 0
    failed = []

    try:
        for i, r in enumerate(recipients, 1):
            if progress.cancelled:
               break
           
            progress.current = r.email or r.phone or r.name

            if channel in ["email", "both"] and r.email:
                try:
                    msg = Message(
                        subject=subject or "Tunu Journal Announcement",
                        recipients=[r.email]
                    )

                    body = template.replace("{{ user.name }}", r.name)

                    msg.html = f"""
                    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto">
                        <h2>Tunu Journal</h2>
                        <p>{body}</p>
                    </div>
                    """

                    mail.send(msg)
                    email_success += 1

                except Exception as e:
                    failed.append(r.email)
                    push_system_log(
                        session.get("user_id"),
                        "500",
                        "CRITICAL",
                        f"Broadcast email failed for {r.email}: {e}"
                    )

            if channel in ["sms", "both"] and r.phone:
                sms_success += 1

            progress.sent = i
            db.session.commit()

    finally:
        progress.running = False
        progress.cancelled = False
        progress.current = ""
        db.session.commit()

    push_system_log(
        session.get("user_id"),
        "200",
        "SUCCESS",
        f"Dispatched unified broadcast: {email_success} emails and {sms_success} SMS notifications."
    )

    if failed:
        flash(
            f"Broadcast completed. {email_success} emails sent, {len(failed)} failed, {sms_success} SMS sent.",
            "warning"
        )
    else:
        flash(
            f"Transmission complete. Dispatched {email_success} Emails and {sms_success} SMS notifications.",
            "success"
        )

    return redirect(url_for("admin_management"))

@app.route('/admin/config/update', methods=['POST'])
def admin_update_configs():
    if not session.get('admin_logged_in'):
        flash("Authorization required.", 'error')
        return redirect(url_for('admin_portal'))
    
    push_system_log('INFO', "System config parameters updated via console dashboard.")
    flash("Configuration settings successfully updated.")
    return redirect(url_for('admin_management'))



# EMAILS AND MARKETING 

@app.route("/send-follow-up")
@limiter.limit('1 per week')
def send_follow_up():
    failed = []

    users = User.query.all()

    progress = EmailProgress.query.first()

    if progress is None:
        progress = EmailProgress(p_type="Auto")
        db.session.add(progress)
        db.session.commit()

    elif progress.running and progress.p_type != "Auto":
        progress = EmailProgress(p_type="Auto")
        db.session.add(progress)
        db.session.commit()

    progress.total = len(users)
    progress.sent = 0
    progress.current = ""
    progress.running = True
    db.session.commit()

    for i, user in enumerate(users, 1):
        progress.current = user.email
        
        if progress.cancelled:
                break
            
        if send_follow_up_email(mail, user, INFO_EMAIL):
            progress.sent = i
        else:
            failed.append(user.email)

        db.session.commit()

    progress.running = False
    progress.cancelled = False
    progress.current = ""
    db.session.commit()

    if failed:
        return jsonify({
            "error": f"Failed to send to: {', '.join(failed)}"
        })

    return jsonify({
        "success": f"Successfully sent emails to {len(users)} users."
    })

@app.route("/cancel-marketing", methods=["POST"])
def cancel_marketing_up():
    progress = EmailProgress.query.filter_by(p_type="Broadcast").first()

    if progress and progress.running:
        progress.cancelled = True
        db.session.commit()
        return jsonify({"success": "Cancellation requested."})

    return jsonify({"error": "No running job found."}), 404

@app.route("/cancel-follow-up", methods=["POST"])
def cancel_follow_up():
    progress = EmailProgress.query.filter_by(p_type="Auto").first()

    if progress and progress.running:
        progress.cancelled = True
        db.session.commit()
        return jsonify({"success": "Cancellation requested."})

    return jsonify({"error": "No running job found."}), 404

@app.route("/email-progress")
def email_progress():
    progress = EmailProgress.query.get(1)

    return {
        "total": progress.total,
        "sent": progress.sent,
        "current": progress.current,
        "running": progress.running
    }

@limiter.limit('1000 per minute')
@app.route("/stan")
def stan():
    return render_template('stan.html')

@app.route("/notifications")
def notifications():
    user_id = session.get("user_id")

    notifications = Notification.query.filter(
        (Notification.category == "system") | (Notification.category == "admin") | (Notification.category == "alerts") | (Notification.category == "manuscripts") |
        (
            (Notification.target_id == user_id) &
            (not Notification.is_read)
        )
    ).all()

    return jsonify({
        "notifications": [n.to_dict() for n in notifications]
    }), 200


@app.route('/api/notifications/read/<string:noti_uid>', methods=['POST'])
def mark_notification_read(noti_uid):

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'Authentication required.'}), 401

    notification = Notification.query.filter_by(uid=noti_uid, target_id=user_id).first()
    if not notification:
        return jsonify({'status': 'error', 'message': 'Notification reference not discovered.'}), 404

    notification.is_read = True
    db.session.commit()
    return jsonify({'status': 'ok', 'message': 'Marked read successfully.'})

@app.route('/api/notifications/read-all', methods=['POST'])
def mark_all_notifications_read():

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'Authentication required.'}), 401

    unread_notifications = Notification.query.filter_by(target_id=user_id, is_read=False).all()
    for n in unread_notifications:
        n.is_read = True
    
    db.session.commit()
    return jsonify({'status': 'ok', 'message': 'All alerts marked as read.'})

@app.route('/api/notifications/clear-all', methods=['POST'])
def clear_all_notifications():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'Authentication required.'}), 401

    Notification.query.filter_by(target_id=user_id).delete()
    db.session.commit()
    return jsonify({'status': 'ok', 'message': 'All system notifications truncated.'})


def create_notification(title, desc, category="system", icon="info-circle", target_id=None, by_id=None, is_single=False):

    now_time = datetime.utcnow() + timedelta(hours=DELTA)

    if not is_single and target_id is None:
        # Resolve target user base based on broadcast requirements.
        # Create unique records per user to guarantee absolute independent 'is_read' state tracking.
        users = User.query.filter_by(is_active=True).all()
        for user in users:
            notif = Notification(
                uid=gen_id('NOTIF', 6),
                title=title,
                desc=desc,
                category=category,
                icon=icon,
                created_at=now_time,
                target_id=user.id,
                by_id=by_id,
                is_read=False,
                is_single=False
            )
            db.session.add(notif)
    else:
        notif = Notification(
            uid=gen_id('NOTIF', 6),
            title=title,
            desc=desc,
            category=category,
            icon=icon,
            created_at=now_time,
            target_id=target_id,
            by_id=by_id,
            is_read=False,
            is_single=is_single
        )
        db.session.add(notif)
        
    db.session.commit()
    return True

@app.route('/admin/user/notify/<string:user_id>', methods=['POST'])
def admin_notify_single_user(user_id):
    """
    Endpoint for dispatching quick personal alerts to targeted scholars directly from the workspace user matrix.
    """
    if not session.get('admin_logged_in'):
        return jsonify({'status': 'error', 'message': 'Unauthorized Administrative Session'}), 401

    title = request.form.get('title', '').strip()
    desc = request.form.get('message', '').strip()
    category = request.form.get('category', 'system')
    icon = request.form.get('icon', 'bell')

    if not title or not desc:
        return jsonify({'status': 'error', 'message': 'Both alert title and payload content are required.'}), 400

    success = create_notification(
        title=title,
        desc=desc,
        category=category,
        icon=icon,
        target_id=user_id,
        by_id=session.get('user_id'),
        is_single=True
    )

    if success:
        return jsonify({'status': 'ok', 'message': 'Scholar notified successfully.'})
    return jsonify({'status': 'error', 'message': 'Database transaction failure.'}), 500

# =========================================================================
# Client Workspace JSON API Endpoints
# =========================================================================

@app.route('/api/notifications', methods=['GET'])
def get_user_notifications():
    """
    Fetches notification items belonging to the currently logged-in user.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'Authentication required.'}), 401

    # Fetch alerts mapped explicitly to user profile, chronologically ordered
    notifications = Notification.query.filter_by(target_id=user_id).order_by(Notification.created_at.desc()).all()
    
    # Process output list
    serialized = []
    for n in notifications:
        serialized.append({
            'id': n.uid,
            'title': n.title,
            'category': n.category,
            'desc': n.desc,
            'icon': n.icon,
            'created_at': n.created_at.strftime("%Y-%m-%d %H:%M:%S") if isinstance(n.created_at, datetime) else str(n.created_at),
            'is_read': n.is_read
        })

    return jsonify({'status': 'ok', 'notifications': serialized})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    print("app.run(debug=True)")
    # app.run(debug=True, host="0.0.0.0", port=5000)