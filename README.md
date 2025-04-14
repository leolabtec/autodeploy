# 🧩 AutoDeploy 自动化部署系统（By LEOLAB）

> 一键部署 · 多站点管理 · Caddy 反代 · 全自动 HTTPS · 备份还原 · 安全封装

---

## 📦 功能特性

- 🚀 一键部署 WordPress / Halo 等多站点服务
- 🔐 内置 Caddy 容器统一反代 + 自动 TLS 证书（支持 Let's Encrypt / ZeroSSL）
- 🛡️ 容器服务默认仅本机可访问，公网无法扫描
- 🔄 支持站点添加 / 删除 / 备份 / 恢复 / 卸载
- 🧩 全部 Python Typer + Rich 编写，交互美观，逻辑清晰
- ✅ 所有代码模块可独立更新、结构化维护

---

## 🚀 快速开始（只需一行命令）

⚠️ 请确保系统已安装：
- `Python3`
- `Docker` 和 `Docker Compose`

```bash
curl -sSL https://raw.githubusercontent.com/leolabtec/autodeploy/refs/heads/main/install.sh | bash
