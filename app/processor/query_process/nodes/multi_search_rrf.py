#rrf多路检索融合节点
from app.processor.query_process.base import BaseNode
from app.processor.query_process.state import QueryGraphState


class MultiSearchRRFNode(BaseNode):
    def process(self, state: QueryGraphState) -> QueryGraphState:

        #1、获取state的向量检索结果和hyde的检索结果

        #2、使用rrf公式计算分数，根据分数降序

        #3、把最终的结果放在列表，更新state返回

        return state