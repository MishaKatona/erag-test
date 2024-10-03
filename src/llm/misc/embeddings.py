from openai import OpenAI
from config import OPENAI_API_KEY, GCP_API_KEY
from time import perf_counter
import google.generativeai as genai


genai.configure(api_key=GCP_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)


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

s = perf_counter()
response = openai_client.embeddings.create(
    input=[prompt_ for _ in range(10)],
    model="text-embedding-3-small"
)
t = perf_counter() - s
print(t)

print(len(response.data))


# s = perf_counter()
# response = genai.embed_content(
#     content=[prompt_ for _ in range(10)],
#     model="models/text-embedding-004"
# )
# t = perf_counter() - s
# print(t)

# print(response)
