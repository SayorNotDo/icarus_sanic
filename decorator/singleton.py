import threading

from utils.logger import logger

lock = threading.Lock()

# instance container
instances = {}


def singleton(cls):
    """ this is decorator to decorate class, make the class singleton """

    def get_instance(*args, **kwargs):
        cls_name = cls.__name__
        try:
            lock.acquire()
            if cls_name not in instances:
                logger.info(f"creating {cls_name} instance")
                instance = cls(*args, **kwargs)
                instances[cls_name] = instance
                logger.info(f"create {cls_name} instance finished")
        finally:
            lock.release()

        return instances[cls_name]

    return get_instance


def get_all_instance():
    """ return all instance in the container """
    return instances
