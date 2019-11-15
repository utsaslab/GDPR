class ExceededDailyTranslateQuotaLimitSpecification():
    def __init__(self, quota_limit_service):
        self.quota_limit_service = quota_limit_service
    def is_satisfied_by(self, quota_limit):
        return (quota_limit > self.quota_limit_service.get_chars_per_day() and self.quota_limit_service.get_chars_per_day() != -1)
