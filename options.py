import json
from pathlib import Path

from platformdirs import user_config_dir


class Option:
    def __init__(self, name: str, value: str | Path | bool | int | float, visible=True):
        self.name = name
        self.value = value
        self.visible = visible

    def toDict(self):
        val = str(self.value) if isinstance(self.value, Path) else self.value
        return {'name': self.name, 'value': val, 'visible': self.visible}


class Options(dict[str, Option]):

    def __init__(self, app_author: str, app_name: str, default_values: list[Option]):
        super().__init__()
        self.file_path = Path(user_config_dir(appname=app_name, appauthor=app_author, ensure_exists=True),'options.json')
        for o in default_values:
            self[o.name] = o

        # Load persisted values
        if self.file_path.exists():
            with open(self.file_path, 'r') as f:
                lst = json.load(f)
                for o in lst:
                    if o['name'] in self:
                        self[o['name']] = Option(o['name'], o['value'], visible=o['visible'])

    def save(self):
        with open(self.file_path,'w') as f:
            json.dump([o.toDict() for o in self.values()], f, sort_keys=True, indent=4)
