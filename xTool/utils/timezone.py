# -*- coding: utf-8 -*-
#
import datetime as dt
import pendulum


# UTC time zone as a tzinfo instance.
TIMEZONE_UTC = pendulum.timezone('UTC')
TIMEZONE_SYSTEM = pendulum.local_timezone()


def get_default_timezone(conf=None):
    """获得默认时区 ."""
    if conf:
        tz = conf.get_default_timezone()
    else:
        tz = 'system'
    if tz == "system":
        timezone = TIMEZONE_SYSTEM
    else:
        timezone = pendulum.timezone(tz)
    return timezone


def is_localized(value):
    """存在时区信息

    Determine if a given datetime.datetime is aware.
    The concept is defined in Python's docs:
    http://docs.python.org/library/datetime.html#datetime.tzinfo
    Assuming value.tzinfo is either None or a proper datetime.tzinfo,
    value.utcoffset() implements the appropriate logic.
    """
    return value.utcoffset() is not None


def is_naive(value):
    """判断不存在时区信息

    Determine if a given datetime.datetime is naive.
    The concept is defined in Python's docs:
    http://docs.python.org/library/datetime.html#datetime.tzinfo
    Assuming value.tzinfo is either None or a proper datetime.tzinfo,
    value.utcoffset() implements the appropriate logic.
    """
    return value.utcoffset() is None


def utcnow():
    """获得当前的utc时间

    Get the current date and time in UTC
    :return:
    """

    # pendulum utcnow() is not used as that sets a TimezoneInfo object
    # instead of a Timezone. This is not pickable and also creates issues
    # when using replace()
    d = dt.datetime.utcnow()
    d = d.replace(tzinfo=TIMEZONE_UTC)

    return d


def system_now():
    """获得当前的系统时间

    Get the current date and time in UTC
    :return:
    """

    # pendulum utcnow() is not used as that sets a TimezoneInfo object
    # instead of a Timezone. This is not pickable and also creates issues
    # when using replace()
    d = dt.datetime.now()
    d = d.replace(tzinfo=TIMEZONE_SYSTEM)

    return d


def utc_epoch():
    """
    Gets the epoch in the users timezone
    :return:
    """

    # pendulum utcnow() is not used as that sets a TimezoneInfo object
    # instead of a Timezone. This is not pickable and also creates issues
    # when using replace()
    d = dt.datetime(1970, 1, 1)
    d = d.replace(tzinfo=TIMEZONE_UTC)

    return d


def convert_to_utc(value, timezone=None):
    """
    1. 给无时区的datetime对象添加默认时区信息，并转化为UTC时区
    2. 将有时区的datetime对象转化为UTC时区

    Returns the datetime with the default timezone added if timezone
    information was not associated
    :param value: datetime
    :return: datetime with tzinfo
    """
    if not value:
        return value

    # 添加默认时区
    if not is_localized(value):
        if timezone is None:
            timezone = TIMEZONE_UTC
        value = pendulum.instance(value, timezone)

    # 将当前时区转化为UTC
    return value.astimezone(TIMEZONE_UTC)


def make_aware(value, timezone=None):
    """将无时区的datetime对象，添加时区信息 

    Make a naive datetime.datetime in a given time zone aware.

    :param value: datetime
    :param timezone: timezone
    :return: localized datetime in settings.TIMEZONE or timezone

    """
    if timezone is None:
        timezone = TIMEZONE_SYSTEM

    # Check that we won't overwrite the timezone of an aware datetime.
    # 如果value已经存在时区信息，则不需要添加了，抛出一个异常
    if is_localized(value):
        raise ValueError(
            "make_aware expects a naive datetime, got %s" % value)

    if hasattr(timezone, 'localize'):
        # This method is available for pytz time zones.
        return timezone.localize(value)
    elif hasattr(timezone, 'convert'):
        # For pendulum
        return timezone.convert(value)
    else:
        # This may be wrong around DST changes!
        return value.replace(tzinfo=timezone)


def make_naive(value, timezone=None):
    """将有时区的datetime对象转为指定时区timezone，并去掉时区信息
    Make an aware datetime.datetime naive in a given time zone.

    :param value: datetime
    :param timezone: timezone
    :return: naive datetime
    """
    if timezone is None:
        timezone = TIMEZONE_SYSTEM

    # Emulate the behavior of astimezone() on Python < 3.6.
    # Since version 3.6, astimezone works with naive (timezone unawared) datetime.
    # If you still working on lower version (<=3.5), timezone unawared datetime has to be awared by calling pytz.localize()
    # 转换为指定时区
    if is_naive(value):
        raise ValueError("make_naive() cannot be applied to a naive datetime")

    o = value.astimezone(timezone)

    # 去掉时区信息
    # cross library compatibility
    naive = dt.datetime(o.year,
                        o.month,
                        o.day,
                        o.hour,
                        o.minute,
                        o.second,
                        o.microsecond)

    return naive


def system_datetime(*args, **kwargs):
    """在使用datetime创建日期时，自动加上配置文件中的时区
    Wrapper around datetime.datetime that adds settings.TIMEZONE if tzinfo not specified

    :return: datetime.datetime
    """
    if 'tzinfo' not in kwargs:
        kwargs['tzinfo'] = TIMEZONE_SYSTEM

    return dt.datetime(*args, **kwargs)


def utc_datetime(*args, **kwargs):
    """在使用datetime创建日期时，自动加上配置文件中的时区
    Wrapper around datetime.datetime that adds settings.TIMEZONE if tzinfo not specified

    :return: datetime.datetime
    """
    if 'tzinfo' not in kwargs:
        kwargs['tzinfo'] = TIMEZONE_UTC

    return dt.datetime(*args, **kwargs)


def parse(string, timezone=None):
    """将日期字符串转化为datetime对象（带有时区信息）
    Parse a time string and return an aware datetime
    :param string: time string
    """
    if timezone is None:
        timezone = TIMEZONE_SYSTEM
    return pendulum.parse(string, tz=timezone)
