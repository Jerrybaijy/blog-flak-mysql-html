from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
import logging
import os

# 初始化扩展，但不绑定到应用
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    try:
        # 初始化扩展
        db.init_app(app)
        login_manager.init_app(app)
        csrf.init_app(app)
        
        # 导入模型以确保它们在创建表之前被加载
        from app import models
        
        # 创建数据库表
        with app.app_context():
            db.create_all()
            app.logger.info("数据库表创建成功")
        
        # 注册蓝图
        from app.routes import main
        app.register_blueprint(main)
        
        app.logger.info("应用创建成功")
        
    except Exception as e:
        app.logger.error(f"应用初始化错误: {str(e)}")
        raise e

    return app 