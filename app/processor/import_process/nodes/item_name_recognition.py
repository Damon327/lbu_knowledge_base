
from app.processor.import_process.base import BaseNode, T

# 商品名识别模块
"""
    # 1 参数校验  chunks切分段数据不能为空
    # 2 获取LLM需要生成提示词数据
    # 3 构建提示词，调用LLM，提取商品名
    # 4 商品名嵌入（bge-m3生成密集和稀疏向量）
    # 5 存储到Milvus向量数据库里面
    # 6 更新state返回
"""
class ItemNameRecognition(BaseNode):

    def process(self, state: T) -> T:
        pass

