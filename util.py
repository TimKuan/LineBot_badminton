import constant
from datetime import datetime
from bs4 import Tag
def analyze_text(text:str):
    use_dic = {}
    datalst = [None,None,None,None,None] # 0縣市 , 1區域 , 2星期 , 3時間 , 4程度
    keyword_lst = text.split()
    while len(keyword_lst) > 0:
        keyword = keyword_lst.pop(0)
        if keyword in constant.taiwan_regions:
            datalst[0] = keyword
        elif any(suffix in keyword for suffix in ['區', '鄉', '鎮']):
            if datalst[0] !=None:
                region  = datalst[0]
                if keyword in constant.taiwan_district.get(region):
                    datalst[1] = keyword
            elif len(keyword_lst)>1 : #如果還沒判斷區域，則先略過  
                keyword_lst.append(keyword)
        elif keyword in constant.weekdays_chinese:
            if datalst[2] !=None:
                datalst[2].append(keyword)
            else:
                datalst[2] = [keyword] 
        elif keyword in constant.daytimes_chinese:
            if datalst[3] !=None:
                datalst[3].append(keyword)
            else:
                datalst[3] = [keyword]
        elif keyword in constant.level_chinese:
            if datalst[4] !=None:
                datalst[4].append(keyword)
            else:
                datalst[4] = [keyword]
    if datalst[0]:
        use_dic['city'] = datalst[0]
    if datalst[1]:
        use_dic['area'] = datalst[1]
    if datalst[2]:
        use_dic['day[]'] = datalst[2]
    if datalst[3]:
        use_dic['time[]'] = datalst[3]
    if datalst[4]:
        use_dic['level[]'] = datalst[4]    
    return use_dic            

def analyze_reslut(element:Tag):
    # 0球隊名稱 , 1縣市區域 , 2打球時間 , 3地點 , 4.聯絡人 5.程度 6. 下一次打球時日期 7.費用 ８. 聯絡資訊
    datalst = [None,None,None,None,None,None,None,None,None]
    all_td = element.find_all('td')

    try:# 0球隊名稱
        name = element.find('td', class_='name').text
        if name:
            datalst[0]= name
    except AttributeError:
        #當找不到特定元素 會返回None,對None 調用.text 會引發AttributeError 
        pass    

    try:#1縣市區域
        #holder > div:nth-child(8) > div:nth-child(2) > div > table > tbody > tr:nth-child(1) > td:nth-child(2)
        area = all_td[1].text
        if area:
            datalst[1]= area
    except AttributeError:
        pass   
    
    try:#2打球時間
        play_time =all_td[2].text
        if play_time:
            datalst[2]= play_time
    except AttributeError:
        pass  


    try:#3地點 #holder > div:nth-child(8) > div:nth-child(2) > div > table > tbody > tr:nth-child(1) > td:nth-child(4)
        play_area =all_td[3].text
        if play_area:
            datalst[3]= play_area

    except AttributeError:
        pass  

    try:#4.聯絡人
        contack_person =element.find('td', class_='contact_person1').text
        
        if contack_person:
            datalst[4]= contack_person
    except AttributeError:
        pass  
    
    try:#5.程度
        level  =element.find('td', class_='level').text
       
        if level:
            datalst[5]= level
    except AttributeError:
        pass    

    try:#6. 下一次打球時日期 
        next_date = element.find('td', class_='next_play_date').text
        if next_date:
            datalst[6]= next_date

    except AttributeError:
        pass  

    try:#7.費用
        fee  = element.find('td', class_='fee_once').text
        if fee:
            datalst[7]= fee
    except AttributeError:
        pass   
    
    try:#８. 聯絡資訊
        href = element.find('a').get('href')
        if href:
            datalst[8]= constant.base_url + href
    except AttributeError:
        pass   
    
    return datalst
    
def analyze_return(resutlst:list):
    # 0球隊名稱 , 1縣市區域 , 2打球時間 , 3地點 , 4.聯絡人 5.程度 6. 下一次打球時日期 7.費用 ８. 聯絡資訊
    title = ['球隊名稱','縣市區域','打球時間','地點','聯絡人','程度','下一次打球時日期','費用','聯絡資訊']
    content = ''
    for index in range(len(resutlst)):
        if resutlst[index]!=None:
            content += f'{title[index]}:{resutlst[index]}\n'
    return content        

def row_filter(element:Tag):
    # 找到下一次打球日期
    next_date_str = element.find('td', class_='next_play_date').text
    # 將下次打球日期 轉換為 datetime
    next_date = datetime.strptime(next_date_str, '%Y-%m-%d')
    # 取得今天日期
    today = datetime.today().date()
    # 如果下次打球日期，在今天之後， 則繼續判斷該團是否已經滿團 或者 停止開放場地
    if next_date.date()> today:
        try:
            # 判斷是否有 停 或者 滿 的 div  
            divtags = element.find('a').find_all('div')
            for div_tag in divtags:
                if div_tag.text == '滿' or div_tag.text == '停':
                    return False
            return True
        except AttributeError:
            #當找不到特定元素 會返回None,對None 調用.text 會引發AttributeError 
            return True   
    else:
        return False     
