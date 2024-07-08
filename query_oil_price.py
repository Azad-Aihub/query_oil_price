import requests
import plugins
from plugins import *
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger

# AI绘画API的基础URL
SD_PAINT_URL = "https://api.pearktrue.cn/api/stablediffusion/"

@plugins.register(name="sd_paint",
                  desc="AI绘画生成图像",
                  version="1.0",
                  author="wyh",
                  desire_priority=100)
class sd_paint(Plugin):

    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info(f"[{__class__.__name__}] inited")

    def get_help_text(self, **kwargs):
        help_text = "发送【sd绘画 对应的绘画关键词】获取SD绘画生成的图片链接"
        return help_text

    def on_handle_context(self, e_context: EventContext):
        # 只处理文本消息
        if e_context['context'].type != ContextType.TEXT:
            return
        content = e_context["context"].content.strip()

        # 检查是否是sd绘画的指令
        if content.startswith("sd绘画") and " " in content:
            prompt = content.split("sd绘画", 1)[1].strip()
            logger.info(f"[{__class__.__name__}] 收到AI绘画请求: {prompt}")
            reply = Reply()
            result = self.get_sd_paint(prompt)
            if result:
                reply.type = ReplyType.TEXT
                reply.content = result
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            else:
                reply.type = ReplyType.ERROR
                reply.content = "生成绘画失败，请稍后再试。"
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS

    def get_sd_paint(self, prompt):
        params = {"prompt": prompt}
        try:
            response = requests.get(url=SD_PAINT_URL, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data["code"] == 200:
                    return f"AI绘画成功：\n绘画关键词: {data['prompt']}\n图片链接: {data['imgurl']}"
                else:
                    logger.error(f"AI绘画接口返回错误信息: {data['msg']}")
                    return None
            else:
                logger.error(f"AI绘画接口返回值异常: {response.text}")
                return None
        except Exception as e:
            logger.error(f"AI绘画接口异常：{e}")
            return None
