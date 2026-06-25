from app import app, db, Volume, Issue, Article, Reference


def seed_database():
    with app.app_context():
        db.create_all()

        if Volume.query.first():
            print("Database already has data. Seed skipped.")
            return

        education_volume = Volume(
            volume_number="Volume 1",
            year="2026",
            subject="Education Studies",
            title="Contemporary Research in Education",
            desc="Research articles on teaching, learning, educational technology, curriculum development, and student achievement."
        )

        kiswahili_volume = Volume(
            volume_number="Volume 1",
            year="2026",
            subject="Kiswahili Studies",
            title="Tafiti za Kiswahili na Fasihi",
            desc="Makala za kitaaluma kuhusu lugha ya Kiswahili, fasihi, isimu jamii, na utamaduni wa Afrika Mashariki."
        )

        technology_volume = Volume(
            volume_number="Volume 1",
            year="2026",
            subject="Technology and Innovation",
            title="Digital Systems and Emerging Technology",
            desc="Research on software development, digital transformation, information systems, and innovation."
        )

        db.session.add_all([
            education_volume,
            kiswahili_volume,
            technology_volume
        ])
        db.session.commit()

        education_issue = Issue(
            issue_number="Issue 1",
            title="Teaching and Learning in Digital Spaces",
            date="June 2026",
            volume_id=education_volume.id
        )

        kiswahili_issue = Issue(
            issue_number="Issue 1",
            title="Lugha, Fasihi na Utamaduni",
            date="June 2026",
            volume_id=kiswahili_volume.id
        )

        technology_issue = Issue(
            issue_number="Issue 1",
            title="Digital Innovation and Society",
            date="June 2026",
            volume_id=technology_volume.id
        )

        db.session.add_all([
            education_issue,
            kiswahili_issue,
            technology_issue
        ])
        db.session.commit()

        article_one = Article(
            title="The Role of Digital Learning Platforms in Student Engagement",
            authors="Lutan K. Mwangi, Dr. Jane W. Njoroge",
            abstract="This article examines how digital learning platforms influence student engagement in higher education. The study explores participation, access to learning materials, feedback systems, and collaborative learning experiences.",
            doi=None,
            keywords_raw="Digital Learning, Student Engagement, Higher Education, E Learning",
            body_text="""
<h2>Introduction</h2>
<p>Digital learning platforms have become important tools in higher education. They support access to learning materials, communication between students and lecturers, and continuous assessment.</p>

<h2>Methodology</h2>
<p>The study used a descriptive research design and collected responses from university students using questionnaires and interviews.</p>

<h2>Findings</h2>
<p>The findings show that students value quick access to notes, online discussions, and timely lecturer feedback.</p>

<h2>Conclusion</h2>
<p>Digital learning platforms can improve student engagement when institutions provide reliable internet access and lecturer support.</p>
""",
            pdf_file=None,
            published_date="2026-06-20",
            issue_id=education_issue.id
        )

        article_two = Article(
            title="Mchango wa Kiswahili katika Kuimarisha Utangamano wa Afrika Mashariki",
            authors="Dkt. Amina Hassan, Prof. Juma M. Kilonzo",
            abstract="Makala hii inachunguza mchango wa Kiswahili katika kukuza utangamano wa kijamii, kiuchumi, na kisiasa katika nchi za Afrika Mashariki.",
            doi=None,
            keywords_raw="Kiswahili, Afrika Mashariki, Utangamano, Lugha, Utamaduni",
            body_text="""
<h2>Utangulizi</h2>
<p>Kiswahili ni lugha muhimu katika mawasiliano ya kikanda Afrika Mashariki. Lugha hii inaendelea kutumika katika biashara, elimu, utawala, na diplomasia.</p>

<h2>Matokeo</h2>
<p>Matumizi ya Kiswahili yanaimarisha mawasiliano kati ya wananchi wa nchi mbalimbali na kusaidia kuunda utambulisho wa pamoja wa kikanda.</p>

<h2>Hitimisho</h2>
<p>Kiswahili kina nafasi kubwa katika kuendeleza utangamano wa Afrika Mashariki.</p>
""",
            pdf_file=None,
            published_date="2026-06-20",
            issue_id=kiswahili_issue.id
        )

        article_three = Article(
            title="Building Secure Web Applications for Modern Institutions",
            authors="Lutan K. Mwangi",
            abstract="This paper discusses practical approaches to building secure web applications for institutions. It focuses on authentication, database protection, secure file uploads, session security, and user access control.",
            doi=None,
            keywords_raw="Web Development, Flask, Cybersecurity, Authentication, Databases",
            body_text="""
<h2>Introduction</h2>
<p>Modern institutions depend on web applications to manage records, communication, payments, and learning systems.</p>

<h2>Security Controls</h2>
<p>Developers should use secure passwords, hashed credentials, protected sessions, role based access control, and validated file uploads.</p>

<h2>Conclusion</h2>
<p>Secure web development protects institutional data and improves trust among users.</p>
""",
            pdf_file=None,
            published_date="2026-06-20",
            issue_id=technology_issue.id
        )

        db.session.add_all([
            article_one,
            article_two,
            article_three
        ])
        db.session.commit()

        references = [
            Reference(
                text="Anderson, T. (2024). Digital Learning and Student Participation. Journal of Educational Technology, 18(2), 44 to 61.",
                article_id=article_one.id
            ),
            Reference(
                text="Mbaabu, I. (2023). Kiswahili na Utangamano wa Afrika Mashariki. Nairobi Academic Press.",
                article_id=article_two.id
            ),
            Reference(
                text="OWASP Foundation. (2025). Web Application Security Guidelines.",
                article_id=article_three.id
            )
        ]

        db.session.add_all(references)
        db.session.commit()

        print("TUNU Journal database seeded successfully.")


if __name__ == "__main__":
    seed_database()