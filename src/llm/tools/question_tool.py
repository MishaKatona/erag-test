from src.llm.tools.abc_tool import ABCTool
from src.llm.tools.field_definitions import load_json_file


class QuestionTool(ABCTool):

    def name(self) -> str:
        return "question_tool"

    def description(self) -> str:
        txt = "Form for filling out questions, given the context."

        return txt

    def parameters(self) -> dict:
        fields = {
            "Question": {
                "description": "The technical question related to the context "
                               "provided. If no engineering concepts or "
                               "information is present respond with 'No' and"
                               "set the 'Technical_Level' to 0.",
                "type": "string"
            },
            "Good_Quality": {
                "description":
                    "Quality of provided context. Text was extracted using "
                    "OCR, and therefore can contain errors. If there are a lot "
                    "of errors, and the context is difficult to understand use "
                    "false. Otherwise, use true.",
                "type": "boolean"
            },
            "Technical_Level": {
                "description":
                    "The (engineering) technical suitability of the context to "
                    "be used for generating questions. If the context does not "
                    "contain enough technical information to generate a good "
                    "question set it to 0 (content page, legal text, etc.). "
                    "If the context is highly technical and contains a self "
                    "sufficient amount of information to generate a question set "
                    "set it to 5.",
                "type": "string",
                "enum": ["0", "1", "2", "3", "4", "5"]
            }
        }

        return fields

    def required_parameters(self) -> list[str]:
        return ["Questions", "Context_Quality", "Technical_Level"]


