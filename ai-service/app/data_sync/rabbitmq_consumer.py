"""RabbitMQ 消息队列消费模块。

异步处理文档向量化任务：
    生产者（Django）将待处理文档推入队列 → 消费者（本模块）异步读取并构建索引。

优势：
    - 削峰填谷：避免大批量文档同时处理压垮服务。
    - 解耦：文档上传与向量化异步分离。
    - 可靠性：消息持久化，服务重启不丢失。
"""
import threading
import json
from typing import Optional

from app.config import RABBITMQ_URL


class RabbitMQConsumer:
    """RabbitMQ 文档向量化任务消费者。"""

    def __init__(self, queue_name: str = "rag_document_queue"):
        self.queue_name = queue_name
        self._thread: Optional[threading.Thread] = None
        self._running = False

    def start(self):
        """启动消费者（后台线程）。"""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._consume, daemon=True)
        self._thread.start()
        print("[RabbitMQConsumer] 消费者已启动")

    def stop(self):
        """停止消费。"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _consume(self):
        """消费主循环。"""
        try:
            import pika

            params = pika.URLParameters(RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()

            # 声明持久化队列
            channel.queue_declare(queue=self.queue_name, durable=True)
            channel.basic_qos(prefetch_count=1)  # 公平派发

            def callback(ch, method, properties, body):
                """消息处理回调。"""
                try:
                    msg = json.loads(body)
                    print(f"[RabbitMQConsumer] 收到消息: {msg.get('type', 'unknown')}")

                    self._process_message(msg)

                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    print(f"[RabbitMQConsumer] 消息处理失败: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            channel.basic_consume(queue=self.queue_name, on_message_callback=callback)

            while self._running:
                connection.process_data_events(time_limit=1)

            connection.close()
        except Exception as e:
            print(f"[RabbitMQConsumer] 消费异常: {e}")

    def _process_message(self, msg: dict):
        """处理消息：根据类型执行对应操作。

        消息格式：
            {"type": "build_index", "course_id": "c_101", "document_path": "/data/..."}
            {"type": "add_document", "course_id": "c_101", "document_path": "/data/..."}
        """
        msg_type = msg.get("type")
        course_id = msg.get("course_id", "")
        document_path = msg.get("document_path", "")

        if not course_id:
            return

        if msg_type in ("build_index", "add_document"):
            from app.data_processing.document_factory import DataProcessorFactory
            from app.services.rag_service import get_rag_service

            # 工厂模式处理文档
            documents = DataProcessorFactory.process_source(document_path)
            if documents:
                rag = get_rag_service()
                rag.build_indexes(course_id, documents=documents)
                print(f"[RabbitMQConsumer] 课程 {course_id} 索引构建完成")
