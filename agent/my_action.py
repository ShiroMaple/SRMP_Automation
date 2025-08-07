from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
import json
from serverchan_sdk import sc_send
#from .utils import parse_query_args,Prompt

sendkey="sctp2102ta-lbduuk43fh2pz462ln61oko4"
title="from MaaFw"
options={"tags":"MaaFw"}

@AgentServer.custom_action("my_action_111")
class MyCustomAction(CustomAction):
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:        

        My_params = json.loads(argv.custom_action_param)  # 解析 JSON    
        Reco_detail= argv.reco_detail  # 获取识别详情    
        best_result = Reco_detail.best_result
        best_result_text=best_result.text if best_result else "No result found" 
        
        #print(f"argv.custom_action_param : {argv.custom_action_param}") #str型字符串
        #print(f"Transfer to JSON : {My_params}")   # Python 字典
        #print(f"Result : {My_params.get("srmp")}")  # 获取 srmp 参数并打印
        #print(f"Reco_detail: {Reco_detail}")
        print(f"best_result_text: {best_result_text}")
        desp="This is a test message from MaaFw\n\n" + My_params.get("srmp", "where is srmp?")  # 获取 srmp 参数，若不存在则使用默认值        
        #response = sc_send(sendkey,title,desp,options)  # 调用 serverchan_sdk 的 sc_send 函数发送消息
        #print(response)  # 打印发送结果
        return True  
    
@AgentServer.custom_action("my_action_sendRedeemCode")
class MyCustomAction(CustomAction):
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:  
        
        GameName=json.loads(argv.custom_action_param).get("GameName","Unknown")
        
        
        RedeemCode = argv.reco_detail.best_result.text if argv.reco_detail.best_result else "No result found"
        desp=GameName+" RedeemCode: " + RedeemCode  
        response = sc_send(sendkey, title, desp, options)
        print(response)
        print(f"{GameName} RedeemCode: {RedeemCode}")

@AgentServer.custom_action("my_action_sendMessage")
class MyCustomAction(CustomAction):
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:  
        
        MessageSource=json.loads(argv.custom_action_param).get("Source","Unknown")        
        
        Reco_Message = argv.reco_detail.best_result.text if argv.reco_detail.best_result else "No result found"
        desp=MessageSource+": " + Reco_Message
        response = sc_send(sendkey, title, desp, options)
        print(response)
        print(f"{MessageSource} : {Reco_Message}")
"""
#运行节点
@AgentServer.custom_action("run")
class Run(CustomAction):
    def run (
            self,context:Context,argv:CustomAction.RunArg
    )-> CustomAction.RunResult | bool:
        try:
            args=parse_query_args(argv)
            type=args.get("type","task")
            key=args.get("key","")

            if type=="" or key=="":
                return False
            if type=="task":
                context.run_task(key)
            elif type=="node":
                context.run_action(key)
            
            return True
        except Exception as e:
            return Prompt.error("运行节点",e)
"""