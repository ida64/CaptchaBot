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
            }),
        })

        with open(self.filename, 'w') as f:
            yaml.dump(default_data, f)

    def get(self, key: str, default=None):
        keys = key.split('.')
        value = self.data
        for k in keys:
            if isinstance(value, CommentedMap) and k in value:
                value = value[k]
            else:
                return default
        return value if value is not None else default
