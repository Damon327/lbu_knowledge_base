# hyde假设文档搜索
from app.processor.query_process.base import BaseNode
from app.processor.query_process.state import QueryGraphState


class HydeSearchNode(BaseNode):

    def process(self, state: QueryGraphState) -> QueryGraphState:
        #1、获取参数并加以校验

        #2、调用llm，根据问题生成建设性答案

        #3、把用户的问题 + 假设性答案给拼接在一起

        #4、拼接在一起之后向量化

        #5、构建查询条件：向量条件 + 标量条件

        #6、执行混合检索


        return state
