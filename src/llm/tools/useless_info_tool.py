from src.llm.tools.abc_tool import ABCTool


class UselessInfoTool(ABCTool):

    def __init__(self):
        pass

    def name(self) -> str:
        return "useless_information"

    def description(self) -> str:
        txt = ("Use this tool if none of the other tools can use the information. "
               "This tool will not extract any information. "
               "Only use this if you are sure that none of the other tools "
               "can use the information in the provided string")
        return txt

    def parameters(self) -> dict:
        return_dict = {
            "best_guess_description": {
                "description":
                    "At most a sentence describing what the provided data is. "
                    "Be very concise. Focus on the type of the information, "
                    "instead of specific details like years or company names.",
                "type": "string"
            }
        }

        return return_dict

    def required_parameters(self) -> list[str]:
        return ["best_guess_description"]

