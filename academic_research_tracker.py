import requests
from bs4 import BeautifulSoup
import time
import argparse

class Studies:
    def __init__(self, university_name, faculty_name, department_name, min_year, exc_delay):
        self.yok_link = "https://akademik.yok.gov.tr"
        self.min_year = min_year
        self.university_name= university_name
        self.faculty_name = faculty_name
        self.department_name = department_name
        self.delay = exc_delay
        self.academic_links = []
        self.articles = []
        
        # Create a requests session
        self.session = requests.Session()
        # Set the user agent
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'

    def find_university_link(self):
        # Go to the home page of yok.akademik.gov.tr
        response = self.session.get(self.yok_link + '/AkademikArama/view/universityListview.jsp')
        
        # Check if the request was successful
        if response.status_code == 200:
            # Create a BeautifulSoup object from the response
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all the links to academicians
            academician_links = soup.find_all('a')
            filtered = filter(lambda link: link.text == self.university_name, academician_links)
            uni = list(filtered)[0]
            
            self.university_link = uni['href']
            
            print("university found", self.university_link)
            time.sleep(self.delay)
        else:
            # Print an error message if the request was not successful
            print('Error: Could not access yok.akademik.gov.tr')
            
    def find_faculty_link(self):
        # Go to the home page of yok.akademik.gov.tr
        response = self.session.get(self.yok_link + self.university_link)

        # Check if the request was successful
        if response.status_code == 200:
            # Create a BeautifulSoup object from the response
            soup = BeautifulSoup(response.content, 'html.parser')
            
            faculty_names = soup.select("div#searchlist a span span")
            
            filtered = filter(lambda link: link.text == self.faculty_name, faculty_names)
            faculty = list(filtered)
            self.faculty_link = faculty[0].parent.parent["href"]
            print("\nfaculty found", self.faculty_link)
            time.sleep(self.delay)
        else:
            # Print an error message if the request was not successful
            print('Error: Could not access UNI-LINK')
            
    def find_department_link(self):
         # Go to the home page of yok.akademik.gov.tr
         response = self.session.get(self.yok_link + self.faculty_link)

         # Check if the request was successful
         if response.status_code == 200:
             # Create a BeautifulSoup object from the response
             soup = BeautifulSoup(response.content, 'html.parser')
             
             department_names = soup.select("div ul a span span")

             filtered = filter(lambda link: link.text == self.department_name, department_names)
             department = list(filtered)
             
             self.department_link = department[0].parent.parent["href"]
             print("\ndepartment found", self.department_link)
             time.sleep(self.delay)

         else:
             # Print an error message if the request was not successful
             print('Error: Could not access FACULTY-LINK')
             
    def find_academic_links(self):
        # Go to the home page of yok.akademik.gov.tr
        response = self.session.get(self.yok_link + self.department_link)

        # Check if the request was successful
        if response.status_code == 200:
            # Create a BeautifulSoup object from the response
            soup = BeautifulSoup(response.content, 'html.parser')
            
            academic_links = soup.select("table#authorlistTb td h4 a")
            print("\nprinting academics links")

            for academic_link in academic_links:
                try:
                    name = academic_link.text
                    link = academic_link['href']
                    self.academic_links.append({"name": name, "link": link})
                except Exception:
                    pass

            time.sleep(self.delay)
        else:
            # Print an error message if the request was not successful
            print('Error: Could not access DEPT-LINK')

    def find_article_links(self, academic):
        print("Searching articles for", academic['name'], ", link:", self.yok_link + academic['link'])
        # Go to the home page of yok.akademik.gov.tr
        response = self.session.get(self.yok_link + academic['link'])
        articles_link = ""
        
        # Check if the request was successful
        if response.status_code == 200:

            # Create a BeautifulSoup object from the response
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all the links to academicians
            articles_link = soup.select("li#articleMenu a")[0]['href']
            time.sleep(self.delay)
            
        else:
            # Print an error message if the request was not successful
            print('Error: Could not access ACADEMIC-LINK')
        
        response = self.session.get(self.yok_link + articles_link)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Create a BeautifulSoup object from the response
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all the links to academicians
            articles = soup.select("div#all table tbody.searchable tr > td")
            for i in range(1, len(articles), 4):
                year = articles[i].text.split(',')
                year = year[len(year)-1].split("\n")[0]
                
                try:
                    if int(year) >= self.min_year:
                        title = articles[i].select("span strong a")[0].text.upper()
                        
                        authors = articles[i].select("a#popoverData")
                        for k in range(len(authors)):
                            authors[k] = authors[k].text
                        
                        #print(int(i/4), "Title:", title, ", Year: ", year, ", authors:", authors)
                        
                        article = {
                            "year": year,
                            "title": title,
                            "authors": authors
                        }
                        self.articles.append(article)
                        #print(int(i/4), article)
                    #else:
                        #print("old article, year:", year)
                except Exception:
                    pass

            time.sleep(self.delay)
            
            self.articles = sorted(self.articles, key=lambda x: x['year'], reverse=True)

        else:
            # Print an error message if the request was not successful
            print('Error: Could not access ARTICLE-LINKS')
        
    def find_project_links(self, academic):
        print("(Not implemented) Searching projects for", academic['name'])
        # Go to the home page of yok.akademik.gov.tr
        #response = self.session.get(self.yok_link + academic.link)
        time.sleep(self.delay)

    def build_art(self, article):
        result = "<li class='article'>" 
        result += "<span class='title'>" + article['title'] + "</span>" 
        result += "<span class='year'>" + article['year'] + "</span>" 
        result += "<span class='authors'>" + ", ".join(article['authors']) + "</span>" 
        result += "</li>"
        
        return result

    def build_html(self):
        html = "<html><head<meta name='author' content='ahmetkasif'></head><body>"
        css = "<style>.article{ display: flex!important; background: #eee; margin-bottom: 1em; padding: 1em; list-style: none; border-radius: 10px; margin-left: -1.5em; font-size: .8em; flex-direction: row; flex-wrap: wrap; align-items: flex-start; line-height: 1.1 } .article > *{ } .article > .title{ font-weight: 700; flex-basis: 80%; flex-grow: 1; } .article > .authors{ font-size:  .8em; color: #320057; width: 100%; } .article > .year{ background: #320057; color: white; padding: 5px; border-radius: 10px; font-size: .8em; line-height: 1; }</style>"
        
        for article in self.articles:
            print("\n", article['title'], ", ", article['year'], ", ", article['authors'])

        result = "".join(map(self.build_art, self.articles))

        html += result + css + "</body></html>"
        print("\n Final HTML:\n")
        return html

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Process data.")

        parser.add_argument('--university_name', type=str, required=True, help="Üniversite Adı")
        parser.add_argument('--faculty_name', type=str, required=True, help="Fakülte Adı")
        parser.add_argument('--department_name', type=str, required=True, help="Bölüm Adı")
        parser.add_argument('--min_year', type=int, required=True, help="Araştırma başlangıç yılı")
        parser.add_argument('--exc_delay', type=float, required=True, help="YÖK sorguları arasında gecikme süresi")

        args = parser.parse_args()

        university_name = args.university_name
        faculty_name = args.faculty_name
        department_name = args.department_name
        min_year = args.min_year
        exc_delay = args.exc_delay

        studies = Studies(university_name, faculty_name, department_name, min_year, exc_delay)

        studies.find_university_link()
        studies.find_faculty_link()
        studies.find_department_link()
        studies.find_academic_links()

        print("\nFinding articles for academics;\n")
        
        for i in range(len(studies.academic_links)):
            studies.find_article_links(studies.academic_links[i])    
        
        studies.session.close()
        
        html = studies.build_html()
        print(html)

    except Exception as e:
       # By this way we can know about the type of error occurring
        print("The error is: ", e)