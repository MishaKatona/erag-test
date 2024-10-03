from src.llm.tools.abc_tool import ABCTool
from src.llm.tools.field_definitions import load_json_file


class BalanceSheetToolNested(ABCTool):

    def __init__(self, years: list[int] = None):
        """Years is a list of years that are expected in the balance sheet.
        This will improve probability that both years are extracted correctly.
        """
        self.years = years

    def name(self) -> str:
        return "extract_balance_sheet_nested"

    def description(self) -> str:
        txt = ("Processes a tabular formated string into a JSON object. The "
               "table will have a header with 'balance sheet' or 'statement "
               "of financial position' in it. The table will usually have 2 "
               "columns of values for the current and previous year. "
               "Occasionally there will be a column for the Notes, which are "
               "not relevant. Keep in mind that all values are integers with "
               "comma thousands separators. Negative values are in () "
               "parentheses. Use this if the string is a balance sheet.")
        if self.years is not None:
            txt += (f" Return values for years {self.years}. The Years array "
                    f"must have one entry each for the years {self.years}.")
        return txt

    def parameters(self) -> dict:
        balance_sheet_fields = load_json_file("balance_sheet_fields.json")
        balance_sheet_type = {
            "Type": {
                "description":
                    "Type of Balance Sheet / Financial Statement either "
                    "Consolidated or Company. If this is not explicitly stated "
                    "then the default is Company.",
                "enum": ["Consolidated", "Company"]
            }
        }

        for k, v in balance_sheet_fields.items():
            if "type" not in v.keys():
                v["type"] = "integer"

        return_dict = {
            **balance_sheet_type,
            "Years": {
                "description": "Years for the balance sheet",
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": balance_sheet_fields,
                }
            },
        }

        if self.years is not None:
            return_dict["Years"]["enum"] = self.years,

        return return_dict

    def required_parameters(self) -> list[str]:
        return ["Type"]


if __name__ == "__main__":
    print(BalanceSheetToolNested().name)
    print(BalanceSheetToolNested().description)
    print(BalanceSheetToolNested().parameters)
    print(BalanceSheetToolNested().required_parameters)
