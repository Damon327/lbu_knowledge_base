# 网络搜索节点 mcp方式
from app.processor.query_process.base import BaseNode
from app.processor.query_process.state import QueryGraphState


class WebSearchNode(BaseNode):
    def process(self, state: QueryGraphState) -> QueryGraphState:
        #1、获取参数并加以校验

        #2、调用mcp工具得到工具返回结果

        #3、返回mcp的结果







        return state
