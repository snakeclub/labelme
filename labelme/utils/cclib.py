#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2019 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
针对CC封装的通用类库
@module cclib
@file cclib.py
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import sys
import time
import copy
import xlwt
import math
import shutil
import traceback
from PIL import Image
from bs4 import BeautifulSoup, PageElement
from HiveNetLib.base_tools.file_tool import FileTool
from HiveNetLib.base_tools.string_tool import StringTool

# 生成TFRecord文件依赖的包
import io
import pandas as pd
import tensorflow as tf
import xml.etree.ElementTree as ET

from PIL import Image
from object_detection.utils import dataset_util
from collections import namedtuple, OrderedDict

# 商品信息展示的字段及排序
PRODUCT_SHOW_PROP_INFO = {
    '店名': '',
    '种地类型': '',
    '款式': '',
    '挂件类型': '',
    '颜色': '',
    '颜色1': '',
    '颜色2': '',
    '描述': ''
}

# 标准参数名转换字典
PROP_NAME_TRAN_DICT = {
    '店名': 'shop_name',
    '店铺地址': 'shop_url',
    '价格': 'price',
    '品牌': 'brand',
    '种地类型': 'species_type',
    '款式': 'type',
    '挂件类型': 'pendant_type',
    '鉴定标识': 'identify_type',
    '鉴定类别': 'identify',
    '价格区间': 'price_area',
    '颜色': 'color',
    '颜色1': 'color1',
    '颜色2': 'color2',
    '描述': 'description'
}

# 标注款式转换字典
PROP_TYPE_TRAN_DICT = {
    '手镯': 'bangle',
    '戒指': 'ring',
    '挂件': 'pendant',
    '耳饰': 'earrings',
    '手链': 'chain_bracelet',
    '项链': 'necklace',
    '原石': 'stone',
    '串珠': 'chain_beads',
    '链饰': 'chain',
    '珠子': 'beads',
    '片料': 'sheet_stock'
}

# 标准参数值转换字典
PROP_VALUE_TRAN_DICT = {
    '挂件类型': {
        '平安扣': 'ping_buckle',
        '无事牌': 'nothing_card',
        '山水牌': 'hill_water_card',
        '佛牌': 'buddha_card',
        '观音牌': 'guanyin_card',
        '葫芦': 'cucurbit',
        '如意': 'wishes',
        '蛋面': 'egg',
        '貔貅': 'pixiu',
        '福豆': 'peas',
        '福瓜': 'melon',
        '福袋': 'package',
        '佛公': 'buddha',
        '观音': 'guanyin',
        '渡母': 'dumu',
        '如来': 'rulai',
        '叶子': 'leaf',
        '白菜': 'cabbage',
        '唐马': 'horse',
    },
    '手镯类型': {
        '圆条': 'bangle_round',  # 正圆形，玉条外圈内圈都是圆的
        '正圈': 'bangle_round_flat',  # 正圆形，玉条外圈圆内圈平
        '方镯': 'bangle_flat',  # 正圆形，玉条外圈内圈都是平的
        '贵妃圆条': 'bangle_oval_round',  # 椭圆形，玉条外圈内圈都是圆的
        '贵妃': 'bangle_oval',  # 椭圆形，玉条外圈圆内圈平
        '贵妃方镯': 'bangle_oval_flat',  # 椭圆形，玉条外圈内圈都是圆的
    }
}

# 设定需要处理的分类清单，一期只处理挂件
USE_CLASS_TEXT_LIST = [
    '平安扣',
    '无事牌',
    '山水牌',
    '葫芦',
    '如意',
    '蛋面',
    '福豆',
    '福瓜',
    '佛公',
    '观音',
    '叶子',
    '福袋',
    '貔貅',
    '唐马',
    '白菜',
    '圆条',
    '正圈',
    '方镯',
    '贵妃圆条',
    '贵妃',
    '贵妃方镯',
    '戒指',
    '耳饰',
    '串珠',
    '链饰',
    '珠子',
    '片料'
]

# 分类名与int的对应关系
CLASS_TEXT_TO_INT = {
    '平安扣': 1,
    '无事牌': 2,
    '山水牌': 3,
    '葫芦': 4,
    '如意': 5,
    '蛋面': 6,
    '福豆': 7,
    '福瓜': 8,
    '佛公': 9,
    '观音': 10,
    '叶子': 11,
    '福袋': 12,
    '貔貅': 13,
    '唐马': 14,
    '白菜': 15,
    '圆条': 16,
    '正圈': 17,
    '方镯': 18,
    '贵妃圆条': 19,
    '贵妃': 20,
    '贵妃方镯': 21,
    '戒指': 22,
    '耳饰': 23,
    '串珠': 24,
    '链饰': 25,
    '珠子': 26,
    '片料': 27
}

# 不同店铺的参数名转换字典
SHOP_PROP_NAME_TRAN_DICT = {
    '兄弟翡翠挂件店': {
        '认证标识': '鉴定标识',
    }
}

# 不同店铺的产品参数转换字典
SHOP_PROP_TRAN_DICT = {
    '绿翠永恒旗舰店': {
        '款式': {
            '手镯': '手镯',
            '吊坠': '挂件',
            '戒指/指环': '戒指',
            '耳饰': '耳饰',
            '手链': '手链',
            '项链': '项链'
        },
    },
    '兄弟翡翠挂件店': {
        '款式': {
            '手镯': '手镯',
            '金镶玉': '挂件',
            '吊坠': '挂件',
            '戒指/指环': '戒指',
            '戒指': '戒指',
            '戒面': '戒指',
            '耳饰': '耳饰',
            '手链': '手链',
            '项链': '项链',
            '其他款式': '其他',
        }
    }
}

