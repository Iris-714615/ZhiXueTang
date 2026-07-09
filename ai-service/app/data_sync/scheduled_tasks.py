"""定时任务调度模块。

基于 APScheduler 实现定时任务：
    - 定时爬取外部学习资源（每日凌晨执行）
    - 定时重建课程索引（每周执行，保持向量库新鲜度）
    - 定时清理过期缓存（每小时执行）

APScheduler 优势：
    - 轻量级，无需额外依赖（对比 Celery beat）。
    - 支持 cron、interval、date 三种触发器。
    - 持久化 jobstore，重启不丢失任务。
"""
import threading
from typing import Optional


class ScheduledTaskManager:
    """定时任务管理器。"""

    def __init__(self):
        self._scheduler = None
        self._started = False

    def start(self):
        """启动定时任务调度器。"""
        if self._started:
            return

        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from apscheduler.triggers.cron import CronTrigger
            from apscheduler.triggers.interval import IntervalTrigger

            self._scheduler = BackgroundScheduler()

            # 1. 每日凌晨2点爬取外部学习资源
            self._scheduler.add_job(
                self._crawl_external_resources,
                CronTrigger(hour=2, minute=0),
                id="crawl_resources",
                name="定时爬取外部资源",
            )

            # 2. 每周日凌晨3点重建全部课程索引
            self._scheduler.add_job(
                self._rebuild_all_indexes,
                CronTrigger(day_of_week="sun", hour=3, minute=0),
                id="rebuild_indexes",
                name="定时重建索引",
            )

            # 3. 每小时清理过期缓存
            self._scheduler.add_job(
                self._clear_expired_cache,
                IntervalTrigger(hours=1),
                id="clear_cache",
                name="清理过期缓存",
            )

            self._scheduler.start()
            self._started = True
            print("[ScheduledTasks] 定时任务调度器已启动（爬取/重建/缓存清理）")
        except Exception as e:
            print(f"[ScheduledTasks] 启动失败: {e}")

    def stop(self):
        """停止调度器。"""
        if self._scheduler:
            self._scheduler.shutdown(wait=False)
            self._started = False
            print("[ScheduledTasks] 调度器已停止")

    def _crawl_external_resources(self):
        """定时爬取外部学习资源。"""
        print("[ScheduledTasks] 执行定时爬取外部资源任务")
        # 实际项目中调用 WebCrawlerProcessor 批量爬取

    def _rebuild_all_indexes(self):
        """定时重建全部课程索引。"""
        print("[ScheduledTasks] 执行定时重建全部索引任务")
        # 实际项目中遍历所有课程，调用 RAGService.build_indexes

    def _clear_expired_cache(self):
        """清理过期缓存。"""
        print("[ScheduledTasks] 执行清理过期缓存任务")
        try:
            from app.retrieval.cache_manager import CacheManager
            CacheManager().clear()
        except Exception as e:
            print(f"[ScheduledTasks] 缓存清理失败: {e}")
