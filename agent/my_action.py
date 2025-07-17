from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context

#运行节点
"""
@AgentServer.custom_action("run")
class Run(CustomAction):

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> CustomAction.RunResult | bool:
            try:
                args =parse_query_args(argv)
                type=args.get("type,"task")
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
        print("my_action_111 is running!")

        return True
"""