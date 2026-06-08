#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：lbu_knowledge_base 
@File    ：pdf_parse_service.py
@IDE     ：PyCharm 
@Author  ：Clark
@Date    ：2026/6/7 11:58 
"""
import shutil
import time
from pathlib import Path
from sys import exception
from typing import Tuple

import requests

from app.process.import_.agent.state import ImportGraphState
from app.shared.config import MinerUConfig
from app.shared.runtime.logger import logger, PROJECT_ROOT, step_log


@step_log("step1_validate_paths")
def step1_validate_paths(state) -> Tuple[Path,Path]:
    """
    验证路径是否存在，不存在则报异常，存在则转为Path对象返回
    :param state:
    :return:
    """
    #1 获取pdf_path local_dir
    pdf_path = state.get("pdf_path")
    local_dir = state.get("local_dir")

    #2 进行校验
    if not pdf_path:
        logger.error(f"{pdf_path}为空，无法获取pdf文件，无法继续业务")
        raise ValueError(f"{pdf_path}为空，无法获取pdf文件，无法继续业务")

    if not local_dir:
        logger.warning(f"{local_dir}为空，创建默认文件夹")
        #怎创建
        local_dir = PROJECT_ROOT / "output"
    #3 转Path
    pdf_path_obj = Path(pdf_path)
    local_dir_obj = Path(local_dir)

    #4 再次校验是否真实存在
    if not pdf_path_obj.exists():
        logger.error(f"{pdf_path}不存在对应的文件,业务无法继续!!")
        raise FileNotFoundError(f"{pdf_path}不存在对应的文件,业务无法继续!!")

    # 再次校验
    if not local_dir_obj.exists():
        logger.warning(f"进行pdf转化md,local_dir值:{local_dir_obj},但是没有对应文件夹! 我们自行创建!!")
        # parents 自动创建多层文件夹  例如: x/x/x/x  -> True会自动创建 x  x   x  x
        # exist_ok = True 当存在的时候不会创建也不会报错!
        local_dir_obj.mkdir(parents=True, exist_ok=True)

    #5 返回
    return pdf_path_obj,local_dir_obj

@step_log("step2_upload_and_poll")
def step2_upload_and_poll(pdf_path_obj):
    # upload_pdf_and_poll(pdf_path_obj: Path) -> str
    #1. 校验 MinerU 配置是否完整
    base_url = MinerUConfig.base_url
    api_key = MinerUConfig.api_key

    if not base_url or not api_key:
        logger.error(f"{base_url}或者{api_key}为空，业务无法继续")
        raise ValueError(f"{base_url}或者{api_key}为空，业务无法继续")

    #2. 调用 `/file-urls/batch` 申请上传地址与 `batch_id`
    url = f"{base_url}/file-urls/batch"
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "files": [
            {"name": f"{pdf_path_obj.stem}.pdf"}
        ],
        "model_version": "vlm"
    }

    #发起请求
    response = requests.post(url=url, headers=header, json=data)

    #先拿下状态码
    status_code = response.status_code
    #然后判断状态码是不是等于200，报异常处理
    if status_code != 200:
        logger.error(f"申请上传地址失败,状态码为{status_code}需要检查minerU的apikey等问题，业务无法继续")
        raise RuntimeError(f"申请上传地址失败,状态码为{status_code}需要检查minerU的apikey等问题，业务无法继续")
    #然后拿到response里面的另外一个码，判断是不是为0，异常处理，这个码直接查看官网看看怎么取
    result = response.json()
    if not result['code'] == 0:
        logger.error(f"申请地址网络状态成功!但是业务失败!错误码:{result['code']}需要检查minerU的apikey等问题，业务无法继续")
        raise RuntimeError(f"申请地址网络状态成功!但是业务失败!错误码:{result['code']}需要检查minerU的apikey等问题，业务无法继续")
    #如果都正常，则取出上传地址和batch_id。
    #获取batch_id
    batch_id = result["data"]["batch_id"]
    #获取上传地址
    file_upload_url = result["data"]["file_urls"][0]

    #3. 使用 `Session(trust_env=False)` 上传 PDF 文件
    #把pdf的path对象转为bytes进行网络传递
    read_bytes = pdf_path_obj.read_bytes()
    #搞一个session 纯净版来上传，不然minerU容易报错，我猜这里是踩坑了之后改进的，是用ai吗
    with requests.session() as session:
        session.trust_env = True
        #上传文件，获取返回对象
        put_response = session.put(url=file_upload_url, data=read_bytes)
        #对返回的对象的状态进行判断
        if put_response.status_code != 200:
            logger.error(f"上传文件失败,返回状态码为:{put_response.status_code},请检查minerU配置!")
            raise RuntimeError(f"上传文件失败,返回状态码为:{put_response.status_code},请检查minerU配置!")

    #4. 根据 `batch_id` 轮询任务状态
    #这里的思路也有官网代码可依，minerU的API文档批量获取文件结果代码示例粘贴过来
    #token = "API管理页面自定创建的token" #我们自己env里面有
    #batch_id = "上一步批量提交返回的 batch_id" #上面的步骤我把batch_id已经取到了
    #url = f"https://mineru.net/api/v4/extract-results/batch/{batch_id}"。#替换前面的公共部分
    poll_url = f"{base_url}/extract-results/batch/{batch_id}" #我们需要对这个地址进行轮询
    timeout = 600 #单位秒  1页pdf 0.5-1秒时间
    interval_time = 3 # 设置轮询的间隔时间
    start_time = time.time() # 当前的时间秒 浮点类型
    while True:
        #先做判断，看看是否超时
        if time.time() - start_time >= timeout:
            logger.error(f"轮询超时,请检查minerU配置!")
            raise TimeoutError(f"轮询超时,请检查minerU配置!")

        try:
            poll_response = requests.get(url, headers=header)
        except Exception as e:
            logger.warning("请求出现异常!可以稍后重试!!")
            time.sleep(interval_time)
            continue

        #我们拿到poll_response，估计要对他的状态码啊做校验，这个码我看了又看，有两个，一个是网络码，一个是业务码
        status_code = poll_response.status_code
        if status_code != 200:
            if 500 <= status_code < 600:
                #给minerU服务器机会
                logger.info("服务器发生了波动，稍后重试")
                time.sleep(interval_time)
                continue
            else:
                logger.error(f"网络异常，状态码为{status_code}")
                raise RuntimeError(f"网络异常，状态码为{status_code}")

        #判断业务码是不是等于0，这玩意要在官网上看
        result = poll_response.json()
        if result['code'] != 0:
            logger.error(f"轮询业务异常,错误码:{result['code']},失败信息:{result['msg']}")
            raise RuntimeError(f"轮询业务异常,错误码:{result['code']},失败信息:{result['msg']}")

        #响应给我们的示例（说实话，我第一次完全不知道响应回来的是这样，我压根不知道为什么这么取值，老师讲了吗我怀疑，他肯定讲了，我就是没听而已）
        """
        {
          "code": 0,
          "data": {
            "batch_id": "2bb2f0ec-a336-4a0a-b61a-241afaf9cc87",
            "extract_result": [
              {
                "file_name": "example.pdf",
                "state": "done",
                "err_msg": "",
                "full_zip_url": "https://cdn-mineru.openxlab.org.cn/pdf/018e53ad-d4f1-475d-b380-36bf24db9914.zip"
              },
              {
                "file_name": "demo.pdf",
                "state": "running",
                "err_msg": "",
                "extract_progress": {
                  "extracted_pages": 1,
                  "total_pages": 2,
                  "start_time": "2025-01-20 11:43:20"
                }
              }
            ]
          },
          "msg": "ok",
          "trace_id": "c876cd60b202f2396de1f9e39a1b0172"
        }
        """
        #获取extract_result，这是第一个文件？
        extract_result = poll_response['data']['extract_result']
        #获取这个是否完成的状态
        extract_result_state = extract_result['state']
        #做状态判断     若任务成功，返回 `full_zip_url`
        if extract_result_state == 'done':
            download_url = extract_result['full_zip_url']
            if not download_url:
                logger.error(f"已经完成了解析,但是zip地址为空!!")
                raise RuntimeError(f"已经完成了解析,但是zip地址为空!!")
            return download_url
        elif extract_result_state == 'failed':
            logger.error(f"已经完成了解析,但是失败了!!失败信息:{extract_result['err_msg']}")
            raise RuntimeError(f"已经完成了解析,但是失败了!!失败信息:{extract_result['err_msg']}")
        else:
            #任务处理状态，完成: done，
            # waiting - file: 等待文件上传排队提交解析任务中，
            # pending: 排队中，
            # running: 正在解析，
            # failed：解析失败，
            # converting：格式转换中
            logger.warning(f"解析正在进行中,状态:{extract_result_state}!")
            time.sleep(interval_time)
            continue


@step_log("step3_download_and_extract")
def step3_download_and_extract(zip_url, local_dir_path_obj, pdf_path_obj):
    """
    向获取的下载地址发送请求，下载文件，并且重命名
    :param zip_url: 
    :param local_dir_obj: 
    :param pdf_path_obj: 
    :return: 
    """
    #发请求下载文件
    response = requests.get(zip_url,timeout=30)

    #查看response的内容
    md_path_obj = local_dir_path_obj / f"{pdf_path_obj.stem}_result.zip"
    #把response的内容写入该文件
    md_path_obj.write_bytes(response.content)
    #把该文件解压
    #解压之前先把原来的文件给删掉，避免重复解压产生脏数据
    extract_path_obj = local_dir_path_obj / pdf_path_obj.stem #规定解压后的文件地址
    if md_path_obj.exists():
        #该删除方法，我不熟悉
        shutil.rmtree(extract_path_obj)
    #创建文件夹
    extract_path_obj.mkdir(parents=True,exist_ok=True)

    #解压
    shutil.unpack_archive(md_path_obj,extract_path_obj)

    #检查解压文件夹是否有md文件
    rglob = extract_path_obj.rglob(".md")
    md_file_list = list(rglob)

    #校验，到处都是校验
    if not md_file_list or len(md_file_list) == 0:
        logger.error(f"文件解压失败,在:{extract_path_obj}没有任何md文件!")
        raise FileNotFoundError(f"文件解压失败,在:{extract_path_obj}没有任何md文件!")

    #重命名
    target_md_obj = None

    #判断解压出来的文件是啥名，如果是原名直接用
    for md_file in md_file_list:
        if md_file.name == f"{pdf_path_obj.stem}.md":
            target_md_obj = md_file
            return target_md_obj
    # full.md
    for md_file in md_file_list:
        if md_file.name.lower() == "full.md":
            target_md_obj = md_file
            break

    # 随机.md
    if not target_md_obj:
        # 没有获取full.md
        # 获取第一个md文件即可
        target_md_obj = md_file_list[0]

    #改名返回
    final_md_path_obj = target_md_obj.rename(target_md_obj.with_name(f"{pdf_path_obj.stem}.md"))
    # 6. 返回md对应的Path对象即可
    return final_md_path_obj


def parse_pdf_to_markdown(state: ImportGraphState) -> ImportGraphState:
    """
    PDF 解析服务：
    1. 调用 MinerU
    2. 下载并解压解析结果
    3. 获取 Markdown 路径和正文内容
    4. 回写 md_path / md_content / local_dir
    """

    #校验pdf和输出地址
    pdf_path_obj,local_dir_path_obj = step1_validate_paths(state)
    
    #上传文件
    zip_url = step2_upload_and_poll(pdf_path_obj)
    
    #下载文件和解压
    md_path_obj = step3_download_and_extract(zip_url, local_dir_path_obj, pdf_path_obj)

    return state