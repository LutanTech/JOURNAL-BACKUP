
from flask_mail import Message

def send_otp(mail, esender, user, otp, resend):
    msg = Message(
        subject=f"Your Verification Code {'[RE-SENT]' if resend  else ''} - Tunu Journal",
        sender = esender,
        reply_to='support@tunujournal.com',
        recipients=[user.email]
    )

    msg.html = f"""
    <div style="font-family: 'Georgia', serif; max-width: 600px; margin: auto; background-color: #f9f7f2; border: 1px solid #d4d4d4; padding: 40px; color: #1a1a1a; border-radius: 4px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
        <div style="text-align: center; border-bottom: 2px solid #c5a059; padding-bottom: 20px; margin-bottom: 30px;">
            <h1 style="color: #1e293b; font-size: 1.8rem; letter-spacing: 0.04em; margin: 0; font-weight: 700;">THE TUNU JOURNAL</h1>
            <p style="font-family: sans-serif; font-size: 0.7rem; letter-spacing: 0.2em; color: #c5a059; margin: 5px 0 0 0; text-transform: uppercase; font-weight: 600;">Archival Repository of Scholarly Works</p>
        </div>

        <p style="font-size: 1.05rem; line-height: 1.6; margin-bottom: 20px;">Hello <b>{ user.name }</b>, Thanks for signing up to Tunu Journal.</p>
        <p style="font-size: 1.05rem; line-height: 1.6; margin-bottom: 30px;">Please use the following single-use verification code to complete your registration:</p>

        <div style="
            font-size: 36px;
            font-weight: bold;
            letter-spacing: 6px;
            padding: 20px;
            background: #ffffff;
            border: 1px solid #d4d4d4;
            text-align: center;
            border-radius: 4px;
            color: #c5a059;
            width: 220px;
            margin: 0 auto 30px auto;
            font-family: monospace;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
        ">
            {otp}
        </div>

        <p style="font-size: 0.9rem; opacity: 0.8; line-height: 1.6; margin-bottom: 30px;">This code will expire in 5 minutes. If you did not initiate this authentication request, please ignore this email.</p>

        <div style="border-top: 1px solid #d4d4d4; padding-top: 20px; text-align: center; font-family: sans-serif; font-size: 0.75rem; opacity: 0.6; letter-spacing: 0.05em; text-transform: uppercase;">
            &copy; 2026 Tunu Publishers. All Rights Reserved.
        </div>
    </div>
    """
    try:
        mail.send(msg)
        print('Success route n hit')
        return True
    except Exception:
        print('Error route fn hit')
        return False


rejected_body = """
<div style="font-family: 'Georgia', serif; max-width: 600px; margin: auto; background-color: #f9f7f2; border: 1px solid #d4d4d4; padding: 40px; color: #1a1a1a; border-radius: 4px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
    <div style="text-align: center; border-bottom: 2px solid #c5a059; padding-bottom: 20px; margin-bottom: 30px;">
        <h1 style="color: #1e293b; font-size: 1.8rem; letter-spacing: 0.04em; margin: 0; font-weight: 700;">THE TUNU JOURNAL</h1>
        <p style="font-family: sans-serif; font-size: 0.7rem; letter-spacing: 0.2em; color: #c5a059; margin: 5px 0 0 0; text-transform: uppercase; font-weight: 600;">Archival Repository of Scholarly Works</p>
    </div>

    <p style="font-size: 1.05rem; line-height: 1.6; margin-bottom: 20px;">Hello {{ user.name }},</p>
    
    <p style="font-size: 1.05rem; line-height: 1.6; margin-bottom: 25px;">Thank you for submitting your research to the Tunu Journal. Following a rigorous evaluation process and editorial board review, we regret to inform you that we are unable to accept your manuscript for publication in the upcoming issue.</p>

    <div style="background-color: #ffffff; border: 1px solid #d4d4d4; border-left: 4px solid #c0392b; padding: 25px; border-radius: 4px; margin-bottom: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.01);">
        <p style="margin: 0 0 8px 0; font-family: sans-serif; font-size: 0.75rem; font-weight: bold; color: #c5a059; text-transform: uppercase; letter-spacing: 0.05em;">Manuscript Identification Details</p>
        <h3 style="margin: 0 0 5px 0; color: #1e293b; font-size: 1.2rem; line-height: 1.3;">{{ sub.title }}</h3>
        <p style="margin: 0; font-family: monospace; font-size: 0.85rem; color: #1a1a1a; opacity: 0.7;">Submission Reference: {{ sub.id }}</p>
    </div>

    <p style="font-size: 0.9rem; opacity: 0.8; line-height: 1.6; margin-bottom: 30px;">Our peer review feedback is accessible directly through your scholar dashboard. If you did not submit this manuscript, please disregard this automated notification.</p>

    <div style="border-top: 1px solid #d4d4d4; padding-top: 20px; text-align: center; font-family: sans-serif; font-size: 0.75rem; opacity: 0.6; letter-spacing: 0.05em; text-transform: uppercase;">
        &copy; 2026 Tunu Publishers. All Rights Reserved.
    </div>
</div>
"""

