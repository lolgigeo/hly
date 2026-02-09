#!/bin/bash
# Jekyll 本地服务器启动脚本
# 确保使用正确的 Ruby 版本

# 初始化 rbenv
eval "$(rbenv init - zsh)"

# 切换到项目目录
cd "$(dirname "$0")"

# 确保使用正确的 Ruby 版本
rbenv local 3.1.0

# 启动 Jekyll 服务器
bundle exec jekyll serve
