import sys
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session, redirect, url_for, flash
# Make sure to import your db instance, User model, and Notification model from your app setup
# from app import db, User, Notification, gen_id, DELTA

admin_notif_bp = Blueprint('admin_notifications', __name__)

def create_notification(title, desc, category="system", icon="info-circle", target_id=None, by_id=None, is_single=False):
    """
    Helper function to dispatch system notifications.
    Creates single targeted records or expands broadcasts across recipients.
    """
    try:
        from app import db, Notification, User, gen_id, DELTA
    except ImportError:
        print("Ensure DB models and configuration imports are resolved in your app entrypoint.")
        return False

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

@admin_notif_bp.route('/admin/marketing/broadcast', methods=['POST'])
def admin_broadcast():
    """
    Unified communication channel processing broadcasts across Email, SMS, or System Notifications.
    """
    from app import db, User
    
    if not session.get('admin_logged_in'):
        flash("Unauthorized administrative session.")
        return redirect(url_for('admin_portal'))

    channel = request.form.get('channel')
    target_role = request.form.get('target_role')
    subject = request.form.get('subject', 'System Announcement')
    message_content = request.form.get('message', '').strip()
    
    # In-App Notification Specific options
    category = request.form.get('notif_category', 'system')
    icon = request.form.get('notif_icon', 'info-circle')

    if not message_content:
        flash("Transmission payload cannot be empty.")
        return redirect('/admin/management#tab-marketing')

    # 1. Handle in-app system notification routing
    if channel in ['notification', 'omni']:
        try:
            if target_role == 'all':
                # Global broadcast
                create_notification(
                    title=subject,
                    desc=message_content,
                    category=category,
                    icon=icon,
                    target_id=None,
                    by_id=session.get('user_id'),
                    is_single=False
                )
            else:
                # Target filtered roles (e.g., 'author', 'reviewer')
                target_users = User.query.filter_by(role=target_role, is_active=True).all()
                for u in target_users:
                    create_notification(
                        title=subject,
                        desc=message_content,
                        category=category,
                        icon=icon,
                        target_id=u.id,
                        by_id=session.get('user_id'),
                        is_single=True
                    )
            flash(f"System notifications successfully dispatched to target group: {target_role}.")
        except Exception as e:
            flash(f"Error processing notification broadcast: {str(e)}")

    # 2. Integrate with your fallback standard channels
    if channel in ['email', 'both', 'omni']:
        # TODO: Execute standard Flask-Mail procedures using dynamic template targets
        pass
    if channel in ['sms', 'both', 'omni']:
        # TODO: Route text payload via Africa's Talking SMS infrastructure
        pass

    return redirect('/admin/management')

@admin_notif_bp.route('/admin/user/notify/<string:user_id>', methods=['POST'])
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

@admin_notif_bp.route('/api/notifications', methods=['GET'])
def get_user_notifications():
    """
    Fetches notification items belonging to the currently logged-in user.
    """
    from app import Notification
    
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

@admin_notif_bp.route('/api/notifications/read/<string:noti_uid>', methods=['POST'])
def mark_notification_read(noti_uid):
    """
    Updates the read status of a specific alert transaction.
    """
    from app import db, Notification
    
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'Authentication required.'}), 401

    notification = Notification.query.filter_by(uid=noti_uid, target_id=user_id).first()
    if not notification:
        return jsonify({'status': 'error', 'message': 'Notification reference not discovered.'}), 404

    notification.is_read = True
    db.session.commit()
    return jsonify({'status': 'ok', 'message': 'Marked read successfully.'})

@admin_notif_bp.route('/api/notifications/read-all', methods=['POST'])
def mark_all_notifications_read():
    """
    Flag all target alerts as read to clean indicators.
    """
    from app import db, Notification
    
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'Authentication required.'}), 401

    unread_notifications = Notification.query.filter_by(target_id=user_id, is_read=False).all()
    for n in unread_notifications:
        n.is_read = True
    
    db.session.commit()
    return jsonify({'status': 'ok', 'message': 'All alerts marked as read.'})

@admin_notif_bp.route('/api/notifications/clear-all', methods=['POST'])
def clear_all_notifications():
    """
    Purge notification list from target workspace view.
    """
    from app import db, Notification
    
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'Authentication required.'}), 401

    Notification.query.filter_by(target_id=user_id).delete()
    db.session.commit()
    return jsonify({'status': 'ok', 'message': 'All system notifications truncated.'})