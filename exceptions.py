class MonitoringError(Exception):
    """Base exception untuk seluruh kesalahan pada Sistem Monitoring Server."""
    pass


class InvalidDataError(MonitoringError):
    """Dilempar ketika data input tidak valid (nama kosong, tipe salah, atau nilai negatif)."""
    pass


class InvalidUrlError(MonitoringError):
    """Dilempar ketika format URL layanan tidak menggunakan http:// atau https://."""
    pass


class ServiceTimeoutError(MonitoringError):
    """Dilempar ketika waktu respons layanan melebihi batas maksimal."""
    def __init__(self, service_name: str, response_time: float, limit: float):
        self.service_name = service_name
        self.response_time = response_time
        self.limit = limit
        super().__init__(
            f"Layanan '{service_name}' timeout: {response_time}s melebihi batas {limit}s"
        )


class ServerDownError(MonitoringError):
    """Dilempar ketika server dalam kondisi mati saat proses monitoring."""
    def __init__(self, server_name: str):
        self.server_name = server_name
        super().__init__(f"Server '{server_name}' sedang mati (OFFLINE). Monitoring dibatalkan.")