# 不同店铺的描述匹配词典
SHOP_PROP_MATCH_DICT = {
    '绿翠永恒旗舰店': {
        '颜色': {
            '飘': '飘花', '墨绿': '乌鸡', '黑': '黑', '雪': '白', '白': '白', '黄': '黄',
            '红': '红', '蓝': '蓝', '紫': '紫', '绿': '绿',
        },
        '挂件类型': {
            '平安扣': '平安扣', '无事牌': '无事牌', '山水牌': '山水牌', '佛牌': '佛牌', '观音牌': '观音牌',
            '葫芦': '葫芦', '如意': '如意', '蛋面': '蛋面', '貔貅': '貔貅',
            '福豆': '福豆', '福瓜': '福瓜', '福袋': '福袋', '如来': '如来', '佛': '佛公',
            '观音': '观音', '渡母': '渡母', '叶': '叶子'
        }
    },
    '兄弟翡翠挂件店': {
        '颜色': {
            '飘': '飘花', '墨绿': '乌鸡', '黑': '黑', '雪': '白', '白': '白', '黄': '黄',
            '红': '红', '蓝': '蓝', '紫': '紫', '绿': '绿',
        },
        '挂件类型': {
            '平安扣': '平安扣', '无事牌': '无事牌', '山水牌': '山水牌', '佛牌': '佛牌', '观音牌': '观音牌',
            '葫芦': '葫芦', '如意': '如意', '蛋面': '蛋面', '貔貅': '貔貅',
            '福豆': '福豆', '福瓜': '福瓜', '福袋': '福袋', '如来': '如来', '佛': '佛公',
            '观音': '观音', '渡母': '渡母', '叶': '叶子'
        }
    },
}

# 清除特定大小的图片
DEL_SHOP_PIC_SIZE = {
    '绿翠永恒旗舰店': [
        3122387, 288428,
    ],
    '兄弟翡翠挂件店': [
        82167, 188754, 118550, 203311,
    ],
}


