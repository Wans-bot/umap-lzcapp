#!/usr/bin/env python3
"""lazycat 种子脚本（幂等，每次启动执行）。

两件事：

1. 确保管理员账号存在（用户名/密码来自 manifest 环境变量，与登录页自动填充、
   简介里的审核凭据是同一组固定值，任一台盒子可复现）。
2. 确保默认底图是中文注记的高德瓦片（上游默认 Positron/OSM 在本环境不可达），
   并把上游其它底图排到列表后面，避免「打开就是空白/花屏」。

失败由 boot.sh 记录日志后继续启动，避免种子异常导致应用起不来。
"""

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "umap.settings")

import django  # noqa: E402

django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from umap.models import TileLayer  # noqa: E402

TILE_NAME = "高德地图"
TILE_URL = (
    "https://webrd01.is.autonavi.com/appmaptile"
    "?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}"
)
TILE_ATTRIBUTION = "&copy; 高德地图"


def ensure_user() -> None:
    username = os.environ.get("LZC_ADMIN_USER", "lazycat")
    password = os.environ.get("LZC_ADMIN_PASS")
    email = os.environ.get("LZC_ADMIN_MAIL", "admin@example.com")
    if not password:
        print("[seed] LZC_ADMIN_PASS 未设置，跳过账号种子")
        return
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username=username, defaults={"email": email}
    )
    user.email = user.email or email
    user.is_staff = True
    user.is_superuser = True
    user.set_password(password)
    user.save()
    print(f"[seed] admin user {username}: {'created' if created else 'updated'}")


def ensure_tilelayer() -> None:
    layer, created = TileLayer.objects.get_or_create(
        name=TILE_NAME,
        defaults={
            "url_template": TILE_URL,
            "attribution": TILE_ATTRIBUTION,
            "rank": -100,
            "minZoom": 0,
            "maxZoom": 18,
        },
    )
    changed = False
    if layer.url_template != TILE_URL:
        layer.url_template = TILE_URL
        changed = True
    if layer.rank != -100:
        layer.rank = -100
        changed = True
    if changed:
        layer.save()
    # 上游自带的默认图层排到后面，保留可选但不再是默认
    for other in TileLayer.objects.exclude(name=TILE_NAME):
        if other.rank is None or other.rank >= 0:
            other.rank = 100
            other.save(update_fields=["rank"])
    print(f"[seed] tilelayer {TILE_NAME}: {'created' if created else 'exists'}")


if __name__ == "__main__":
    try:
        ensure_user()
        ensure_tilelayer()
    except Exception as exc:  # noqa: BLE001
        print(f"[seed] failed: {exc}", file=sys.stderr)
        sys.exit(1)
