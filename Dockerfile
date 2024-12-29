# 使用Python 3.12基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# 复制依赖文件
COPY requirements.txt requirements.txt

# 安装依赖
RUN pip install -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"] 