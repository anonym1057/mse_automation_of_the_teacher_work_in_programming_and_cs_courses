import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from app.db import get_db
from stepic_api import StepicAPI

bp = Blueprint('auth', __name__, url_prefix='/auth')
stepic = StepicAPI()
redirect_uri = 'http://127.0.0.1:5000/auth/login'

@bp.route('/login')
def login():
    error = request.args.get('error')
    code = request.args.get('code')

    if not error and code:
        stepic.init_token(code,redirect_uri)

        print(stepic.get_user_id())
        print(stepic.get_user_name())

        db = get_db()
        user_id = stepic.get_user_id()
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (user_id,)
        ).fetchone()

        if user is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (user_id, ' '))
            db.commit()

        session.clear()
        session['user_id'] = user_id
    else:
        print("ERROR: get token error")

    return redirect(url_for('index'))


@bp.before_app_request
def load_logged_in_user():
    user_id= session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = stepic.get_user_name()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login_stepic'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/login_stepic')
def login_stepic():
    return redirect(stepic.get_url_authorize(redirect_uri))
