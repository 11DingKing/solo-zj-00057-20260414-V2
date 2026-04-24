import os

from celery import Celery

celery_app = None

if not bool(os.getenv('DOCKER')): # if running example without docker
    celery_app = Celery(
        "worker",
        backend="redis://:password123@localhost:6379/0",
        broker="amqp://user:bitnami@localhost:5672//"
    )
else: # running example with docker
    celery_app = Celery(
        "worker",
        backend="redis://:password123@redis:6379/0",
        broker="amqp://user:bitnami@rabbitmq:5672//"
    )

# 全局配置
celery_app.conf.update(
    # 任务追踪
    task_track_started=True,
    
    # 全局超时配置（秒）
    task_soft_time_limit=300,  # 软超时，触发 SoftTimeLimitExceeded 异常
    task_time_limit=360,       # 硬超时，直接终止任务
    
    # 任务结果过期时间（24小时）
    result_expires=86400,
    
    # 任务队列配置
    task_routes={
        # 高优先级任务（用户主动触发）
        "app.worker.celery_worker.test_celery": "high-priority",
        "app.worker.celery_worker.user_triggered_task": "high-priority",
        # 低优先级任务（定时批处理）
        "app.worker.celery_worker.batch_process_task": "low-priority",
        "app.worker.celery_worker.scheduled_task": "low-priority",
    },
    
    # 任务队列定义
    task_queues={
        "high-priority": {
            "exchange": "high-priority",
            "routing_key": "high-priority",
        },
        "low-priority": {
            "exchange": "low-priority",
            "routing_key": "low-priority",
        },
    },
    
    # 默认队列
    task_default_queue="high-priority",
    
    # 任务确认配置
    task_acks_late=True,
    worker_prefetch_multiplier=1,  # 每次只预取一个任务，防止任务堆积
    
    # 重试配置
    task_max_retries=3,  # 默认最大重试次数
)
