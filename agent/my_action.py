from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
import json
from serverchan_sdk import sc_send

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

        params = json.loads(argv.custom_action_param)  # 解析 JSON        
        
        #print(f"argv.custom_action_param : {argv.custom_action_param}") #str型字符串
        #print(f"Transfer to JSON : {params}")   # Python 字典
        print(f"Result : {params.get("srmp")}")  # 获取 srmp 参数并打印
        sendkey="sctp2102ta-lbduuk43fh2pz462ln61oko4"
        title="from MaaFw"
        desp="This is a test message from MaaFw\n\n" + params.get("srmp", "where is srmp?")  # 获取 srmp 参数，若不存在则使用默认值
        options={"tags":"MaaFw"}
        response = sc_send(sendkey,title,desp,options)  # 调用 serverchan_sdk 的 sc_send 函数发送消息
        print(response)  # 打印发送结果
        return True  
