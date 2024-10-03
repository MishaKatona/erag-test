from src.llm.tools.abc_tool import ABCTool
from src.llm.tools.field_definitions import load_json_file


class BalanceSheetToolFlat(ABCTool):

    def __init__(self, years: list[int] = None):
        """Years is a list of years that are expected in the balance sheet.
        This will improve probability that both years are extracted correctly.
        """
        self.years = years

    def name(self) -> str:
        return "extract_balance_sheet_flat"

    def description(self) -> str:
        txt = ("Processes a tabular formated string into a JSON object. The "
               "table will have a header with 'balance sheet' or 'statement "
               "of financial position' in it. The table will usually have 2 "
               "columns of values for the current and previous year. "
               "Occasionally there will be a column for the Notes, which are "
               "not relevant. Keep in mind that all values are integers with "
               "comma thousands separators. Negative values are in () "
               "parentheses. Use this if the string is a balance sheet."
               "For each parameter return the value for each year in an "
               "array. YOU MUST KEEP THE ORDER OF THE VALUES THE SAME. "
               "Each array can have at most 2 values. ONLY USE THIS FOR "
               "BALANCE SHEETS OR STATEMENT OF FINANCIAL POSITIONS. The table"
               "should contain fields such as: Assets, Liabilities, Equity, "
               "Current Assets, Investments ect. DO NOT USE FOR OTHER TYPES "
               "OF TABLES. If a table has more than 2 values for each year "
               "then it is not a balance sheet and this should not be used.")
        if self.years is not None:
            txt += (f" Return values for years {self.years}. The Years array "
                    f"must have one entry each for the years {self.years}.")
        return txt

    def parameters(self) -> dict:
        balance_sheet_fields = load_json_file("balance_sheet_fieldsV2.json")
        balance_sheet_type = {
            "Sheet_Type": {
                "description":
                    "Type of Balance Sheet / Financial Statement either "
                    "Consolidated or Company. If this is not explicitly stated "
                    "then the default is Company.",
                "enum": ["Consolidated", "Company"],
                "type": "string"
            }
        }

        for k, v in balance_sheet_fields.items():
            definition = {
                "description": v,
                "type": "array",
                "items": {"type": "integer"}
            }
            balance_sheet_fields[k] = definition

        if self.years is not None:
            balance_sheet_fields["Years"]["items"]["enum"] = self.years

        return_dict = {**balance_sheet_type, **balance_sheet_fields}

        return return_dict

    def required_parameters(self) -> list[str]:
        return ["Sheet_Type"]


if __name__ == "__main__":
    print(BalanceSheetToolFlat().name)
    print(BalanceSheetToolFlat().description)
    print(BalanceSheetToolFlat().parameters)
    print(BalanceSheetToolFlat().required_parameters)
