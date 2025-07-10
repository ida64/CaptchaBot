from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

yaml = YAML()

class Config:
    def __init__(self, filename: str):
        self.filename = filename
        self.data = CommentedMap()

    @staticmethod
    def load_config(filename: str) -> 'Config':
        config = Config(filename)
        try:
            config.load()
        except FileNotFoundError:
            config.save_default()
            config.load()
        return config

    def load(self):
        with open(self.filename, 'r') as f:
            self.data = yaml.load(f)

    def save(self):
        with open(self.filename, 'w') as f:
            yaml.dump(self.data, f)

    def save_default_locale_en_us(self) -> None:
        default_locale_data = CommentedMap({
            'verification_view': CommentedMap({
                'embed': CommentedMap({
                    'title': "Captcha Verification",
                    'description': "Click the button below to complete a captcha challenge.\nIf the challenge is too difficult to read, click the button again to get a new one.",
                }),
                'button': CommentedMap({
                    'label': ":robot: Start Verification",
                }),
            }),
        })

        localization_dir = "localization"
        locale_file = f"{localization_dir}/en_US.yaml"
        with open(locale_file, 'w') as f:
            yaml.dump(default_locale_data, f)

    def save_default(self) -> None:
        default_data = CommentedMap({
            'discord': CommentedMap({
                'authentication': CommentedMap({
                    'token': '',
                }),
                'serviced_guild': CommentedMap({
                    'id': 0,
                    'prompt_channel_id': 0,
                    'verified_role_id': 0,
                    'log_channel_id': 0,
                }),
                'localization_dir': 'localization',
            }),
        })
        self.data = default_data
        self.save()
        self.save_default_locale_en_us()


    def get(self, key: str, default=None):
        keys = key.split('.')
        value = self.data
        for k in keys:
            if isinstance(value, CommentedMap) and k in value:
                value = value[k]
            else:
                return default
        return value if value is not None else default

if __name__ == "__main__":
    config = Config.load_config('config.yaml')
    print(config.data)