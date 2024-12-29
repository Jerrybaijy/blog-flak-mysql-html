class Config:
    SECRET_KEY = 'dev'  # 开发环境使用，生产环境应该使用复杂的随机字符串
    # 使用 URL 编码的用户名和密码
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost/blog_db'  # 请替换为你的实际配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False