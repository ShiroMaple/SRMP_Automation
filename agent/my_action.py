from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
import json
from serverchan_sdk import sc_send
from utils.logger import logger
from utils.actionUtils import *
import re
from maa.notification_handler import NotificationHandler, NotificationType

#serverchan params
sendkey = "sctp2102ta-lbduuk43fh2pz462ln61oko4"
title = "Msg from MaaFw"
options = {"tags": "MaaFw"}

@AgentServer.custom_action("HandleError")
class HandleError(CustomAction):
    def run(
        self,
        context:Context,
        argv:CustomAction.RunArg
    ) -> bool:
        task_detail=argv.task_detail
        task_name=task_detail.entry
        error_node=task_detail.nodes[-1].name
        msg=f"任务 {task_name} 节点{error_node}触发on_error"
        logger.warning(msg)
        add_notice("异常",msg)        
        return CustomAction.RunResult(success=True)

def GameNameDict(GameName:str)->str:    
    match GameName:
        case "原神":
            GameNameEng = "Genshin"
        case "星穹铁道" | "崩坏：星穹铁道"|"坏：星穹铁道"|"崩坏星":
            GameNameEng = "Starrail"
        case "绝区零":
            GameNameEng = "ZZZ"
        case "明日方舟":
            GameNameEng = "Arknights"
        case "女神异闻录" | "女神异闻录：夜幕魅影"|"女神异闻录：夜嘉"|"女神異闻录：夜幕魅影":
            GameNameEng = "P5X"
        case _:
            GameNameEng = "Unknown"
    return GameNameEng

def find_latest_reco_text(pattern,node_list) -> str:    
    """
    反向遍历 List[node_list]，找到最后一个节点名称符合 pattern 的节点
    示例pattern=r"ab.*cde"
    返回匹配节点的 recognition.best_result
    """
    for node in reversed(node_list):  # 从后往前遍历
        if re.fullmatch(pattern, node.name):  # 精确匹配 name 模式
            return node.recognition.best_result.text
    logger.info(f"{pattern}无匹配节点")
    return None  # 无匹配节点

def fetch_spec_reco_text(str,context,args) -> str: 
    """
    把指定的节点名和context和json格式化后的custom_action_param传入
    示例args = json.loads(argv.custom_action_param)
    返回最近一次运行该节点后的识别结果
    """    
    NameNode = args.get("NameNode", "Unknown")  
    # 需要在自定义动作参数中传入识别名称的节点"NameNode"
    # logger.info(NameNode)
    if NameNode == "Unknown": logger.warning("未传入名称识别节点")
    nodeDetial = context.tasker.get_latest_node(NameNode)  # 获取最近一次"NameNode”的节点详情
    name = (nodeDetial.recognition.best_result.text if nodeDetial else "")  # 从节点详情中获取到识别结果
    return name

@AgentServer.custom_action("my_action_111")
class MyCustomAction(CustomAction):
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:

        My_params = json.loads(argv.custom_action_param)  # 解析 JSON
        Reco_detail = argv.reco_detail  # 获取识别详情
        best_result = Reco_detail.best_result   #当前节点的匹配结果
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
        """
        node_dicts = [
        {
            'node_id': node.node_id,
            'name': node.name,
            'completed': node.completed
        }
            for node in a1
        ]              
        logger.info(f"nodes:\n{node_dicts}")
        """
        pattern=r".*OCR"
        latest_best_result = find_latest_reco_text(pattern,a1)     
        logger.info(latest_best_result)

        context.tasker.post_stop()        

        return True

@AgentServer.custom_action("sendRedeemCode")
class SendRedeemCode(CustomAction):
    """
    功能：根据传入的节点名找到其OCR的识别结果，通过serverchan发送通知，如果设置了返回点前缀，跳转到拼接名称后的返回点
    参数：
        pattern         节点名称的正则匹配表达式
        BackNodePrefix  (可选)  返回节点名的前缀  
    示例："custom_action_param":{"pattern":"TapTap-recoName","BackNodePrefix":"TapTap-pass"}
    """
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:

        args = json.loads(argv.custom_action_param)
        try:
            pattern=args.get("pattern")
        except Exception as e:
            logger.warning("传入的pattern异常",e)
            return CustomAction.RunResult(success=False)
        GameName = find_latest_reco_text(pattern,argv.task_detail.nodes )
        GameNameEng=GameNameDict(GameName)
        RedeemCode = (
            argv.reco_detail.best_result.text
            if argv.reco_detail.best_result
            else "No result found"
        )  # 从调用本方法的节点参数中获取识别结果
        #desp = GameNameEng + " RedeemCode: " + RedeemCode
        #response = sc_send(sendkey, title, desp, options)   #通过serverchan推送消息
        msg=f"{GameNameEng}: {RedeemCode}"
        add_notice("RedeemCode",msg)
        #print(response)
        #print(f"{GameNameEng} RedeemCode: {RedeemCode}")

        BackNodePrefix = args.get("BackNodePrefix", "")
        if not BackNodePrefix:
            logger.info("未声明返回节点前缀，不覆写跳转")
            return CustomAction.RunResult(success=True)
        else:
            CallingNode = argv.node_name  # 获取调用源节点名
            BackNode = (BackNodePrefix + GameNameEng)  # 将传入的返回点和游戏名称组合成要返回的节点名称
            ppover = {CallingNode: {"next": BackNode}}
            context.override_pipeline(ppover)
            logger.info(f"NodeOverride: {ppover}")
        return CustomAction.RunResult(success=True)

