"""MySQL Binlog 监听模块。

监听课程表数据变更（INSERT/UPDATE/DELETE），
自动触发对应课程的向量索引重建，实现数据实时同步。

工作原理：
    1. pymysql-replication 连接 MySQL 作为 replica。
    2. 解析 binlog 事件，过滤课程相关表变更。
    3. 将变更事件推入处理队列，异步重建索引。
"""
import threading
from typing import Optional

from app.config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB


class BinlogListener:
    """MySQL Binlog 监听器。

    监听课程表变更，自动触发向量索引重建。
    """

    def __init__(self, server_id: int = 100):
        """初始化 binlog 监听器。

        Args:
            server_id: 复制服务器 ID（MySQL slave 标识，需唯一）。
        """
        self.server_id = server_id
        self._thread: Optional[threading.Thread] = None
        self._running = False
        # 需要监听的表（课程相关）
        self.watch_tables = {"courses", "chapter", "lesson", "teacher"}

    def start(self):
        """启动 binlog 监听（后台线程）。"""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._listen, daemon=True)
        self._thread.start()
        print("[BinlogListener] 监听已启动")

    def stop(self):
        """停止监听。"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        print("[BinlogListener] 监听已停止")

    def _listen(self):
        """binlog 监听主循环。"""
        try:
            from pymysqlreplication import BinLogStreamReader
            from pymysqlreplication.row_event import (
                WriteRowsEvent, UpdateRowsEvent, DeleteRowsEvent,
            )

            # pymysqlreplication 参数名（兼容新旧版本）
            stream_settings = {
                "connection_settings": {
                    "host": MYSQL_HOST,
                    "port": MYSQL_PORT,
                    "user": MYSQL_USER,
                    "passwd": MYSQL_PASSWORD,
                },
                "server_id": self.server_id,
                "only_schemas": [MYSQL_DB],
                "only_tables": list(self.watch_tables),
                "resume_stream": True,
            }

            stream = BinLogStreamReader(**stream_settings)

            for event in stream:
                if not self._running:
                    break
                if isinstance(event, (WriteRowsEvent, UpdateRowsEvent, DeleteRowsEvent)):
                    self._handle_event(event)

            stream.close()
        except Exception as e:
            print(f"[BinlogListener] 监听异常: {e}")

    def _handle_event(self, event):
        """处理 binlog 变更事件。

        提取变更的课程 ID，触发索引异步重建。
        """
        table = event.table
        action = "INSERT" if isinstance(event, WriteRowsEvent) else \
                 "UPDATE" if isinstance(event, UpdateRowsEvent) else "DELETE"

        for row in event.rows:
            course_id = self._extract_course_id(table, row)
            if course_id:
                print(f"[BinlogListener] 检测到 {table} 表 {action}，课程 {course_id} 触发索引重建")
                self._trigger_rebuild(course_id)

    def _extract_course_id(self, table: str, row: dict) -> Optional[str]:
        """从行数据中提取课程 ID。"""
        values = row.get("values", {})
        if table == "courses":
            return str(values.get("id", ""))
        # chapter/lesson 等关联表通过 course 字段关联
        return str(values.get("course_id", values.get("course", ""))) or None

    def _trigger_rebuild(self, course_id: str):
        """触发课程索引重建（异步）。"""
        try:
            from app.services.rag_service import get_rag_service
            rag = get_rag_service()
            # 在实际项目中应放入 Celery 任务队列异步执行
            threading.Thread(
                target=rag.build_indexes,
                args=(course_id,),
                daemon=True,
            ).start()
        except Exception as e:
            print(f"[BinlogListener] 索引重建触发失败: {e}")
