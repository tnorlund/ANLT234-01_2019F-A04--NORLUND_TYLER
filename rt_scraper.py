import requests
from bs4 import BeautifulSoup
import pandas as pd
from pprint import pprint
import re
import os
from tqdm import tqdm
import json
import matplotlib.pyplot as plt
import datetime
import numpy as np

single_fig_size = (10, 5)
stacked_fig_size = (10, 10)


with open("novalue.json") as json_file:
    no_values = json.load(json_file)

rt_list = []

def scrape_mojo():
    base_url = "https://www.boxofficemojo.com"
    for year in range(2000, 2019):
        page = requests.get("https://www.boxofficemojo.com/weekend/by-year/{}/".format(year))
        bs = BeautifulSoup(page.text)
        rows = bs.findAll(
            "tr"
        )
        # 1. Weekend date
        # 2. Top 10 Gross
        # 3. Top 10 Gross % change
        # 4. Overall Gross
        # 5. Overall Gross % change
        # 6. Num Releases
        # 7. #1 Release
        # 8. Week Num
        text_in_rows = [
            [elem.text for elem in row.findAll("td") if not elem.text == "-"]
            for row in rows 
        #     if len(row.findAll("td")) > 0
        ]
        # 1. Weekend Link
        # 2. Top Performing Movie Link
        links_in_rows = [
            [base_url + elem.get('href') for elem in row.findAll("a")][0:2]
            for row in rows
        ]
        text_in_rows.pop(0)
        links_in_rows.pop(0)
        print("num text: {}\nnum link: {}".format(len(text_in_rows), len(links_in_rows)))
        for ii in range(len(text_in_rows)):
            text_in_rows[ii].append(links_in_rows[ii][0])
            text_in_rows[ii].append(links_in_rows[ii][1])
        weekends = [row[7] for row in text_in_rows if len(row) > 0]
        duplicates = list(set([x for x in weekends if weekends.count(x) > 1]))
        print("Found duplicate at : {}".format(duplicates))
        dup_rows = [row for row in text_in_rows if len(row) > 0 if row[7] in duplicates]
        print("Before removing duplicates, we have {} rows.".format(len(text_in_rows)))
        [text_in_rows.remove(row) for row in dup_rows if len(row) > 0 if row[7] in duplicates]
        print("After removing duplicates, we have {} rows.".format(len(text_in_rows)))
        cleaned_rows = [row for row in dup_rows if not "wknd" in row[0] if not "Day" in row[0]]
        text_in_rows = text_in_rows + cleaned_rows
        print("After cleaning, we have {} rows.".format(len(text_in_rows)))
        df = pd.DataFrame(
            {
                "weekend":[row[0] for row in text_in_rows],
                "top10gross":[int("".join(row[1][1:].split(","))) for row in text_in_rows],
                "top10percentchange":[
                    -1*float(row[2][1:-1]) if row[2][0] == "-" 
                    else float(row[2][1:-1])
                    for row in text_in_rows
                ],
                "overallgross":[int("".join(row[3][1:].split(","))) for row in text_in_rows],
                "overallpercentchange":[
                    -1*float(row[4][1:-1]) if row[4][0] == "-" 
                    else float(row[4][1:-1])
                    for row in text_in_rows
                ],
                "numreleases":[int(row[5]) for row in text_in_rows],
                "num1release":[row[6] for row in text_in_rows],
                "weeknum":[int(row[7]) for row in text_in_rows],
                "weekendlink":[row[8] for row in text_in_rows],
                "num1link":[row[9] for row in text_in_rows]
            }
        )
        df = df.sort_values('weeknum')
        df.to_csv("mojo_{}.csv".format(year))

