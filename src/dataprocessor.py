import datetime
from pathlib import Path
import pandas as pd
from nltk.corpus import stopwords

rootpath_to_files = "/Users/isaacduong/nodejs/"


def clean_fetched_data(
    date: str,
    no_letter: int,
    rootpath_to_files: str = "/Users/isaacduong/nodejs/",
    geo: str = "en",
    marketplace: str = "amazon",
):

    """function to clean the fetched data
    Args:

    rootpath_to_files (string): directory containing all the files

    date (string): date of the data, when the data was retrieved
        format year-month-date e.g 2022-5-10

    no_letter (int): length of seed letters used to retrieve the data
        only 2,3 or 4 are supported

    geo (string): country, where the data was retrieved from
        e.g 'de' or 'en'

    marketplace (string):  'amazon' or ' ebay' are supported

    Returns
    pandas dataframe

    """
    if (
        not geo in ["de", "en"]
        or not marketplace in ["amazon", "ebay"]
        or not no_letter in [2, 3, 4]
    ):
        raise ValueError("Invalid, please read the documentation for help")

    filepath = Path(rootpath_to_files) / Path(
        "%s/%s_%s_kwf%slets_%s.csv" % (date, marketplace, geo, no_letter, date)
    )
    df = pd.read_csv(filepath, names=["keyword"], header=None, on_bad_lines="skip")
    # eliminate duplicates
    df.drop_duplicates(inplace=True, ignore_index=True)
    # split keyword and rank
    df = df.keyword.str.split(":rank", expand=True)
    df.columns = ["keyword", "rank"]
    df["rank"] = df["rank"].astype(int)
    # delete row with rank 51,52,41,42,31,32
    if no_letter == 4:
        index_to_drop = df.loc[df["rank"].isin([50, 51, 52])].index
    elif no_letter == 3:
        index_to_drop = df.loc[df["rank"].isin([40, 41, 42])].index
    elif no_letter == 2:
        index_to_drop = df.loc[df["rank"].isin([30, 31, 32])].index
    df.drop(index=index_to_drop, inplace=True)
    # select last duplicate
    index_dup = df.keyword.drop_duplicates().index
    df = df.loc[index_dup, :]
    # eliminate stopwords
    # stops=stopwords.words('english')
    # df['keyword']=df['keyword'].apply(lambda w :' '.join([x for x in w.split() if x not in stops]))
    df["splitted_keyword"] = df.loc[:, "keyword"].str.split()
    # count length of keywords
    df["len_keyword"] = df.loc[:, "splitted_keyword"].apply(lambda li: len(li))
    # select keywords with count more than one
    df = df[df["len_keyword"] > 1]

    return df


def concat_data_of_2days(
    recent_day,
    previous_day,
    no_letter=4,
    geo="en",
    marketplace="amazon",
):
    """function concatenating data of two days and presenting the search trend of every keyword

    Args:
        recent_day (string): of format year-month-day
            e.g 2022-7-20
        previous_day (string):of format year-month-day
        rootpath_to_files (str): directory to all files containing retrieved data.
        no_letter (int, optional): length of seed keyword. Defaults to 4.
        geo (str, optional): 'en' and 'de' are supported. Defaults to "en".
        marketplace (str, optional): only 'amazon' and 'ebay' are supported. Defaults to "amazon".

    Returns:
        pandas dataframe: dataframe of processed and concated data
    """

    data_previous = clean_fetched_data(previous_day, no_letter)
    data_recent = clean_fetched_data(recent_day, no_letter)

    # concatenate dataframes
    data_concated = data_recent.set_index("keyword").join(
        data_previous.set_index("keyword"),
        on="keyword",
        lsuffix=" recent_day",
        rsuffix=" last_day",
    )
    # create reversed trend column
    data_concated["trends"] = (
        data_concated["rank last_day"] - data_concated["rank recent_day"]
    )
    # create trend column, consider the number of initiate search letter

    # only interested in positive trend > 0
    data_concated.loc[data_concated["trends"] > 0].sort_values(
        "trends", ascending=False
    )[:50]

    return data_concated


def get_full_processed_data_of_date(date, rootpath, geo="en", marketplace="amazon"):
    """function to get full processed data retrieved from all seed keywords of one day

    Args:
        date (string): date when to get full processed data
        rootpath (string): path to the root folder
        geo (str, optional): 'en' and 'de' are supported . Defaults to 'en'.
        marketplace (str, optional): 'amazon' and 'ebay' are supported . Defaults to 'amazon'.

    Returns:
        list: of all keywords retrieved
        pandas dataframe: full processed data
    """

    data_f2_letters = clean_fetched_data(date, 2, rootpath, geo, marketplace)
    data_f3_letters = clean_fetched_data(date, 3, rootpath, geo, marketplace)
    data_f4_letters = clean_fetched_data(date, 4, rootpath, geo, marketplace)

    full_df = pd.concat([data_f2_letters, data_f3_letters, data_f4_letters])
    # all keywords of this date
    keywords = full_df.keyword.tolist()
    keywords = [kw.replace("/", " ").replace("'", "") for kw in keywords]

    return keywords, full_df


def truncated_keywords(words):

    """function to truncate keywords from long tail keywords to 2 or 3-words keywords

    Args:
        words (list): list of keywords to truncate

    Returns:
        list: list of truncated keywords
    """

    keywords = []
    stops = stopwords.words("english")
    for kw in words:
        if len(kw.split()) <= 3:
            keywords.append(kw)
        elif len(kw.split()) > 3:
            kw = " ".join([w for w in kw.split() if w not in stops])
            if len(kw.split()) > 3:
                kw = kw.split()[0] + " " + kw.split()[1] + " " + kw.split()[2]

            keywords.append(kw)
    keywords.sort()

    return list(set(keywords))


def write_keywords_file(keywords, filepath):
    """function to write keywords file

    Args:
        keywords (list): list of keywords to write
        filepath (string): file path to write keywords to
    """
    with open(filepath, "a+") as file:
        file.seek(0)
        words_in_file = file.readlines()
        for kw in keywords:
            if (kw + "\n") not in words_in_file:
                file.write("%s\n" % kw)


def append_new_appeared_keywords(rootpath):
    """function that append new keywords to file

    Args:
        rootpath (string): root directory
    """

    keywords = []
    today_date = datetime.now().strftime("%Y-%-m-%-d")
    keywords_today, _ = get_full_processed_data_of_date(today_date, rootpath)
    today_day = datetime.now().strftime("%-d")

    if int(today_day) < 15:
        filepath = (
            Path(rootpath)
            / Path(datetime.now().strftime("%Y-%-m-%" + "1"))
            / Path("googletrends/googletrends_keywords.csv")
        )
        for i in range(1, int(today_day)):
            date = datetime.now().strftime("%Y-%-m") + "-" + str(i)
            keywords_, _ = get_full_processed_data_of_date(date, rootpath)
            keywords.extend(keywords_)
    else:
        filepath = (
            Path(rootpath)
            / Path(datetime.now().strftime("%Y-%-m-%" + "15"))
            / Path("googletrends/googletrends_keywords.csv")
        )
        for i in range(15, int(today_day)):
            date = datetime.now().strftime("%Y-%-m") + "-" + str(i)
            keywords_, _ = get_full_processed_data_of_date(date, rootpath)
            keywords.extend(keywords_)

    new_keywords = list(set(keywords_today).difference(set(keywords)))
    new_keywords = truncated_keywords(new_keywords)
    new_keywords.sort()
    print(len(new_keywords))
    write_keywords_file(new_keywords, filepath)
    print("writing keywords to file successfully")

    return
