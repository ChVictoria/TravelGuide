from api import ConsoleUI
from guide import Guide
from re import *
from deep_translator import GoogleTranslator
import time

class Controller:
    def __init__(self, model: Guide, view: ConsoleUI):
        self.model = model
        self.view = view
        self.user_location = None

    def tell_about_sight(self, text):
        sight_to_tell = self.model.check_sight(text)
        if sight_to_tell:
            self.view.answer(self.model.tell_about_sight(sight_to_tell))
            return True

    def ask_location(self):
        self.view.answer("Чи бажаєте здійснити пошук біля якоїсь локації?")
        if self.view.get_user_speech().lower() == "так":
            self.view.answer("Скажіть, будь ласка, локацію")
            check_loc = None
            while not check_loc:
                user_location = self.view.get_user_speech()
                check_loc = self.model.check_location(user_location)
                if check_loc:
                    self.model.set_distance(user_location)
                    return user_location
                else:
                    self.view.answer("Не знаю такої локації. Спробуйте, будь ласка, ще раз.")


    def check_and_set_location(self):
        if not self.user_location:
            self.user_location = self.ask_location()

    def single_propose(self, text):
        propose_one_pat = compile("пам'ятк[уа]")
        if search(propose_one_pat, text.lower()):
            self.check_and_set_location()
            result = self.model.propose_to_visit(self.model.sights)
            self.output_sights(result)
            return True

    def get_criteria(self):
        criteria = ""
        for cr in self.model.get_criteria():
            criteria += GoogleTranslator(source='en', target=self.view.lang).translate(cr) + " "
        return criteria

    def output_sights(self, result):
        self.view.output_data(self.model.get_sights_for_output(result))
    def multiple_propose(self, text):
        propose_multiple_pat = compile("топ.*\d")
        mul_condition = findall(propose_multiple_pat, text.lower())
        if mul_condition:
            self.check_and_set_location()
            criteria = self.get_criteria()
            self.view.answer('Чи бажаєте обрати найважливіший критерій для пошуку?')
            if "так" in self.view.get_user_speech().lower():
                self.view.answer('Оберіть один з цих, будь ласка:' + criteria)
                prime_cr = GoogleTranslator(source=self.view.lang, target="en").translate(
                    self.view.get_user_speech().lower())
                result = self.model.propose_to_visit(self.model.sights, quantity=int(mul_condition[-1][-1]),
                                                                        prime_criterion=prime_cr)
                self.output_sights(result)
                return True
            else:
                result = self.model.propose_to_visit(self.model.sights, quantity=int(mul_condition[-1][-1]))
                self.output_sights(result)
                return True

    def display_all(self, text):
        if search(compile("[ув]сіx{0,1}"), text.lower()):
            sorted_sights = self.ask_for_sort(self.model.sights)
            self.output_sights(sorted_sights)
            return True

    def ask_for_sort(self, sights):
        self.view.answer("Відсортувати результат?")
        if "так" in self.view.get_user_speech().lower():
            criteria = self.get_criteria()
            self.view.answer("Виберіть за яким критерієм відсортувати: " + criteria)
            cr = GoogleTranslator(source=self.view.lang, target="en").translate(self.view.get_user_speech())
            return self.model.sort_sights(sights, cr)
        return sights

    def find_all(self, text):
        self.check_and_set_location()
        types = {"замок": "замки", "собор": "собори", "палац": "палаци", "музей": "музеї", "площа": "площі"}
        for t in types.keys():
            if (t in text.lower()) or (types[t] in text.lower()):
                sorted_sights = self.ask_for_sort(self.model.find_sights(t))
                self.output_sights(sorted_sights)
                return True

    def goodbye(self, text):
        if ("бувай" in text.lower()) or ("до побачення" in text.lower()):
            self.view.end_conv()
            return True

    def process_speech(self, text):
        if not self.tell_about_sight(text):
            if not self.single_propose(text):
                if not self.multiple_propose(text):
                    if not self.find_all(text):
                        if not self.display_all(text):
                            if not self.goodbye(text):
                                self.view.unknown_command()

    def run_bot(self):
        self.view.start_conv()
        user_text = self.view.get_user_speech()
        while user_text:
            self.process_speech(user_text)
            time.sleep(2)
            self.view.answer("Слухаю наступне питання...")
            user_text = self.view.get_user_speech()
        self.view.end_conv()


v = ConsoleUI()
m = Guide("sights.json")
controller = Controller(m, v)
controller.run_bot()
