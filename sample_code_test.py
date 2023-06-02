import requests
from bs4 import BeautifulSoup

# 设置目标网址和请求头
base_url = 'https://dl.acm.org'
conference_url = base_url + '/doi/proceedings/10.1145/3526113'  # 替换为实际的UIST Conference网址
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

# 发送HTTP请求获取网页内容
response = requests.get(conference_url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

# 解析网页并提取文章链接
article_links = []
articles = soup.find_all('a', class_='section__title accordion-tabbed__control left-bordered-title')
for article in articles:
    article_link = base_url + article['href']
    article_links.append(article_link)

print(article_links)
# 遍历文章链接并输出
# for link in article_links:
#     response = requests.get(link, headers=headers)
#     article_soup = BeautifulSoup(response.content, 'html.parser')
#     title = article_soup.find('h1', class_='citation__title').text.strip()
#     authors = article_soup.find('div', class_='loa__body').text.strip()
#     abstract = article_soup.find('div', class_='abstractSection abstractInFull').text.strip()
#
#     print('Title:', title)
#     print('Authors:', authors)
#     print('Abstract:', abstract)
#     print('--------------------------------------')
