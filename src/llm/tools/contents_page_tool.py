from src.llm.tools.abc_tool import ABCTool


class ContentsPageTool(ABCTool):

    def name(self) -> str:
        return "extract_contents_page"

    def description(self) -> str:
        return ("Processes a string to extract a table of contents. The"
                "string will usually have text followed by a page number or "
                "a range of page numbers. The page number will be an integer. "
                "Use this if the passed string is a table of contents. If the "
                "page number is a range (e.g. 1-3), return a list of integers, "
                "(e.g. [1, 2, 3]). ONLY USE IF IT'S THE CONTENTS PAGE.")

    def parameters(self) -> dict:
        return_dict = {
            "consolidated_balance_sheet_page_number": {
                "description": "The page number of group or consolidated balance sheet or financial statements."
            },
            "company_balance_sheet_page_number": {
                "description": "The page number of company balance sheet or financial statements."
            }
        }

        for k, v in return_dict.items():
            if "type" not in v.keys():
                v["type"] = "array"
                v["items"] = {"type": "integer"}

        return return_dict

    def required_parameters(self) -> list[str] or None:
        return None


if __name__ == "__main__":
    print(ContentsPageTool().name)
    print(ContentsPageTool().description)
    print(ContentsPageTool().parameters)
    print(ContentsPageTool().required_parameters)