accepted_body = """
<div style="font-family: 'Georgia', serif; max-width: 600px; margin: auto; background-color: #f9f7f2; border: 1px solid #d4d4d4; padding: 40px; color: #1a1a1a; border-radius: 4px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
    <div style="text-align: center; border-bottom: 2px solid #c5a059; padding-bottom: 20px; margin-bottom: 30px;">
        <h1 style="color: #1e293b; font-size: 1.8rem; letter-spacing: 0.04em; margin: 0; font-weight: 700;">THE TUNU JOURNAL</h1>
        <p style="font-family: sans-serif; font-size: 0.7rem; letter-spacing: 0.2em; color: #c5a059; margin: 5px 0 0 0; text-transform: uppercase; font-weight: 600;">Archival Repository of Scholarly Works</p>
    </div>

    <p style="font-size: 1.05rem; line-height: 1.6; margin-bottom: 20px;">Hello {{ user.name }},</p>
    
    <p style="font-size: 1.05rem; line-height: 1.6; margin-bottom: 25px;">We are pleased to inform you that following a comprehensive peer evaluation and editorial board review, your manuscript has been formally accepted for archival publication in the Tunu Journal.</p>

    <div style="background-color: #ffffff; border: 1px solid #d4d4d4; border-left: 4px solid #27ae60; padding: 25px; border-radius: 4px; margin-bottom: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.01);">
        <p style="margin: 0 0 8px 0; font-family: sans-serif; font-size: 0.75rem; font-weight: bold; color: #c5a059; text-transform: uppercase; letter-spacing: 0.05em;">Manuscript Identification Details</p>
        <h3 style="margin: 0 0 5px 0; color: #1e293b; font-size: 1.2rem; line-height: 1.3;">{{ sub.title }}</h3>
        <p style="margin: 0; font-family: monospace; font-size: 0.85rem; color: #1a1a1a; opacity: 0.7;">Submission Reference: {{ sub.id }}</p>
    </div>

    <p style="font-size: 0.9rem; opacity: 0.8; line-height: 1.6; margin-bottom: 30px;">Our production office will contact you shortly regarding proofing, metadata checks, and publication scheduling. If you did not submit this manuscript, please disregard this automated notification.</p>

    <div style="border-top: 1px solid #d4d4d4; padding-top: 20px; text-align: center; font-family: sans-serif; font-size: 0.75rem; opacity: 0.6; letter-spacing: 0.05em; text-transform: uppercase;">
        &copy; 2026 Tunu Publishers. All Rights Reserved.
    </div>
</div>
"""

