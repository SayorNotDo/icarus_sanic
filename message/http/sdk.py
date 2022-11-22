# encoding:utf-8
from __future__ import unicode_literals

import datetime
import json
import re

import aiohttp

__NAME_PATTERN = re.compile(r"^[#a-zA-Z][a-zA-Z0-9_]{0,49}$", re.I)
__VERSION__ = "1.0.0"
SERVER_URI = "http://127.0.0.1:80/v1/api/user/add_user"
is_print = True

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

try:
    isinstance("", basestring)


    def is_str(s):
        return isinstance(s, basestring)
except NameError:
    def is_str(s):
        return isinstance(s, str)
try:
    isinstance(1, long)


    def is_int(n):
        return isinstance(n, int) or isinstance(n, long)
except NameError:
    def is_int(n):
        return isinstance(n, int)

try:
    from enum import Enum

    ROTATE_MODE = Enum('ROTATE_MODE', ('DAILY', 'HOURLY'))
except ImportError:
    class ROTATE_MODE(object):
        DAILY = 0
        HOURLY = 1


def is_number(s):
    if is_int(s):
        return True
    if isinstance(s, float):
        return True
    return False


def assert_properties(action_type, properties):
    if properties is not None:
        if "#event_time" in properties.keys():
            try:
                time_temp = properties.get('#time')
                if isinstance(time_temp, datetime.datetime) or isinstance(time_temp, datetime.date):
                    pass
                else:
                    raise IAIllegalDataException(
                        'Value of #time should be datetime.datetime or datetime.date')
            except Exception as e:
                raise IAIllegalDataException(e)

        for key, value in properties.items():
            if not is_str(key):
                raise IAIllegalDataException(
                    "Property key must be a str. [key=%s]" % str(key))

            if value is None:
                continue

            if not __NAME_PATTERN.match(key):
                raise IAIllegalDataException(
                    "type[%s] property key must be a valid variable name. [key=%s]" % (action_type, str(key)))

            if 'user_add' == action_type.lower() and not is_number(value) and not key.startswith('#'):
                raise IAIllegalDataException(
                    'user_add properties must be number type')


def log(msg=None):
    if all([msg, is_print]):
        print('[ThinkingAnalytics-Python SDK V%s]-%s' % (__VERSION__, msg))


class IAException(Exception):
    pass


class IAIllegalDataException(IAException):
    pass


class IANetworkException(IAException):
    pass


class IADateTimeSerializer(json.JSONEncoder):
    """
    实现 date 和 datetime 类型的自动转化
    """

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            head_fmt = "%Y-%m-%d %H:%M:%S"
            return obj.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        elif isinstance(obj, datetime.date):
            fmt = '%Y-%m-%d'
            return obj.strftime(fmt)
        return json.JSONEncoder.default(self, obj)


class IcarusAnalytics(object):
    __strict = False

    def __init__(self, consumer, strict=None):
        """
        :param consumer:
        :param strict:
        """

        self.__consumer = consumer
        if isinstance(consumer, IcarusConsumer):
            self.__strict = True
        if strict is not None:
            self.__strict = strict

    async def flush(self):
        """
        立即提交数据到相应的接收端
        """
        await self.__consumer.flush()

    async def close(self):
        """关闭并退出 sdk

        请在退出前调用本接口，以避免缓存内的数据丢失
        """
        await self.__consumer.close()

    async def __add(self, task_id, send_type, event_name=None, event_id=None, properties_add=None):
        if task_id is None:
            raise IAException("task_id must be set")
        data = {'#type': send_type}
        if send_type.find("track") != -1 and event_id is not None:
            if send_type == "track":
                self.__build_data(data, '#first_check_id', event_id)
            else:
                self.__build_data(data, '#event_id', event_id)

        if properties_add:
            properties = properties_add.copy()
        else:
            properties = {}
        # self.__move_preset_properties(["#ip", "#first_check_id", "#app_id", "#time", '#uuid'], data, properties)
        if self.__strict:
            assert_properties(send_type, properties)
        if '#event_time' not in data:
            data['#event_time'] = datetime.datetime.now()
        self.__build_data(data, '#event_name', event_name)
        self.__build_data(data, '#task_id', task_id)
        data['properties'] = properties
        content = json.dumps(data, separators=(
            ',', ':'), cls=IADateTimeSerializer)
        log("collect data={}".format(content))
        await self.__consumer.add(content)

    @staticmethod
    def __build_data(data, key, value):
        if value is not None:
            data[key] = value

    @staticmethod
    def __move_preset_properties(keys, data, properties):
        for key in keys:
            if key in properties.keys():
                data[key] = properties.get(key)
                del (properties[key])

    @staticmethod
    def enable_log(isPrint=False):
        global is_print
        is_print = isPrint


class IcarusConsumer(object):
    """逐条、同步的发送数据给接收服务器

    服务端会对数据进行严格校验，当某个属性不符合规范时，整条数据都不会入库. 当数据格式错误时抛出包含详细原因的异常信息.
    """

    def __init__(self, server_uri, task_id, timeout=30000):
        """创建 Consumer

        Args:
            server_uri: 服务器的 URL 地址
            task_id: 任务 ID
            timeout: 请求的超时时间, 单位毫秒, 默认为 30000 ms
        """
        server_url = urlparse(server_uri)
        self.__server_uri = server_url.geturl()
        self.__task_id = task_id
        self.__timeout = timeout
        IcarusAnalytics.enable_log(True)

    async def add(self, data=None):
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Content-Type": "application/json;charset=UTF-8",
                           "task_id": "task_id",
                           "ICARUS-Integration-Type": "python-sdk",
                           "ICARUS-Integration-Version": __VERSION__}
                async with session.post(self.__server_uri, data=data, headers=headers,
                                        timeout=self.__timeout) as response:
                    if response.status == 200:
                        response = await response.read()
                        response_data = json.loads(response.decode())
                        log('response={}'.format(response_data))
                        if response_data["status_code"] == 200:
                            return True
                        else:
                            print("Unexpected result : \n %s" % response_data)
                    else:
                        raise IANetworkException(
                            "Unexpected http status code: " + str(response.status))
        except ConnectionError as e:
            raise IANetworkException(
                "Data transmission failed due to " + repr(e))

    def flush(self, throw_exception=True):
        pass

    def close(self):
        pass
