#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@description:
@author: borlittle
@contact:borlittle@163.com
@version: 1.0.0
@file: image_spider_multhreads.py
@time: 2020/12/20 12:48
"""
# coidng:utf-8
import requests
from bs4 import BeautifulSoup
import os
import time
import re
from concurrent.futures import ThreadPoolExecutor
from utils import *
path = 'img'


def get_image(url, filename, root_path):
    img = requests.get(url)
    if (filename[-4:] == "html"):
        filename = filename.replace("html", "jpg")
    img_path = os.path.join(root_path, filename)
    with open(img_path, "wb+") as f:
        f.write(img.content)
    # print(filename + "保存成功\n")


def get_cur_page_imgs(soup, make_dirs=False, folder=None):
    title = "/" + soup.title.string
    p = soup.find("article", {"class": "article-content"})
    img_s = p.find_all("img")

    folder_dir = os.path.join(path, get_dir_name(title))
    # print("文件夹路径：" + folder_dir)
    if (not os.path.exists(folder_dir) and make_dirs == True):  # 如果没有这个文件夹就建一个
        os.makedirs(folder_dir)

    for a in img_s:
        if a["src"] != '':
            # 读取图片的地址并且保存
            img_src = a["src"]
            # print(img_src)
            filename = img_src.split("/")[-1]
            # print(filename)
            if (folder == None):  # 如果文件夹名为None就用刚刚建的文件夹
                get_image(img_src, filename, folder_dir)
            else:  # 否则就用传入的文件夹
                get_image(img_src, filename, folder)


def get_next_img_page_address(soup, init_url):
    p = soup.find("li", {"class": "next-page"})
    if p != None:
        link_a_s = p.find_all("a")

        for each in link_a_s:
            href = each["href"]
            # print(href)

            if (href[-4:] == "html" and len(href) < 16):  # 如果下一页还有的话
                # print("该页面还有下一页，进行迭代操作")
                filename = init_url.split("/")[-1]
                init_url = init_url.replace(filename, href)
                print("下一个url：", init_url)
                # time.sleep(1)
                return init_url
        return None
    return None


def spider_one_group(init_url, make_dirs=False, folder=None):
    r = requests.get(init_url)
    r.encoding = "gbk"
    soup = BeautifulSoup(r.text, "html.parser")
    get_cur_page_imgs(soup, make_dirs, folder)
    # time.sleep(0.2)  # 休眠一秒
    return get_next_img_page_address(soup, init_url)


def get_dir_name(title):
    str_2 = title.replace('/', '').replace(':', '')
    pattern = '^(.+)\['
    res = re.findall(pattern, str_2)
    if res != []:
        name = res[0]
        # print(name)
    else:
        name = str_2
    return name


def start_down_one_group_imgs(start_url):
    print(start_url)
    init_url = start_url
    next_url = spider_one_group(init_url, make_dirs=True, folder=None)
    while (next_url != None):
        next_url = spider_one_group(next_url, make_dirs=True, folder=None)


def start_from_local_file(file_path):
    cur_dir = os.getcwd()
    file_p = os.path.join(cur_dir, file_path)
    try:
        fp = open(file_p, 'r')
        lines = fp.readlines()
        fp.close()
        for each in lines:
            url = each.strip('\n').strip(' ')
            start_down_one_group_imgs(url)
    except Exception as e:
        print(e)


def start_from_local_file_via_multhreads(file_path):
    cur_dir = os.getcwd()
    file_p = os.path.join(cur_dir, file_path)
    try:
        fp = open(file_p, 'r')
        lines = fp.readlines()
        fp.close()
        task_urls = []
        for each in lines:
            url = each.strip('\n').strip(' ')
            task_urls.append(url)


        task_count_each_turn = 10

        task_count = len(task_urls)
        threadPool = ThreadPoolExecutor(max_workers=task_count_each_turn, thread_name_prefix="test_")
        task_turn_count = task_count // task_count_each_turn
        left = task_count % task_count_each_turn
        index = 0
        for j in range(0,task_turn_count):

            for i in range(0, task_count_each_turn):
                url=task_urls[index]
                future = threadPool.submit(start_down_one_group_imgs, url)
                index += 1
            time.sleep(5)
            # threadPool.shutdown(wait=True)
        # threadPool = ThreadPoolExecutor(max_workers=task_count_each_turn, thread_name_prefix="test_")
        for i in range(0, left):
            url = task_urls[index]
            future = threadPool.submit(start_down_one_group_imgs, url)
            index += 1
        threadPool.shutdown(wait=True)
        return
    except Exception as e:
        print(e)


def start_down_groups_urls(site_base_url, start_url, file):
    if os.path.exists(file):
        try:
            os.remove(file)
        except Exception as e:
            print(e)
            print('delete file %s failed' % file)
    init_url = start_url
    next_url = spider_img_group_urls(site_base_url, init_url, file)
    while (next_url != None):
        next_url = spider_img_group_urls(site_base_url, next_url, file)


def get_next_group_page_address(soup, init_url):
    p = soup.find("li", {"class": "next-page"})
    if p != None:
        link_a_s = p.find_all("a")
        for each in link_a_s:
            href = each["href"]
            print(href)

            if (href[-4:] == "html" and len(href) < 16):  # 如果下一页还有的话
                # print("该页面还有下一页，进行迭代操作")

                if init_url[-4:] != "html":
                    init_url = init_url + href
                    print("下一个url：", init_url)
                    return init_url
                else:
                    filename = init_url.split("/")[-1]
                    init_url = init_url.replace(filename, href)
                    print("下一个url：", init_url + "\n")
                    return init_url

        return None
    return None


def spider_img_group_urls(site_base_url, init_url, file):
    r = requests.get(init_url)
    r.encoding = "gbk"
    soup = BeautifulSoup(r.text, "html.parser")

    fp = open(file, 'a')
    div = soup.find_all("article", {"class": 'excerpt excerpt-one'})
    url_list = []
    for each in div:
        hrefs = each.find_all("a")
        for item in hrefs:
            if 'htm' in item['href']:
                url = site_base_url + item['href']
                print(site_base_url + item['href'])

                if url not in url_list:
                    url_list.append(url)
                    fp.write(url)
                    fp.write('\n')
    fp.close()
    time.sleep(1)
    return get_next_group_page_address(soup, init_url)


if __name__ == "__main__":
    # 判断根目录有没有文件夹
    # exist = os.path.exists("imgs")
    # if not exist:
    #     os.makedirs("imgs")
    # url = "https://qqh52.vip/MFStar/2019/1130/8015.html"
    # start_from_local_file('urls.txt')
    # get_dir_name('[MiiTao]蜜桃社第一期爱丽莎Lisa[81P]_kjl')
    # 获取主题列表url，保存到本地
    # start_down_groups_urls('https://xx.vip', 'xxx', '1.txt')
    # 读取文件中的url，依次逐个主题下载
    start_from_local_file_via_multhreads('1.txt')
