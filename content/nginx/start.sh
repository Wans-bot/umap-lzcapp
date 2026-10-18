#!/bin/sh
# nginx 前置启动链：从随包内容复制配置，再以前台方式启动。
# 静态文件（/static）与媒体文件（/data）来自应用容器写入的同一持久目录。
set -e

cp /lzcapp/pkg/content/nginx/nginx.conf /etc/nginx/nginx.conf
mkdir -p /etc/nginx/snippets
cp /lzcapp/pkg/content/nginx/umap-snippet.conf /etc/nginx/snippets/umap.conf

exec nginx -g 'daemon off;'