def read_rt_data():
    for csv_file in os.listdir("rt_data"):
        df = pd.read_csv("rt_data/{}".format(csv_file))
        year = re.findall(r"rt_([0-9]+).csv", csv_file)
        if len(year) == 1:
            year = int(year[0])
        else:
            raise Exception("Could not parse file's year")
        for index, row in tqdm(df.iterrows()):
            page = requests.get(row["RTLink"])
            bs = BeautifulSoup(page.text, features="html.parser")
            scores = [elem.text.strip() for elem in bs.findAll("span", {"class": "mop-ratings-wrap__percentage"})]
            if len(scores) == 2:
                tomato_score = scores[0]
                aud_score = scores[1]
            else:
                if row["num1release"] in no_values["aud_score"]:
                    aud_score = tomato_score
                else:
                    raise Exception("Could not find all scores:\n{}\n{}\nFile: {}".format(row["num1release"], scores, csv_file))
            synopsis = bs.findAll("div", {"id": "movieSynopsis"})
            if len(synopsis) == 1:
                synopsis = synopsis[0].text.strip()
            else:
                raise Exception("Could not find all synopsis:\n{}".format(synopsis))
            meta_data = bs.findAll("li", {"class": "meta-row clearfix"})

            for data in meta_data:
                if "Rating: " in data.find("div", {"class": "meta-label subtle"}).text:
                    rating = data.find("div", {"class": "meta-value"}).text.strip()
                if "Genre: " in data.find("div", {"class": "meta-label subtle"}).text:
                    genres = [
                        {
                            "link":"https://rottentomatoes.com" + link.get('href'),
                            "text":link.text
                        } 
                        for link in data.findAll("a")
                    ]
                if "Directed By: " in data.find("div", {"class": "meta-label subtle"}).text:
                    directors = [
                        {
                            "link":"https://rottentomatoes.com" + link.get('href'),
                            "text":link.text
                        } 
                        for link in data.findAll("a")
                    ]
                if "Written By: " in data.find("div", {"class": "meta-label subtle"}).text:
                    writers = [
                        {
                            "link":"https://rottentomatoes.com" + link.get('href'),
                            "text":link.text
                        } 
                        for link in data.findAll("a")
                    ]
                if "In Theaters: " in data.find("div", {"class": "meta-label subtle"}).text:
                    date_theaters = data.find("time")['datetime']
                if "On Disc/Streaming:" in data.find("div", {"class": "meta-label subtle"}).text:
                    date_disc = data.find("time")['datetime']
                if "Runtime: " in data.find("div", {"class": "meta-label subtle"}).text:
                    runtime = data.find("div", {"class": "meta-value"}).text.strip()
                    runtime = re.findall(r"([0-9]+)\sminutes", runtime)
                    if len(runtime) == 1:
                        runtime = int(runtime[0])
                    else:
                        raise Exception("Could not parse runtime {}".format(data))
                if "Studio: " in data.find("div", {"class": "meta-label subtle"}).text:
                    studio = data.find("div", {"class": "meta-value"}).text.strip()


            rt_list.append(
                {
                    "year":year,
                    "tomato_score":int(tomato_score[:-1]),
                    "aud_score":int(aud_score[:-1]),
                    "synopsis":synopsis,
                    "rating":rating,
                    "genres":genres,
                    "directors":directors,
                    "writers":writers,
                    "date_theaters":date_theaters,
                    "date_disc":date_disc,
                    "runtime":runtime,
                    "top10gross":row["top10gross"],
                    "top10percentchange":row["top10percentchange"],
                    "overallgross":row["overallgross"],
                    "overallpercentchange":row["overallpercentchange"],
                    "numreleases":row["numreleases"],
                    "num1release":row["num1release"],
                    "weeknum":row["weeknum"],
                    "num1link":row["num1link"]
                }
            )

    with open('rt_data.json', 'w') as outfile:
        json.dump(rt_list, outfile)

def plot_aud_and_tomato_scores(year=2000):
    """
    Plots both the tomato score and the audience scores for a specific year.

    Parameters
    ----------
    year : int
        The year used to compare the two different scores

    Raises
    ------
    - When the given year is not found in the data
    """
    with open("rt_data.json") as json_file:
        datas = json.load(json_file)
        
    year_data = [data for data in datas if data["year"] == year]
    if len(year_data) < 1:
        raise Exception("Could not find all the recordings for the year")
    df = pd.DataFrame(
        {
            "week": [data["weeknum"] for data in year_data],
            "aud_score": [data["aud_score"] for data in year_data],
            "tomato_score": [data["tomato_score"] for data in year_data],
            "movie_name": [data["num1release"] for data in year_data]
        }
    )
    fig, (a0, a1) = plt.subplots(2, 1, figsize=stacked_fig_size)
    a0.plot(df["week"], df["aud_score"])
    a1.plot(df["week"], df["tomato_score"])
    a0.set_title("Audience Score {}".format(year), fontsize=20, y=0.95)
    a1.set_title("Tomato Score {}".format(year), fontsize=20, y=0.95)

    for ax in [a0, a1]:
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')
        ax.set_xlabel("Week in Year", fontsize=15, y=1.05)
        ax.set_ylabel("Percentage", fontsize=15)
    plt.savefig("graphs/aud_and_tomato_{}.png".format(year), bbox_inches="tight")
    plt.close()

