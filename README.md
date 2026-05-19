# HiClaw Manager (`hiclaw-mgr`)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen)
![Matrix](https://img.shields.io/badge/matrix-conduwuit-purple)

`hiclaw-mgr` 是专为 HiClaw / Tuwunel (基于 Rust 的高性能轻量级 Matrix 底座) 设计的极简命令行用户与群组自动化管理工具。

由于 HiClaw 底层引擎出于轻量化和高并发考量，未暴露常规的外部 REST Admin API，传统的运维操作必须通过控制台房间（Admin Room）与 `@conduit` 机器人对话完成。本项目通过原生 Python 无依赖异步封装，巧妙实现了通过终端命令行直接调用底层控制台接口，大幅简化了多实例 Agent 基础设施的日常运维。

---

## 🌟 核心特性 (Key Features)

- **🚀 零依赖架构**：基于 Python 标准库 `urllib` 编写，无需安装 `requests` 或任何第三方包，开箱即用。
- **👥 用户全生命周期管理**：支持一键查询用户花名册、极速注册新员工/Agent 账号、重置密码及停用离职账号。
- **🗂️ 幽灵房间与群组治理**：支持查看任意用户的所属群组列表、强制拉群以及硬核从数据库层面永久销毁报错/异常群组。
- **⚡ 宿主机无缝桥接**：提供极简 Shell 桥接层，无需手动输入繁琐的 `docker exec` 命令，直接在宿主机全局执行。

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

在宿主机任意目录下，直接输入 `hiclaw-mgr` 即可查看完整帮助文档：

```bash
HiClaw User & Room Management CLI (hiclaw-mgr)
----------------------------------------------
Usage:
  hiclaw-mgr list                    - List all registered users
  hiclaw-mgr add <user> <pass>       - Create a new user
  hiclaw-mgr reset <user> <newpass>  - Reset user password
  hiclaw-mgr deactivate <user>       - Deactivate a user
  hiclaw-mgr list-rooms <user_id>    - List all rooms a user is in
  hiclaw-mgr force-join <user> <room>- Force join a user to a room
  hiclaw-mgr delete-room <room_id>   - Permanently delete a room from DB
```

### 常用操作示例

#### 📋 查看所有已注册用户
```bash
hiclaw-mgr list
```

#### ➕ 为新入职员工或 AI Agent 创建账号
```bash
hiclaw-mgr add zhaoyang 123456
```

#### 🔑 一键重置用户密码
```bash
hiclaw-mgr reset zhaoyang newpass123
```

#### 🗂️ 查询某特定 Agent 所在的所有房间
```bash
hiclaw-mgr list-rooms @xiaoli:matrix-local.hiclaw.io:58080
```

#### 💥 永久销毁因网络异常卡死的幽灵房间
```bash
hiclaw-mgr delete-room !SvzC61KSsccIxbszoX:matrix-local.hiclaw.io:58080
```

---

## 🏗️ 底层架构与通信原理 (Architecture)

1. **登录鉴权**：脚本启动时自动向 `http://127.0.0.1:6167/_matrix/client/v3/login` 发起请求，使用预设的 `admin` 凭据换取高权限 `access_token`。
2. **PUT 事务封装**：将用户输入的管理指令封装为 Matrix 原生的 `m.room.message` 文本事件，通过 `PUT` 方法准实时写入底层系统控制台房间 (`!STjS5Mz5IdHsnAW5jA:matrix-local.hiclaw.io:58080`)。
3. **异步回执解析**：发送完毕后等待 1.5 秒，调用 `messages` 接口向后回溯解析 `@conduit` 机器人的最新 `m.notice` 回复，将其提取并优雅呈现给终端用户。

---

## 📄 许可证 (License)

本项目采用 [MIT License](LICENSE) 开源协议。欢迎提出 Issue 和 Pull Request 共建 Matrix 基础设施生态！
