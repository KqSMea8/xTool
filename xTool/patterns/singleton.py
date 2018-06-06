# -*- coding:utf-8 -*-
'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2010 Task Coach developers <developers@taskcoach.org>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


class Singleton(type):
    ''' Singleton metaclass. Use by defining the metaclass of a class Singleton,
        e.g.: class ThereCanBeOnlyOne:
                  __metaclass__ = Singleton
        ��Python 2������ͨ������������ж���metaclass
        ���������߶���һ��������༶���(class-level)__metaclass__���ԣ�������Ԫ�ࡣ��
        Python 3�__metaclass__�����Ѿ���ȡ���ˡ�

        ����Ԫ��

        instance = Singleton(class_name): ������class_name��һ��ʵ��
    '''              

    def __call__(class_, *args, **kwargs):
        # �ڶ��󴴽�ʱֱ�ӷ���__call__�����ݣ�ʹ�ø÷�������ģ�⾲̬������
        # ���ʵ�������ڣ��򴴽�ʵ��
        # ���ʵ�����ڣ���ֱ�ӷ�����ǰ������ʵ��
        if not class_.hasInstance(): # �ж���class_�Ƿ����ʵ��
            # pylint: disable-msg=W0201
            # ����һ������Ϊclass_�����ʵ��
            # �����class_û��ʵ�����򴴽�һ��ʵ��
            class_.instance = super(Singleton, class_).__call__(*args, **kwargs) # ������class_��һ��ʵ��
        # ���ش��������ʵ��
        return class_.instance

    def deleteInstance(class_):
        ''' Delete the (only) instance. This method is mainly for unittests so
            they can start with a clean slate. 
            ɾ��ʵ�������ʵ������
        '''
        if class_.hasInstance():
            del class_.instance

    def hasInstance(class_):
        ''' Has the (only) instance been created already? 
            �ж�ʵ���Ƿ����
        '''
        return hasattr(class_, 'instance')
        
