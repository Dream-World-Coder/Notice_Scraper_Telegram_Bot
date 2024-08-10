import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import datetime
import argparse # for cli use


class IIEST:

    def __init__(self, notice_type):
        self.notice_type = notice_type.capitalize()
        self.base_url = "https://www.iiests.ac.in/IIEST/Notices/"
        self.notice_types = [
            'Admission', 'Employment', 'Tenders', 'Student', 'General',
            'Finance', 'Placement', 'CMS', 'Faculty'
        ]
        self.element_to_find = {
            'tag': 'table',
            'class': 'table',
            'id': 'example1'
        }
        
        if self.notice_type not in self.notice_types:
            raise ValueError(f'{self.notice_type} is not valid.')
        
        self.url = f'{self.base_url}?type={self.notice_type}'
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            raise ConnectionError(f"Request timed out for {self.url}")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f'Request failed: {e}')
        
        soup = BeautifulSoup(response.content, 'html.parser')
        elem = soup.find(self.element_to_find['tag'], {
            'class': self.element_to_find['class'],
            'id': self.element_to_find['id']
        })

        if not elem:
            raise ValueError(f"{self.element_to_find['tag']} not found for {self.notice_type}. Check the HTML structure and class/id names.")
        
        self.rows = elem.find('tbody').find_all('tr')


    def get_notice(self, num=3):
        requested_rows = self.rows[:num]
        notices = [f'\n\nLast {num} notices for {self.notice_type.upper()}:\n']
        notices.append('\n')

        for row in requested_rows:
            serial = row.find('th').text.strip()
            
            notice_tag = row.find_all('td')[0].find('a')
            notice_data = notice_tag.text.strip()
            
            href = notice_tag.get('href', '#')
            encoded_href = quote(href, safe=":/")
            
            date = row.find_all('td')[1].text.strip()
            notices.append(f"{serial}. {notice_data}, Date: {date}\nLink: '{encoded_href}'\n")
            notices.append('\n')
            
        return "".join(notices)
                    
    
    def find_info(self, requested_date, keywordsList):
        notices = []
        if len(keywordsList) == 0:
            for row in self.rows:
                date = row.find_all('td')[1].text.strip()
                if date == requested_date:
                    serial = row.find('th').text.strip()
                    
                    notice_tag = row.find_all('td')[0].find('a')
                    notice_data = notice_tag.text.strip()
                    
                    href = notice_tag.get('href', '#')
                    encoded_href = quote(href, safe=":/")
                    notices.append(f"{serial}. {notice_data}\nLink: '{encoded_href}'")
                    notices.append('\n')
        else:
            for row in self.rows:
                date = row.find_all('td')[1].text.strip()
                if date == requested_date:
                    notice_tag = row.find_all('td')[0].find('a')
                    notice_data = notice_tag.text.strip()
                    notice_items = notice_data.split(' ')
                    
                    if any(item.lower() == keyword.lower().strip() for item in notice_items for keyword in keywordsList):
                        serial = row.find('th').text.strip()
                        href = notice_tag.get('href', '#')
                        encoded_href = quote(href, safe=":/")
                        notices.append(f"{serial}. {notice_data}\nLink: '{encoded_href}'\n")
                        notices.append('\n')

        return "".join(notices) if notices else None
    
    def get_notice_by_date(self, day=None, month=None, year=None, isprecise=True, keywords=()):
        results = []
        if isprecise:
            if day is not None and month is not None and year is not None:
                requested_date = f'{str(day).zfill(2)}/{str(month).zfill(2)}/{str(year)}'
                result = self.find_info(requested_date, keywordsList=keywords)
                if result:
                    results.append(f'Notice for {self.notice_type.upper()} on {requested_date}:\n{result}')
            elif year is not None and month is not None and day is None:
                for dd in range(1, 32):
                    requested_date = f'{str(dd).zfill(2)}/{str(month).zfill(2)}/{str(year)}'
                    result = self.find_info(requested_date, keywordsList=keywords)
                    if result:
                        results.append(f'Notice for {self.notice_type.upper()} on {requested_date}:\n{result}')
            elif year is not None and month is None and day is None:
                for mm in range(1, 13):
                    for dd in range(1, 32):
                        requested_date = f'{str(dd).zfill(2)}/{str(mm).zfill(2)}/{str(year)}'
                        result = self.find_info(requested_date, keywordsList=keywords)
                        if result:
                            results.append(f'Notice for {self.notice_type.upper()} on {requested_date}:\n{result}')
            else:
                return 'Error: Invalid date parameters provided.'
        else:
            dt = datetime.date.today()
            current_year = int(dt.year)
            current_month = int(dt.month)
            current_day = int(dt.day)
            
            if year is None:
                return 'Error: Year must be provided for unprecise search.'
            
            if year > current_year:
                return 'Error: Future dates are not allowed.'
            
            if month is not None and month > current_month and year == current_year:
                return 'Error: Invalid month provided for current year.'
            
            for yy in range(year, current_year + 1):
                start_month = month if (month is not None) else 1
                end_month = current_month if yy == current_year else 12
                
                for mm in range(start_month, end_month + 1):
                    start_day = day if (day is not None) else 1
                    end_day = current_day if (yy == current_year and mm == current_month) else 31
                    
                    for dd in range(start_day, end_day + 1):
                        requested_date = f'{str(dd).zfill(2)}/{str(mm).zfill(2)}/{str(yy)}'
                        result = self.find_info(requested_date, keywordsList=keywords)
                        if result:
                            results.append(f'Notice for {self.notice_type.upper()} on {requested_date}:\n{result}')
                    
        return "\n".join(results)


def main():
    # Inputs
    notice_query_type = 'general'
    # notice_query_type = 'student'
    
    no = 5
    
    day = None
    month = None
    year = 2024
    
    try:
        college = IIEST(notice_query_type)
        x = college.get_notice(num=no)
        print(f'{x}\n\n\n')
        r = college.get_notice_by_date(day=day, month=month, year=year)
        print(f'{r}\n\n\n')
        print('\n\n\n')

        # college.get_notice_by_date(isprecise=False, year=2024, keywords=('Riya', 'Manna'))
    except ValueError as ve:
        print(f"Error: {ve}")
    except ConnectionError as ce:
        print(f"Error: {ce}")


if __name__ == "__main__":
    main()

'''
how to convert the input to lowers

free server for bot
ai chatbot, 
also u can convert image here
'''