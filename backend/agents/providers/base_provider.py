from abc import ABC, abstractmethod


class BaseProvider(ABC):
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name

    @abstractmethod
    def generate(self, prompt: str) -> str:
        ...

    def is_out_of_credit_error(self, exc: Exception) -> bool:
        """Trả True cho mọi lỗi mà cách xử lý hợp lý là chuyển sang key/provider
        khác thay vì retry lại chính key đó — hết credit/quota, bị chặn, hoặc
        provider (kể cả self-hosted) đang không sẵn sàng/không kết nối được."""
        msg = str(exc).lower()
        keywords = [
            # credit / quota / billing
            "quota", "billing", "insufficient_quota", "rate_limit",
            "resource_exhausted", "credits", "credit", "429",
            "payment_required", "402", "401", "403", "unauthorized",
            "invalid_api_key", "invalid api key", "forbidden",
            # kết nối / khả dụng — key/endpoint không sẵn sàng
            "connection", "connect", "timeout", "timed out", "unreachable",
            "max retries exceeded", "failed to establish", "refused",
            "name or service not known", "502", "503", "504",
        ]
        return any(k in msg for k in keywords)

    def health_check(self) -> bool:
        """Kiểm tra nhanh, rẻ, không tốn quota, chạy 1 lần lúc tạo phòng để
        loại các key/provider không sẵn sàng ra khỏi vòng xoay ngay từ đầu.
        Mặc định coi là sẵn sàng — provider nào có cách kiểm tra rẻ tiền
        (self-hosted, không tính phí theo request) thì override lại."""
        return True
