#!/bin/sh
# uMap 应用容器启动链（lazycat 自持启动，替代镜像原 entrypoint）
#
# 为什么不使用 setup_script：lzcinit 包裹的 setup_script 在「脚本结束 → 拉起服务」的
# 交接处存在内部竞争（首装约 1/4 概率 panic: waitid: no child processes，容器 Exited(2)），
# 已由 wavelog 实测复现。这里改用 entrypoint + command，由本脚本自持整条启动链。
#
# 顺序：目录准备 → 稳定 SECRET_KEY → collectstatic → 等库 → 迁移 → 种子 → uvicorn
set -e

export PATH="/venv/bin:$PATH"

# 1) 持久/缓存目录（AJAX_PROXY_CACHE_DIR 必须存在，否则 Django system check 报错）
mkdir -p /lzcapp/var/umap/uploads /lzcapp/var/umap/static /lzcapp/cache/umap-proxy-cache

# 2) 稳定 SECRET_KEY：首次生成后持久保存；随机化的密钥会让已签发的会话/CSRF 失效
if [ ! -s /lzcapp/var/umap/secret.key ]; then
  /venv/bin/python -c "import secrets; print(secrets.token_urlsafe(64))" > /lzcapp/var/umap/secret.key
  chmod 600 /lzcapp/var/umap/secret.key
fi
export SECRET_KEY="$(cat /lzcapp/var/umap/secret.key)"

# 3) 静态文件（应用容器的 /srv/umap/static 与 nginx 容器共享同一持久目录）
umap collectstatic --noinput

# 4) 等待数据库就绪，再执行迁移
umap wait_for_database
umap migrate --noinput

# 5) 种子数据：管理员账号 + 默认底图。失败不阻塞启动（日志里可查）。
if ! /venv/bin/python /lzcapp/pkg/content/init/seed.py; then
  echo "[lzc-boot] seed failed; continuing startup" >&2
fi

# 6) 启动 ASGI 服务（与上游 entrypoint 相同）
exec uvicorn --proxy-headers --no-access-log --host 0.0.0.0 umap.asgi:application
