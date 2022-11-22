# encoding:utf-8
from __future__ import unicode_literals

import datetime
import json
import re
import os
import queue
import aiohttp
import asyncio

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
                if isinstance(time_temp, datetime.datetime) or isinstance(
                        time_temp, datetime.date):
                    pass
                else:
                    raise IAIllegalDataException(
                        'Value of #time should be datetime.datetime or datetime.date'
                    )
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
                    "type[%s] property key must be a valid variable name. [key=%s]"
                    % (action_type, str(key)))

            if 'user_add' == action_type.lower(
            ) and not is_number(value) and not key.startswith('#'):
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

    async def track(self, task_id=None, event_name=None, properties=None):
        await self.__add(task_id=task_id,
                         send_type='track',
                         event_name=event_name,
                         properties_add=properties)

    async def __add(self,
                    task_id,
                    send_type,
                    event_name=None,
                    event_id=None,
                    properties_add=None):
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
        data_list = list()
        data_list.append(data)
        content = json.dumps(data_list,
                             separators=(',', ':'),
                             cls=IADateTimeSerializer)
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


class AIter:

    def __init__(self, N):
        self.i = 0
        self.N = N

    def __aiter__(self):
        return self

    async def __anext__(self):
        i = self.i
        if i >= self.N:
            raise StopAsyncIteration
        self.i += 1
        return i


