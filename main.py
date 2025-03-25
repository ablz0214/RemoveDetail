from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
import re

# 注册插件
@register(name="RemoveDetail", description="专门移除消息中的所有<details>标签及其内容", version="0.3",
          author="ablz0214")
class RemoveDetailsPlugin(BasePlugin):

    def __init__(self, host: APIHost):
        super().__init__(host)

    async def initialize(self):
        pass

    def remove_details_content(self, msg: str) -> str:
        """
        专门移除<details>标签及其内容，处理各种异常情况
        """
        # 1. 先处理完整的<details>...</details>标签对
        msg = re.sub(
            r'<details\b[^>]*>[\s\S]*?</details>', 
            '', 
            msg, 
            flags=re.DOTALL | re.IGNORECASE
        )
        
        # 2. 处理只有<details>开始标签没有结束标签的情况
        msg = re.sub(
            r'<details\b[^>]*>[\s\S]*', 
            '', 
            msg, 
            flags=re.IGNORECASE
        )
        
        # 3. 专门处理只有</details>结束标签的情况
        # 3.1 分割消息，只保留</details>之后的部分
        parts = re.split(r'</details>', msg, flags=re.IGNORECASE)
        if len(parts) > 1:  # 如果找到</details>标签
            msg = parts[-1]  # 只保留最后一部分
        else:
            msg = parts[0]  # 没有找到则保留全部
        
        # 优化换行和空格
        msg = re.sub(r'\n{3,}', '\n\n', msg)
        msg = re.sub(r'(\S)\n{2,}(\S)', r'\1\n\2', msg)
        msg = re.sub(r' +', ' ', msg)  # 合并多个空格
        
        return msg.strip()

    @handler(NormalMessageResponded)
    async def normal_message_responded(self, ctx: EventContext):
        msg = ctx.event.response_text
        # 检测任何形式的details标签
        if re.search(r'<details|</details>', msg, re.IGNORECASE):
            processed_msg = self.remove_details_content(msg)
            if processed_msg:
                ctx.add_return("reply", [processed_msg])
            else:
                self.ap.logger.warning("移除details标签后消息为空，跳过回复")

    def __del__(self):
        pass