def plot_diff_in_scores_year(year=2000):
    with open("rt_data.json") as json_file:
        datas = json.load(json_file)
        
    year_data = [data for data in datas if data["year"] == year]
    df = pd.DataFrame(
        {
            "week": [data["weeknum"] for data in year_data],
            "aud_score": [data["aud_score"] for data in year_data],
            "tomato_score": [data["tomato_score"] for data in year_data],
            "movie_name": [data["num1release"] for data in year_data]
        }
    )
    fig, ax = plt.subplots(1, 1, figsize=single_fig_size)
    ax.plot(df["week"], df["aud_score"] - df["tomato_score"])
    ax.axhline(y=0, color='k', linestyle='-', linewidth=1)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.set_xlabel("Week in Year", fontsize=15, y=1.05)
    ax.set_ylabel("Difference in Score", fontsize=15)
    ax.set_title("Score Difference {}".format(year), fontsize=20)
    plt.savefig("graphs/score_diff_{}.png".format(year), bbox_inches="tight")
    plt.close()

def plot_diff_in_decades():
    with open("rt_data.json") as json_file:
        datas = json.load(json_file)
    aud_score_year = []
    avg_year = []
    for year in range(2000, 2010):
        year_data = [data for data in datas if data["year"] == year]
        df = pd.DataFrame(
            {
                "week": [data["weeknum"] for data in year_data],
                "aud_score": [data["aud_score"] for data in year_data],
                "tomato_score": [data["tomato_score"] for data in year_data],
                "movie_name": [data["num1release"] for data in year_data]
            }
        )
        aud_score_year.append((df["aud_score"] - df["tomato_score"]).tolist())
        avg_year.append(np.average((df["aud_score"] - df["tomato_score"]).tolist()))

    fig, ax = plt.subplots(1, 1, figsize=single_fig_size)
    ax.violinplot(aud_score_year)
    ax.plot(range(1, len(avg_year)+1), avg_year, label="Average")
    ax.set_xticklabels(
        [
            list(range(1999, 2014))[int(loc)] 
            for loc in [ 0,  2,  4,  6,  8, 10, 12]
        ], 
        fontsize = 12, 
        rotation=0
    )
    ax.axhline(y=0, color='k', linestyle='-', linewidth=1)
    ax.set_xlabel("Year", fontsize=15, y=1.05)
    ax.set_ylabel("Difference in Score", fontsize=15)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.set_title("Score Differences 2000-2009", fontsize=20)
    ax.tick_params(axis="y", labelsize=12)
    plt.legend()
    plt.savefig("graphs/score_diff_2000-2009.png".format(year), bbox_inches="tight")
    plt.close()
    aud_score_year = []
    avg_year = []
    for year in range(2010, 2020):
        year_data = [data for data in datas if data["year"] == year]
        df = pd.DataFrame(
            {
                "week": [data["weeknum"] for data in year_data],
                "aud_score": [data["aud_score"] for data in year_data],
                "tomato_score": [data["tomato_score"] for data in year_data],
                "movie_name": [data["num1release"] for data in year_data]
            }
        )
        aud_score_year.append((df["aud_score"] - df["tomato_score"]).tolist())
        avg_year.append(np.average((df["aud_score"] - df["tomato_score"]).tolist()))

    fig, ax = plt.subplots(1, 1, figsize=single_fig_size)
    ax.violinplot(aud_score_year)
    ax.plot(range(1, len(avg_year)+1), avg_year, label="Average")
    ax.set_xticklabels(
        [
            list(range(2009, 2024))[int(loc)]
            for loc in [ 0,  2,  4,  6,  8, 10, 12]
        ], 
        fontsize = 12, 
        rotation=0
    )
    ax.axhline(y=0, color='k', linestyle='-', linewidth=1)
    ax.set_xlabel("Year", fontsize=15, y=1.05)
    ax.set_ylabel("Difference in Score", fontsize=15)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.set_title("Score Differences 2010-2019", fontsize=20)
    ax.tick_params(axis="y", labelsize=12)
    plt.legend()
    plt.savefig("graphs/score_diff_2010-2019.png".format(year), bbox_inches="tight")
    plt.close()