under_review_body = """
<div style="font-family: 'Georgia', serif; max-width: 600px; margin: auto; background-color: #f9f7f2; border: 1px solid #d4d4d4; padding: 40px; color: #1a1a1a; border-radius: 4px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
    <div style="text-align: center; border-bottom: 2px solid #c5a059; padding-bottom: 20px; margin-bottom: 30px;">
        <h1 style="color: #1e293b; font-size: 1.8rem; letter-spacing: 0.04em; margin: 0; font-weight: 700;">THE TUNU JOURNAL</h1>
        <p style="font-family: sans-serif; font-size: 0.7rem; letter-spacing: 0.2em; color: #c5a059; margin: 5px 0 0 0; text-transform: uppercase; font-weight: 600;">Archival Repository of Scholarly Works</p>
    </div>

    <p style="font-size: 1.05rem; line-height: 1.6; margin-bottom: 20px;">Hello {{ user.name }},</p>
    
    <p style="font-size: 1.05rem; line-height: 1.6; margin-bottom: 25px;">Your submitted research manuscript has successfully advanced through our initial editorial checks and has now transitioned into the official Peer Review stage.</p>

    <div style="background-color: #ffffff; border: 1px solid #d4d4d4; border-left: 4px solid #2980b9; padding: 25px; border-radius: 4px; margin-bottom: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.01);">
        <p style="margin: 0 0 8px 0; font-family: sans-serif; font-size: 0.75rem; font-weight: bold; color: #c5a059; text-transform: uppercase; letter-spacing: 0.05em;">Manuscript Identification Details</p>
        <h3 style="margin: 0 0 5px 0; color: #1e293b; font-size: 1.2rem; line-height: 1.3;">{{ sub.title }}</h3>
        <p style="margin: 0; font-family: monospace; font-size: 0.85rem; color: #1a1a1a; opacity: 0.7;">Submission Reference: {{ sub.id }}</p>
    </div>

    <p style="font-size: 0.9rem; opacity: 0.8; line-height: 1.6; margin-bottom: 30px;">You can track real-time changes to your review status from your personal workspace at any time. If you did not submit this manuscript, please disregard this automated notification.</p>

    <div style="border-top: 1px solid #d4d4d4; padding-top: 20px; text-align: center; font-family: sans-serif; font-size: 0.75rem; opacity: 0.6; letter-spacing: 0.05em; text-transform: uppercase;">
        &copy; 2026 Tunu Publishers. All Rights Reserved.
    </div>
</div>
"""


def send_submission_email(mail, status, user, sub):
    msg = Message(
        subject=f"Manuscript Status Update: {sub.id}",
        recipients=[user.email]
    )

    status_lower = status.lower()
    if status_lower == "accepted":
        body = accepted_body
    elif status_lower == "rejected":
        body = rejected_body
    else:
        body = under_review_body

    body = body.replace("{{ user.name }}", user.name)
    body = body.replace("{{ sub.id }}", sub.id)
    body = body.replace("{{ sub.title }}", sub.title)

    msg.html = body
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(str(e))
        return False


