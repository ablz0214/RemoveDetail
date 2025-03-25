from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
import re

"""
收到消息时，移除消息中的所有<details>标签及其内容，保留其他标签处理逻辑
"""

# 注册插件
@register(name="RemoveDetail", description="专门移除消息中的所有<details>标签及其内容", version="0.1",
          author="ablz0214")
class RemoveDetailsPlugin(BasePlugin):

    def __init__(self, host: APIHost):
        super().__init__(host)

    async def initialize(self):
        pass

    def remove_details_content(self, msg: str) -> str:
        """
        专门移除<details>标签及其内容
        """
        # 优先处理<details>标签（完整标签对）
        msg = re.sub(
            r'<details\b[^>]*>[\s\S]*?</details>', 
            '', 
            msg, 
            flags=re.DOTALL | re.IGNORECASE
        )
        
        # 处理未闭合的<details>标签（从开始标签到消息结尾）
        msg = re.sub(
            r'<details\b[^>]*>[\s\S]*', 
            '', 
            msg, 
            flags=re.IGNORECASE
        )
        
        # 处理单独的</details>结束标签
        msg = re.sub(
            r'</details>', 
            '', 
            msg, 
            flags=re.IGNORECASE
        )
        
        # 保留原有的换行处理逻辑
        msg = re.sub(r'\n{3,}', '\n\n', msg)
        msg = re.sub(r'(\S)\n{2,}(\S)', r'\1\n\2', msg)
        
        return msg.strip()

    @handler(NormalMessageResponded)
    async def normal_message_responded(self, ctx: EventContext):
        msg = ctx.event.response_text
        # 只检测<details>标签（不区分大小写）
        if re.search(r'<details', msg, re.IGNORECASE):
            processed_msg = self.remove_details_content(msg)
            if processed_msg:
                ctx.add_return("reply", [processed_msg])
            else:
                self.ap.logger.warning("移除<details>后消息为空，跳过回复")

    def __del__(self):
        pass
