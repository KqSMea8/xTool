# -*- coding: utf-8 -*-

import errno
import logging
import os

from xTool.utils.helpers import parse_template_string
from datetime import datetime


class FileProcessorHandler(logging.Handler):
    """根据日期分日期文件夹写入日志文件，并增加lastest链接 ."""

    def __init__(self, base_log_folder, filename_template, resouce_folder):
        """
        :param base_log_folder: Base log folder to place logs.
        :param filename_template: template filename string
        """
        super(FileProcessorHandler, self).__init__()
        self.handler = None
        # 日志目录
        self.base_log_folder = base_log_folder
        # 资源目录，在日志目录下先创建资源文件，在资源文件下创建时间文件夹
        self.resouce_folder = resouce_folder
        # 日志文件名的格式
        self.filename_template, self.filename_jinja_template = \
            parse_template_string(filename_template)

        self._cur_date = datetime.today()

        # 创建日志日期目录
        if not os.path.exists(self._get_log_directory()):
            try:
                os.makedirs(self._get_log_directory())
            except OSError as e:
                # only ignore case where the directory already exist
                if e.errno != errno.EEXIST:
                    raise

                logging.warning("%s already exists", self._get_log_directory())
        
        # 在日志目录中创建 latest 链接
        self._symlink_latest_log_directory()

    def set_context(self, filename):
        """
        Provide filename context to airflow task handler.
        :param filename: filename in which the dag is located
        """
        # 创建日志文件
        local_loc = self._init_file(filename)
        self.handler = logging.FileHandler(local_loc)
        self.handler.setFormatter(self.formatter)
        self.handler.setLevel(self.level)

        if self._cur_date < datetime.today():
            self._symlink_latest_log_directory()
            self._cur_date = datetime.today()

    def emit(self, record):
        if self.handler is not None:
            self.handler.emit(record)

    def flush(self):
        if self.handler is not None:
            self.handler.flush()

    def close(self):
        if self.handler is not None:
            self.handler.close()

    def _render_filename(self, filename):
        """使用文件名渲染文件名模板 ."""
        filename = os.path.relpath(filename, self.resouce_folder)
        ctx = dict()
        ctx['filename'] = filename

        if self.filename_jinja_template:
            return self.filename_jinja_template.render(**ctx)

        return self.filename_template.format(filename=ctx['filename'])

    def _get_log_directory(self):
        """获得带有日期的日志目录 ."""
        now = datetime.utcnow()
        return os.path.join(self.base_log_folder, now.strftime("%Y-%m-%d"))

    def _symlink_latest_log_directory(self):
        """
        Create symbolic link to the current day's log directory to
        allow easy access to the latest scheduler log files.

        :return: None
        """
        log_directory = self._get_log_directory()
        latest_log_directory_path = os.path.join(self.base_log_folder, "latest")
        if os.path.isdir(log_directory):
            try:
                # if symlink exists but is stale, update it
                if os.path.islink(latest_log_directory_path):
                    if os.readlink(latest_log_directory_path) != log_directory:
                        os.unlink(latest_log_directory_path)
                        os.symlink(log_directory, latest_log_directory_path)
                elif (os.path.isdir(latest_log_directory_path) or
                          os.path.isfile(latest_log_directory_path)):
                    logging.warning(
                        "%s already exists as a dir/file. Skip creating symlink.",
                        latest_log_directory_path
                    )
                else:
                    os.symlink(log_directory, latest_log_directory_path)
            except OSError:
                logging.warning("OSError while attempting to symlink "
                                "the latest log directory")

    def _init_file(self, filename):
        """
        Create log file and directory if required.
        :param filename: task instance object
        :return relative log path of the given task instance
        """
        # 渲染文件名模板
        relative_path = self._render_filename(filename)
        full_path = os.path.join(self._get_log_directory(), relative_path)
        directory = os.path.dirname(full_path)
        # 创建日志目录
        if not os.path.exists(directory):
            os.makedirs(directory)
        # 创建日志文件
        if not os.path.exists(full_path):
            open(full_path, "a").close()

        return full_path
