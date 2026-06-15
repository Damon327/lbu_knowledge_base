import os
from pathlib import Path
from typing import re

from app.processor.import_process.base import BaseNode, T
from app.processor.import_process.config import get_config
from app.processor.import_process.exceptions import FileProcessingError
from app.processor.import_process.state import ImportGraphState


class MdImageNode(BaseNode):

    def process(self, state: ImportGraphState) -> ImportGraphState:

        #1、获取数据。已经pdf文件已经转为md文件存在了md_path
        md_content,md_path_obj,image_path = self.get_md_content(state)

        #1.2验证是否存在图片
        if not image_path.exists():
            state['md_content'] = md_content
            return state

        #2、获取图片上下文
        target_images_context = self.get_images_context(md_content, image_path)

        #3、用视觉语言模型VLM生成图片摘要
        image_summaries = self.create_image_summary(md_path_obj, target_images_context)

        #4、获取图片，把图片存如minIO

        #5、更新md里面图片内容，包含摘要+文件访问地址
        new_md_content = self.upload_img_update_md(md_path_obj,md_content,image_summaries,target_images_context)
        #6、更新state数据返回
        state['md_content'] = new_md_content
        return state

    def get_md_content(self, state):
        #获取md的路径
        md_path = state.get("md_path")
        #转为Path对象
        md_path_obj = Path(md_path)
        #判断文件是否存在
        if not md_path_obj.exists():
            raise FileProcessingError("md文件不存在")
        #获取文件内容
        with open(md_path_obj, "r", encoding="utf-8") as f:
            md_content = f.read()

        #获取image_path
        image_path = md_path_obj.parent / "image"

        return md_content,md_path_obj,image_path

    def get_images_context(self, md_content, image_path):
        """
        获取md文件中图片的上下文
        :param md_content:
        :param image_path:
        :return:
        """

        #定义最终封装的图片上下文容器
        target_images_context = []

        #循环获取图片
        for image_name in os.listdir("md_path"):
            #判断是否是图片
            #这一步拿到的是一个字符串.md
            file_ext = os.path.splitext(image_name)[1]
            config = get_config()
            #判断切分后的文件后缀是不是在config的预设中
            if file_ext not in config.image_extensions:
                continue

            # 3 把复合格式要求图片，生成上下文内容，抽取方法
            # 参数 图片名称  和  md内容
            # 返回：图片对应上下文数据
            # list
            # [("图片前一个标题","图片上文","图片下文")]
            #定义方法生成图片的上下文
            img_context = self.build_image_context(md_content, image_name)

            if not img_context:
                continue





        return target_images_context



    def build_image_context(self, md_content, image_name):
        """
        根据图片名称 和 md内容生成上下文内容
        :param md_content:
        :param image_name:
        :return: [("图片前一个标题","图片上文","图片下文")]
        """
        # 根据图片文件名称 到 md内容找图片位置
        # 正则匹配
        re_pattern = re.compile(r"!\[.*?\]\(.*?" + re.escape(image_name) + r".*?\)")

        #切分md_content然后想办法匹配，按行\n
        md_content_lines = md_content.split("\n")

        #定义图片上下文
        img_context = []

        #遍历md_content_lines,然后用正则做匹配
        for line_index, line in enumerate(md_content_lines):
            #判断当前行是否包含图片
            if not re_pattern.search(line):
                #如果匹配不到图片，就结束，继续下一行匹配
                continue

            head_title = "" #封装图片的title
            head_index = -1 #封装图片位置

            # 获取图片上文
            # 思路：从图片这一行，开始向上找，直到找到标题行
            for i in range(line_index - 1, -1, -1):
                # 找到标题  在md格式   1-6个#空格
                if re.match(r"^#{1,6}\s+", md_content_lines[i]):
                    #获取标题
                    head_title = md_content_lines[i]
                    #获取标题位置
                    head_index = i
                    break

            # 获取图片位置 和 上面标题位置，之间的内容
            # ["0","1","2","3","4"]
            # head_index:标题位置 0
            # line_index：图片位置 4
            # [1,4)  左闭右开
            # pre_content 是图片上文内容
            pre_content = md_content_lines[head_index + 1:line_index]

            # 根据获取图片上文内容，对截取，获取上面200字符
            # "front" 从图片开始向上截取
            final_img_pre_context = self.image_context_limit(pre_content, "front")


            # 获取图片下文
            end_index = len(md_content_lines)
            for i in range(line_index+1,end_index):
                if re.match(r"^#{1,6}\s+",md_content_lines[i]):
                    end_index = i
                    break

            # 获取图片，下面标题之间内容
            post_context = md_content_lines[line_index+1:end_index]
            # 调研方法截取
            # "back" 向下截取
            final_img_post_context = self.image_context_limit(post_context,"back")

            #封装图片上下文
            img_context.append((head_title, final_img_pre_context, final_img_post_context))

            return img_context


    def image_context_limit(self, substr_content, substr_type):
        """
        根据传入的内容，截取上文front和下文back
        :param substr_content: 列表：pre_content = md_content_lines[head_index + 1:line_index]
        :param substr_type:
        :return:
        """

        current_content = []
        final_content = []

        img_pattern = re.compile(r"^!\[.*?\]\(.*?\)$")

        #循环列表substr_content,这个列表是
        for line in substr_content:
            #去空格
            clean_line = line.strip()
            #非空，非图片
            if clean_line and not img_pattern.search(clean_line):
                current_content.append(clean_line)
            else:
                #如果当前行是图片，或者空行，说明上一段完整的话结束了，就结束
                final_content.append("\n".join(current_content))
                current_content = []

        #处理循环结束后最后一段内容
        if current_content:
            final_content.append("\n".join(current_content))

        # 向上截取
        if substr_type=="front":
            # 反转  1 2 3  =》 3 2 1
            final_content.reverse()

        max_char = 200

        total = 0
        selected = []
        for para in final_content:
            para_len = len(para)
            if (total + para_len) > max_char and selected:
                break
            selected.append(para)
            total += para_len

        if substr_type == "back":
            selected.reverse()

        # 6. 返回上下文
        return "\n\n".join(selected)


    #3 调用视觉大模型生成图片摘要
    # 根据图片本身  +  图片上下文内容  =》 调用视觉模型 =》 生成图片摘要
    # 参数：md路径 Path类型
    #      上下文数据：类型
    # List[("图片名称1", "图片路径1", ("图片前一个标题", "图片上文", "图片下文"))]
    def create_image_summary(self, md_path_obj, target_images_context):
        pass




















