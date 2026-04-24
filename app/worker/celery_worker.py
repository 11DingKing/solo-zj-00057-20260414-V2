from time import sleep
import logging

from celery import current_task
from celery.exceptions import SoftTimeLimitExceeded, Retry

from .celery_app import celery_app

log = logging.getLogger(__name__)


def cleanup_resources(task_id: str):
    """清理任务资源的函数"""
    log.info(f"正在清理任务 {task_id} 的资源...")
    pass


@celery_app.task(
    acks_late=True,
    soft_time_limit=30,
    time_limit=60,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
)
def test_celery(word: str) -> str:
    task_id = current_task.request.id
    log.info(f"任务 {task_id} 开始执行: test_celery")
    
    try:
        current_task.update_state(
            state='RUNNING',
            meta={
                'status': 'running',
                'process_percent': 0,
                'message': '任务开始执行'
            }
        )
        
        for i in range(1, 11):
            sleep(1)
            current_task.update_state(
                state='PROGRESS',
                meta={
                    'status': 'in_progress',
                    'process_percent': i * 10,
                    'message': f'处理中 {i * 10}%'
                }
            )
        
        return f"test task return {word}"
        
    except SoftTimeLimitExceeded as e:
        log.warning(f"任务 {task_id} 软超时，执行清理操作")
        cleanup_resources(task_id)
        
        current_task.update_state(
            state='FAILURE',
            meta={
                'exc_type': 'SoftTimeLimitExceeded',
                'exc_message': '任务执行超时',
                'process_percent': 100
            }
        )
        raise
        
    except Exception as e:
        log.error(f"任务 {task_id} 执行出错: {str(e)}")
        cleanup_resources(task_id)
        raise


@celery_app.task(
    acks_late=True,
    soft_time_limit=120,
    time_limit=180,
    max_retries=3,
    default_retry_delay=120,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def user_triggered_task(data: dict) -> dict:
    task_id = current_task.request.id
    log.info(f"高优先级任务 {task_id} 开始执行: user_triggered_task")
    
    try:
        current_task.update_state(
            state='RUNNING',
            meta={
                'status': 'running',
                'process_percent': 0,
                'message': '任务开始执行'
            }
        )
        
        sleep(2)
        current_task.update_state(
            state='PROGRESS',
            meta={
                'status': 'in_progress',
                'process_percent': 50,
                'message': '处理中 50%'
            }
        )
        
        sleep(2)
        
        return {
            'task_id': task_id,
            'status': 'success',
            'data': data,
            'message': '用户触发任务执行完成'
        }
        
    except SoftTimeLimitExceeded as e:
        log.warning(f"高优先级任务 {task_id} 软超时，执行清理操作")
        cleanup_resources(task_id)
        raise
        
    except Exception as e:
        log.error(f"高优先级任务 {task_id} 执行出错: {str(e)}")
        cleanup_resources(task_id)
        raise


@celery_app.task(
    acks_late=True,
    soft_time_limit=600,
    time_limit=900,
    max_retries=2,
    default_retry_delay=300,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=1800,
    retry_jitter=True,
)
def batch_process_task(items: list) -> dict:
    task_id = current_task.request.id
    log.info(f"低优先级批处理任务 {task_id} 开始执行: batch_process_task")
    total_items = len(items)
    
    try:
        current_task.update_state(
            state='RUNNING',
            meta={
                'status': 'running',
                'process_percent': 0,
                'message': '批处理任务开始执行',
                'total_items': total_items,
                'processed_items': 0
            }
        )
        
        for idx, item in enumerate(items):
            sleep(0.5)
            processed = idx + 1
            percent = int((processed / total_items) * 100)
            
            current_task.update_state(
                state='PROGRESS',
                meta={
                    'status': 'in_progress',
                    'process_percent': percent,
                    'message': f'批处理中 {processed}/{total_items}',
                    'total_items': total_items,
                    'processed_items': processed
                }
            )
        
        return {
            'task_id': task_id,
            'status': 'success',
            'total_items': total_items,
            'processed_items': total_items,
            'message': '批处理任务执行完成'
        }
        
    except SoftTimeLimitExceeded as e:
        log.warning(f"低优先级批处理任务 {task_id} 软超时，执行清理操作")
        cleanup_resources(task_id)
        raise
        
    except Exception as e:
        log.error(f"低优先级批处理任务 {task_id} 执行出错: {str(e)}")
        cleanup_resources(task_id)
        raise


@celery_app.task(
    acks_late=True,
    soft_time_limit=1800,
    time_limit=2700,
    max_retries=1,
    default_retry_delay=600,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=3600,
    retry_jitter=True,
)
def scheduled_task(params: dict) -> dict:
    task_id = current_task.request.id
    log.info(f"低优先级定时任务 {task_id} 开始执行: scheduled_task")
    
    try:
        current_task.update_state(
            state='RUNNING',
            meta={
                'status': 'running',
                'process_percent': 0,
                'message': '定时任务开始执行'
            }
        )
        
        sleep(3)
        
        current_task.update_state(
            state='PROGRESS',
            meta={
                'status': 'in_progress',
                'process_percent': 50,
                'message': '定时任务处理中 50%'
            }
        )
        
        sleep(3)
        
        return {
            'task_id': task_id,
            'status': 'success',
            'params': params,
            'message': '定时任务执行完成'
        }
        
    except SoftTimeLimitExceeded as e:
        log.warning(f"低优先级定时任务 {task_id} 软超时，执行清理操作")
        cleanup_resources(task_id)
        raise
        
    except Exception as e:
        log.error(f"低优先级定时任务 {task_id} 执行出错: {str(e)}")
        cleanup_resources(task_id)
        raise