def plot_average_score_diff():
    with open("rt_data.json") as json_file:
        datas = json.load(json_file)
    std_year = []
    avg_year = []
    for year in range(2000, 2020):
        year_data = [data for data in datas if data["year"] == year]
        df = pd.DataFrame(
            {
                "week": [data["weeknum"] for data in year_data],
                "aud_score": [data["aud_score"] for data in year_data],
                "tomato_score": [data["tomato_score"] for data in year_data],
                "movie_name": [data["num1release"] for data in year_data]
            }
        )
        diff = (df["aud_score"] - df["tomato_score"]).tolist()
        std_year.append(np.std(diff))
        avg_year.append(np.average(diff))
    fig, ax = plt.subplots(1, 1, figsize=single_fig_size)

    ax.plot(range(len(avg_year)), avg_year, label="AVG")
    ax.xaxis.set_ticks(range(0, 20))
    fig.canvas.draw()
    ax.set_xticklabels(ax.get_xticks())
    ax.set_xticklabels(
        [
            "'0" + item.get_text() if int(item.get_text()) < 10 
            else "'" + item.get_text() 
            for item in ax.get_xticklabels()
        ]
    )
    # ax.legend()
    ax.set_title("Average Score Differences", fontsize=20)
    ax.tick_params(axis="y", labelsize=12)
    ax.tick_params(axis="x", labelsize=12)
    ax.set_xlabel("Year", fontsize=15, y=1.05)
    ax.set_ylabel("Difference in Score", fontsize=15)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    plt.savefig("graphs/average_score_diff.png".format(year), bbox_inches="tight")
    plt.close()

def plot_top10_gross_in_decades():
    with open("rt_data.json") as json_file:
        datas = json.load(json_file)
    top10gross = []
    top10gross_avg = []
    for year in range(2000, 2010):
        year_data = [data for data in datas if data["year"] == year]
        df = pd.DataFrame(
            {
                "week": [data["weeknum"] for data in year_data],
                "top10gross": [data["top10gross"] for data in year_data]
            }
        )
        top10gross.append((df["top10gross"]/1_000_000).tolist())
        top10gross_avg.append(
            np.average(df["top10gross"].tolist())/1_000_000
        )

    fig, ax = plt.subplots(1, 1, figsize=single_fig_size)
    ax.violinplot(top10gross)
    ax.plot(range(1, len(top10gross_avg)+1), top10gross_avg, label="Average")
    ax.set_xticklabels(ax.get_xticks())
    ax.set_yticklabels(ax.get_yticks())
    ax.set_xticklabels(
        [
            list(range(1999, 2014))[int(loc)]
            for loc in [ 0,  2,  4,  6,  8, 10, 12]
        ], 
        fontsize = 12, 
        rotation=0
    )
    ax.set_yticklabels(
        [
            "" if item.get_text() == "0.0" 
            else"$" + str(int(float(item.get_text())))
            for item in ax.get_yticklabels()
        ]
    )
    ax.set_xlabel("Year", fontsize=15, y=1.05)
    ax.set_ylabel("Total Gross\n(Millions)", fontsize=15)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.set_title("Top 10 Grossing Films 2000-2009", fontsize=20)
    ax.tick_params(axis="y", labelsize=12)
    plt.legend()
    plt.savefig("graphs/top_10_gross_2000-2009.png".format(year), bbox_inches="tight")
    plt.close()
    top10gross = []
    top10gross_avg = []
    for year in range(2010, 2020):
        year_data = [data for data in datas if data["year"] == year]
        df = pd.DataFrame(
            {
                "week": [data["weeknum"] for data in year_data],
                "top10gross": [data["top10gross"] for data in year_data]
            }
        )
        top10gross.append((df["top10gross"]/1_000_000).tolist())
        top10gross_avg.append(
            np.average(df["top10gross"].tolist())/1_000_000
        )

    fig, ax = plt.subplots(1, 1, figsize=single_fig_size)
    ax.violinplot(top10gross)
    ax.plot(range(1, len(top10gross_avg)+1), top10gross_avg, label="Average")
    ax.set_xticklabels(ax.get_xticks())
    ax.set_yticklabels(ax.get_yticks())
    ax.set_xticklabels(
        [
            list(range(2009, 2024))[int(loc)]
            for loc in [ 0,  2,  4,  6,  8, 10, 12]
        ], 
        fontsize = 12, 
        rotation=0
    )
    ax.set_yticklabels(
        [
            "" if item.get_text() == "0.0" 
            else"$" + str(int(float(item.get_text())))
            for item in ax.get_yticklabels()
        ]
    )
    ax.set_xlabel("Year", fontsize=15, y=1.05)
    ax.set_ylabel("Total Gross\n(Millions)", fontsize=15)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.set_title("Top 10 Grossing Films 2010-2019", fontsize=20)
    ax.tick_params(axis="y", labelsize=12)
    plt.legend()
    plt.savefig("graphs/top_10_gross_2010-2019.png".format(year), bbox_inches="tight")
    plt.close()

