import requests
from bs4 import BeautifulSoup
import mysql.connector
import time
import pandas as df
# #
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'hanif',
}


def db_connection():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Create a table if it doesn't exist
    create_table_query = """
           CREATE TABLE IF NOT EXISTS nfl_scores (
               id INT AUTO_INCREMENT PRIMARY KEY,
               team1_fg INT,
               team1_pt INT,
               team1_fp INT,
               team1_oreb INT,
               team1_to INT,
               team2_fg INT,
               team2_pt INT,
               team2_fp INT,
               team2_oreb INT,
               team2_to INT
           )
           """
    cursor.execute(create_table_query)

db_connection()

def db_insertion(team1_fg, team1_pt, team1_fp, team1_oreb, team1_to, team2_fg2, team2_pt2, team2_fp2, team2_oreb2, team2_to2):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        # Insert DataFrame records into the MySQL table
        insert_query = "INSERT INTO nfl_scores (team1_fg, team1_pt, team1_fp, team1_oreb, team1_to, team2_fg2, team2_pt2, team2_fp2, team2_oreb2, team2_to2) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        records = df.values.tolist()
        cursor.executemany(insert_query, records)
        print("here is line no 50", records)
        # Commit changes
        conn.commit()

        print("Data inserted successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close connections
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


class GetMatchScore:

    def __init__(self):
        self.teams_detail = []
        self.url = "https://www.espn.com/mens-college-basketball/scoreboard/_/date/20240121/group/50"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

    def fetch_html(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def is_match_live(self, main_page_html):
        soup = BeautifulSoup(main_page_html, 'html.parser')
        halftime_condition = None
        try:
            while True:

                for first_half in soup.find_all('div',
                                                   class_="ScoreCell__Time ScoreboardScoreCell__Time h9 clr-negative", string="2st"):
                    self.scrap_main_page_data(main_page_html, first_half)

                for half_time in soup.find_all('div',
                                                   class_="ScoreCell__Time ScoreboardScoreCell__Time h9 clr-negative",
                                                   string='Halftime'):
                    self.scrap_main_page_data(main_page_html, half_time)
                for second_half in soup.find_all('div',
                                                   class_="ScoreCell__Time ScoreboardScoreCell__Time h9 clr-negative",
                                                   string='2nd'):
                    self.scrap_main_page_data(main_page_html, second_half)

        except:
            pass

    def scrap_main_page_data(self, main_page_html, conditions):

        if conditions in ["Halftime", "1st", "2nd"]:
            soup = BeautifulSoup(main_page_html, 'html.parser')

            box_score_links = soup.find_all('a',
                                            class_='AnchorLink Button Button--sm Button--anchorLink Button--alt mb4 w-100 mr2',
                                            href=lambda x: x and "/boxscore/_/gameId/" in x)


            for box_score_link in box_score_links:
                try:
                    box_score_url = box_score_link['href']
                    self.headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
                    }
                    html = requests.get(f"https://www.espn.com{box_score_url}", headers=self.headers).text
                    box_score_soup = BeautifulSoup(html, 'html.parser')
                    box_score_scrap = box_score_soup.find_all()

                    status = box_score_soup.select_one('.game-status')
                    teams = box_score_soup.select('.BoxscoreItem__TeamName')
                    halftime_condition = box_score_soup.find_all('div',
                                                             class_='ScoreCell__Time ScoreboardScoreCell__Time h9 clr-negative',
                                                             text='2OT')
                    if conditions:

                        element = box_score_soup.find_all(class_='Table__customHeader Table__TD')
                        team1_fg = element[31].text
                        team1_pt = element[32].text
                        team1_fp = element[33].text
                        team1_oreb = element[34].text
                        team1_to = element[40].text

                        team2_fg2 = element[87].text
                        team2_pt2 = element[88].text
                        team2_fp2 = element[89].text
                        team2_oreb2 = element[90].text
                        team2_to2 = element[96].text

                        db_insertion(team1_fg, team1_pt, team1_fp, team1_oreb, team1_to, team2_fg2, team2_pt2, team2_fp2, team2_oreb2, team2_to2)

                except:
                    pass


    # def save_to_csv(self):
    #     file_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_college_basketball_scores.csv"
    #     with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
    #         csv_writer = csv.writer(csvfile)
    #
    #         # Write header row to the CSV file
    #         header = ['status', 'team_one', 'team_one_score', 'team_two', 'team_two_score', 'box_score_url',
    #                   'team_one_fg', 'team_one_3pt', 'team_one_ft', 'team_one_orb', 'team_one_to',
    #                   'team_two_fg', 'team_two_3pt', 'team_two_ft', 'team_two_orb', 'team_two_to']
    #         csv_writer.writerow(header)
    #
    #         # Write data rows to the CSV file
    #         for detail in self.teams_detail:
    #             csv_writer.writerow([detail.get(key, '') for key in header])
    #
    #     print(f"CSV file '{file_name}' created successfully.")

    def execute(self):
        try:
            main_page_html = self.fetch_html(self.url)
            if main_page_html:
                self.is_match_live(main_page_html)
                self.save_to_csv()
        finally:
            # Add any cleanup code if needed
            pass

if __name__ == "__main__":
    match_score = GetMatchScore()
    match_score.execute()

