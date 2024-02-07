import requests

url = "https://dramatimealter.dramahood.fun/Admin_api/add_season"

payload = "webseries_id=4035&modal_Season_Name=Moi&modal_Order=&Modal_Status=1"
headers = {
  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'X-Requested-With': 'XMLHttpRequest',
  'Cookie': 'ci_session=7n329uljbh8d5jao86tga1c3ijbb3vla'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
