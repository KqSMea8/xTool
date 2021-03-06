# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import object
import imp
import inspect
import os
import re
import sys

from xTool import configuration
from xTool.utils.log.logging_mixin import LoggingMixin

log = LoggingMixin().log


class XToolPluginException(Exception):
    pass


class XToolPlugin(object):
    name = None
    operators = []
    sensors = []
    hooks = []
    executors = []
    macros = []
    admin_views = []
    flask_blueprints = []
    menu_links = []

    @classmethod
    def validate(cls):
        """验证插件必须定义name静态变量 ."""
        if not cls.name:
            raise XToolPluginException("Your plugin needs a name.")


# 获得插件目录
plugins_folder = configuration.get('core', 'plugins_folder')
if not plugins_folder:
    plugins_folder = configuration.get('core', 'airflow_home') + '/plugins'
plugins_folder = os.path.expanduser(plugins_folder)

# 将插件目录加入到系统路径中
if plugins_folder not in sys.path:
    sys.path.append(plugins_folder)

plugins = []

norm_pattern = re.compile(r'[/|.]')

# Crawl through the plugins folder to find AirflowPlugin derivatives
for root, dirs, files in os.walk(plugins_folder, followlinks=True):
    for f in files:
        try:
            # 获得插件目录下的所有文件路径
            filepath = os.path.join(root, f)
            if not os.path.isfile(filepath):
                continue
            # 判断文件的后缀是否是.py
            mod_name, file_ext = os.path.splitext(
                os.path.split(filepath)[-1])
            if file_ext != '.py':
                continue

            log.debug('Importing plugin module %s', filepath)
            # 将路径转换为命名空间
            # normalize root path as namespace
            # e.g.:
            # __data__home__user00__application__airflow__plugins_rest_api_plugin
            # mod_name 为文件名（去掉后缀）
            namespace = '_'.join([re.sub(norm_pattern, '__', root), mod_name])

            # 根据文件名加载模块
            m = imp.load_source(namespace, filepath)

            # 将所加载模块中的 XToolPlugin 子类添加到 plugins 列表中
            # 遍历模块的属性值
            for obj in list(m.__dict__.values()):
                # 判断模块中的类是否为 XToolPlugin 的子类
                if (
                        inspect.isclass(obj) and
                        issubclass(obj, XToolPlugin) and
                        obj is not XToolPlugin):
                    # 验证子类中是否定义了name静态变量
                    obj.validate()
                    # 将类加入到插件列表中
                    if obj not in plugins:
                        plugins.append(obj)

        except Exception as e:
            log.exception(e)
            log.error('Failed to import plugin %s', filepath)


def make_module(name, objects):
    """动态创建模块 .

    :param name: 模块名称
    :param objects: 模块中需要包含的对象列表
    """
    log.debug('Creating module %s', name)
    name = name.lower()
    # 创建模块
    module = imp.new_module(name)
    # 给模块设置_name属性 （插件名）
    module._name = name.split('.')[-1]
    # 给模块设置_object属性（插件中所有的类名）
    module._objects = objects
    # 给模块设置属性 （类名 => 类）
    module.__dict__.update((o.__name__, o) for o in objects)

    # 返回新创建的模块
    return module


# Plugin components to integrate as modules
operators_modules = []
sensors_modules = []
hooks_modules = []
executors_modules = []
macros_modules = []

# Plugin components to integrate directly
admin_views = []
flask_blueprints = []
menu_links = []

for p in plugins:
    # 创建新模块
    operators_modules.append(
        make_module('airflow.operators.' + p.name, p.operators + p.sensors))
    sensors_modules.append(
        make_module('airflow.sensors.' + p.name, p.sensors)
    )
    hooks_modules.append(make_module('airflow.hooks.' + p.name, p.hooks))
    executors_modules.append(
        make_module('airflow.executors.' + p.name, p.executors))
    macros_modules.append(make_module('airflow.macros.' + p.name, p.macros))

    admin_views.extend(p.admin_views)
    flask_blueprints.extend(p.flask_blueprints)
    menu_links.extend(p.menu_links)