class CommonLib(object):
    """
    CC通用库
    """

    #############################
    # 公共函数
    #############################
    @classmethod
    def get_product_info_dict(cls, image_file: str) -> dict:
        """
        通过图片文件路径获取商品信息字典

        @param {str} image_file - 图片文件

        @returns {dict}
        """
        _info_dict = dict()
        _path = os.path.split(image_file)[0]
        _info_file = os.path.join(_path, 'info.json')
        if os.path.exists(_info_file):
            with open(_info_file, 'rb') as f:
                _eval = str(f.read(), encoding='utf-8')
                _info = eval(_eval)
                _info_dict = copy.deepcopy(PRODUCT_SHOW_PROP_INFO)
                for _key in _info_dict:
                    if _key in _info.keys():
                        _info_dict[_key] = _info[_key]
        else:
            _info_dict['Info file not found'] = ''

        return _info_dict

    @classmethod
    def get_dom_file_list(cls, path: str):
        """
        获取指定目录下需要处理的dom文件清单

        @param {str} path - 要处理的主目录
        """
        _file_list = []
        if not os.path.exists(path):
            return _file_list

        # 遍历获取所有 dom.html 文件
        cls._get_dom_files(path, _file_list)

        return _file_list

    @classmethod
    def change_product_info_file(cls, file: str, prop_name: str, prop_value: str) -> bool:
        """
        修改指定图片的info文件

        @param {str} file - 传入图片文件或所在目录
        @param {str} prop_name - 属性名
        @param {str} prop_value - 属性值

        @returns {bool} - 处理结果
        """
        _info_file = ''
        if os.path.isdir(file):
            _info_file = os.path.join(file, 'info.json')
        else:
            _info_file = os.path.join(os.path.split(file)[0], 'info.json')

        if os.path.exists(_info_file):
            # 有信息文件才处理
            _info = dict()
            with open(_info_file, 'rb') as f:
                _eval = str(f.read(), encoding='utf-8')
                _info = eval(_eval)
            _info[prop_name] = prop_value
            # 保存JSON文件
            _json = str(_info)
            with open(_info_file, 'wb') as f:
                f.write(str.encode(_json, encoding='utf-8'))
            return True
        else:
            return False

    @classmethod
    def analyse_dom_file(cls, file: str, redo=False) -> bool:
        """
        解析dom文件，在相同目录生成info.json字典文件

        @param {str} file - dom.html文件
        @param {bool} redo - 是否要重做

        @returns {bool} - 返回处理结果
        """
        _path = os.path.split(file)[0]
        _save_path = os.path.join(_path, 'info.json')

        # 判断是否已经处理过
        if not redo and os.path.exists(_save_path):
            return True

        try:
            # 获取文件内容
            _html = ''
            with open(file, 'r', encoding='utf-8') as f:
                _html = f.read()

            # 开始解析
            _info = dict()
            _soup = BeautifulSoup(_html, 'html.parser')

            # 店铺信息
            _element = _soup.find('a', attrs={'class': 'slogo-shopname'})
            if _element is not None:
                # 天猫
                _info['店名'] = _element.strong.string
                _info['店铺地址'] = _element['href']
            else:
                # 淘宝
                _element = _soup.find('div', attrs={'class': 'tb-shop-name'})
                _info['店名'] = _element.dl.dd.strong.a['title']
                _info['店铺地址'] = _element.dl.dd.strong.a['href']

            # 价格
            _element = _soup.find('span', attrs={'class': 'tm-price'})
            if _element is not None:
                _info['价格'] = _element.string
            else:
                _element = _soup.find('strong', attrs={'id': 'J_StrPrice'})
                _info['价格'] = _element.em.next_sibling.string

            # 标准参数获取
            _prop_name_tran_dict = {}
            if _info['店名'] in SHOP_PROP_NAME_TRAN_DICT.keys():
                _prop_name_tran_dict = SHOP_PROP_NAME_TRAN_DICT[_info['店名']]

            _element = _soup.find('ul', attrs={'id': 'J_AttrUL'})
            if _element is None:
                _element = _soup.find('ul', attrs={'class': 'attributes-list'})

            for _li in _element.children:
                if _li.name != 'li':
                    continue
                # 解析文本
                _prop_str: str = _li.string
                _index = _prop_str.find(':')
                if _index == -1:
                    continue
                _prop_name = _prop_str[0:_index].strip()
                _prop_value = _prop_str[_index + 1:].strip()

                # 转换标准名
                if _prop_name in _prop_name_tran_dict.keys():
                    _prop_name = _prop_name_tran_dict[_prop_name]

                _info[_prop_name] = _prop_value

            # 各店铺自有参数获取
            if _info['店名'] in SHOP_PROP_SELF_FUN.keys():
                SHOP_PROP_SELF_FUN[_info['店名']](_soup, _info)

            # 转换标准参数值
            for _key in SHOP_PROP_TRAN_DICT[_info['店名']].keys():
                if _key in _info.keys():
                    _value = _info[_key]
                    if _value in SHOP_PROP_TRAN_DICT[_info['店名']][_key].keys():
                        _info[_key] = SHOP_PROP_TRAN_DICT[_info['店名']][_key][_value]
                    else:
                        print('%s not in SHOP_PROP_TRAN_DICT["%s"]["%s"]' % (
                            _value, _info['店名'], _key))

            # # 测试
            # print(_info)
            # return True

            # 保存JSON文件
            _json = str(_info)
            with open(_save_path, 'wb') as f:
                f.write(str.encode(_json, encoding='utf-8'))

            return True
        except:
            print('analyse_dom_file error: %s\r\n%s' % (file, traceback.format_exc()))
            return False

    @classmethod
    def product_info_to_xls(cls, path: str) -> bool:
        """
        将产品信息写入excel文件

        @param {str} path - 要获取产品信息的目录

        @returns {bool} - 处理是否成功
        """
        try:
            # 标题行
            _title = dict()
            _col = 2
            for _key in PROP_NAME_TRAN_DICT.keys():
                _title[_key] = _col
                _col += 1

            # 创建excel文件
            _xls_file = os.path.join(path, 'product_info_list.xls')
            if os.path.exists(_xls_file):
                # 删除文件
                FileTool.remove_file(_xls_file)

            # 创建一个新的Workbook
            _book = xlwt.Workbook()
            _sheet = _book.add_sheet('product_info')  # 在工作簿中新建一个表格

            # 写入标题
            _sheet.write(0, 0, '网站产品ID')
            _sheet.write(0, 1, '产品目录')
            for _word in _title.keys():
                print()
                _sheet.write(0, _title[_word], _word)

            _current_row = [1]  # 当前行

            # 逐个产品进行写入
            cls._write_product_info_to_xls(path, _sheet, _title, _current_row)

            # 保存excel
            _book.save(_xls_file)
            return True
        except:
            print('product_info_to_xls error:\r\n%s' % (traceback.format_exc(), ))
            return False

    @classmethod
    def clean_file_path(cls, path: str):
        """
        清理文件目录
        1、批量删除带括号的图片文件(重复下载)
        2、删除宣传图片
        2、将文件名修改为"产品编号_main/detail_序号"的格式
        3、将文件夹按款式进行分类

        @param {str} path - 要清理的文件夹

        @return {iter_list} - 通过yield返回的处理进度信息清单
            [总文件数int, 当前已处理文件数int, 是否成功]
        """
        try:
            _path = path
            if not (_path.endswith('/') or _path.endswith('\\')):
                _path = _path + '/'

            # 创建分类目录
            _class_path = os.path.join(
                FileTool.get_parent_dir(_path),
                FileTool.get_dir_name(_path) + '_class'
            )
            if not os.path.exists(_class_path):
                FileTool.create_dir(_class_path, exist_ok=True)

            # 获取目录清单
            _dir_list = cls._get_child_dir_list(path, with_root=True)
            _total = len(_dir_list)
            _deal_num = 0

            # 先返回进度情况
            if _total == 0:
                yield [_deal_num, _total, True]
                return

            # 遍历目录执行处理
            for _dir in _dir_list:
                yield [_deal_num, _total, True]
                cls._clean_file_path(_dir, _class_path)
                _deal_num += 1

            yield [_deal_num, _total, True]
        except:
            print('clean_file_path error: %s\r\n%s' % (path, traceback.format_exc()))
            yield [-1, -1, False]

    #############################
    # 内部函数
    #############################
    @classmethod
    def _get_dom_files(cls, path: str, files: list):
        """
        获取指定目录下的所有dom.html文件

        @param {str} path - 路径
        @param {list} files - 找到的文件清单
        """
        # 先找当前目录下的文件
        _temp_list = FileTool.get_filelist(path, regex_str=r'^dom\.html$', is_fullname=True)
        files.extend(_temp_list)

        # 遍历所有子目录获取文件
        _dirs = FileTool.get_dirlist(path)
        for _dir in _dirs:
            cls._get_dom_files(_dir, files)

    @classmethod
    def _get_match_info(cls, _str: str, match_list: dict) -> list:
        """
        从字符串中获取match_list对应的字符

        @param {str} _str - 要匹配的字符串
        @param {dict} match_list - 比较清单

        @returns {list} - 按顺序匹配到的字符
        """
        _list = []
        for _matc_str in match_list.keys():
            if _str.find(_matc_str) != -1:
                _list.append(match_list[_matc_str])

        return _list

    @classmethod
    def _write_product_info_to_xls(cls, path: str, sheet, title: dict, current_row: list):
        """
        按目录逐个将产品信息写入excel文件>

        @param {str} path - 要处理的目录
        @param {object} sheet - excel的sheet对象
        @param {dict} title - 标题清单
        @param {list} current_row - 当前行
        """
        # 先处理自己
        _info_file = os.path.join(path, 'info.json')
        if os.path.exists(_info_file):
            # 有信息文件才处理
            _info = dict()
            with open(_info_file, 'rb') as f:
                _eval = str(f.read(), encoding='utf-8')
                _info = eval(_eval)

            # 产品编号和产品目录
            _product_num = FileTool.get_dir_name(path)
            sheet.write(current_row[0], 0, _product_num)
            sheet.write(current_row[0], 1, path)

            # 逐个信息项写入
            for _key in _info.keys():
                if _key in title.keys():
                    sheet.write(current_row[0], title[_key], _info[_key])
                else:
                    # 要新增列标题
                    _col = len(title) + 2
                    title[_key] = _col
                    sheet.write(0, _col, _key)
                    # 写入信息值
                    sheet.write(current_row[0], _col, _info[_key])

            # 换到下一行
            current_row[0] += 1

        # 处理子目录
        _dirs = FileTool.get_dirlist(path)
        for _dir in _dirs:
            cls._write_product_info_to_xls(_dir, sheet, title, current_row)

    @classmethod
    def _get_child_dir_list(cls, path: str, with_root: bool = True) -> list:
        """
        获取目录及子目录清单
        (保证顺序为先子目录，再父目录)

        @param {str} path - 开始目录
        @param {bool} with_root=True - 是否包含当前目录

        @returns {list} - 文件夹清单
        """
        _list = []

        for _dir in FileTool.get_dirlist(path):
            _temp_list = cls._get_child_dir_list(_dir, with_root=True)
            _list.extend(_temp_list)

        if with_root:
            _list.append(path)

        return _list

    @classmethod
    def _clean_file_path(cls, path: str, class_path: str):
        """
        清理当前目录文件

        @param {str} path - 要处理的目录地址
        @param {str} class_path - 类目录
        """
        # 处理自身目录，先获取商品信息
        _info = dict()
        _info_file = os.path.join(path, 'info.json')
        if os.path.exists(_info_file):
            with open(_info_file, 'rb') as f:
                _eval = str(f.read(), encoding='utf-8')
                _info = eval(_eval)

            # 判断是否不处理
            _shop_name = _info['店名']
            # if _info['款式'] == '挂件' and _info['挂件类型'] == '':
            #     return

            # 遍历文件进行处理
            _product_num = FileTool.get_dir_name(path)
            _files = FileTool.get_filelist(path)
            _order = 1
            for _file in _files:
                _file_ext = FileTool.get_file_ext(_file).lower()
                if _file_ext not in ['jpg', 'jpeg', 'png', 'bmp']:
                    # 不是合适的文件类型
                    continue

                # 判断是否有括号
                if _file.find('(') >= 0:
                    FileTool.remove_file(_file)
                    continue

                # 判断是否匹配上要删除的图片大小
                if _shop_name in DEL_SHOP_PIC_SIZE.keys() and os.path.getsize(_file) in DEL_SHOP_PIC_SIZE[_shop_name]:
                    FileTool.remove_file(_file)
                    continue

                # 修改文件名
                if not FileTool.get_file_name(_file).startswith(_product_num):
                    os.rename(
                        _file, os.path.join(
                            path, '%s_%s_%d.%s' % (
                                _product_num,
                                'main' if _file.find('主图') >= 0 or _file.find(
                                    'main') >= 0 else 'detail',
                                _order, _file_ext
                            )
                        )
                    )

                # 下一个文件
                _order += 1

            # 移动文件夹到指定的分类目录
            _class_path = _info['款式']
            if _class_path in PROP_TYPE_TRAN_DICT.keys():
                _class_path = PROP_TYPE_TRAN_DICT[_info['款式']]
            shutil.move(
                path,
                os.path.join(class_path, _class_path, _product_num)
            )

        # 处理完成，返回
        return

    @classmethod
    def _get_prop_self_lcyh(cls, soup: BeautifulSoup, info: dict):
        """
        获取属性的自有方法
        (绿翠永恒旗舰店)

        @param {BeautifulSoup} soup - 页面解析对象
        @param {dict} info - 返回的字典
        """
        # 获取描述页面
        _element: PageElement = soup.find('div', attrs={'id': 'description'})
        _spans = _element.find_all('span')
        _desc_list = []
        for _span in _spans:
            if _span.string is None:
                continue
            _desc = _span.string.strip()
            _desc_list.append(_desc)
            if _desc.startswith('【描述】'):
                for _key in SHOP_PROP_MATCH_DICT['绿翠永恒旗舰店'].keys():
                    _match = cls._get_match_info(
                        _desc, SHOP_PROP_MATCH_DICT['绿翠永恒旗舰店'][_key]
                    )
                    if len(_match) > 1 and _key == '颜色' and _match[0] == '飘花':
                        # 飘花，有两种颜色
                        info[_key] = _match[0]
                        info['颜色1'] = _match[1]
                        if len(_match) > 2:
                            info['颜色2'] = _match[2]
                    else:
                        if len(_match) > 0:
                            info[_key] = _match[0]
                        else:
                            info[_key] = ''

            elif _desc.startswith('【产地】'):
                info['产地'] = _desc[4:].strip()

        # 添加描述
        info['描述'] = '\n'.join(_desc_list)

    @classmethod
    def _get_prop_self_xdfcgjd(cls, soup: BeautifulSoup, info: dict):
        """
        获取属性的自有方法
        (兄弟翡翠挂件店)

        @param {BeautifulSoup} soup - 页面解析对象
        @param {dict} info - 返回的字典
        """
        # 获取描述页面
        _element: PageElement = soup.find('div', attrs={'id': 'J_DivItemDesc'})

        # 获取详细描述
        _desc_list = []
        for _p in _element.children:
            if _p.name != 'p':
                continue
            if _p.span is not None and _p.span.span is not None:
                _str = ''
                for _font in _p.span.span.children:
                    if _font.string is not None:
                        _str += _font.string
                _desc_list.append(_str)

        # 添加描述
        info['描述'] = '\n'.join(_desc_list)

        # 根据描述获取信息
        for _key in SHOP_PROP_MATCH_DICT['兄弟翡翠挂件店'].keys():
            _match = cls._get_match_info(
                info['描述'], SHOP_PROP_MATCH_DICT['兄弟翡翠挂件店'][_key]
            )
            if len(_match) > 1 and _key == '颜色' and _match[0] == '飘花':
                # 飘花，有两种颜色
                info[_key] = _match[0]
                info['颜色1'] = _match[1]
                if len(_match) > 2:
                    info['颜色2'] = _match[2]
            else:
                if len(_match) > 0:
                    info[_key] = _match[0]
                else:
                    info[_key] = ''


