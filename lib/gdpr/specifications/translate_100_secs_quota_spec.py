class Translate100SecsQuotaSpec():
    def __init__(self, quota_limit_service):
        self.quota_limit_service = quota_limit_service
    def is_satisfied_by(self, quota_limit):
        print('quota_limit:', quota_limit)
        print('per 100 secs:', self.quota_limit_service.get_characters_per_100_secs_per_project_per_user())
        return (quota_limit > self.quota_limit_service.get_characters_per_100_secs_per_project_per_user())
