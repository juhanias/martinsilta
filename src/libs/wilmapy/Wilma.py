import pprint

import bs4
import requests

import src.libs.wilmapy.WilmaModels as WilmaModels


class Wilma:
    def __init__(self, username, password, id):
        self.url = "https://turku.inschool.fi/"
        self.username = username
        self.password = password
        self.wilma2sid = None
        self.formkey = None
        self.id = id
        self.session = requests.Session()

    def initialize_connection(self):
        """
        Initialize the connection to wilma
        :return: None
        """
        _initial_login_url = self._get_initial_login_url()
        _form_action_url = self._get_form_action_url(_initial_login_url)
        _code, _id_token, _state = self._return_final_tokens(_form_action_url)
        self._finalize_login(_code, _id_token, _state)

    def _get_initial_login_url(self):
        data = self.session.get(
            self.url,
        ).text
        bs = bs4.BeautifulSoup(data, "html.parser")
        login_page_url = bs.find("a", {"class": "pull-left oid-login-button"})["href"]
        return login_page_url

    def _get_form_action_url(self, login_page_url):
        data = self.session.get(
            login_page_url,
        )

        bs = bs4.BeautifulSoup(data.text, "html.parser")
        # Get the form action url from the login page
        form_action_url = bs.find("form", {"id": "options"})["action"]
        return form_action_url

    def _return_final_tokens(self, form_action_url):
        data3 = self.session.post(
            form_action_url,
            data={
                "UserName": self.username,
                "Password": self.password,
                "AuthMethod": "FormsAuthentication",
            },
            headers={
                "Referer": form_action_url
            }
        )
        bs = bs4.BeautifulSoup(data3.text, "html.parser")
        code = bs.find("input", {"name": "code"})["value"]
        id_token = bs.find("input", {"name": "id_token"})["value"]
        state = bs.find("input", {"name": "state"})["value"]
        return code, id_token, state

    def _finalize_login(self, code, id_token, state):
        final_url = "https://turku.inschool.fi/api/v1/external/openid"
        fr = self.session.post(
            final_url,
            data={
                "code": code,
                "id_token": id_token,
                "state": state,
            },
        )
        bs = bs4.BeautifulSoup(fr.text, "html.parser")
        pprint.pp(fr.headers)
        pprint.pp(self.session.cookies)
        self.wilma2sid = self.session.cookies["Wilma2SID"]
        self.formkey = bs.find("input", {"name": "formkey"})["value"]
        print(self.formkey)
        print(self.wilma2sid)

    def logout(self):
        self.session.post(
            "https://turku.inschool.fi/logout",
            data={
                "formkey": self.formkey,
            },
            headers={
                "Cookie": f"Wilma2SID={self.wilma2sid}"
            }
        )
        try:
            if self.session.cookies["Wilma2SID"]:
                return False
        except KeyError:
            return True

    def get_overview(self):
        data = self.session.post(
            f"https://turku.inschool.fi/!{self.id}/overview",
            headers={
                "Cookie": f"Wilma2SID={self.wilma2sid}"
            },
            data={
                "formkey": self.formkey,
            }
        ).json()
        return data

    def get_past_exams(self):
        data = self.session.get(
            f"https://turku.inschool.fi/!{self.id}/exams/calendar/past",
            headers={
                "Cookie": f"Wilma2SID={self.wilma2sid}"
            },
        )
        bs = bs4.BeautifulSoup(data.text, "html.parser")
        return [WilmaModels.Exam(exam) for exam in bs.find("tbody").find_all("tr")]