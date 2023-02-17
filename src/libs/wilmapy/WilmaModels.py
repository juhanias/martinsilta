class Exam:
    """Represents an exam. Contains all the info that appears in Wilma Frontend."""

    def __init__(self, bs):
        if len(bs.find_all("td")[2].text.split(":")) == 3:
            self.name = [subject.strip() for subject in bs.find_all("td")[2].text.split(":")][0]
            self.course_fullname = [subject.strip() for subject in bs.find_all("td")[2].text.split(":")][1]
            self.course_name = [subject.strip() for subject in bs.find_all("td")[2].text.split(":")][2]
        else:
            # Exam name field filled.
            self.name = "Kokeen nimi ei ole määritelty :("
            self.course_fullname = [subject.strip() for subject in bs.find_all("td")[2].text.split(":")][0]
            self.course_name = [subject.strip() for subject in bs.find_all("td")[2].text.split(":")][1]
        self.date_humanreadable = [subject.strip() for subject in bs.find_all("td")[0]][0]
        self.teachers = [Teacher(teacher) for teacher in bs.find_all('td')[1].find_all('a')]
        try:
            # Get the additional info and replace all the <br> elements from the code with line breaks
            self.additional_info = bs.find_all("td")[3].text.replace("<br>", "\n")
        except TypeError:
            self.additional_info = None

        try:
            self.results = [subject.strip() for subject in bs.find_all("td")[4].text.split(":")][0]
        except IndexError:
            self.results = None
        except TypeError:
            self.results = None

        try:
            if [subject.strip() for subject in bs.find_all("td")[5]][0] != "":
                self.review = [subject.strip() for subject in bs.find_all("td")[5]][0]
            else:
                self.review = None
        except IndexError:
            self.review = None
        except TypeError:
            self.review = None

    def has_been_graded(self) -> bool:
        if self.results is not None and self.results is not "":
            print(f"Exam {self.name} has been graded. ({self.results})")
            return True
        else:
            print(f"Exam {self.name} has NOT been graded. ({self.results})")
            return False


class Teacher:
    def __init__(self, bs):
        self.name = bs["title"]
        self.url = bs["href"]
