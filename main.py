import argparse
import sys
import re
import time
import random
import requests
import pandas as pd
from random import choice
from bs4 import BeautifulSoup as bs


def parse_args():
    parser = argparse.ArgumentParser(description="Search articles based on keywords")
    parser.add_argument(
        "--update_venue_list",
        type=bool,
        default=False,
        choices=[True, False]
    )
    parser.add_argument(
        "--v_n",
        "--venue_name",
        type=str,
        default=["UIST"],
        nargs="+",
        choices=["CHI", "ASSETS", "UIST", "IMWUT", "TEI", "IDC", "DIS", "CSCW"],
        # required=True,
        help="Enter the name of the venues to be searched. For example, CHI, ASSETS, UIST. This part is required."
    )
    parser.add_argument(
        "--k_l",
        "--keyword_list",
        type=str,
        default="keyword.txt",
        # required=True,
        help="Enter the name of keyword list file. It must be txt file."
    )
    args = parser.parse_args()
    return args


def pull_venue_list(arg):
    if "UIST" in arg.v_n:
        url = "https://dl.acm.org/conference/uist/proceedings"
        http = random_useragent(url)
        soup = bs(http, 'lxml')
        uist_list = soup.find_all(href=re.compile("/doi/proceedings/10.1145"))
        with open('uist_list.txt', 'w') as f:
            for line in uist_list:
                f.write(f"{line}\n")
    if "CHI" in arg.v_n:
        url = "https://dl.acm.org/conference/chi/proceedings"
        http = random_useragent(url)
        soup = bs(http, 'lxml')
        chi_list = soup.find_all(href=re.compile("/doi/proceedings/"))
        with open('chi_list.txt', 'w') as f:
            for line in chi_list:
                f.write(f"{line}\n")
    if "ASSETS" in arg.v_n:
        url = "https://dl.acm.org/conference/assets/proceedings"
        http = random_useragent(url)
        soup = bs(http, 'lxml')
        assets_list = soup.find_all(href=re.compile("/doi/proceedings/10.1145"))
        with open('assets_list.txt', 'w') as f:
            for line in assets_list:
                f.write(f"{line}\n")


def random_sleep_1s(mu=1.1, sigma=0.4):
    secs = random.normalvariate(mu, sigma)
    if secs <= 0:
        secs = mu
    time.sleep(secs)


def random_useragent(url):
    HEADERS = {
        'User-Agent': 'Mozilla/5.0'
    }
    UAS = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
        'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36'
    ]
    HEADERS['User-Agent'] = choice(UAS)
    random_sleep_1s(mu=1.1, sigma=0.4)
    http = requests.get(url, headers=HEADERS).content
    return http


def save_paper_to_dict(venue, doi, title, abstract):
    print("========Got Paper=========")
    print(venue)
    print(title)
    print(doi)
    print(abstract)
    print("========Paper End=========")
    dict_back = {"Venue": venue, "Title": title, "Abstract": abstract, "DOI": doi}
    return dict_back


def find_paper_detail(paper_venue, paper_item):
    paper_title = str(paper_item).split('">')[2][:-9]
    paper_doi = "https://dl.acm.org" + str(paper_item).split(">")[1][9:][:-1]
    paper_html = random_useragent(paper_doi)
    soup_paper_html = bs(paper_html, 'lxml')
    paper_abstract_raw = soup_paper_html.find_all("div", class_="abstractSection abstractInFull")
    if not paper_abstract_raw:
        paper_abstract = "No abstract available for this paper."
    else:
        paper_abstract = str(paper_abstract_raw[0]).split("p>")[1][:-2]
    paper_dict = save_paper_to_dict(paper_venue, paper_doi, paper_title, paper_abstract)
    return paper_dict


