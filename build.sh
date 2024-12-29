#!/bin/bash

# 清理旧的构建文件
rm -rf build/ dist/ *.egg-info

# 运行测试(如果有)
# python -m pytest

# 构建项目
python setup.py sdist bdist_wheel

# 构建Docker镜像
docker build -t blog-flask:latest .

echo "Build completed!" 