@AgentServer.custom_action("TapTap_Jump")   #TapTap跳转至Pass节点
class TapTapJump(CustomAction): 
    def run(
            self,
            context:Context,
            argv:CustomAction.RunArg
    )->bool:        
        CallingNode = argv.node_name  # 获取调用源节点名
        Nodes=argv.task_detail.nodes  #获取当前任务节点集合
        pattern=r"TapTap-flag.*Page"
        GameName=find_latest_reco_text(pattern,Nodes)     
        GameNameEng=GameNameDict(GameName)
        #logger.info(f"GameName:{GameName}")

        NextNode="TapTap-pass"+GameNameEng #拼接返回节点名
        ppover={CallingNode:{"next":NextNode}}
        context.override_pipeline(ppover)
        logger.debug(f"NodeOverride: {ppover}")
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

from typing import Dict, Any
from collections import defaultdict

# 解析查询字符串 from https://github.com/kqcoxn/MaaNewMoonAccompanying/blob/main/agent/customs/utils.py
def parse_query_args(argv: CustomAction.RunArg) -> dict[str, Any]:
    if not argv.custom_action_param:
        return {}

    # 预处理参数：去除首尾引号并按'&'分割参数列表
    args: list[str] = argv.custom_action_param.strip("\"'").split("&")

    # 解析键值对到字典
    params: Dict[str, Any] = {}
    for arg in args:
        # 分割键值
        parts = arg.split("=")
        if len(parts) >= 2:
            params[parts[0]] = parts[1]

    return params

#延迟提醒列表
noticelist = defaultdict(list)  # 自动按 key 分组存储 focus

def add_notice(tag:str, message:str):
    """
    添加通知到 noticelist
    :param tag: 通知的标签
    :param message: 通知内容
    """
    global noticelist
    current_time = datetime.now().strftime("%H:%M:%S")
    noticelist[tag].append((current_time,message))
    logger.info(f"添加通知: {tag} - [{current_time}] {message}")

# 添加延迟提醒
@AgentServer.custom_action("delay_focus_hook")
class DelayFocusHook(CustomAction):
    def run(
        self, context: Context, argv: CustomAction.RunArg
    ) -> CustomAction.RunResult | bool:
        global delay_focus,noticelist 
        try:
            args = parse_query_args(argv)
            tag = args.get("tag", "")
            msg = args.get("msg", "")
            add_notice(tag,msg)
            #logger.info(f"当前提醒列表:{noticelist}")   #添加调试信息
            return CustomAction.RunResult(success=True)
        except Exception as e:
            return logger.warning(f"添加延迟提醒{e}")

# 执行延迟提醒
@AgentServer.custom_action("delay_focus")
class DelayFocus(CustomAction):
    def run(
        self, context: Context, argv: CustomAction.RunArg
    ) -> CustomAction.RunResult | bool:
        global noticelist

        for tag, notice_list in noticelist.items():
            #logger.info(f"Tag: {key}, Message: {notice_list}")
            logger.info(f"Tag: {tag}")
            for notice in notice_list:
                logger.info(f"  {notice}")
        final_notice()
        return CustomAction.RunResult(success=True)

#将字典格式的数据构建为 Markdown 格式的 desp
def build_markdown_desp(data_dict):
    desp_lines = []    
    for tag, notice_list in data_dict.items():
        # 添加 tag 作为标题
        desp_lines.append(f"##  {tag}") #(共 {len(notice_list)} 个msg)")
        desp_lines.append("")  # 空行
        
        # 添加每个 msg 作为列表项
        for i, (time, msg) in enumerate(notice_list, 1):
            desp_lines.append(f"{i}. [{time}] {msg}")
        
        desp_lines.append("")  # 空行分隔不同的 tag
        desp_lines.append("---")  # 分隔线
        desp_lines.append("")  # 空行
    
    # 将列表转换为字符串，用换行符连接
    return "\n".join(desp_lines)

def final_notice():
    """
    执行最终通知，将 noticelist 中的所有通知发送到 serverchan
    """
    global noticelist
    if noticelist:
        desp=build_markdown_desp(noticelist)
        response = sc_send(sendkey, title, desp, options)
        logger.info("已通过serverchan推送通知")
    else:
        logger.info("没有通知需要发送")       

class AdvancedNotificationHandler(NotificationHandler):
    def on_tasker_task(self, noti_type, detail):
        if noti_type == NotificationType.Starting:
            logger.info(f"🚀 开始执行任务: {detail}")
        elif noti_type == NotificationType.Succeeded:
            logger.info(f"✅ 任务完成: {detail}")
        elif noti_type == NotificationType.Failed:
            logger.error(f"❌ 任务失败: {detail}, 错误: {detail}")
            # 可以在这里触发重试机制或发送警报
    


"""
#尝试用swipe解锁图案
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
