# utils/grpc_pool.py
import grpc
import threading
from grpc import ChannelConnectivity

class GrpcChannelPool:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._channels = {}
        return cls._instance

    def get_channel(self, target):
        with self._lock:
            if target not in self._channels or self._check_disconnected(target):
                self._channels[target] = grpc.insecure_channel(
                    target,
                    options=[
                        ('grpc.keepalive_time_ms', 10000),
                        ('grpc.max_connection_age_ms', 300000)
                    ]
                )
            return self._channels[target]

    def _check_disconnected(self, target):
        channel = self._channels.get(target)
        if channel:
            try:
                return channel.get_state(True) == ChannelConnectivity.TRANSIENT_FAILURE
            except:
                return True
        return True