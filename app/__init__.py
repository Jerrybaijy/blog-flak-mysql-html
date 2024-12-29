from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
import logging
import pymysql

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
csrf = CSRFProtect()

def init_db(app):
    """初始化数据库"""
    try:
        # 连接MySQL
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='123456'
        )
        cursor = conn.cursor()
        
        # 只在数据库不存在时创建
        cursor.execute("CREATE DATABASE IF NOT EXISTS blog_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
        cursor.close()
        conn.close()
        
        # 连接到blog_db数据库
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='blog_db'
        )
        cursor = conn.cursor()
        
        # 创建表（如果不存在）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(64) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(1024)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS post (
                id INT PRIMARY KEY AUTO_INCREMENT,
                title VARCHAR(140),
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id INT,
                FOREIGN KEY (user_id) REFERENCES user(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        app.logger.info("数据库和表初始化成功")
            
    except Exception as e:
        app.logger.error(f"数据库初始化错误: {str(e)}")
        raise e

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    try:
        # 初始化数据库和表
        init_db(app)
        
        # 初始化扩展
        db.init_app(app)
        login_manager.init_app(app)
        csrf.init_app(app)
        
        # 注册蓝图
        from app.routes import main
        app.register_blueprint(main)
        
        app.logger.info("应用创建成功")
        
    except Exception as e:
        app.logger.error(f"应用初始化错误: {str(e)}")
        raise e

    return app 