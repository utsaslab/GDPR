class Translate100SecsQuotaSpec():
    def __init__(self, quota_service):
        self.quota_service = quota_service
    def is_satisfied_by(self, quota_limit):
        return (quota_limit > self.quota_service.get_characters_per_100_secs_per_user())
