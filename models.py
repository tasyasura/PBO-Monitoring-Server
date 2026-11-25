from exceptions import (
    InvalidDataError,
    InvalidUrlError,
    ServiceTimeoutError,
    ServerDownError,
)


class Server:
    total = 0

    def __init__(self, name: str, status: bool = True):
        self.name = name
        self.status = status
        Server.total += 1

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise InvalidDataError("Nama server tidak boleh kosong.")
        self._name = value.strip()

    @property
    def status(self) -> bool:
        return self.__status

    @status.setter
    def status(self, value: bool):
        if not isinstance(value, bool):
            raise InvalidDataError("Status server harus bertipe boolean (True/False).")
        self.__status = value

    def check_status(self) -> bool:
        return self.status

    def __str__(self) -> str:
        kondisi = "ONLINE" if self.status else "OFFLINE"
        return f"Server {self.name}: {kondisi}"

    def __eq__(self, other) -> bool:
        return isinstance(other, Server) and self.name == other.name


class Service:
    def __init__(self, name: str, url: str, response_time: float = 0.0):
        self.name = name
        self.url = url
        self.status = True
        self.response_time = response_time

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise InvalidDataError("Nama layanan tidak boleh kosong.")
        self._name = value.strip()

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, value: str):
        if not isinstance(value, str) or not (
            value.startswith("http://") or value.startswith("https://")
        ):
            raise InvalidUrlError(
                f"URL '{value}' tidak valid. Harus diawali 'http://' atau 'https://'."
            )
        self._url = value

    @property
    def response_time(self) -> float:
        return self._response_time

    @response_time.setter
    def response_time(self, value: float):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
            raise InvalidDataError("Waktu respons harus berupa angka dan tidak boleh negatif.")
        self._response_time = float(value)

    def check_status(self) -> bool:
        return self.status


class MonitoredService(Service):
    def __init__(self, name: str, url: str, response_time: float = 0.0):
        super().__init__(name, url, response_time)

    def check_status(self) -> bool:
        return super().check_status()


class WebsiteService(MonitoredService):
    LIMIT = 2.0

    @staticmethod
    def is_valid_url(url: str) -> bool:
        return isinstance(url, str) and (
            url.startswith("http://") or url.startswith("https://")
        )

    @classmethod
    def default_website(cls, name: str, url: str):
        return cls(name, url, 0.5)

    def check_status(self) -> bool:
        if not self.is_valid_url(self.url):
            raise InvalidUrlError(f"URL website tidak valid: {self.url}")
        if self.response_time > self.LIMIT:
            self.status = False
            raise ServiceTimeoutError(self.name, self.response_time, self.LIMIT)
        return super().check_status()


class ApiService(MonitoredService):
    LIMIT = 3.0

    def check_status(self) -> bool:
        if self.response_time > self.LIMIT:
            self.status = False
            raise ServiceTimeoutError(self.name, self.response_time, self.LIMIT)
        return super().check_status()


class Alert:
    VALID_LEVELS = {"INFO", "WARNING", "CRITICAL"}

    def __init__(self, message: str, level: str = "WARNING"):
        if not isinstance(message, str) or not message.strip():
            raise InvalidDataError("Pesan alert tidak boleh kosong.")
        if level not in self.VALID_LEVELS:
            raise InvalidDataError(f"Level alert harus salah satu dari {self.VALID_LEVELS}.")
        self.message = message.strip()
        self.level = level

    def __str__(self) -> str:
        return f"[{self.level}] {self.message}"


class MonitoringSystem:
    def __init__(self, server: Server):
        if not isinstance(server, Server):
            raise InvalidDataError("Objek yang dipantau harus merupakan instance dari Server.")
        self.server = server
        self.alerts: list[Alert] = []

    def add_alert(self, alert: Alert):
        self.alerts.append(alert)

    def monitor(self, services: list[MonitoredService]):
        if not self.server.check_status():
            alert = Alert(f"Server {self.server.name} mati", "CRITICAL")
            self.add_alert(alert)
            raise ServerDownError(self.server.name)

        for service in services:
            try:
                service.check_status()
            except ServiceTimeoutError as e:
                self.add_alert(Alert(str(e), "WARNING"))
                raise