def plot_average_top10_gross():
    with open("rt_data.json") as json_file:
        datas = json.load(json_file)
    top10gross_avg = []
    for year in range(2000, 2020):
        year_data = [data for data in datas if data["year"] == year]
        df = pd.DataFrame(
            {
                "week": [data["weeknum"] for data in year_data],
                "top10gross": [data["top10gross"] for data in year_data]
            }
        )
        top10gross_avg.append(
            np.average(df["top10gross"].tolist())/1_000_000
        )
    fig, ax = plt.subplots(1, 1, figsize=single_fig_size)
    ax.plot(range(len(top10gross_avg)), top10gross_avg, label="AVG")
    ax.xaxis.set_ticks(range(0, 20))
    ax.set_xticklabels(ax.get_xticks())
    ax.set_yticklabels(ax.get_yticks())
    ax.set_xticklabels(
        [
            "'0" + item.get_text() if int(item.get_text()) < 10 
            else "'" + item.get_text() 
            for item in ax.get_xticklabels()
        ]
    )
    ax.set_yticklabels(
        [
            "" if item.get_text() == "0.0" 
            else"$" + str(int(float(item.get_text())))
            for item in ax.get_yticklabels()
        ]
    )
    ax.set_title("Average Top 10 Grossing", fontsize=20)
    ax.tick_params(axis="y", labelsize=12)
    ax.tick_params(axis="x", labelsize=12)
    ax.set_xlabel("Year", fontsize=15, y=1.05)
    ax.set_ylabel("Total Gross\n(Millions)", fontsize=15)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    plt.savefig("graphs/top_10_gross_avg.png".format(year), bbox_inches="tight")
    plt.close()

def plot_top10_gross_year(year=2000):
    with open("rt_data.json") as json_file:
        datas = json.load(json_file)
    year_data = [data for data in datas if data["year"] == year]
    df = pd.DataFrame(
        {
            "week": [data["weeknum"] for data in year_data],
            "top10gross": [data["top10gross"] for data in year_data]
        }
    )
    fig, ax = plt.subplots(1, 1, figsize=single_fig_size)
    ax.plot(df["week"].astype(int), df["top10gross"]/1_000_000)
    ax.set_xticklabels(ax.get_xticks())
    ax.set_yticklabels(ax.get_yticks())
    ax.set_yticklabels(
        [
            "" if item.get_text() == "0.0" 
            else"$" + str(int(float(item.get_text())))
            for item in ax.get_yticklabels()
        ]
    )
    ax.set_xticklabels(
        [
            str(int(float(item.get_text())))
            for item in ax.get_xticklabels()
        ]
    )
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.set_xlabel("Week in Year", fontsize=15, y=1.05)
    ax.set_ylabel("Total Gross\n(Millions)", fontsize=15)
    ax.set_title("Average Top 10 Grossing {}".format(year), fontsize=20)
    plt.savefig("graphs/top_10_gross_{}.png".format(year), bbox_inches="tight")
    plt.close()

def plot_top10_gross_all():
    with open("rt_data.json") as json_file:
        datas = json.load(json_file)

    fig, ax = plt.subplots(1, 1, figsize=single_fig_size)
    for year in range(2000, 2020):
        year_data = [data for data in datas if data["year"] == year]
        df = pd.DataFrame(
            {
                "week": [data["weeknum"] for data in year_data],
                "top10gross": [data["top10gross"] for data in year_data]
            }
        )
        ax.plot(df["week"].astype(int), df["top10gross"]/1_000_000, c=u'#1f77b4')

    ax.text(17+0.75, 357_115_007/1_000_000, "Endgame")
    ax.scatter(17-0.02, 357_115_007/1_000_000)
    ax.set_xticklabels(ax.get_xticks())
    ax.set_yticklabels(ax.get_yticks())
    ax.set_yticklabels(
        [
            "" if item.get_text() == "0.0" 
            else"$" + str(int(float(item.get_text())))
            for item in ax.get_yticklabels()
        ]
    )
    ax.set_xticklabels(
        [
            str(int(float(item.get_text())))
            for item in ax.get_xticklabels()
        ]
    )
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.set_xlabel("Week in Year", fontsize=15, y=1.05)
    ax.set_ylabel("Total Gross\n(Millions)", fontsize=15)
    ax.set_title("Average Top 10 Grossing", fontsize=20)
    plt.savefig("graphs/top_10_gross_all.png".format(year), bbox_inches="tight")
    plt.close()

