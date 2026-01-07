#!/usr/bin/env bash
# build.sh - Render 部署构建脚本

set -e

echo "=== 安装 Node.js 依赖 ==="
cd frontend
npm install

echo "=== 编译 Vue 前端 ==="
npm run build

echo "=== 复制编译文件到后端 ==="
rm -rf ../backend/res
cp -r dist ../backend/res

echo "=== 安装 Python 依赖 ==="
cd ../backend
pip install -r requirements.txt

echo "=== 构建完成 ==="
