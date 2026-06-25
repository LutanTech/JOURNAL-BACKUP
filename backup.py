import os

from flask import (
    Flask,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from werkzeug.utils import secure_filename

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "articles")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change_this_secret_key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "tunu_journal.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)


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


@app.route("/volume/<int:volume_id>")
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
        flash("The PDF for this article has not been uploaded yet.")
        return redirect(article.article_url)

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], article.pdf_file)

    if not os.path.exists(file_path):
        flash("The PDF file could not be found.")
        return redirect(article.article_url)

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
            "name": "Prof. Arthur Pendelton",
            "role": "Editor in Chief",
            "institution": "TUNU Journal"
        },
        {
            "name": "Dr. Helen Vance",
            "role": "Associate Editor",
            "institution": "TUNU Journal"
        },
        {
            "name": "Prof. Marcus Vance",
            "role": "Editorial Board Member",
            "institution": "TUNU Journal"
        }
    ]

    return render_template(
        "faculty.html",
        faculty=faculty_members
    )


@app.route("/about")
def about():
    return render_template("about.html")


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


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(413)
def file_too_large(error):
    flash("That PDF is too large. Maximum allowed size is 25MB.")
    return redirect(request.referrer or url_for("home"))


# ADMIN PORTAL CONTROLLERS & ACTIONS

@app.route('/admin')
def admin_portal():
    volumes = Volume.query.all()
    error = request.args.get('error')
    return render_template('admin.html', volumes=volumes, error=error)


@app.route('/admin/login', methods=['POST'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username == "admin" and password == "tunu2026":
        session['admin_logged_in'] = True
        return redirect(url_for('admin_portal'))
    else:
        return redirect(url_for('admin_portal', error="Invalid administrative identification credentials."))


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_portal'))


@app.route('/admin/structure')
def admin_structure():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_portal', error="Authorization required."))
    volumes = Volume.query.all()
    return render_template('admin_structure.html', volumes=volumes)


@app.route('/admin/publish')
def admin_publish():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_portal', error="Authorization required."))
    volumes = Volume.query.all()
    return render_template('admin_publish.html', volumes=volumes)


@app.route('/admin/add-volume', methods=['POST'])
def admin_add_volume():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_portal', error="Authorization required."))
    
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
        return redirect(url_for('admin_portal', error="Authorization required."))
    
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
        return redirect(url_for('admin_portal', error="Authorization required."))
    
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


# DATA EDIT, UPDATE, AND DELETION PROCESSORS

@app.route('/admin/volume/edit/<int:volume_id>', methods=['GET'])
def admin_edit_volume(volume_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_portal', error="Authorization required."))
    volume = Volume.query.get_or_404(volume_id)
    return render_template('admin_edit_volume.html', volume=volume)


@app.route('/admin/volume/update/<int:volume_id>', methods=['POST'])
def admin_update_volume(volume_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_portal', error="Authorization required."))
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
        return redirect(url_for('admin_portal', error="Authorization required."))
    volume = Volume.query.get_or_404(volume_id)
    db.session.delete(volume)
    db.session.commit()
    return redirect(url_for('admin_portal'))


@app.route('/admin/issue/edit/<int:issue_id>', methods=['GET'])
def admin_edit_issue(issue_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_portal', error="Authorization required."))
    issue = Issue.query.get_or_404(issue_id)
    volumes = Volume.query.all()
    return render_template('admin_edit_issue.html', issue=issue, volumes=volumes)


@app.route('/admin/issue/update/<int:issue_id>', methods=['POST'])
def admin_update_issue(issue_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_portal', error="Authorization required."))
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
        return redirect(url_for('admin_portal', error="Authorization required."))
    issue = Issue.query.get_or_404(issue_id)
    db.session.delete(issue)
    db.session.commit()
    return redirect(url_for('admin_portal'))


@app.route('/admin/article/edit/<int:article_id>', methods=['GET'])
def admin_edit_article(article_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_portal', error="Authorization required."))
    article = Article.query.get_or_404(article_id)
    volumes = Volume.query.all()
    return render_template('admin_edit_article.html', article=article, volumes=volumes)


@app.route('/admin/article/update/<int:article_id>', methods=['POST'])
def admin_update_article(article_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_portal', error="Authorization required."))
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
        return redirect(url_for('admin_portal', error="Authorization required."))
    article = Article.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    return redirect(url_for('admin_portal'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)