from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
import json
from serverchan_sdk import sc_send
from utils.logger import logger
from utils.actionUtils import *
import re

sendkey = "sctp2102ta-lbduuk43fh2pz462ln61oko4"
title = "from MaaFw"
options = {"tags": "MaaFw"}


@AgentServer.custom_action("my_action_111")
class MyCustomAction(CustomAction):
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:

        My_params = json.loads(argv.custom_action_param)  # 解析 JSON
        Reco_detail = argv.reco_detail  # 获取识别详情
        best_result = Reco_detail.best_result
        best_result_text = best_result.text if best_result else "No result found"

        # print(f"argv.custom_action_param : {argv.custom_action_param}") #str型字符串
        # print(f"Transfer to JSON : {My_params}")   # Python 字典
        # print(f"Result : {My_params.get("srmp")}")  # 获取 srmp 参数并打印
        # print(f"Reco_detail: {Reco_detail}")
        #print(f"best_result_text: {best_result_text}")
        #desp = "This is a test message from MaaFw\n\n" + My_params.get("srmp", "where is srmp?"        )  # 获取 srmp 参数，若不存在则使用默认值
        # response = sc_send(sendkey,title,desp,options)  # 调用 serverchan_sdk 的 sc_send 函数发送消息
        # print(response)  # 打印发送结果
        a1=argv.task_detail.nodes
        
        node_dicts = [
        {
            'node_id': node.node_id,
            'name': node.name,
            'completed': node.completed
        }
            for node in a1
        ]              
        logger.info(f"nodes:\n{node_dicts}")
        

        def find_latest_taptap_node(node_list) -> str:    
            """
            反向遍历 List[NodeDetail]，找到最近一个 name 符合条件的节点，并返回其 recognition.best_result.text
            """
            for node in reversed(node_list):  # 从后往前遍历
                if re.fullmatch(r"TapTap-flag.*Page", node.name):  # 精确匹配 name 模式
                    return node.recognition.best_result.text
            return None  # 无匹配节点

        # 调用示例
        latest_best_result = find_latest_taptap_node(a1)  # a1: List[NodeDetail]        
        logger.info(latest_best_result)
        
        context.tasker.post_stop()        

        return True


@AgentServer.custom_action("my_action_sendRedeemCode")
class SendRedeemCode(CustomAction):
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:

        args = json.loads(argv.custom_action_param)
        GameNameNode = args.get(
            "GameNameNode", "Unknown"
        )  # 需要在自定义动作参数中传入识别名称的节点"GameNameNode”
        # logger.info(GameNameNode)
        if GameNameNode == "Unknown":
            logger.warning("未传入游戏名称识别节点")
        nodeDetial = context.tasker.get_latest_node(
            GameNameNode
        )  # 获取最近一次"GameNameNode”的节点详情
        GameName = (
            nodeDetial.recognition.best_result.text if nodeDetial else ""
        )  # 从节点详情中获取到识别结果
        match GameName:
            case "原神":
                GameName = "Genshin"
            case "星穹铁道" | "崩坏：星穹铁道":
                GameName = "Starrail"
            case "绝区零":
                GameName = "ZZZ"
            case "明日方舟":
                GameName = "Arknights"
            case "女神异闻录" | "女神异闻录：夜幕魅影":
                GameName = "P5X"
            case _:
                GameName = "Unknown"
        RedeemCode = (
            argv.reco_detail.best_result.text
            if argv.reco_detail.best_result
            else "No result found"
        )  # 从调用本方法的节点参数中获取识别结果
        desp = GameName + " RedeemCode: " + RedeemCode
        # response = sc_send(sendkey, title, desp, options)   #通过serverchan推送消息
        # print(response)
        print(f"{GameName} RedeemCode: {RedeemCode}")

        BackPoint = args.get("BackPoint", "")
        if not BackPoint:
            logger.info("没有设置返回点")
        else:
            CallingNode = argv.node_name  # 获取调用源节点名
            BackPointNode = (
                BackPoint + GameName
            )  # 将传入的返回点和游戏名称组合成要返回的节点名称
            ppover = {CallingNode: {"next": BackPointNode}}
            context.override_pipeline(ppover)
            logger.info(f"NodeOverride: {ppover}")
        return CustomAction.RunResult(success=True)

@AgentServer.custom_action("TapTap_Jump")   #TapTap跳转至Pass节点
class TapTapJump(CustomAction): 
    #def recoGameName(self,context:Context)->str:
        #nodeDetial = context.tasker.get_latest_node("TapTap-recoGameName")  # 获取最近一次"GameNameNode”的节点详情
        #GameName = (nodeDetial.recognition.best_result.text if nodeDetial else "")  # 从节点详情中获取到识别结果
    def GameNameDict(self,GameName:str)->str:    
        match GameName:
            case "原神":
                GameName = "Genshin"
            case "星穹铁道" | "崩坏：星穹铁道"|"坏：星穹铁道":
                GameName = "Starrail"
            case "绝区零":
                GameName = "ZZZ"
            case "明日方舟":
                GameName = "Arknights"
            case "女神异闻录" | "女神异闻录：夜幕魅影"|"女神异闻录：夜嘉":
                GameName = "P5X"
            case _:
                GameName = "Unknown"
        return GameName
    def find_latest_name(self,node_list) -> str:    
            """
            反向遍历 List[NodeDetail]，找到最后一个 name 符合 "TapTap-flag***Page" 的节点，
            并返回其 recognition.best_result。
            """
            for node in reversed(node_list):  # 从后往前遍历
                if re.fullmatch(r"TapTap-flag.*Page", node.name):  # 精确匹配 name 模式
                    return node.recognition.best_result.text
            return None  # 无匹配节点

    def run(
            self,
            context:Context,
            argv:CustomAction.RunArg
    )->bool:        
        CallingNode = argv.node_name  # 获取调用源节点名
        Nodes=argv.task_detail.nodes  
        GameName=self.find_latest_name(Nodes)
        logger.info(f"GameName:{GameName}")        
        GameName=self.GameNameDict(GameName)
        logger.info(f"GameName:{GameName}")

        NextNode="TapTap-pass"+GameName
        ppover={CallingNode:{"next":NextNode}}
        context.override_pipeline(ppover)
        logger.info(f"NodeOverride: {ppover}")
        return CustomAction.RunResult(success=True)
    

@AgentServer.custom_action("my_action_sendMessage")
class SendMessage(CustomAction):
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:

        MessageSource = json.loads(argv.custom_action_param).get("Source", "Unknown")

        Reco_Message = (
            argv.reco_detail.best_result.text
            if argv.reco_detail.best_result
            else "No result found"
        )
        desp = MessageSource + ": " + Reco_Message
        response = sc_send(sendkey, title, desp, options)
        print(response)
        print(f"{MessageSource} : {Reco_Message}")
        return True


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
"""
        x2=int(args.get("x2"))
        y2=int(args.get("y2"))
        x3=int(args.get("x3"))
        y3=int(args.get("y3"))
        x4=int(args.get("x4"))
        y4=int(args.get("y4"))
        Tasker.get_controller(context).post_swipe(x1,y1,x2,y2,300)
        Tasker.get_controller(context).post_touch_down(x1,y1,0,1)
        Tasker.get_controller(context).post_touch_move(x2,y2,0,1)
        Tasker.get_controller(context).post_touch_move(x3,y3,0,1)
        Tasker.get_controller(context).post_touch_move(x4,y4,0,1)
        Tasker.get_controller(context).post_touch_up(0)
        return True
"""
