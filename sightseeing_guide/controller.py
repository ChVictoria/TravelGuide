from api import ConsoleUI
from guide import Guide
from re import *
from geopy.geocoders import Nominatim
from deep_translator import GoogleTranslator


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
            test_geolocator = Nominatim(user_agent="travelguidetest1")
            self.view.answer("Скажіть, будь ласка, локацію")
            user_location = self.view.get_user_speech()
            geocode = test_geolocator.geocode(user_location)
            if geocode:
                self.model.set_distance(user_location)
                return user_location
            else:
                self.view.answer("Не знаю такої локації. Спробуйте, будь ласка, ще раз.")
                return

    def single_propose(self, text):
        propose_one_pat = compile("пам'ят[кц]")
        if search(propose_one_pat, text.lower()):
            if not self.user_location:
                self.user_location = self.ask_location()
            if self.user_location:
                self.view.output_data(self.model.propose_to_visit(self.model.sights))
                return True
            else:
                self.view.output_data(self.model.propose_to_visit(self.model.sights))
                return True

    def get_criteria(self):
        criteria = ""
        for cr in self.model.sights.index:
            criteria += GoogleTranslator(source='auto', target=self.view.lang).translate(cr) + " "
        return criteria

    def multiple_propose(self, text):
        propose_multiple_pat = compile("топ*\d")
        mul_condition = search(propose_multiple_pat, text.lower())
        if mul_condition:
            criteria = self.get_criteria()
            self.view.answer('Чи є для вас найважливіший критерій з цих:' + criteria)
            if "так" in self.view.get_user_speech().lower():
                self.view.answer('Назвіть його, будь ласка.')
                prime_cr = self.view.get_user_speech().lower()
                self.view.output_data(self.model.propose_to_visit(self.model.sights,
                                      quantity=int(mul_condition[len(mul_condition)-1]), prime_criterion=prime_cr))
                return True
            else:
                self.view.output_data(self.model.propose_to_visit(self.model.sights,
                                                                  quantity=int(mul_condition[len(mul_condition) - 1])))
                return True


    def display_all(self, text):
        if search(compile("[ув]сі"), text.lower()):
            sorted = self.ask_for_sort(self.model.sights)
            self.view.output_data(sorted)


    def ask_for_sort(self, sights):
        self.view.answer("Відсортувати результат?")
        if "так" in self.view.get_user_speech().lower():
            if not self.user_location:
                self.user_location = self.ask_location()
            criteria = self.get_criteria()
            self.view.answer("Виберіть за яким критерієм: "+criteria)
            cr = GoogleTranslator(self.view.get_user_speech().lower(), target="en", source=self.view.lang).translate(cr)
            return self.model.sort_sights(sights, cr)
        return sights


    def find_all(self, text):
        types = {"замок":"замки", "собор":"собори", "палац":"палаци", "музей":"музеї", "площа":"площі"}
        for type in types.keys():
            if type or types[type] in text:
                sorted = self.ask_for_sort(self.model.find_sights(type))
                self.view.output_data(sorted)

    def goodbye(self, text):
        if "бувай" in text.lower() or "до побаченння" in text.lower():
            self.view.end_conv()

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
        while (user_text):
            self.process_speech(user_text)
            #TODO delay?
            self.view.answer("Слухаю наступне питання...")
            user_text = self.view.get_user_speech()
        self.view.end_conv()




v = ConsoleUI()
m = Guide("sights.json")
controller = Controller(m, v)
controller.run_bot()
