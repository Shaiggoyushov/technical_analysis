def getBalanceSheet(stock, exchange = "USD", language = "ENG", writeExcel = False):
    import requests
    from bs4 import BeautifulSoup
    import pandas as pd

    # stocks = []
    # url = "https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/sirket-karti.aspx?hisse=ACSEL"
    # r = requests.get(url)
    # s = BeautifulSoup(r.text)
    # s1 = s.find("select", id = "ddlAddCompare")
    # c1 = s1.findChild("optgroup").findAll("option")

    # for a in c1:
    #     stocks.append(a.string)

    stocks = []
    stocks.append(stock)
    exchange = exchange
    if language == "ENG":
        language_drop = "itemDescTr"
    else:
        language_drop = "itemDescEng"

    for i in stocks:
        stock = i
        group = []
        date = []
        years = []
        periods = []

        url1 = "https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/sirket-karti.aspx?hisse="+stock
        r1 = requests.get(url1)
        soup = BeautifulSoup(r1.text, 'html.parser')
        option = soup.find("select", id = "ddlMaliTabloFirst")
        option2 = soup.find("select", id = "ddlMaliTabloGroup")

        try:
            children = option.findChildren("option")
            group = option2.find("option")["value"]
            for i in children:
                date.append(i.string.rsplit("/"))
            
            for j in date:
                years.append(j[0]) 
                periods.append(j[1])
            
            if len(date) >= 4:
                parameters = (
                        ("companyCode", stock),
                        ("exchange", exchange),
                        ("financialGroup", group),
                        ("year1", years[0]),
                        ("period1", periods[0]),
                        ("year2", years[1]),
                        ("period2", periods[1]),
                        ("year3", years[2]),
                        ("period3", periods[2]),
                        ("year4", years[3]),
                        ("period4", periods[3]),
                )

                url2 = "https://www.isyatirim.com.tr/_layouts/15/IsYatirim.Website/Common/Data.aspx/MaliTablo"
                r2 = requests.get(url2, params=parameters).json()['value']
                data = pd.DataFrame.from_dict(r2)
                data.drop(columns = ["itemCode", language_drop], inplace = True)
            
            else:
                continue
        except AttributeError:
            continue

        del date[0:4]
        alldata = [data]

        for _ in range(0, int(len(date)+1)):
            if len(date) == len(years):
                del date[0:4]
            else:
                years = []
                periods = []
                for j in date:
                    years.append(j[0])
                    periods.append(j[1])
            
                if len(date)>=4:
                    parameters2 = (
                            ("companyCode", stock),
                            ("exchange", exchange),
                            ("financialGroup", group),
                            ("year1", years[0]),
                            ("period1", periods[0]),
                            ("year2", years[1]),
                            ("period2", periods[1]),
                            ("year3", years[2]),
                            ("period3", periods[2]),
                            ("year4", years[3]),
                            ("period4", periods[3]),
                    )

                    r3 = requests.get(url2, params=parameters2).json()['value']
                    data2 = pd.DataFrame.from_dict(r3)
                    try:
                        data2.drop(columns = ["itemCode", "itemDescTr", "itemDescEng"], inplace = True)
                        alldata.append(data2)
                    except KeyError:
                        continue
        data3 = pd.concat(alldata, axis = 1)
        if language == "ENG":
            header = ["Balance Sheet"]
        else:
            header = ["Bilanço"]

        for i in children:
            header.append(i.string)
        
        header_diff = len(header) - len(data3.columns)
        if header_diff != 0:
            del header[-header_diff:]
        data3.set_axis(header, axis = 1, inplace = True)
        data3[header[1:]] = data3[header[1:]].astype(float)
        data3.fillna(0, inplace=True)
        if language == "ENG":
            h = "Balance Sheet"
        else:
            h = "Bilanço"
        data3.set_index(h, inplace=True)
        data3 = data3[data3.index != 0]

        if writeExcel == True:
            data3.to_excel(f"{stock}.xlsx", index = False)

        return data3
