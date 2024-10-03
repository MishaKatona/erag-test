from src.llm.api_wrappers import OpenaiAPI, GeminiAPI, ClaudeAPI

# api = OpenaiAPI(temperature=0.2, model_name="gpt-4o-mini")
# api = ClaudeAPI(temperature=0.2)
api = GeminiAPI(temperature=0.2)

# prompt_ = "What is the capital city of France?"
# system_prompt_ = ("Respond to questions with a concise poem where the first"
#                   " letters of each line spell out the answer.")
# system_prompt_ += "Respond in json format with your answer having the key 'poem'"
# print("------- Text response -------")
# s = perf_counter()
# response = api.get_json_response(prompt_, system_prompt_)
# print(f"Time taken: {perf_counter() - s:.2f}s")
# print(response.get_as_str())
# response.print_cost()
# print()

system_prompt_v2 = """
Extract numerical values from the tabular data provided into a json format. 
For each key extract an array of values for each year. For example 
"key": ["value_of_current_year", "value_of_previous_year"]. Always return an array
for each key in the dictionary. Keep in mind that dates can either be a year 
number or a date string of various formats, there is nearly always 2 years present.
Use integers without separators for the values. Fill in the following 
template from the table provided, providing an array of integers for each key.
Exclude keys not in the table. Do not repeat descriptions:

{
    "Years": "Years of the values in each column formatted as YYYY",
    "Tangible_Assets": "Physical assets like fixtures, machinery, vehicles. AKA Fixed Assets, Property and Equipment",
    "Intangible_Assets": "Non-physical assets like software, IP, crypto. AKA Non-physical Assets, Intellectual Property",
    "Investments": "Liquid investments like stocks, securities. AKA Marketable Securities, Financial Investments",
    "Long_Term_Investments": "Non-liquid investments not easily converted to cash. AKA Non-current Investments, Fixed Investments",
    "Debtors": "Receivables due within one year. AKA Accounts Receivable, Trade Receivables",
    "Cash_At_Bank": "Cash and cash equivalents. AKA Bank Balance, Cash Reserves",
    "Current_Assets": "Total current assets. AKA Working Capital, Net Working Capital",
    "Creditors_Due_Within_One_Year": "Liabilities payable within one year. AKA Current Liabilities, Short-term Payables",
    "Creditors_Due_After_One_Year": "Liabilities payable after one year. AKA Long-term Liabilities, Non-current Liabilities",
    "Other_Provisions": "Other financial provisions. AKA Miscellaneous Provisions, Contingency Funds",
    "Net_Current_Assets": "Current assets minus current liabilities. AKA (Net) Working Capital, Current Capital",
    "Net_Assets": "Total assets minus total liabilities. AKA Net Worth, Equity",
    "Share_Capital": "Capital from share issuance. AKA Issued Capital, Equity Capital",
    "Revaluation_Reserve": "Reserve for asset revaluation. AKA Asset Revaluation Reserve, Revaluation Surplus",
    "Capital_Redemption_Reserve": "Reserve for share redemption or buyback. AKA Redemption Reserve, Share Buyback Reserve",
    "Retained_Earnings": "Accumulated retained earnings. AKA Profit and Loss Reserve, Retained Profits",
    "Total_Equity": "Sum of all equity components. AKA Shareholders' Equity, Owners' Equity"
}

Respond with {"table": false} if the passed table does not seem to be a balance 
sheet/financial statement, for example if it's the contents page. If it is a 
balance sheet then process both year in the table. There should be 2 separate years.
    """

prompt_ = """
    CONSOLIDATED STATEMENT OF FINANCIAL POSITION
AS AT 31 DECEMBER 2023
As restated  2023 2022
Note £ £
Fixed assets  1,139,705 657,702
Tangible assets 12 1,039,716 657,702
Investments 13 99,989 0
Current assets  52,427,405 46,770,501
Debtors: amounts falling due within one year 14 31,422,714 27,879,596
Cash at bank and in hand 21,004,691 18,890,905
Creditors: amounts falling due within one year 15 (38,803,171) (36,249,859)
Net current assets 13,624,234 10,520,642
Total assets less current liabilities 14,763,939 11,178,344
Provisions for liabilities  (140,000) (140,000)
Other provisions 17 (140,000) (140,000)
Net assets 14,623,939 11,038,344
Capital and reserves  14,623,939 11,038,344
Called up share capital 18 344,564 344,564
Capital redemption reserve 19 210,389 210,389
Profit and loss account 19 14,068,986 10,483,391
Equity attributable to owners of the parent Company 14,623,939 11,038,344
The financial statements were approved and authorised for issue by the board and were signed on its behalf by :
T.J. Benzecry T. Diossi"""

response = api.get_json_response(prompt_, system_prompt_v2)
response.print_as_dict()
print(response.get_time_taken())

# response = api.get_tool_response(prompt_, "",
#                                  tools=[BalanceSheetToolYears(years=[2023, 2022]),
#                                         ContentsPageTool()])
response.print_as_dict()
print(response.get_time_taken())

# prompts = [prompt_ for _ in range(10)]
# responses = api.get_async_tool_response(
#     prompts,
#     "Only use function, do not respond",
#     tools=[BalanceSheetToolYears(years=[2023, 2022]),
#            ContentsPageTool()],
# )
#
# for response in responses:
#     # response.print_as_dict()
#     print(response.get_time_taken())
#     print()