def send_welcome_email(user, mail):
    
    msg = Message(
        subject=f"Welcome to Tunu Journal Website {user.name}",
        recipients=[user.email]
    )

    msg.html = f"""
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml" lang="en">
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
            <title>Welcome to The Tunu Journal</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
            
            <style type="text/css">
                body, table, td, a {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
                table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
                img {{ -ms-interpolation-mode: bicubic; }}
                img {{ border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }}
                table{{ border-collapse: collapse !important; }}
                body {{ height: 100% !important; margin: 0 !important; padding: 0 !important; width: 100% !important; }}
                a[x-apple-data-detectors] {{
                    color: inherit !important;
                    text-decoration: none !important;
                    font-size: inherit !important;
                    font-family: inherit !important;
                    font-weight: inherit !important;
                    line-height: inherit !important;
                }}
                .btn-primary:hover {{
                    background-color: #1a1a1a !important;
                    border-color: #1a1a1a !important;
                }}
                .btn-secondary:hover {{
                    background-color: #1e293b !important;
                    color: #ffffff !important;
             }}
             </style>
        </head>
        <body style="margin: 0; padding: 0; background-color: #f3f1eb; font-family: 'Georgia', serif; -webkit-font-smoothing: antialiased;">

            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed; background-color: #f3f1eb;">
                <tr>
                    <td align="center" style="padding: 20px 10px;">
                        
                        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 580px; background-color: #ffffff; border: 1px solid #d4d4d4; border-radius: 6px; overflow: hidden; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04);">
                            
                            <tr>
                                <td align="center" style="background-color: #1e293b; background-image: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 25px 20px; border-bottom: 3px solid #c5a059;">
                                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                        <tr>
                                            <td align="center">
                                                <table border="0" cellpadding="0" cellspacing="0" style="margin: 0 auto 10px auto;">
                                                    <tr>
                                                        <td align="center" valign="middle" style="background-color: rgba(255, 255, 255, 0.04); border: 2px solid #c5a059; border-radius: 50%; width: 42px; height: 42px; text-align: center; color: #c5a059;">
                                                            <i class="fas fa-book-open" style="color: #c5a059; font-size: 16px; line-height: 38px; vertical-align: middle;"></i>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td align="center" style="color: #ffffff; font-family: 'Georgia', serif; font-size: 20px; font-weight: bold; letter-spacing: 0.06em; line-height: 1.2; text-transform: uppercase;">
                                                THE TUNU JOURNAL
                                            </td>
                                        </tr>
                                        <tr>
                                            <td align="center" style="color: #c5a059; font-family: sans-serif; font-size: 9px; font-weight: 600; letter-spacing: 0.22em; line-height: 1.4; margin-top: 4px; text-transform: uppercase;">
                                                Archival Repository of Scholarly Works
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>

                            <tr>
                                <td style="padding: 30px 30px 20px 30px; background-color: #ffffff;">
                                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                        
                                        <tr>
                                            <td style="color: #2c3e50; font-family: 'Georgia', serif; font-size: 18px; font-weight: bold; line-height: 1.3; padding-bottom: 12px;">
                                                Dear { user.name },
                                            </td>
                                        </tr>

                                        <tr>
                                            <td style="color: #1a1a1a; font-family: 'Georgia', serif; font-size: 14.5px; line-height: 1.5; padding-bottom: 20px;">
                                                Thank you for joining <strong>The Tunu Journal</strong>, an international open-access repository dedicated to the permanent digital preservation and global dissemination of peer-reviewed multidisciplinary inquiry. Our secure, double-blind environment is ready for your contributions.
                                            </td>
                                        </tr>

                                        <tr>
                                            <td style="padding-bottom: 20px;">
                                                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f9f7f2; border-left: 3px solid #c5a059; border-top: 1px solid #e8e6e0; border-right: 1px solid #e8e6e0; border-bottom: 1px solid #e8e6e0; border-radius: 4px;">
                                                    <tr>
                                                        <td style="padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;">
                                                            <span style="font-family: sans-serif; font-size: 11px; font-weight: bold; color: #555555; text-transform: uppercase; letter-spacing: 0.05em; margin-right: 10px; margin-top: 4px; margin-bottom: 4px;">Registered Identifier Code:</span>
                                                            <code style="font-family: monospace; font-size: 13px; font-weight: bold; background-color: #ffffff; border: 1px solid #d4d4d4; padding: 3px 8px; border-radius: 3px; color: #2c3e50; display: inline-block; margin-top: 4px; margin-bottom: 4px;">
                                                                { user.uid }
                                                            </code>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>

                                        <tr>
                                            <td align="center" style="padding: 10px 0 20px 0;">
                                                <table border="0" cellpadding="0" cellspacing="0" style="margin: 0 auto;">
                                                    <tr>
                                                        <td align="center" style="border-radius: 4px; background-color: #c5a059;">
                                                            <a href="{{ explore_url | default('https://tunujournal.com') }}" class="btn-primary" target="_blank" style="font-family: sans-serif; font-size: 11.5px; font-weight: 600; color: #ffffff; text-decoration: none; border-radius: 4px; padding: 10px 18px; border: 1px solid #c5a059; display: inline-block; text-transform: uppercase; letter-spacing: 0.05em; transition: all 0.2s ease;">
                                                                Explore Catalog
                                                            </a>
                                                        </td>
                                                        <td width="15">&nbsp;</td>
                                                        <td align="center" style="border-radius: 4px;">
                                                            <a href="{{ dashboard_url | default('https://tunujournal.com/dashboard') }}" class="btn-secondary" target="_blank" style="font-family: sans-serif; font-size: 11.5px; font-weight: 600; color: #1a1a1a; text-decoration: none; border-radius: 4px; padding: 10px 18px; border: 1px solid #1a1a1a; display: inline-block; text-transform: uppercase; letter-spacing: 0.05em; transition: all 0.2s ease;">
                                                                Submit Manuscript
                                                            </a>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>

                                        <tr>
                                            <td align="center" style="border-top: 1px solid #e8e6e0; padding-top: 15px; padding-bottom: 5px;">
                                                <span style="font-family: sans-serif; font-size: 10px; font-weight: bold; color: #c5a059; text-transform: uppercase; letter-spacing: 0.1em; display: inline-block; margin-bottom: 8px;">Preserved Areas of Scientific Inquiry:</span>
                                                <div style="font-family: 'Georgia', serif; font-size: 12.5px; color: #555555; line-height: 1.4; font-style: italic;">
                                                    Kiswahili Studies &bull; Educational Studies
                                                </div>
                                            </td>
                                        </tr>

                                    </table>
                                </td>
                            </tr>

                            <tr>
                                <td style="background-color: #f9f7f2; border-top: 1px solid #e8e6e0; padding: 20px 30px; text-align: center;">
                                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                        <tr>
                                            <td style="font-family: 'Georgia', serif; font-size: 12.5px; color: #475569; line-height: 1.5;">
                                                <strong>The Tunu Journal</strong> &bull; Tunu Publishers<br/>
                                                Donholm, Nairobi, Kenya
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="font-family: sans-serif; font-size: 11px; padding-top: 8px; color: #64748b;">
                                                <a href="mailto:archives@tunujournal.com" style="color: #c5a059; text-decoration: none; font-weight: 600;">archives@tunujournal.com</a>
                                                <span style="color: #cbd5e1; margin: 0 6px;">|</span>
                                                <a href="mailto:support@tunujournal.com" style="color: #c5a059; text-decoration: none; font-weight: 600;">support@tunujournal.com</a>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="font-family: 'Georgia', serif; font-size: 11px; font-style: italic; color: #94a3b8; padding-top: 12px; line-height: 1.4;">
                                                "Advancing knowledge through rigorous peer-reviewed scholarship and permanent digital preservation."
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            
                        </table>

                    </td>
                </tr>
            </table>

        </body>
        </html>"""
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(str(e))
        return False

