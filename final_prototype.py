import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import os


class IIEST:
    def __init__(self, notice_type):
        self.notice_type = notice_type # for functions
        self.base_url = "https://www.iiests.ac.in/IIEST/Notices/"
        self.notice_types = [
            'Admission',
            'Employment',
            'Tenders',
            'Student',
            'General',
            'Finance',
            'Placement',
            'CMS'
        ]
        self.element_to_find = {
            'name' : 'table',
            'tag' : 'table',
            'class' : 'table',
            'id' : 'example1'
        }
        
        if notice_type.capitalize() not in self.notice_types:
            raise ValueError(f'{self.notice_type} is not valid.')
        
        self.url = f'{self.base_url}?type={notice_type.capitalize()}'
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            raise  ConnectionError(f"Request timed out for {self.url}")
        except requests.exceptions.RequestException as e:
            raise  ConnectionError(f'Request failed: {e}')
            
        soup = BeautifulSoup(response.content, 'html.parser')
        elem = soup.find(self.element_to_find['tag'], {
            'class': self.element_to_find['class'],
            'id' : self.element_to_find['id']
        })

        if not elem:
            raise  ValueError(f"{self.element_to_find['name']} not found for {notice_type}. Check the HTML structure and class/id names.")
            
        else:
            self.rows = elem.find('tbody').find_all('tr')
        
    
    def get_notice(self, num=3):
        requested_rows = self.rows[:num]
        
        print(f'\n\nLast {num} notices for {self.notice_type.upper()}:\n')
        for row in requested_rows:
            serial = row.find('th').text.strip()
            
            notice_tag = row.find_all('td')[0].find('a')
            notice_data = notice_tag.text.strip()
            
            href = notice_tag.get('href', '#')
            encoded_href = quote(href, safe=":/")

            date = row.find_all('td')[1].text.strip()
            print(f"{serial}. {notice_data}, Date: {date}\nLink: '{encoded_href}'\n")
                    
        
    def get_notice_by_date(self, day='04', month='06', year='2024', unprecise=False):
        requested_date = f'{str(day)}/{str(month)}/{str(year)}'
        
        print(f'\n\nNotices for {self.notice_type.upper()} on {requested_date}:\n')
        for row in self.rows:
            date = row.find_all('td')[1].text.strip()
            if date == requested_date:
                serial = row.find('th').text.strip()
                
                notice_tag = row.find_all('td')[0].find('a')
                notice_data = notice_tag.text.strip()
                
                href = notice_tag.get('href', '#')
                encoded_href = quote(href, safe=":/")
                
                print(f"{serial}. {notice_data}\nLink: '{encoded_href}'\n")
                
            else:
                return  print("No more notices, cazz")

        
def main():
    # inputs
    notice_query_type = 'student'
    
    no = 5
    
    day = '04'
    month = '06'
    year = '2024'
    
    college = IIEST(notice_query_type)
    college.get_notice(num=no)
    college.get_notice_by_date(day=day, month=month, year=year)
    
    
if __name__ == "__main__":
    main()