import json
import pandas as pd


with open("train_pairs.json", "r") as f:
    train_dict = json.load(f)

with open("eval_pairs.json", "r") as f:
    eval_dict = json.load(f)

train_anchor = list(train_dict.keys())
train_positive = list(train_dict.values())

eval_anchor = list(eval_dict.keys())
eval_positive = list(eval_dict.values())

anchors = train_anchor + eval_anchor
positives = train_positive + eval_positive

data = [anchors, positives]

df = pd.DataFrame(data).T
# set columns as anchors, positives
df = df.rename(columns={0: "anchors", 1: "positives"})

# save to csv without column
df.to_csv("train_eval_pairs.csv", index=False)



