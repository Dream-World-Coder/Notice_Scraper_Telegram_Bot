import requests
from bs4 import BeautifulSoup

def scrape_notifications(notice_type):
    base_url = "https://www.iiests.ac.in/IIEST/Notices/"
    url = f"{base_url}?type={notice_type}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to retrieve data from {url}")
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Locate the notification section (you may need to adjust the class or tag based on the actual HTML structure)
    notifications = soup.find_all('div', class_='panel panel-default')
    
    last_three_notifications = notifications[:3]
    
    for notification in last_three_notifications:
        date = notification.find('span', class_='noticetime').text.strip()
        title = notification.find('a').text.strip()
        print(f"Date: {date}, Notification: {title}")

# Example usage
scrape_notifications('Student')
scrape_notifications('General')
scrape_notifications('Placement')
scrape_notifications('Admission')
scrape_notifications('Finance')

