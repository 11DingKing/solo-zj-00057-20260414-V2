# FastAPI Celery

## 项目简介
FastAPI + Celery 异步任务处理示例项目，使用 RabbitMQ 作为消息代理，Redis 作为结果后端。包含 Celery Flower 监控面板。接收单词输入后通过 Celery 异步处理任务。

## 快速启动

### Docker 启动（推荐）

```bash
# 克隆项目
git clone <GitHub 地址>
cd solo-zj-00057-20260414

# 启动所有服务
docker compose up -d

# 查看运行状态
docker compose ps
```

### 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| FastAPI | http://localhost:8000 | API 服务 |
| RabbitMQ 管理 | http://localhost:15672 | 用户: user / 密码: bitnami |
| Celery Flower | http://localhost:5555 | 用户: user / 密码: test |
| Redis | localhost:6379 | 结果后端 |

### 停止服务

```bash
docker compose down
```

## 项目结构
- `app/main.py` - FastAPI 应用入口
- `app/worker/` - Celery Worker 定义

## 来源
- 原始来源: https://github.com/GregaVrbancic/fastapi-celery
- GitHub（上传）: https://github.com/11DingKing/solo-zj-00057-20260414
