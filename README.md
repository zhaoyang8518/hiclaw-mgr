# HiClaw Manager (`hiclaw-mgr`)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen)
![Matrix](https://img.shields.io/badge/matrix-conduwuit-purple)

`hiclaw-mgr` 是专为 HiClaw / Tuwunel (基于 Rust 的高性能轻量级 Matrix 底座) 及 OpenClaw AI Workbench 生态设计的极简命令行用户、Agent Worker 与群组自动化管理工具。

本项目不仅无缝对接 Matrix 底层核心控制台（Admin Room）完成联邦通信治理，更深度集成了 OpenClaw AI 工作台数据卷下的 `humans-registry.json` 与 `workers-registry.json` 本地注册表管理，实现了底层通信账号与上层 AI 业务权限的统一协同调度。

---

## 🌟 核心特性 (Key Features)

- **🚀 零依赖架构**：基于 Python 标准库 `urllib` 与 `json` 编写，无需安装任何第三方包，开箱即用。
- **👥 Matrix 底座管理**：支持一键查询底层 Matrix 花名册、极速注册新账号、重置密码及停用离职账号。
- **🤖 OpenClaw 业务台注册表治理**：
  - 独立管理 `humans-registry.json`：配置人类用户的 Matrix 绑定与工作台权限等级（Permission Level）。
  - 独立管理 `workers-registry.json`：配置 Agent 机器人（Worker）的状态监控（如 online）与显示名映射。
- **🗂️ 幽灵房间与群组治理**：支持查看任意用户的所属群组列表、强制拉群以及硬核从数据库层面永久销毁报错/异常群组。
- **⚡ 宿主机无缝桥接**：提供极简 Shell 桥接层，直接在宿主机全局无感调用。

---

## 🛠️ 安装与部署 (Installation)

本项目标准部署架构分为两层：容器内核心逻辑层与宿主机桥接层。

### 1. 部署容器内核心脚本

将 `hiclaw-mgr.py` 拷贝至 `hiclaw-controller` 容器内并赋予执行权限：

```bash
docker cp hiclaw-mgr.py hiclaw-controller:/usr/local/bin/hiclaw-mgr
docker exec hiclaw-controller chmod +x /usr/local/bin/hiclaw-mgr
```

### 2. 部署宿主机桥接命令

将 `hiclaw-mgr` 桥接脚本放置于宿主机 `/usr/local/bin/` 下：

```bash
sudo cp hiclaw-mgr /usr/local/bin/hiclaw-mgr
sudo chmod +x /usr/local/bin/hiclaw-mgr
```

---

## 📖 使用指南 (Usage)

在宿主机任意目录下输入 `hiclaw-mgr` 即可查看完整命令矩阵：

```bash
HiClaw User, Worker & Room Management CLI (hiclaw-mgr)
------------------------------------------------------
Matrix Core Commands:
  hiclaw-mgr list                    - List all registered users in Matrix DB
  hiclaw-mgr add <user> <pass>       - Create a new user in Matrix DB
  hiclaw-mgr reset <user> <newpass>  - Reset user password in Matrix DB
  hiclaw-mgr deactivate <user>       - Deactivate a user in Matrix DB

OpenClaw Registry Commands (Humans & Workers):
  hiclaw-mgr list-humans             - List human users in humans-registry.json
  hiclaw-mgr list-workers            - List agent workers in workers-registry.json
  hiclaw-mgr add-human <id> <matrix_id> <name> [perm] - Add/update human in registry
  hiclaw-mgr add-worker <id> <matrix_id> <name> [status] - Add/update worker in registry
  hiclaw-mgr remove-human <id>       - Remove human from registry
  hiclaw-mgr remove-worker <id>      - Remove worker from registry

Room Governance Commands:
  hiclaw-mgr list-rooms <user_id>    - List all rooms a user is in
  hiclaw-mgr force-join <user> <room>- Force join a user to a room
  hiclaw-mgr delete-room <room_id>   - Permanently delete a room from Matrix DB
```

### 常用操作示例

#### 📋 查看所有已注册的 Agent Worker 名单
```bash
hiclaw-mgr list-workers
```

#### ➕ 为工作台登记新入职的员工权限
```bash
hiclaw-mgr add-human zhaoyang @zhaoyang:matrix-local.hiclaw.io:58080 "Zhao Yang" 1
```

#### 🤖 登记新上线的 AI Agent / Worker 状态
```bash
hiclaw-mgr add-worker dev2 @dev2:matrix-local.hiclaw.io:58080 "开发助手2号" online
```

#### 💥 永久销毁因网络异常卡死的幽灵房间
```bash
hiclaw-mgr delete-room !SvzC61KSsccIxbszoX:matrix-local.hiclaw.io:58080
```

---

## 🏗️ 底层文件结构与通信原理 (Architecture)

1. **Matrix 控制台通信**：利用登录换取的 `access_token`，将指令封装为 `m.room.message` 发送至底层系统控制台房间 (`!STjS5Mz5IdHsnAW5jA:matrix-local.hiclaw.io:58080`)，轮询解析回执。
2. **OpenClaw 注册表直连**：脚本直接操作容器挂载数据卷下的两个持久化 JSON 注册表：
   - `/root/hiclaw-fs/agents/manager/humans-registry.json`
   - `/root/hiclaw-fs/agents/manager/workers-registry.json`
   实现业务层元数据的高效原位读写与时间戳同步。

---

## 📄 许可证 (License)

本项目采用 [MIT License](LICENSE) 开源协议。欢迎提出 Issue 和 Pull Request 共建 Matrix 基础设施生态！
