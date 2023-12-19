import pandas as pd
import os

directory_path = "/home/"

file_paths = [
    "{}/{}".format(directory_path, f)
    for f in os.listdir(directory_path) 
    if os.path.isfile(os.path.join(directory_path, f))
]

modal_dfs = (
    pd.concat([pd.read_csv(x) for x in file_paths])
    [["metadata/description", "metadata/title", "text", "url"]]
)

for x in modal_dfs.to_dict(orient = "records"):
    content = "\n\n".join([x['url'], x['metadata/title'], x["metadata/description"], x['text']])
    with open("/home/data/{}.txt".format(x["metadata/title"]), "w") as f: f.write(content)