class IcarusConsumer(object):
    """发送数据给接收服务器

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
                headers = {
                    "Content-Type": "application/json;charset=UTF-8",
                    "task_id": "task_id",
                    "ICARUS-Integration-Type": "python-sdk",
                    "ICARUS-Integration-Version": __VERSION__
                }
                async for i in AIter(3):
                    async with session.post(
                            self.__server_uri,
                            data=data,
                            headers=headers,
                            timeout=self.__timeout) as response:
                        if response.status == 200:
                            response = await response.read()
                            response_data = json.loads(response.decode())
                            log('response={}'.format(response_data))
                            if response_data["status_code"] == 200:
                                return True
                            else:
                                print("Unexpected result : \n %s" %
                                      response_data)
                # TODO: restore message locally and raise exception
                # TODO: resend message operation
                raise IANetworkException("Unexpected http status code: " +
                                         str(response.status))
        except aiohttp.ClientConnectionError as e:
            raise IANetworkException("Data transmission failed due to " +
                                     repr(e))

    def flush(self, throw_exception=True):
        pass

    def close(self):
        pass


class _IAFileLock(object):

    def __init__(self, file_handler) -> None:
        self._file_handler = file_handler

    def __enter__(self) -> object:
        _lock(self._file_handler)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        _unlock(self._file_handler)


class LoggingConsumer(object):
    """
    """
    _mutex = queue.Queue()
    _mutex.put(1)

    class _FileWriter(object):
        _writers = {}
        _writeMutex = queue.Queue()
        _writeMutex.put(1)

        @classmethod
        def instance(cls, filename) -> object:
            cls._writeMutex.get(block=True, timeout=None)
            try:
                if filename in cls._writers.keys():
                    result = cls._writers[filename]
                    result._count = result._count + 1
                else:
                    result = cls(filename)
                    cls._writers[filename] = result
                return result
            finally:
                cls._writeMutex.put(1)

        def __init__(self, filename) -> None:
            self._filename = filename
            self._filename = filename
            self._file = open(self._filename, "a")
            self._count = 1

        def close(self) -> None:
            LoggingConsumer._FileWriter._writeMutex.get(block=True,
                                                        timeout=None)
            try:
                self._count = self._count - 1
                if self._count == 0:
                    self._file.close()
                    del LoggingConsumer._FileWriter._writers[self._filename]
            finally:
                LoggingConsumer._FileWriter._writeMutex.put(1)

        def is_valid(self, filename) -> bool:
            return self._filename == filename

        def write(self, messages) -> None:
            with _IAFileLock(self._file):
                for message in messages:
                    self._file.write(message)
                    self._file.write("\n")
                self._file.flush()

    @classmethod
    def construct_filename(cls, directory, date_suffix, file_size,
                           file_prefix) -> str:
        filename = file_prefix + ".log." + date_suffix if file_prefix is not None else "log." + date_suffix

        if file_size > 0:
            count = 0
            file_path = directory + filename + "_" + str(count)
            while os.path.exists(file_path) and cls.file_size_out(
                    file_path, file_size):
                count += 1
                file_path = directory + filename + "_" + str(count)
            return file_path
        else:
            return directory + filename

    @classmethod
    def file_size_out(cls, file_path, file_size) -> bool:
        f_size = os.path.getsize(file_path)
        f_size = f_size / float(1024 * 1024)
        if f_size > file_size:
            return True
        return False

    @classmethod
    def unlock_logging_consumer(cls) -> None:
        cls._mutex.put(1)

    @classmethod
    def lock_logging_consumer(cls) -> None:
        cls._mutex.get(block=True, timeout=None)

    def __init__(self,
                 log_directory,
                 log_size=0,
                 buffer_size=5,
                 rotate_mode=ROTATE_MODE.DAILY,
                 file_prefix=None):
        """Constructor  for logging consumer"""
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        self.log_directory = log_directory
        self.sdf = "%Y-%m-%d-%H" if rotate_mode == ROTATE_MODE.HOURLY else "%Y-%m-%d"
        self.suffix = datetime.datetime.now().strftime(self.sdf)
        self._fileSize = log_size
        if not self.log_directory.endswith("/"):
            self.log_directory = self.log_directory + "/"
        self._buffer = []
        self._buffer_size = buffer_size
        self._file_prefix = file_prefix
        self.lock_logging_consumer()
        filename = LoggingConsumer.construct_filename(self.log_directory,
                                                      self.suffix,
                                                      self._fileSize,
                                                      self._file_prefix)
        self._writer = LoggingConsumer._FileWriter.instance(filename)
        self.unlock_logging_consumer()

    def add(self, msg) -> None:
        messages = None
        self.lock_logging_consumer()
        self._buffer.append(msg)
        if len(self._buffer) >= self._buffer_size:
            messages = self._buffer
            self.refresh_writer()
            self._buffer = []
        if messages:
            self._writer.write(messages)
        self.unlock_logging_consumer()

    def flush_with_close(self, is_close) -> None:
        messages = None
        self.lock_logging_consumer()
        if len(self._buffer) > 0:
            messages = self._buffer
            self.refresh_writer()
            self._buffer = []
        if messages:
            self._writer.write(messages)
        if is_close:
            self._writer.close()
        self.unlock_logging_consumer()

    def refresh_writer(self) -> None:
        date_suffix = datetime.datetime.now().strftime(self.sdf)
        if self.suffix != date_suffix:
            self.suffix = date_suffix
        filename = LoggingConsumer.construct_filename(self.log_directory,
                                                      self.suffix,
                                                      self._fileSize,
                                                      self._file_prefix)
        if not self._writer.is_valid(filename):
            self._writer.close()
            self._writer = LoggingConsumer._FileWriter.instance(filename)

    def flush(self):
        self.flush_with_close(False)

    def close(self):
        self.flush_with_close(True)


if __name__ == "__main__":
    ia = IcarusAnalytics(IcarusConsumer(server_uri=SERVER_URI,
                                        task_id="debug"))
    properties = {
        "#time": datetime.datetime.now(),
        # 设置这条event发生的时间，如果不设置的话，则默认是当前时间
        "#ip": "192.168.1.1",
        # 设置用户的IP，tda会自动根据该IP解析省份、城市
        # "#uuid":uuid.uuid1(),#选填，如果上面enable_uuid开关打开，不需要填
        "Product_Name": "商品名",
        "Price": 30,
        "OrderId": "订单号abc_123"
    }

    async def func():
        await ia.track(task_id="debug", properties=properties)

    asyncio.run(func())
