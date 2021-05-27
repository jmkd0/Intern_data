import pandas as pd
import numpy as np
import requests #pip install requests
from bs4 import BeautifulSoup #pip install bs4

class ScrapData:
    def __init__(self, url, depth):
        self.url = url
        self.depth = depth
        self.raw_data = []
        
    def get_area_and_link_to_childs(self, url):
        areas = []
        html_data = requests.get(url)
        soup = BeautifulSoup(html_data.text, 'html.parser')
        lists = soup.find_all("div", {"class": "card-body"})
        elements = lists[0].find_all("a")
        for element in elements:
            areas.append([element.text, element["href"]])
        return areas
    
    def create_database(self, url=None, depth = 1):
        areas = self.get_area_and_link_to_childs(url)
        for area in areas:
            url = self.url+area[1]
            self.raw_data.append([depth, area[0]])
            if depth == self.depth:
                continue
            self.create_database(url, depth + 1)
            
    def transform(self):
        area_data = pd.DataFrame(self.raw_data, columns=["status", "area"])
        status = area_data[["status"]].drop_duplicates(subset=["status"])["status"].to_list()
        cols = max(status)
        rows = len(area_data[area_data.status == cols])
        data = area_data[area_data.status == cols]
        for i in range(1, cols):
            gap = area_data[area_data.status == cols-i]
            data["status_"+str(i)] = None
            gap_index = gap.index
            for j in range(len(gap_index) - 1):
                data.loc[((data.index > gap_index[j]) & (data.index < gap_index[j+1])), "status_"+str(i)] = gap.loc[gap_index[j], "area"]
            data.loc[(data.index > gap_index[len(gap_index)-1]), "status_"+str(i)] = gap.loc[gap_index[len(gap_index)-1], "area"]
        return data[list(data)[::-1]].drop(["status"], axis=1).reset_index(drop=True)
    
url = "https://www.codepostalmonde.com"
scrap = ScrapData(url, 2)
scrap.create_database(url+"/netherlands")
data = scrap.transform()