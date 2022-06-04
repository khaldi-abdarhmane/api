# don't print warning in console
import warnings
warnings.filterwarnings("ignore")

import os
from pathlib import Path
import argparse

import pandas as pd
import matplotlib.pyplot as plt

# get args of cmd
parser = argparse.ArgumentParser(description="explore dataset")
parser.add_argument(
    "train_data_path",
    metavar="train_data_path",
    type=str,
    help=" the path of training dataset",
)
parser.add_argument(
    "validation_data_path",
    metavar="validation_data_path",
    type=str,
    help=" the path of validation dataset",
)
parser.add_argument(
    "plot_path",
    metavar="plot_path",
    type=str,
    help="path for stock plots of exploratory",
)
args = parser.parse_args()

train_data_path = args.train_data_path
validation_data_path = args.validation_data_path
plot_path = args.plot_path

# create the folder that stock plots
Path(plot_path).mkdir(parents=True, exist_ok=True)


lists = os.listdir(train_data_path)
diseases = []
crops = []
file_lst = []
for folder in lists:
    files = os.listdir(os.path.join(train_data_path, folder))
    files = [folder + "/" + file for file in files]
    file_lst.extend(files)
    if folder != "background":
        diseases.extend([folder for i in range(len(files))])
        crops.extend([folder.split(sep="___")[0] for i in range(len(files))])
train_df = pd.DataFrame(
    list(zip(file_lst, crops, diseases)), columns=["Paths", "Crops", "Diseases"]
)

fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(20, 8))
with plt.style.context("ggplot"):
    train_df["Crops"].value_counts().plot(
        kind="pie", title="Validation data", ax=axes[0], subplots=True
    )
    train_df["Diseases"].value_counts().plot(
        kind="bar", color="C1", title="Validation data", ax=axes[1], subplots=True
    )

plt.savefig(os.path.join(plot_path, "train.png"))

lists = os.listdir(validation_data_path)
diseases = []
crops = []
file_lst = []
for folder in lists:
    files = os.listdir(os.path.join(validation_data_path, folder))
    files = [folder + "/" + file for file in files]
    file_lst.extend(files)
    if folder != "background":
        diseases.extend([folder for i in range(len(files))])
        crops.extend([folder.split(sep="___")[0] for i in range(len(files))])
validation_df = pd.DataFrame(
    list(zip(file_lst, crops, diseases)), columns=["Paths", "Crops", "Diseases"]
)

fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(20, 8))
with plt.style.context("ggplot"):
    validation_df["Crops"].value_counts().plot(
        kind="pie", title="Validation data", ax=axes[0], subplots=True
    )
    validation_df["Diseases"].value_counts().plot(
        kind="bar", color="C1", title="Validation data", ax=axes[1], subplots=True
    )

plt.savefig(os.path.join(plot_path, "valid.png"))
