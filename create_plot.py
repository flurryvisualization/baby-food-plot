import datetime as dt
import os

from dotenv import load_dotenv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

load_dotenv()

DATA_FILE = "data/feed_qty.csv"
DATE_OF_BIRTH = dt.datetime.strptime(os.getenv("DATE_OF_BIRTH"), "%Y-%m-%d") # type: ignore

def create_scatterplot(df_scatter: pd.DataFrame, filename: str) -> None:

    color_axis = "xkcd:charcoal"
    color_figure = "xkcd:white"
    color_scatter = "xkcd:pine"

    custom_params = {
        # Color settings
        "figure.facecolor": color_figure,
        "figure.edgecolor": color_axis,
        "axes.facecolor": color_figure,
        "axes.edgecolor": color_axis,
        "axes.labelcolor": color_axis,
        "axes.titlecolor": color_axis,
        "xtick.color": color_axis,
        "ytick.color": color_axis,    
        "grid.color": color_axis,
        "legend.facecolor": color_figure,
        "legend.edgecolor": color_axis,
        "legend.labelcolor": color_scatter,
        "lines.markerfacecolor": color_scatter,

        # Axis location settings
        "xtick.top": True,
        "xtick.labeltop": True,
        "ytick.right": True,
        "ytick.labelright": True,
    }
        
    sns.set_theme(style="ticks", rc=custom_params)

    f, ax = plt.subplots(2, 1, figsize=(10,8), sharex=True, squeeze=True, height_ratios=[4, 1])
    f1 = sns.scatterplot(
        data=df_scatter, 
        x="WEEK", 
        y="TIJD",    
        size="Food Amount", 
        size_order=df_scatter["Food Amount"].sort_values(ascending=False).unique(), 
        color=color_scatter,
        alpha=0.75,
        edgecolor=None,
        ax=ax[0]
        )

    # Plot title
    plt.suptitle("BABY'S FIRST YEAR MILK FEEDING", color=color_axis)

    ax[0].grid(alpha=0.2)
    ax[0].set_ylim([1440, 0])
    ax[0].set_yticks(ticks=[1440, 1260, 1080, 900, 720, 540, 360, 180, 0], labels=["0:00", "21:00", "18:00", "15:00", "12:00", "09:00", "06:00", "03:00", "0:00"])
    ax[0].set_ylabel("TIME")    

    ax[0].set_xlabel("WEEKS SINCE BIRTH")   
    ax[0].xaxis.set_label_position("top") 

    legend = ax[0].legend(title="VOLUME (ml)")
    LH = legend.legend_handles
    [lh.set_color(color_scatter) for lh in LH]
    plt.setp(legend.get_title(), color=color_scatter)

    df_scatter["DAY"] = df_scatter["WEEK"] * 7
    df_line = df_scatter.groupby("DAY", as_index=False)["VOEDING"].sum()
    df_line["WEEK"] = df_line["DAY"] / 7

    sns.lineplot(
        data=df_line, # type: ignore
        x="WEEK",
        y="VOEDING",
        color=color_scatter
    )

    ax[1].grid(alpha=0.2)
    ax[1].set_xlabel("WEEKS SINCE BIRTH")
    ax[1].set_xticks(ticks=[0,1,2,4,6,8,10,12,16,20,24,28,32,36,40,44, 48, 52])
    ax[1].set_xlim([-1, 53])

    ax[1].set_ylim([0, 1250])
    ax[1].set_yticks(ticks=range(0, 1500, 250))
    ax[1].set_ylabel("VOLUME BY DAY (ml)")

    plt.tight_layout()

    f.savefig(filename, transparent=False)


def load_data() -> pd.DataFrame:

    base_df = pd.read_csv(DATA_FILE, sep=";")

    # Only select rows with a value in TIJD (TIME)
    base_df = base_df[base_df["TIJD"].notna()]

    # Combine DATE (DATUM) and TIME (TIJD) to DATETIME (DATUMTIJD) column
    base_df["DATUMTIJD"] = base_df.apply(lambda x: f'{x["DATUM"]} {x["TIJD"]}', axis=1)
    base_df["DATUMTIJD"] = pd.to_datetime(base_df["DATUMTIJD"], format='%d-%m-%Y %H:%M')

    # Get DATE and TIME from DATETIME for standardization
    df_scatter = base_df.copy().drop(columns=["DATUM", "TIJD"])
    df_scatter["DATUM"] = df_scatter["DATUMTIJD"].dt.date
    df_scatter["TIJD"] = df_scatter["DATUMTIJD"].dt.hour * 60 + df_scatter["DATUMTIJD"].dt.minute

    # Combine food quantity from breastmilk and formula to qet a single value
    df_scatter["VOEDING"] = df_scatter["FORMULEVOEDING"] + df_scatter["BORSTVOEDING"]

    # Label weeks and months relative to date of birth
    df_scatter["WEEK"] = (pd.to_datetime(df_scatter["DATUM"]) - DATE_OF_BIRTH).dt.days / 7
    df_scatter["MONTH"] = (pd.to_datetime(df_scatter["DATUM"]) - DATE_OF_BIRTH).dt.days / 30

    # Create bins of food quantity for scatter size legend
    bin_size = 100
    bin_borders = [i for i in range(0, df_scatter["VOEDING"].max()+bin_size, bin_size)]
    bin_labels = [f"{bin_border} - {bin_border + bin_size-1}" for bin_border in bin_borders[:-1]]
    df_scatter["Food Amount"] = pd.cut(df_scatter["VOEDING"], bin_borders, labels=bin_labels)

    return df_scatter

def main() -> None:

    df = load_data()
    create_scatterplot(df, "scatterplot.png")

if __name__ == "__main__":
    main()