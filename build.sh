#!/usr/bin/env bash
# build.sh - Render 部署构建脚本 (使用 uv 和 Python 3.13)

set -e

echo "=== 安装 uv ==="
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

echo "=== 安装 Node.js 依赖 ==="
cd frontend
npm install

echo "=== 编译 Vue 前端 ==="
npm run build

echo "=== 复制编译文件到后端 ==="
rm -rf ../backend/res
cp -r dist ../backend/res

echo "=== 安装 Python 依赖 (uv sync) ==="
cd ../backend
uv sync

echo "=== 构建完成 ==="
