from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
import json


@AgentServer.custom_action("my_action_111")
class MyCustomAction(CustomAction):
    """
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:

        print("my_action_111 is running!")

        return True
    """
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        # 1. 解析 custom_action_param (JSON 字符串 -> Python 字典)
        try:
            params = json.loads(argv.custom_action_param)  # 解析 JSON
            srmp = params.get("srmp")  # 获取 srmp 参数
        except json.JSONDecodeError:
            print("Error: custom_action_param is not valid JSON!")
            return False

        # 2. 打印 srmp 的值
        print(f"Received parameter : {srmp}")
        return True  
