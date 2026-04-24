import os
import logging
from threading import Thread
from typing import Optional, Any

from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel

from app.worker.celery_app import celery_app

log = logging.getLogger(__name__)

app = FastAPI()


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None
    meta: Optional[dict] = None
    traceback: Optional[str] = None


class HighPriorityTaskRequest(BaseModel):
    data: dict


class LowPriorityBatchRequest(BaseModel):
    items: list


class LowPriorityScheduledRequest(BaseModel):
    params: dict


def celery_on_message(body):
    log.warn(body)


def background_on_message(task):
    log.warn(task.get(on_message=celery_on_message, propagate=False))


def get_task_status(task_id: str) -> TaskStatusResponse:
    task = celery_app.AsyncResult(task_id)
    
    if task.status == 'PENDING':
        return TaskStatusResponse(
            task_id=task_id,
            status='PENDING',
            meta={'message': '任务等待执行'}
        )
    
    if task.status == 'STARTED' or task.status == 'RUNNING':
        meta = task.info if isinstance(task.info, dict) else {}
        return TaskStatusResponse(
            task_id=task_id,
            status='RUNNING',
            meta=meta
        )
    
    if task.status == 'PROGRESS':
        meta = task.info if isinstance(task.info, dict) else {}
        return TaskStatusResponse(
            task_id=task_id,
            status='PROGRESS',
            meta=meta
        )
    
    if task.status == 'SUCCESS':
        return TaskStatusResponse(
            task_id=task_id,
            status='SUCCESS',
            result=task.result
        )
    
    if task.status == 'FAILURE':
        meta = task.info if isinstance(task.info, dict) else {}
        return TaskStatusResponse(
            task_id=task_id,
            status='FAILURE',
            meta=meta,
            traceback=task.traceback
        )
    
    return TaskStatusResponse(
        task_id=task_id,
        status=task.status,
        result=task.result if task.ready() else None
    )


@app.get("/{word}")
async def root(word: str, background_task: BackgroundTasks):
    task_name = "app.worker.celery_worker.test_celery"

    task = celery_app.send_task(task_name, args=[word])
    print(task)
    background_task.add_task(background_on_message, task)

    return {"message": "Word received", "task_id": task.id}


@app.get("/task/{task_id}", response_model=TaskStatusResponse)
async def get_task(task_id: str):
    task = celery_app.AsyncResult(task_id)
    
    if task.status == 'PENDING':
        if task.result is None and not task.ready():
            backend = celery_app.backend
            if hasattr(backend, 'get'):
                try:
                    result = backend.get(task_id)
                    if result is None:
                        raise HTTPException(
                            status_code=404,
                            detail=f"任务 {task_id} 不存在或已过期（24小时后过期）"
                        )
                except Exception as e:
                    pass
    
    return get_task_status(task_id)


@app.post("/task/high-priority")
async def submit_high_priority_task(
    request: HighPriorityTaskRequest,
    background_task: BackgroundTasks
):
    task_name = "app.worker.celery_worker.user_triggered_task"
    
    task = celery_app.send_task(
        task_name,
        args=[request.data],
        queue='high-priority'
    )
    
    background_task.add_task(background_on_message, task)
    
    return {
        "message": "高优先级任务已提交",
        "task_id": task.id,
        "queue": "high-priority",
        "priority": "high"
    }


@app.post("/task/low-priority/batch")
async def submit_low_priority_batch_task(
    request: LowPriorityBatchRequest,
    background_task: BackgroundTasks
):
    task_name = "app.worker.celery_worker.batch_process_task"
    
    task = celery_app.send_task(
        task_name,
        args=[request.items],
        queue='low-priority'
    )
    
    background_task.add_task(background_on_message, task)
    
    return {
        "message": "低优先级批处理任务已提交",
        "task_id": task.id,
        "queue": "low-priority",
        "priority": "low",
        "total_items": len(request.items)
    }


@app.post("/task/low-priority/scheduled")
async def submit_low_priority_scheduled_task(
    request: LowPriorityScheduledRequest,
    background_task: BackgroundTasks
):
    task_name = "app.worker.celery_worker.scheduled_task"
    
    task = celery_app.send_task(
        task_name,
        args=[request.params],
        queue='low-priority'
    )
    
    background_task.add_task(background_on_message, task)
    
    return {
        "message": "低优先级定时任务已提交",
        "task_id": task.id,
        "queue": "low-priority",
        "priority": "low"
    }


@app.delete("/task/{task_id}")
async def revoke_task(task_id: str, terminate: bool = Query(False, description="是否终止正在执行的任务")):
    celery_app.control.revoke(task_id, terminate=terminate)
    
    return {
        "message": f"任务 {task_id} 已撤销",
        "task_id": task_id,
        "terminated": terminate
    }