suspended_body = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Account Suspension Notice - The Tunu Journal</title>
    <style type="text/css">
        body, table, td, a { -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }
        table, td { mso-table-lspace: 0pt; mso-table-rspace: 0pt; }
        img { -ms-interpolation-mode: bicubic; }
        img { border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }
        table { border-collapse: collapse !important; }
        body { height: 100% !important; margin: 0 !important; padding: 0 !important; width: 100% !important; }
        a[x-apple-data-detectors] {
            color: inherit !important;
            text-decoration: none !important;
            font-size: inherit !important;
            font-family: inherit !important;
            font-weight: inherit !important;
            line-height: inherit !important;
        }
        .btn-primary:hover {
            background-color: #1a1a1a !important;
            border-color: #1a1a1a !important;
        }
    </style>
</head>
<body style="margin: 0; padding: 0; background-color: #f3f1eb; font-family: 'Georgia', serif; -webkit-font-smoothing: antialiased;">
    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed; background-color: #f3f1eb;">
        <tr>
            <td align="center" style="padding: 40px 10px;">
                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border: 1px solid #d4d4d4; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);">
                    <tr>
                        <td align="center" style="background-color: #1e293b; background-image: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 40px 20px; border-bottom: 4px solid #e74c3c;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="center">
                                        <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#e74c3c" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display: block; margin: 0 auto 15px auto;">
                                            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                                            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                                        </svg>
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" style="color: #ffffff; font-family: 'Georgia', serif; font-size: 24px; font-weight: bold; letter-spacing: 0.06em; line-height: 1.2; text-transform: uppercase;">
                                        THE TUNU JOURNAL
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" style="color: #e74c3c; font-family: sans-serif; font-size: 10px; font-weight: 600; letter-spacing: 0.25em; line-height: 1.4; margin-top: 5px; text-transform: uppercase;">
                                        Administrative Security Notification
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 40px; background-color: #ffffff;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td style="color: #2c3e50; font-family: 'Georgia', serif; font-size: 20px; font-weight: bold; line-height: 1.3; padding-bottom: 15px;">
                                        Dear {{ user.name }},
                                    </td>
                                </tr>
                                <tr>
                                    <td style="color: #1a1a1a; font-family: 'Georgia', serif; font-size: 16px; line-height: 1.6; padding-bottom: 25px;">
                                        Please be advised that your scholar workspace account with <strong>The Tunu Journal</strong> has been temporarily suspended by the editorial office administration team.
                                    </td>
                                </tr>
                                <tr>
                                    <td style="color: #1a1a1a; font-family: 'Georgia', serif; font-size: 16px; line-height: 1.6; padding-bottom: 25px;">
                                        While under suspension, you will not be able to log in to your scholar dashboard, submit new research drafts, or access active peer-review panels associated with your registered credentials.
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding-bottom: 30px;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #fdf2f2; border-left: 4px solid #e74c3c; border-top: 1px solid #f5baba; border-right: 1px solid #f5baba; border-bottom: 1px solid #f5baba; border-radius: 4px;">
                                            <tr>
                                                <td style="padding: 20px;">
                                                    <p style="margin: 0 0 5px 0; font-family: sans-serif; font-size: 11px; font-weight: bold; color: #e74c3c; text-transform: uppercase; letter-spacing: 0.05em;">Scholar Account Status</p>
                                                    <p style="margin: 0 0 8px 0; font-family: 'Georgia', serif; font-size: 15px; color: #1a1a1a; line-height: 1.4;">The security lock has been applied to the following unique academic registration hash:</p>
                                                    <code style="font-family: monospace; font-size: 14px; font-weight: bold; background-color: #ffffff; border: 1px solid #f5baba; padding: 4px 8px; border-radius: 3px; color: #c0392b; display: inline-block;">
                                                        {{ user.tkv }}
                                                    </code>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="color: #1a1a1a; font-family: 'Georgia', serif; font-size: 16px; line-height: 1.6; padding-bottom: 25px;">
                                        If you believe this suspension was executed in error, or if you need to provide outstanding peer-review reports or correct metadata inconsistencies to restore your account state, please contact our administrative desk immediately.
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 20px 0 10px 0;">
                                        <table border="0" cellpadding="0" cellspacing="0" style="margin: 0 auto;">
                                            <tr>
                                                <td align="center" style="border-radius: 4px; background-color: #1e293b;">
                                                    <a href="mailto:support@tunujournal.com" class="btn-primary" style="font-family: sans-serif; font-size: 13px; font-weight: 600; color: #ffffff; text-decoration: none; border-radius: 4px; padding: 14px 28px; border: 1px solid #1e293b; display: inline-block; text-transform: uppercase; letter-spacing: 0.05em; transition: all 0.2s ease;">
                                                        Contact Support Desk
                                                    </a>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 40px 0 20px 0;">
                                        <hr style="border: 0; border-top: 1px solid #d4d4d4;" />
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f9f7f2; border-left: 4px solid #e74c3c; border-top: 1px solid #d4d4d4; border-right: 1px solid #d4d4d4; border-bottom: 1px solid #d4d4d4; border-radius: 6px; padding: 25px;">
                                            <tr>
                                                <td style="font-family: 'Georgia', serif; font-size: 15px; font-weight: bold; color: #2c3e50; padding-bottom: 5px; border-bottom: 2px solid #e74c3c; display: inline-block;">
                                                    Editorial Office
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-family: 'Georgia', serif; font-size: 14px; color: #1a1a1a; line-height: 1.5; padding-top: 12px;">
                                                    <strong>The Tunu Journal</strong> &bull; Tunu Publishers<br/>
                                                    P.O. Box 7188-00100<br/>
                                                    Harambee SACCO Shopping Centre, Donholm<br/>
                                                    Nairobi, Kenya
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-family: sans-serif; font-size: 13px; padding-top: 15px; color: #2c3e50; line-height: 1.5;">
                                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#e74c3c" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px; display: inline-block;">
                                                        <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                                                        <polyline points="22,6 12,13 2,6"/>
                                                    </svg><a href="mailto:archives@tunujournal.com" style="color: #2c3e50; text-decoration: none; font-weight: 600; vertical-align: middle;">archives@tunujournal.com</a><br/>
                                                    <div style="height: 6px; font-size: 6px; line-height: 6px;">&nbsp;</div>
                                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#e74c3c" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px; display: inline-block;">
                                                        <circle cx="12" cy="12" r="10"/>
                                                        <line x1="12" y1="16" x2="12" y2="12"/>
                                                        <line x1="12" y1="8" x2="12.01" y2="8"/>
                                                    </svg><a href="mailto:support@tunujournal.com" style="color: #2c3e50; text-decoration: none; font-weight: 600; vertical-align: middle;">support@tunujournal.com</a>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" style="font-family: 'Georgia', serif; font-size: 13px; font-style: italic; color: #1a1a1a; opacity: 0.75; line-height: 1.4; padding-top: 30px;">
                                        "Advancing knowledge through rigorous peer-reviewed scholarship and permanent digital preservation."
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

