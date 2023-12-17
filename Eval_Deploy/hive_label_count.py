import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random


def get_random_color():
    r = lambda: random.randint(0, 255)
    color = "#%02X%02X%02X" % (r(), r(), r())
    return color


count_dict = dict()

with open("prediction.json") as f:
    data = json.load(f)
    columns = data["columns"]
    rows = data["data"]
    for row in rows:
        labels = json.loads(row[2])
        for label in labels:
            if label["class"] in count_dict:
                count_dict[label["class"]] += 1
            else:
                count_dict[label["class"]] = 1

df = pd.DataFrame([count_dict])
df.to_csv("label_count_hive.csv")
list_color = [0] * 18
ax = df.plot(
    kind="bar",
    color=['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080'],
)
get_random_color()
# plt.xlabel('xlabel')
for p in ax.patches:
    height = p.get_height()
    if np.isnan(height):
        height = 0
    ax.text(
        p.get_x() + p.get_width() / 2.0,
        height,
        "%d" % round(height),
        fontsize=8,
        color="red",
        ha="center",
        va="bottom",
    )
plt.show()
