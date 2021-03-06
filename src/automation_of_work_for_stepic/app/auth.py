import functools

from flask import (
    Blueprint, g, redirect, render_template, request, session, url_for
)
from flask import current_app as app

#from automation_of_work_for_stepic.app.db import get_db
from automation_of_work_for_stepic.stepic_api import StepicAPI
from automation_of_work_for_stepic.information_processor import InformationsProcessor

bp = Blueprint('auth', __name__, url_prefix='/auth')
stepic = StepicAPI()
redirect_uri = 'http://127.0.0.1:5000/auth/login'

@bp.route('/login')
def login():
    """
    Авторизация пользователя
    :return:
    """
    #ошибка
    error = request.args.get('error')
    #код авторищации
    code = request.args.get('code')

    #если нет ошибки и есть код
    if not error and code:
        #получаем токен
        stepic.init_token(code, redirect_uri)

        if app.config['ENV'] == 'development':
            stepic.save_token(app.instance_path)

        #очищаем ссесию
        session.clear()
        session['user_id'] = stepic.current_user_id()
        session['user_name'] = stepic.get_user_name()
        InformationsProcessor().__init__(session['user_id'])
        #session['processor']= InformationsProcessor(session['user_id']).__dict__
        return redirect(url_for('page.start'))
    else:
        return render_template('error/401.html')
        print("Error:login: get code error")


@bp.before_app_request
def load_logged_in_user():
    """
    Загрузка информации перел открытием страницы
    :return:
    """
    user_name= session.get('user_name')

    if stepic.token is None:
        g.token = False
    else:
        g.token = True
        g.user = session.get('user_name')

    if app.config['ENV'] == 'development':
        g.dev = True
    else:
        g.dev = None


@bp.route('/logout')
def logout():
    """
    Выход пользователя
    :return:
    """
    session.clear()
    stepic.clear_token()
    return redirect(url_for('page.start'))

def login_required(view):
    """
    Декоратор, проверяющий залогинен ли пользователь
    :param view:
    :return:
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.token:
            
            return render_template('error/401.html')

        return view(**kwargs)

    return wrapped_view

@bp.route('/login_stepic')
def login_stepic():
    """
    Авторизация пользователя через степик
    :return:
    """
    return redirect(stepic.get_url_authorize(redirect_uri))

@bp.route('/login_dev')
def login_dev():
    """
    Авторизация пользователя через степик  в режиме разработчика
    :return:
    """
    if stepic.load_token(app.instance_path):

        # очищаем ссесию
        session.clear()
        session['user_id'] = stepic.current_user_id()
        session['user_name']= stepic.get_user_name()
        InformationsProcessor().__init__(session['user_id'])
        #['processor'] = InformationsProcessor(session['user_id'])
        return redirect(url_for('page.start'))
    else:
        #переходим на авторизаци степика
        return redirect(stepic.get_url_authorize(redirect_uri))