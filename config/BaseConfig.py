db_config = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": "127.0.0.1",
                "port": "3306",
                "user": "root",
                "password": "test1234",
                "database": "icarus",
                "maxsize": "15",
                "minsize": "5"
            }
        },
        # "default": "mysql://root:root@127.0.0.1:3306/icarus"
    },
    "apps": {
        "user": {
            "models": ["apps.user.models"],
            "default_connection": "default"
        }
    }
}


class BaseConfig:
    DB_CONFIG = db_config
