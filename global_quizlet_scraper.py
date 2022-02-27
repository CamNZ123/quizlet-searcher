from requests import get
from bs4 import BeautifulSoup
import os
from difflib import SequenceMatcher

headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'}


class QuizletObject:
    def __init__(self, link: str, data=None):
        if data is None:
            data = []
        self.link = link
        self.data = data

    def __len__(self):
        return len(self.data)

    def add(self, question: str, answer: str):
        self.data.append((question, answer))


class Question:

    def __init__(self, question: str, answers=None) -> None:
        """
        Declares variables for future use
        :param question: str
            The question that is is searching for
        """
        self.question = question
        self.answers = answers
        self.search_question = ""
        self.flag = None
        self.links = set()
        self.quizlet_objects = []
        self.answer = ""

    def did_you_mean(self) -> None:
        """
        defines a search question by spell checking the requested question
        """
        raw = get(f"https://www.google.com/search?q={self.question}").text
        soup = BeautifulSoup(raw, 'html.parser')
        did_you_mean = soup.find("div", {"class": "MUxGbd v0nnCb lyLwlc"})
        if did_you_mean is not None:
            self.search_question, self.flag = did_you_mean.a.text, True
        self.search_question, self.flag = self.question, False

    def search(self, input_question: str) -> None:
        """
        Searches each of the questions and gets the quizlet links
        :param input_question: str
            The valid questions for the google search
        """
        search_string = "https://www.google.com/search?q=" + input_question
        html = get(search_string, headers=headers)
        soup = BeautifulSoup(html.text, 'html.parser')
        divs = soup.findAll(class_="yuRUbf")
        results = []
        for div in divs:
            results.append(div.find("a")["href"])
        # links of results
        for link in results[:2]:
            self.links.add(link)

    def get_links(self) -> None:
        """
        Searches all combinations for questions formats
        """
        self.did_you_mean()
        self.search(self.search_question + " site:quizlet.com")
        self.search(rf'"{self.search_question}" site:quizlet.com')
        if self.flag:
            self.search(rf'{self.question} site:quizlet.com')
            self.search(rf'"{self.question}" site:quizlet.com')

    def get_best_answer(self) -> None:
        """
        Goes through the quizlet and finds the term and answer which is closest to the
        question that we have given.
        """
        quiz = ""
        answer = ""
        link = ""
        best_similarity = 0.0
        good_answer_found = False

        for quizlet in self.quizlet_objects:
            for term in range(len(quizlet)):
                if not good_answer_found:
                    for i in range(2):
                        match = SequenceMatcher(None, a=self.question, b=quizlet.data[term][i]).ratio()
                        if match > best_similarity:
                            quiz = quizlet.data[term][i]
                            best_similarity = match
                            answer = quizlet.data[term][int(not i)]
                            link = quizlet.link
                            if best_similarity > 0.95:
                                good_answer_found = True
                                break
        self.print_answer(quiz, best_similarity, answer, link)

    def print_answer(self, quiz, best_similarity, answer, link) -> None:
        """
        Prints out the answer to the quizlet
        :param quiz: The question that has been found
        :param best_similarity: The percent that it matches with the original question
        :param answer: The answer to the found question
        :param link: The link to the found quizlet
        """
        print("Question: " + self.question)
        print("Found Question: " + quiz)
        print(f"Match: {int(best_similarity * 100)}%")
        print()
        print("Answer: " + answer.lower())
        print()
        print("Link: " + link)

    def get_quizlet_objects(self):
        """
        Creates a quizlet object for each of the links
        """
        # Gets list of quizlet objects and creates a list in self.quizlet_objects
        # for each in self.links

        for link in self.links:
            soup = BeautifulSoup(get(link, headers=headers).content, 'html.parser')
            new_obj = QuizletObject(link)
            for i, (question, answer) in enumerate(
                    zip(soup.select('a.SetPageTerm-wordText'), soup.select('a.SetPageTerm-definitionText')), 1):
                question_text = question.get_text(strip=True, separator='\n')
                answer_text = answer.get_text(strip=True, separator='\n')
                new_obj.add(question_text, answer_text)
            self.quizlet_objects.append(new_obj)


def single_question():
    while True:
        question = input("Question: ")
        print()
        print("=" * 25 + f" LOADING " + "=" * 25)
        question_object = Question(question)
        print("Created question")
        question_object.get_links()
        print(f"Found {len(question_object.links)} quizlet links")
        question_object.get_quizlet_objects()
        print(f"Created quizlet objects")
        print("Finding best answer ...")
        print()
        question_object.get_best_answer()
        print()


single_question()
