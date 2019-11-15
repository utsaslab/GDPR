# https://cloud.google.com/translate/quotas#content
class GoogleTranslateQuotaLimitService():
    chars_per_day = 10**9
    characters_per_100_secs_per_project = 10**6
    characters_per_100_secs_per_project_per_user = 10**4

    def get_chars_per_day(self):
        return self.chars_per_day

    def set_characters_per_100_secs_per_project(self, number):
        self.characters_per_100_secs_per_project = number

    def set_characters_per_100_secs_per_project_per_user(self, number):
        self.characters_per_100_secs_per_project_per_user = number

    def set_chars_per_day(self, number):
        self.chars_per_day = number

    def get_characters_per_100_secs_per_project(self):
        return self.characters_per_100_secs_per_project

    def get_characters_per_100_secs_per_project_per_user(self):
        return self.characters_per_100_secs_per_project_per_user
