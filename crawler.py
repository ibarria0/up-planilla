import urllib.parse
import lxml.html
import payload
import csv
import requests

fields = ['nombre','cedula','unidad','cargo','estamiento','fecha_ingreso','servicios','salario','gastos','total']
base_url = 'http://www.up.ac.pa/portalup/planilla.aspx'

def reset_page(data):
    d = data.copy()
    d['__EVENTARGUMENT'] = ['Page$1']
    return d

def increment_page(data,viewstate,validation):
    d = data.copy()
    page = int(d['__EVENTARGUMENT'][0].split('$')[-1])
    d['__EVENTARGUMENT'] = ['Page$' + str(page + 1)]
    d['__VIEWSTATE'] = viewstate
    d['__EVENTVALIDATION'] = validation
    d['ScriptManager1'] = ['UpdatePanel1|GridView1']
    d['__EVENTTARGET'] = ['GridView1']
    return d

def parse_html(html):
   erows = get_employee_rows(html)[1:-1]
   return [parse_employe_row(er) for er in erows]

def get_employee_rows(html):
   return html.xpath('//*[@id="GridView1"]/tr')

def parse_employe_row(erow):
   return [e.text_content() for e in list(erow)]

def get_viewstate(html):
   return html.xpath('//*[@id="__VIEWSTATE"]')[0].get('value')

def get_eventvalidation(html):
   return html.xpath('//*[@id="__EVENTVALIDATION"]')[0].get('value')

def fetch_employees(data,csvw):
    response = requests.post(base_url, headers={'Content-Type':'application/x-www-form-urlencoded'}, data=data)
    raw_html = response.text
    html = lxml.html.fromstring(raw_html)
    csvw.writerows(parse_html(html))
    return (get_viewstate(html),get_eventvalidation(html))

if __name__ == "__main__":
    data = payload.data
    #data = reset_page(data)
    with open('planilla.csv', 'w') as csvfile:
        csvw = csv.writer(csvfile, delimiter=',')
        csvw.writerow(fields)
        while True:
            viewstate,validation = fetch_employees(data,csvw)
            data = increment_page(data,viewstate,validation)
