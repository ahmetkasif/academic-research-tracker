import requests
from bs4 import BeautifulSoup
import time
import argparse
import re

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
        response = self.session.get(self.yok_link + academic['link'])
        if response.status_code != 200:
            print('Error: Could not access ACADEMIC-LINK')
            return

        soup = BeautifulSoup(response.content, 'html.parser')
        article_tab = soup.select_one("li#articleMenu a")
        if not article_tab:
            print("No article tab found for", academic['name'])
            return

        articles_link = article_tab['href']
        time.sleep(self.delay)

        response = self.session.get(self.yok_link + articles_link)
        if response.status_code != 200:
            print('Error: Could not access ARTICLE-LINKS')
            return

        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.select("div#all table tbody.searchable tr > td")

        for i in range(1, len(articles), 4):
            try:
                year_parts = articles[i].text.split(',')
                raw_year = year_parts[-1].split("\n")[0].strip()
                if not raw_year.isdigit() or not (1900 <= int(raw_year) <= 2100):
                    continue
                year = int(raw_year)
                if year < self.min_year:
                    continue


                title_tag = articles[i].select_one("span strong a")
                if not title_tag or not title_tag.text.strip():
                    continue
                title = title_tag.text.strip().upper()


                cell_html = str(articles[i])
                soup_authors = BeautifulSoup(cell_html, 'html.parser')

                a_tag_authors = [a.get_text(strip=True) for a in soup_authors.find_all('a', class_='popoverData')]


                full_text = soup_authors.get_text(separator=" ", strip=True)
                authors_and_meta = full_text.split(', Yayın Yeri')[0] if ', Yayın Yeri' in full_text else full_text

                raw_names = [x.strip() for x in re.split(r',|;', authors_and_meta) if x.strip()]
                filtered_names = []
                for name in raw_names:
                    if not any(w in name for w in ["Yayın Yeri", "Hakemli", "SCI", "Makale", "https", "doi", "Index", "Expanded"]):
                        if 2 <= len(name.split()) <= 4 and all(c.isalpha() or c.isspace() for c in name):
                            filtered_names.append(name)

                all_authors = list(dict.fromkeys(a_tag_authors + filtered_names))

                self.articles.append({
                    "year": str(year),
                    "title": title,
                    "authors": all_authors
                })

            except Exception as e:
                print("Hata:", e)
                continue

        time.sleep(self.delay)
        self.articles = sorted(self.articles, key=lambda x: x['year'], reverse=True)
        unique_articles = {}

        for art in self.articles:
            unique_articles[art['title']] = art  # Aynı başlık varsa en sonuncusu kalır

        self.articles = sorted(unique_articles.values(), key=lambda x: x['year'], reverse=True)

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
        all_years = sorted({int(article["year"]) for article in self.articles if article["year"].isdigit()})
        min_year = 2022
        max_year = max(all_years) if all_years else 2025
        year_options = [y for y in range(min_year, max_year + 1)]

        html = """
        <html>
        <head>
            <meta charset='UTF-8'>
            <meta name='author' content='ahmetkasif'>
            <style>
                body {
                    font-family: sans-serif;
                    padding: 2em;
                    background: #fdfdfd;
                }
                .filters {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 1em;
                    flex-wrap: wrap;
                    gap: 1em;
                }
                .filter-group {
                    display: flex;
                    align-items: center;
                    gap: 0.5em;
                }
                label {
                    font-weight: bold;
                    font-size: 0.9em;
                }
                input[type="text"], select {
                    padding: 0.5em;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    font-size: 1em;
                }
                ul {
                    padding-left: 0;
                }
                .article {
                    display: flex;
                    background: #eee;
                    margin-bottom: 1em;
                    padding: 1em;
                    list-style: none;
                    border-radius: 10px;
                    font-size: .9em;
                    flex-direction: row;
                    flex-wrap: wrap;
                    align-items: flex-start;
                    line-height: 1.3;
                }
                .article > .title {
                    font-weight: 700;
                    flex-basis: 80%;
                    flex-grow: 1;
                }
                .article > .authors {
                    font-size:  .8em;
                    color: #320057;
                    width: 100%;
                }
                .article > .year {
                    background: #320057;
                    color: white;
                    padding: 5px;
                    border-radius: 10px;
                    font-size: .8em;
                    line-height: 1;
                }
            </style>
        </head>
        <body>
            <div class="filters">
                <div class="filter-group">
                    <label for="searchBox">Ara</label>
                    <input type="text" id="searchBox" placeholder="Makale Ara...">
                </div>
                <div class="filter-group">
                    <label for="yearFilter">Yıllara Göre Filtrele</label>
                    <select id="yearFilter">
                        <option value="all">Tüm Yıllar</option>"""
        for y in year_options:
            html += f'<option value="{y}">{y} ve sonrası</option>'
        html += """</select>
                </div>
            </div>
            <ul id="articleList">"""

        for article in self.articles:
            html += f"""
            <li class='article' data-title='{article['title']}' data-year='{article['year']}'>
                <span class='title'>{article['title']}</span>
                <span class='year'>{article['year']}</span>
                <span class='authors'>{', '.join(article['authors'])}</span>
            </li>"""

        html += """</ul>
        <script>
            const searchBox = document.getElementById('searchBox');
            const yearFilter = document.getElementById('yearFilter');
            const articles = document.querySelectorAll('.article');

            function filterArticles() {
                const query = searchBox.value.toLowerCase();
                const selectedYear = yearFilter.value;

                articles.forEach(article => {
                    const title = article.dataset.title.toLowerCase();
                    const year = parseInt(article.dataset.year);
                    const matchTitle = title.includes(query);
                    const matchYear = (selectedYear === "all") || (year >= parseInt(selectedYear));
                    article.style.display = (matchTitle && matchYear) ? "flex" : "none";
                });
            }

            searchBox.addEventListener("input", filterArticles);
            yearFilter.addEventListener("change", filterArticles);
        </script>
        </body>
        </html>
        """
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