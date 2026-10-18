# 第三方组件与许可说明（uMap LPK）

本 LPK 打包的是上游 uMap 官方发行版，未修改上游应用源码。本文件汇总各组件的
许可与来源，完整许可证文本随包提供或被引用。

## 1. uMap（应用本体）

- 来源：https://github.com/umap-project/umap ，tag `3.8.1`
  （commit `580d7659b82e371a42a3688e37409e7afaa34d28`，2026-08-19 发布）。
- 许可：AGPL-3.0（完整文本见 `licenses/UMAP-AGPL-3.0.txt`）。
- 镜像：`registry.lazycat.cloud/wans/umap/umap:da00c04772aab154`，
  由上游 Docker Hub 镜像 `umap/umap:3.8.1` 原样中转，未做二次构建。
- 源码获取：上述仓库对应 tag 的源码包即可对照构建；
  本轮使用的源码包 SHA-256 为
  `af52ad410fa61ca904ab3640b3e36d08f00af19b998cd78fedf32326a90b1c8f`
  （`umap-3.8.1.tar.gz`，来自 codeload.github.com 的官方 tag 归档）。

## 2. PostgreSQL / PostGIS（数据库）

- 镜像：`registry.lazycat.cloud/wans/postgis/postgis:0a0ae8a65098cb00`，
  由 `postgis/postgis:14-3.3-alpine` 原样中转。
- 许可：PostgreSQL License（PostgreSQL）、GPL-2.0（PostGIS）。
  许可文本见各上游发行包与 https://postgis.net/ 。

## 3. nginx（静态文件与反向代理前置）

- 镜像：`registry.lazycat.cloud/wans/library/nginx:098fb79c84151799`，
  由 `nginx:1.27-alpine` 原样中转。
- 许可：BSD-2-Clause（https://nginx.org/LICENSE ）。

## 4. 随包集成脚本（本 LPK 新增，不改动上游代码）

以下文件是懒猫微服适配层，不是上游 uMap 的一部分：

- `content/init/boot.sh`、`content/init/seed.py`：启动链与种子数据；
- `content/umap/umap.conf`：站点覆盖配置（默认语言、默认中心点）；
- `content/nginx/*`：基于上游 `docker/nginx.conf`、`docker/umap-snippet.conf`
  的部署配置（仅改上游代理目标地址与上传体积上限）；
- `content/lazycat-injects/umap-login-autofill.js`、
  `content/lazycat-injects/umap-download-bridge.js`：浏览器端注入脚本；
- `content/lazycat-injects/lzc-file-chooser-inject.js`：懒猫微服官方提供的
  网盘文件选择器脚本（取自 https://developer.lazycat.cloud/lazycat-file-picker-auto-intercept.html ，
  SHA-256 `4da22e7d0b3167de57a63cb5f31af13a2e98292a17c344ca71bce70331d453b5`）。

这些脚本仅通过配置与浏览器注入与 uMap 交互，不复制或修改 uMap 源码。