# 不同店铺的个性获取私有函数
SHOP_PROP_SELF_FUN = {
    '绿翠永恒旗舰店': CommonLib._get_prop_self_lcyh,
    '兄弟翡翠挂件店': CommonLib._get_prop_self_xdfcgjd,
}


class TFRecordCreater(object):
    """
    生成TFRecord文件格式的方法
    """
    @classmethod
    def create_cc_type_pbtxt(cls, save_path: str) -> bool:
        """
        创建CC的款式labelmap.pbtxt文件

        @param {str} save_path - 文件保存路径

        @return {bool} - 处理结果
        """
        try:
            _fix_str = "item {\n    id: %d\n    name: '%s'\n}"
            _list = []
            # 只处理所设定的分类
            for _type in USE_CLASS_TEXT_LIST:
                _id = CLASS_TEXT_TO_INT[_type]
                _name = ''
                if _type in PROP_TYPE_TRAN_DICT.keys():
                    _name = PROP_TYPE_TRAN_DICT[_type]
                else:
                    for _dict_key in PROP_VALUE_TRAN_DICT.keys():
                        if _type in PROP_VALUE_TRAN_DICT[_dict_key].keys():
                            _name = PROP_VALUE_TRAN_DICT[_dict_key][_type]
                            break

                _list.append(_fix_str % (_id, _name))

            # 保存到文件中
            FileTool.create_dir(save_path, exist_ok=True)
            with open(os.path.join(save_path, 'labelmap.pbtxt'), 'wb') as f:
                f.write(str.encode('\n\n'.join(_list), encoding='utf-8'))

            return True
        except:
            print('create_cc_type_pbtxt error: \r\n%s' % (traceback.format_exc(),))
            return False

    @classmethod
    def labelimg_to_tfrecord(cls, input_path: str, output_file: str, num_per_file: int = None,
                             class_to_int_fun=None, is_cc: bool = False, copy_img_path=None):
        """
        将LabelImg标注后的图片目录转换为TFRecord格式文件

        @param {str} input_path - 输入图片清单目录，注意labelimg标注的xml与图片文件在一个目录中
        @param {str} output_file - 输出的TFRecord格式文件路径（含文件名，例如xx.record）
        @param {int} num_per_file=None - 拆分每个TFRecord文件的文件大小
        @param {function} class_to_int_fun=None - 将分类名转换为int的函数
            如果传None代表类名为数字，可以直接将类名转换为数字
        @param {bool} is_cc=False - 是否CC项目的处理
        @param {str} copy_img_path=None - 如果传值了则复制对应的图片到对应目录

        @returns {iter_list} - 通过yield返回的处理进度信息清单
            [总文件数int, 当前已处理文件数int, 是否成功]
        """
        try:
            # 遍历所有文件夹，获取需要处理的文件数量
            _file_list = cls._get_labelimg_annotation_file_list(input_path)
            _total = len(_file_list)
            _deal_num = 0

            # 先返回进度情况
            if _total == 0:
                yield [_deal_num, _total, True, {}]
                return

            # 基础变量
            _output_file = output_file
            _current_package = 1  # 当前包序号
            _package_file_num = 0  # 当前包文件数量
            _total_pkg_num = 1  # 包总数量
            if num_per_file is not None:
                _total_pkg_num = math.ceil(_total / num_per_file)
                _output_file = '%s-%.5d-of-%.5d' % (output_file, _current_package, _total_pkg_num)

            # 创建文件夹
            FileTool.create_dir(os.path.split(_output_file)[0], exist_ok=True)

            if copy_img_path is not None:
                FileTool.create_dir(copy_img_path, exist_ok=True)

            # 标签的统计信息
            _flags_count = dict()

            # TFRecordWriter
            _writer = tf.io.TFRecordWriter(_output_file)

            # 遍历文件进行处理
            _writer_closed = False
            for _file in _file_list:
                # 当前进展
                yield [_deal_num, _total, True, _flags_count]

                # 写入当前文件
                _tf_example = cls._create_labelimg_tf_example(
                    _file, class_to_int_fun=class_to_int_fun, is_cc=is_cc,
                    copy_img_path=copy_img_path, flags_count=_flags_count
                )
                _deal_num += 1

                if _tf_example is not None:
                    _writer.write(_tf_example.SerializeToString())
                    _package_file_num += 1
                else:
                    # 没有找到写入信息，直接下一个
                    continue

                if num_per_file is not None:
                    if _package_file_num >= num_per_file:
                        # 一个文件数据已写够
                        _writer.close()
                        if _current_package >= _total_pkg_num:
                            # 已经是最后一个包
                            _writer_closed = True
                            break
                        else:
                            # 要处理下一个包
                            _current_package += 1
                            _package_file_num = 0
                            _output_file = '%s-%.5d-of-%.5d' % (output_file,
                                                                _current_package, _total_pkg_num)
                            _writer = tf.io.TFRecordWriter(_output_file)

            # 最后的保存
            if not _writer_closed:
                _writer.close()

            # 返回结果
            yield [_total, _total, True, _flags_count]
        except:
            print('labelimg_to_tfrecord error: %s\r\n%s' % (input_path, traceback.format_exc()))
            yield [-1, -1, False, {}]

    @classmethod
    def labelimg_flags_count(cls, input_path: str):
        """
        统计指定目录中的labelimg标记对应标签的数量

        @param {str} input_path - 要统计的目录

        @returns {iter_list} - 通过yield返回的处理进度信息清单
            [总文件数int, 当前已处理文件数int, 是否成功, 统计结果字典(标签名, 数量)]
        """
        try:
            # 遍历所有文件夹，获取需要处理的文件数量
            _file_list = cls._get_labelimg_annotation_file_list(input_path)
            _total = len(_file_list)
            _deal_num = 0
            _flags_count = dict()

            # 先返回进度情况
            if _total == 0:
                yield [_deal_num, _total, True, _flags_count]
                return

            # 遍历文件进行处理
            for _file in _file_list:
                # 当前进展
                yield [_deal_num, _total, True, _flags_count]

                # 统计当前文件
                _tree = ET.parse(_file)
                _root = _tree.getroot()
                # 逐个标签处理
                for _member in _root.findall('object'):
                    _member_class = _member[0].text
                    if _member_class == '翡翠':
                        # 需要转换为当前类型
                        _info_file = os.path.join(os.path.split(_file)[0], 'info.json')
                        _info = dict()
                        with open(_info_file, 'rb') as f:
                            _eval = str(f.read(), encoding='utf-8')
                            _info = eval(_eval)

                        if _info['款式'] == '挂件':
                            # 挂件，需要二级分类
                            _member_class = _info['挂件类型']
                        else:
                            # 一级分类
                            _member_class = _info['款式']

                    if _member_class in _flags_count.keys():
                        _flags_count[_member_class] += 1
                    else:
                        _flags_count[_member_class] = 1

            # 返回结果
            yield [_total, _total, True, _flags_count]
        except:
            print('labelimg_flags_count error: %s\r\n%s' % (input_path, traceback.format_exc()))
            yield [-1, -1, False]

    @classmethod
    def labelimg_copy_flags_pics(cls, input_path: str, output_path: str, is_cc: bool = False):
        """
        按类别复制图片和标注文件到指定目录

        @param {str} input_path - 图片路径
        @param {str} output_path - 输出路径
        @param {bool} is_cc=False - 是否CC项目

        @returns {iter_list} - 通过yield返回的处理进度信息清单
            [总文件数int, 当前已处理文件数int, 是否成功]
        """
        try:
            # 遍历所有文件夹，获取需要处理的文件数量
            _file_list = cls._get_labelimg_annotation_file_list(input_path)
            _total = len(_file_list)
            _deal_num = 0

            # 先返回进度情况
            if _total == 0:
                yield [_deal_num, _total, True]
                return

            # 创建复制文件夹
            FileTool.create_dir(output_path, exist_ok=True)

            # 遍历处理
            for _file in _file_list:
                # 当前进展
                yield [_deal_num, _total, True]

                # 逐个标注文件进行处理
                _tree = ET.parse(_file)
                _root = _tree.getroot()

                _annotations = dict()
                _annotations['filename'] = _root.find('filename').text
                _annotations['file_path'] = os.path.join(
                    os.path.split(_file)[0], _annotations['filename']
                )

                # 逐个标签处理
                _save_class_path = ''  # 要保存到的分类路径
                _is_copy = False  # 标注是否已复制文件
                _is_change_class = False  # 标注是否有修改分类名
                _new_xml_name = ''  # 新的xml名
                for _member in _root.findall('object'):
                    _member_class = _member[0].text
                    if is_cc:
                        # CC专属的类型转换
                        if _member_class == '翡翠':
                            # 需要获取真实的信息
                            _info_file = os.path.join(os.path.split(_file)[0], 'info.json')
                            _info = dict()
                            with open(_info_file, 'rb') as f:
                                _eval = str(f.read(), encoding='utf-8')
                                _info = eval(_eval)

                            if _info['款式'] == '挂件':
                                # 挂件，需要二级分类
                                _member_class = _info['挂件类型']
                            else:
                                # 一级分类
                                _member_class = _info['款式']

                            # 变更分类名
                            _member[0].text = _member_class
                            _is_change_class = True

                        # 过滤不需要的类别
                        if _member_class not in USE_CLASS_TEXT_LIST:
                            _deal_num += 1
                            continue

                        # 保存分类路径
                        _save_class_path = os.path.join(
                            output_path, cls._cc_get_class_text(_member_class)
                        )
                    else:
                        # 普通分类
                        _save_class_path = os.path.join(
                            output_path, _member_class
                        )

                    # 复制文件
                    if not _is_copy:
                        # 处理重复文件名
                        _file_name = FileTool.get_file_name_no_ext(_annotations['filename'])
                        _file_ext = FileTool.get_file_ext(_annotations['filename'])
                        _rename_num = 1
                        _new_file_name = '%s.%s' % (_file_name, _file_ext)
                        _new_xml_name = '%s.xml' % (_file_name, )
                        while os.path.exists(os.path.join(_save_class_path, _new_file_name)):
                            _new_file_name = '%s_%d.%s' % (_file_name, _rename_num, _file_ext)
                            _new_xml_name = '%s_%d.xml' % (_file_name, _rename_num)
                            _rename_num += 1

                        # 创建文件夹
                        FileTool.create_dir(_save_class_path, exist_ok=True)
                        shutil.copyfile(
                            _annotations['file_path'],
                            os.path.join(_save_class_path, _new_file_name)
                        )

                        _is_copy = True

                if _is_copy:
                    # 有复制文件
                    if _is_change_class:
                        # 有修改xml内容
                        _tree.write(
                            os.path.join(_save_class_path, _new_xml_name),
                            encoding='utf-8', method="xml",
                            xml_declaration=None
                        )
                    else:
                        shutil.copyfile(
                            _file,
                            os.path.join(_save_class_path, _new_xml_name)
                        )

                # 继续循环处理
                _deal_num += 1

            # 返回结果
            yield [_total, _total, True]
        except:
            print('labelimg_copy_flags_pics error: %s\r\n%s' % (input_path, traceback.format_exc()))
            yield [-1, -1, False]

    @classmethod
    def labelimg_rename_filename(cls, path: str, fix_len: int = 10):
        """
        重名名labelimg对应目录下的文件名（图片文件和标注文件同步修改）

        @param {str} path - 要修改文件名的路径
        @param {int} fix_len=10 - 文件名长度
        """
        _path = os.path.realpath(path)
        _files = FileTool.get_filelist(path=_path, is_fullname=False)
        _index = 1
        for _file in _files:
            _file_ext = FileTool.get_file_ext(_file)
            if _file_ext == 'xml':
                # 标签文件不处理
                continue

            _file_no_ext = FileTool.get_file_name_no_ext(_file)
            # 获取最新的文件名
            while True:
                _new_name = StringTool.fill_fix_string(str(_index), fix_len, '0', left=True)
                _new_file = _new_name + '.' + _file_ext
                _index += 1
                if os.path.exists(os.path.join(path, _new_file)):
                    # 文件名已存在
                    _index += 1
                    continue

                # 文件名不存在，跳出循环
                break

            # 修改文件名
            os.rename(
                os.path.join(_path, _file), os.path.join(_path, _new_file)
            )
            if os.path.exists(os.path.join(_path, _file_no_ext + '.xml')):
                # 需要修改标签文件
                _xml_file = _new_name + '.xml'
                os.rename(
                    os.path.join(_path, _file_no_ext + '.xml'), os.path.join(_path, _xml_file)
                )

                # 修改标签文件内容
                _tree = ET.parse(os.path.join(_path, _xml_file))
                _root = _tree.getroot()
                _root.find('filename').text = _new_file
                _root.find('path').text = os.path.join(_path, _new_file)
                _tree.write(
                    os.path.join(_path, _xml_file),
                    encoding='utf-8', method="xml",
                    xml_declaration=None
                )

    @classmethod
    def labelimg_del_not_rgb_pic(cls, path: str):
        """
        删除位深不为RGB三通道的图片
        （解决image_size must contain 3 elements[4]报错）

        @param {str} path - 要处理的路径
        """
        _path = os.path.realpath(path)
        # 遍历所有子目录
        _sub_dirs = FileTool.get_dirlist(path=_path, is_fullpath=True)
        for _dir in _sub_dirs:
            # 递归删除子目录的信息
            cls.labelimg_del_not_rgb_pic(_dir)

        # 检查自己目录下的图片
        _files = FileTool.get_filelist(path=_path, is_fullname=False)
        for _file in _files:
            _file_ext = FileTool.get_file_ext(_file)
            if _file_ext == 'xml':
                # 标签文件不处理
                continue

            # 打开图片判断位深
            _fp = open(os.path.join(_path, _file), 'rb')
            _img = Image.open(_fp)
            if _img.mode != 'RGB':
                # 需要删除掉
                _fp.close()
                _img_file = os.path.join(_path, _file)
                _xml_file = os.path.join(_path, FileTool.get_file_name_no_ext(_file) + '.xml')
                print('delete %s' % _img_file)
                FileTool.remove_file(_img_file)
                if os.path.exists(_xml_file):
                    FileTool.remove_file(_xml_file)
            else:
                _fp.close()

    #############################
    # 内部函数
    #############################
    @classmethod
    def _cc_get_class_text(cls, annotation_class: str) -> str:
        """
        获取CC的分类文本（从中文转换为英文）

        @param {str} annotation_class - 标注的分类文本（中文）

        @returns {str} - 返回CC对应的标注文本
        """
        if annotation_class in PROP_TYPE_TRAN_DICT.keys():
            # 中文转英文
            return PROP_TYPE_TRAN_DICT[annotation_class]
        elif annotation_class in PROP_VALUE_TRAN_DICT['手镯类型'].keys():
            return PROP_VALUE_TRAN_DICT['手镯类型'][annotation_class]
        elif annotation_class in PROP_VALUE_TRAN_DICT['挂件类型'].keys():
            # 挂件中文转英文
            return PROP_VALUE_TRAN_DICT['挂件类型'][annotation_class]
        else:
            # 原样返回
            return annotation_class

    @classmethod
    def _cc_get_class_text_int(cls, class_text: str) -> int:
        """
        根据英文的分类名获取对应的int值

        @param {str} class_text - 分类名（英文）

        @returns {int} - 对应的int值
        """
        _type = cls._get_keys_by_value(PROP_TYPE_TRAN_DICT, class_text)
        if _type is None:
            for _dict_type in PROP_VALUE_TRAN_DICT.keys():
                _type = cls._get_keys_by_value(PROP_VALUE_TRAN_DICT[_dict_type], class_text)
                if _type is not None:
                    break

        return CLASS_TEXT_TO_INT[_type]

    @classmethod
    def _get_keys_by_value(cls, d: dict, value):
        """
        根据字典的值获取key

        @param {dict} d - 字典
        @param {str} value - 值
        """
        for _key in d.keys():
            if d[_key] == value:
                return _key

        # 找不到
        return None

    @classmethod
    def _get_labelimg_annotation_file_list(cls, input_path: str) -> list:
        """
        获取要处理的LabelImg标注文件清单

        @param {str} input_path - 起始目录

        @returns {list} - 返回文件清单
        """
        _list = []

        # 先获取当前目录下的所有xml文件
        for _file in FileTool.get_filelist(input_path, regex_str=r'.*\.xml$'):
            _pic_file = _file[0:-3] + 'jpg'
            if os.path.exists(_pic_file):
                _list.append(_file)

        # 获取子目录
        for _dir in FileTool.get_dirlist(input_path):
            _temp_list = cls._get_labelimg_annotation_file_list(_dir)
            _list.extend(_temp_list)

        return _list

    @classmethod
    def _create_labelimg_tf_example(cls, annotation_file: str, class_to_int_fun=None,
                                    is_cc: bool = False,
                                    copy_img_path: str = None,
                                    flags_count: dict = {}) -> tf.train.Example:
        """
        生成指定标注的Example对象

        @param {str} annotation_file - 标注xml文件
        @param {function} class_to_int_fun=None - 将分类名转换为int的函数
            如果传None代表类名为数字，可以直接将类名转换为数字
        @param {bool} is_cc=False - 是否CC项目的处理
        @param {str} copy_img_path=None - 如果传值了则复制对应的图片到对应目录
        @param {dict} flags_count={} - 标签统计信息

        @returns {tf.train.Example} - Example对象
        """
        # 获取标注文件信息
        _tree = ET.parse(annotation_file)
        _root = _tree.getroot()
        _annotations = dict()
        _annotations['filename'] = _root.find('filename').text
        _annotations['file_path'] = os.path.join(
            os.path.split(annotation_file)[0], _annotations['filename']
        )
        _annotations['width'] = int(_root.find('size')[0].text)
        _annotations['height'] = int(_root.find('size')[1].text)

        # 图片文件二进制处理
        with tf.io.gfile.GFile(_annotations['file_path'], 'rb') as fid:
            _encoded_jpg = fid.read()
        _encoded_jpg_io = io.BytesIO(_encoded_jpg)
        _image = Image.open(_encoded_jpg_io)
        _width, _height = _image.size

        # 处理信息要素
        _filename = _annotations['filename'].encode('utf8')
        _image_format = b'jpg'
        _xmins = []
        _xmaxs = []
        _ymins = []
        _ymaxs = []
        _classes_text = []
        _classes = []

        # 逐个标签处理
        for _member in _root.findall('object'):
            _member_class = _member[0].text
            _class_int = 0
            if is_cc:
                # CC专属的类型转换
                if _member_class == '翡翠':
                    # 需要获取真实的信息
                    _info_file = os.path.join(os.path.split(annotation_file)[0], 'info.json')
                    _info = dict()
                    with open(_info_file, 'rb') as f:
                        _eval = str(f.read(), encoding='utf-8')
                        _info = eval(_eval)

                    if _info['款式'] == '挂件':
                        # 挂件，需要二级分类
                        _member_class = _info['挂件类型']
                    else:
                        # 一级分类
                        _member_class = _info['款式']

                if _member_class in USE_CLASS_TEXT_LIST:
                    _member_class = cls._cc_get_class_text(_member_class)
                    _class_int = cls._cc_get_class_text_int(_member_class)
                else:
                    # 不在处理清单的标签，不处理
                    if _member_class in flags_count.keys():
                        flags_count[_member_class] -= 1
                    else:
                        flags_count[_member_class] = -1
                    continue
            else:
                if class_to_int_fun is None:
                    _class_int = int(_member_class)
                else:
                    _class_int = class_to_int_fun(_member_class)

            _xmins.append(int(_member[4][0].text) / _width)
            _xmaxs.append(int(_member[4][2].text) / _width)
            _ymins.append(int(_member[4][1].text) / _height)
            _ymaxs.append(int(_member[4][3].text) / _height)
            _classes_text.append(_member_class.encode('utf8'))
            _classes.append(_class_int)
            if _member_class in flags_count.keys():
                flags_count[_member_class] += 1
            else:
                flags_count[_member_class] = 1

        if len(_classes_text) == 0:
            # 没有找到适用的内容，返回None
            return None
        else:
            # 复制文件
            # print(_annotations['file_path'])
            if copy_img_path is not None:
                shutil.copyfile(
                    annotation_file,
                    os.path.join(copy_img_path, os.path.split(annotation_file)[1])
                )
                shutil.copyfile(
                    _annotations['file_path'],
                    os.path.join(copy_img_path, _annotations['filename'])
                )

        tf_example = tf.train.Example(features=tf.train.Features(feature={
            'image/height': dataset_util.int64_feature(_height),
            'image/width': dataset_util.int64_feature(_width),
            'image/filename': dataset_util.bytes_feature(_filename),
            'image/source_id': dataset_util.bytes_feature(_filename),
            'image/encoded': dataset_util.bytes_feature(_encoded_jpg),
            'image/format': dataset_util.bytes_feature(_image_format),
            'image/object/bbox/xmin': dataset_util.float_list_feature(_xmins),
            'image/object/bbox/xmax': dataset_util.float_list_feature(_xmaxs),
            'image/object/bbox/ymin': dataset_util.float_list_feature(_ymins),
            'image/object/bbox/ymax': dataset_util.float_list_feature(_ymaxs),
            'image/object/class/text': dataset_util.bytes_list_feature(_classes_text),
            'image/object/class/label': dataset_util.int64_list_feature(_classes),
        }))

        return tf_example


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # CommonLib.analyse_dom_file(r'D:\ccproject\绿翠永恒旗舰店\606401921833\dom.html')

    # 复制标注文件到分类中
    # _progress = TFRecordCreater.labelimg_copy_flags_pics(
    #     r'E:\ccproject\xdfcgjd_class', r'D:\ccproject\train_set', is_cc=True
    # )

    # _end = None
    # for _p in _progress:
    #     _end = _p

    # print(_end)

    # 生成pbtxt文件
    # _result = TFRecordCreater.create_cc_type_pbtxt(
    #     r'D:\ccproject\ssd_mobilenet_v2')
    # print('create_cc_type_pbtxt %s' % str(_result))

    # _result = TFRecordCreater.create_cc_type_pbtxt(
    #     '/home/ubuntu18/cc/training/ssd_mobilenet_v2/00001/')
    # print('create_cc_type_pbtxt %s' % str(_result))

    # 生成tfrecord文件
    # _progress = TFRecordCreater.labelimg_to_tfrecord(
    #     r'D:\ccproject\ssd_mobilenet_v2\test_set_00001',
    #     output_file=r'D:\ccproject\ssd_mobilenet_v2\tfrecord_00001/test_set_00001.record',
    #     num_per_file=None, is_cc=True,
    #     # copy_img_path='/home/ubuntu18/cc/temp1/copy_img/'
    # )
    # _end = None
    # for _p in _progress:
    #     _end = _p

    # print(_end)

    # _progress = TFRecordCreater.labelimg_to_tfrecord(
    #     r'D:\ccproject\ssd_mobilenet_v2\train_set_00001',
    #     output_file=r'D:\ccproject\ssd_mobilenet_v2\tfrecord_00001/train_set_00001.record',
    #     num_per_file=None, is_cc=True,
    #     # copy_img_path='/home/ubuntu18/cc/temp1/copy_img/'
    # )
    # _end = None
    # for _p in _progress:
    #     _end = _p

    # print(_end)

    # _progress = TFRecordCreater.labelimg_to_tfrecord(
    #     '/home/ubuntu18/cc/temp1',
    #     output_file='/home/ubuntu18/cc/training/ssd_mobilenet_v2/00001/ssd_m_class.record',
    #     num_per_file=200, is_cc=True,
    #     # copy_img_path='/home/ubuntu18/cc/temp1/copy_img/'
    # )
    # _end = None
    # for _p in _progress:
    #     _end = _p

    # print(_end)

    # TFRecordCreater.labelimg_rename_filename(
    #     r'D:\ccproject\ssd_mobilenet_v2\train_set_00001\bangle_oval_flat')

    TFRecordCreater.labelimg_del_not_rgb_pic(
        r'D:\ccproject\ssd_mobilenet_v2\train_set_00001')
