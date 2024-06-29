import util
import constant
import requests
from bs4 import BeautifulSoup

def reptile(params:dict):
    url = constant.base_url+'/search.php?'
    response = requests.get(url,params)
    soup = BeautifulSoup(response.text,'html.parser')

    # 使用 CSS 選擇器找到包含結果的表格元素
    elements = soup.select('#holder > div:nth-child(8) > div:nth-child(2) > div > table > tbody > tr')
    # 判斷是否有搜尋到含結果的表格
    if len(elements)>0:
      result = []
      for row in elements:
          # 找到每個 <tr> 元素，並判斷是否符合需求
          if util.row_filter(row):
              # # 將符合需求的元素資料取出，並放入串列
              result.append(util.analyze_reslut(row))

      if len(result)>0:
         return result
      else:
         return '場地皆已滿，請搜尋其他條件的場地' 

    else: # 如果沒有，則搜尋錯誤錯誤資訊
        elements = soup.select('#holder > div:nth-child(8) > div:nth-child(2) > div > font')
        return elements[0].text
                    

