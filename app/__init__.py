from flask import Flask
from datetime import timedelta
from app.db import POOL

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    app.jinja_env.auto_reload = True
    # 防止静态文件缓存不刷新
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)

    from app.tutor import tutor
    app.register_blueprint(tutor, url_prefix='/tutor')

    from app.user import user
    app.register_blueprint(user)

    return app