def send_suspension_email(user, mail):
    msg = Message(
        subject=f"Account Status Notification - The Tunu Journal",
        recipients=[user.email]
    )

    body = suspended_body.replace("{{ user.name }}", user.name).replace("{{ user.tkv }}", user.uid)

    msg.html = body
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(str(e))
        return False
    

def send_follow_up_email(mail, user, esender):
    msg = Message(
        subject=f"Greetings {user.name},  Tunu Journal",
        sender = esender,
        reply_to='support@tunujournal.com',
        recipients=[user.email]
    )
    msg.html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="margin:0;padding:30px;background:#f4f6f9;font-family:Arial,Helvetica,sans-serif;color:#333;">

            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                    <td align="center">

                        <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;overflow:hidden;">

                            <tr>
                                <td style="background:#1e293b;padding:25px;text-align:center;">
                                    <img src="https://tunujournal.com/assets/icons/icon_nbg.png" alt="Tunu Journal" style="height:70px;">
                                    <h2 style="color:#ffffff;margin:15px 0 0;">Greetings from Tunu Journal</h2>
                                </td>
                            </tr>

                            <tr>
                                <td style="padding:35px;line-height:1.7;font-size:15px;">

                                    <p>Dear { user.name },</p>

                                    <p>
                                        We hope this message finds you well and that your research,
                                        teaching, and professional activities are progressing
                                        successfully.
                                    </p>

                                    <p>
                                        At <strong>Tunu Journal</strong>, we sincerely appreciate
                                        having you as part of our growing community of researchers,
                                        academics and professionals dedicated to advancing knowledge
                                        and innovation.
                                    </p>

                                    <p>
                                        This email is simply a friendly greeting to let you know that
                                        we value our connection with you. We hope your current
                                        projects are progressing well and wish you continued success
                                        in your academic and professional journey.
                                    </p>

                                    <p>
                                        Our editorial team is always available should you have any
                                        questions or require assistance regarding our journal,
                                        publishing process or future collaborations.
                                    </p>

                                    <p>
                                        Thank you for being a valued member of the Tunu Journal
                                        community. We look forward to staying connected and
                                        celebrating your future achievements.
                                    </p>

                                    <p>
                                        Warm regards,<br><br>

                                        <strong>Editorial Office</strong><br>
                                        Tunu Journal<br>
                                        📧 support@tunujournal.com<br>
                                        🌐 <a href="https://www.tunujournal.com" style="color:#1e3a8a;text-decoration:none;">www.tunujournal.com</a>
                                    </p>

                                </td>
                            </tr>

                            <tr>
                                <td style="background:#f1f5f9;padding:20px;text-align:center;font-size:12px;color:#666;">
                                    You are receiving this email because you are part of the Tunu Journal academic community.
                                </td>
                            </tr>

                        </table>

                    </td>
                </tr>
            </table>

        </body>
            """
  
    try:
        mail.send(msg)
        print('Success route n hit')
        return True
    except Exception:
        print('Error route fn hit')
        return False

