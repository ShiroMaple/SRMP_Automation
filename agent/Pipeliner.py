from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context

from utils import parse_query_args, parse_list_input, Prompt


# 解析参数
def parse_pipeline_args(argv: CustomAction.RunArg):
    args = parse_query_args(argv)
    node = args.get("node")
    keys = args.get("keys")
    values = args.get("values")
    return node, keys, values


# 设置字符串节点
@AgentServer.custom_action("set_str_node_attrs")
class SetStrNodeAttrs(CustomAction):
    def run(
        self, context: Context, argv: CustomAction.RunArg
    ) -> CustomAction.RunResult | bool:
        try:
            node, keys, values = parse_pipeline_args(argv)
            keys = parse_list_input(keys)
            values = parse_list_input(values)

            if len(keys) != len(values):
                #return Prompt.error("设置节点字符串类型属性", "keys和values长度不一致")
                return print("设置节点字符串类型属性", "keys和values长度不一致")


            for i in range(len(keys)):
                key = keys[i]
                value = values[i]
                if value == "[]":
                    value = []
                context.override_pipeline({node: {key: value}})

            return True
        except Exception as e:
            #return Prompt.error("设置节点字符串类型属性", e)
            return print("设置节点字符串类型属性", e)


# 运行节点
@AgentServer.custom_action("run")
class Run(CustomAction):
    def run(
        self, context: Context, argv: CustomAction.RunArg
    ) -> CustomAction.RunResult | bool:
        try:
            args = parse_query_args(argv)
            type = args.get("type", "task")
            key = args.get("key", "")

            if type == "" or key == "":
                return False

            if type == "task":
                context.run_task(key)
            elif type == "node":
                context.run_action(key)

            return True
        except Exception as e:
            return Prompt.error("运行节点", e)


# 阻断
@AgentServer.custom_action("break")
class Break(CustomAction):
    def run(
        self, context: Context, argv: CustomAction.RunArg
    ) -> CustomAction.RunResult | bool:
        return False

#指定下一节点   调用设置字符串节点，直接传入下一个节点名
@AgentServer.custom_action("next_node")
class NextNode(CustomAction):
    def run(
        self,context:Context,argv:CustomAction.RunArg        
    ) -> CustomAction.RunResult | bool:
        SetStrNodeAttrs.run(self,context,argv)
        return True