def average_tomato_score_all():
    with open("rt_data.json") as json_file:
        datas = json.load(json_file)
    tomato_scores = []
    for year in range(2000, 2020):
        year_data = [data for data in datas if data["year"] == year]
        df = pd.DataFrame(
            {
                "week": [data["weeknum"] for data in year_data],
                "tomato_score": [data["tomato_score"] for data in year_data],
                "movie_name": [data["num1release"] for data in year_data]
            }
        )
        tomato_scores.append(np.average(df["tomato_score"].tolist()))
    fig, ax = plt.subplots(1, 1, figsize=single_fig_size)

    ax.plot(range(len(tomato_scores)), tomato_scores, label="AVG")
    ax.xaxis.set_ticks(range(0, 20))
    ax.set_xticklabels(ax.get_xticks())
    ax.set_yticklabels(ax.get_yticks())
    ax.set_xticklabels(
        [
            "'0" + item.get_text() if int(item.get_text()) < 10 
            else "'" + item.get_text() 
            for item in ax.get_xticklabels()
        ]
    )
    ax.set_yticklabels(
        [
            str(int(float(item.get_text()))) + "%" 
            for item in ax.get_yticklabels()
        ]
    )
    ax.set_title("Average Yearly Tomato Scores\nof Best Weekend Films", fontsize=20)
    ax.tick_params(axis="y", labelsize=12)
    ax.tick_params(axis="x", labelsize=12)
    ax.set_xlabel("Year", fontsize=15, y=1.05)
    ax.set_ylabel("Average Tomato Scores", fontsize=15)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    plt.savefig("graphs/tomato_score_all.png", bbox_inches="tight")
    plt.close()

def average_aud_score_all():
    with open("rt_data.json") as json_file:
        datas = json.load(json_file)
    aud_scores = []
    for year in range(2000, 2020):
        year_data = [data for data in datas if data["year"] == year]
        df = pd.DataFrame(
            {
                "week": [data["weeknum"] for data in year_data],
                "aud_score": [data["aud_score"] for data in year_data],
                "movie_name": [data["num1release"] for data in year_data]
            }
        )
        aud_scores.append(np.average(df["aud_score"].tolist()))
    fig, ax = plt.subplots(1, 1, figsize=single_fig_size)

    ax.plot(range(len(aud_scores)), aud_scores, label="AVG")
    ax.xaxis.set_ticks(range(0, 20))
    ax.set_xticklabels(ax.get_xticks())
    ax.set_yticklabels(ax.get_yticks())
    ax.set_xticklabels(
        [
            "'0" + item.get_text() if int(item.get_text()) < 10 
            else "'" + item.get_text() 
            for item in ax.get_xticklabels()
        ]
    )
    ax.set_yticklabels(
        [
            str(int(float(item.get_text()))) + "%" 
            for item in ax.get_yticklabels()
        ]
    )
    # ax.legend()
    ax.set_title("Average Yearly Audience Scores\nof Best Weekend Films", fontsize=20)
    ax.tick_params(axis="y", labelsize=12)
    ax.tick_params(axis="x", labelsize=12)
    ax.set_xlabel("Year", fontsize=15, y=1.05)
    ax.set_ylabel("Average Tomato Scores", fontsize=15)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    plt.savefig("graphs/aud_score_all.png", bbox_inches="tight")
    plt.close()

[plot_aud_and_tomato_scores(year) for year in range(2000,2020)]
[plot_diff_in_scores_year(year) for year in range(2000,2020)]
[plot_top10_gross_year(year) for year in range(2000,2020)]
plot_diff_in_decades()
plot_average_score_diff()
plot_top10_gross_in_decades()
plot_average_top10_gross()
plot_top10_gross_all()
average_tomato_score_all()
average_aud_score_all()