def get_uist_paper():
    try:
        f = open("uist_list.txt", "r")
    except (Exception,):
        sys.exit("UIST list not found, please update venue list.")
    uist_dataframe = pd.DataFrame(columns=['Venue', 'Title', 'Abstract', 'DOI'])
    for lines in f:
        print("Lines read in txt file: ", lines)  # This line is for testing purpose
        if "Adjunct" not in lines and lines != "\n":
            paper_venue = lines[(lines.find(">UIST")):(lines.find("</a>"))][1:]
            print("Paper venue name: ", paper_venue)  # This line is for testing purpose
            year_str = paper_venue[(paper_venue.find("'")):(paper_venue.find(":"))][1:]
            print("Years: ", year_str)  # This line is for testing purpose
            try:
                year = int(year_str)
            except (Exception,):
                uist_dataframe.to_csv('uist_paper_data.csv', index=False)
                sys.exit("Can Not locate venue year number, check program code.")
            url = lines.split('"')[1]
            if year in range(1, 50, 1):  # Check the year if that is from 2001 to present (2050),
                url = "https://dl.acm.org" + url + "?tocHeading=heading"
                i = 1  # Section number
                while i < 30:  # Section number less than 30.
                    str_i = str(i)
                    data_url = url + str_i
                    print(data_url)  # This line is for testing purpose
                    venue_yearly = random_useragent(data_url)
                    soup_venue_yearly = bs(venue_yearly, 'lxml')
                    paper_list_yearly = soup_venue_yearly.find_all("h5", class_="issue-item__title")
                    # print(paper_list_yearly)
                    for paper_item in paper_list_yearly:
                        uist_dataframe.loc[len(uist_dataframe)] = find_paper_detail(paper_venue, paper_item)
                    if paper_list_yearly:
                        i = i + 1
                        # break  # This line is for testing purpose
                    else:
                        print("All papers has been catch in this year UIST")
                        break
                # break  # This line is for testing purpose
            else:
                data_url = "https://dl.acm.org" + url
                # print(data_url)  # This line is for testing purpose
                venue_yearly = random_useragent(data_url)
                soup_venue_yearly = bs(venue_yearly, 'lxml')
                paper_list_yearly = soup_venue_yearly.find_all("h5", class_="issue-item__title")
                # print(paper_list_yearly)
                for paper_item in paper_list_yearly:
                    # print(paper_item)
                    uist_dataframe.loc[len(uist_dataframe)] = find_paper_detail(paper_venue, paper_item)
                    # break  # This line is for testing purpose
                print("All papers has been catch in this year UIST")
                # break  # This line is for testing purpose
        else:
            pass
    uist_dataframe.to_csv('uist_paper_data.csv', index=False)


def get_chi_paper():
    try:
        f = open("chi_list.txt", "r")
    except (Exception,):
        sys.exit("CHI list not found, please update venue list.")
    chi_dataframe = pd.DataFrame(columns=['Venue', 'Title', 'Abstract', 'DOI'])
    for lines in f:
        # print("Lines read in txt file: ", lines)  # This line is for testing purpose
        if '<a href="/doi/proceedings' and 'Proceedings of the' in lines:
            paper_venue = lines[(lines.find(">CHI")):(lines.find("</a>"))][1:]
            year_str = paper_venue[(paper_venue.find("'")):(paper_venue.find(":"))][1:]
            # print("Paper venue name: ", paper_venue)  # This line is for testing purpose
            # print("Years: ", year_str)  # This line is for testing purpose
            try:
                year = int(year_str)
            except (Exception,):
                chi_dataframe.to_csv('chi_paper_data.csv', index=False)
                sys.exit("Can Not locate venue year number, check program code.")
            url = lines.split('"')[1]
            # print(url)  # This line is for testing purpose
            if year in range(2, 50, 1):  # Check the year if that is from 2001 to present (2050)
                url = "https://dl.acm.org" + url + "?tocHeading=heading"
                i = 1  # Section number
                while i < 99:  # Section number less than 99.
                    str_i = str(i)
                    data_url = url + str_i
                    # print(data_url)  # This line is for testing purpose
                    venue_yearly = random_useragent(data_url)
                    soup_venue_yearly = bs(venue_yearly, 'lxml')
                    paper_list_yearly = soup_venue_yearly.find_all("h5", class_="issue-item__title")
                    # print(paper_list_yearly)
                    for paper_item in paper_list_yearly:
                        chi_dataframe.loc[len(chi_dataframe)] = find_paper_detail(paper_venue, paper_item)
                    if paper_list_yearly:
                        i = i + 1
                        # break  # This line is for testing purpose
                    else:
                        print("All papers has been catch in this year CHI")
                        break
                # break  # This line is for testing purpose
            else:
                data_url = "https://dl.acm.org" + url
                # print(data_url)  # This line is for testing purpose
                venue_yearly = random_useragent(data_url)
                soup_venue_yearly = bs(venue_yearly, 'lxml')
                paper_list_yearly = soup_venue_yearly.find_all("h5", class_="issue-item__title")
                # print(paper_list_yearly)
                for paper_item in paper_list_yearly:
                    chi_dataframe.loc[len(chi_dataframe)] = find_paper_detail(paper_venue, paper_item)
                    # break  # This line is for testing purpose
                print("All papers has been catch in this year CHI")
                # break  # This line is for testing purpose
        else:
            pass
    print("Save data to file.")
    chi_dataframe.to_csv('chi_paper_data.csv', index=False)


def get_assets_paper():
    try:
        f = open("assets_list.txt", "r")
    except (Exception,):
        sys.exit("ASSETS list not found, please update venue list.")
    assets_dataframe = pd.DataFrame(columns=['Venue', 'Title', 'Abstract', 'DOI'])


def main():
    args = parse_args()
    print("Venue: ", args.v_n)
    print("Keyword file: ", args.k_l)
    if args.update_venue_list is True:
        pull_venue_list(args)
    for name in args.v_n:
        if name == "UIST":
            get_uist_paper()
        elif name == "CHI":
            get_chi_paper()
        elif name == "ASSETS":
            get_assets_paper()
        else:
            print("Venue name not found, please check venue list.")
    print("======================== Program ends ========================")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

