import os

from gtts import gTTS
from playsound import playsound
import speech_recognition as sr

class ConsoleUI:
    def __init__(self):
        self.lang = "uk"
        self.recognizer = sr.Recognizer()

    def start_conv(self):
        self.answer('Добрий день')#, я - ваш помічник з відвідування історичних пам’яток Львова! Чим можу допомогти?')

    def output_data(self, dataframe):
        self.answer('Ось результати за Вашим запитом!')
        for column in dataframe.columns:
            print(dataframe.loc[:, [column]].to_string())#TODO translate row names
            print('*+~-~+'*50)

    def answer(self, text):
        print(text)
        if os.path.exists("answer.mp3"):
            os.remove("answer.mp3")
        voice = gTTS(text=text, lang=self.lang, slow=False)
        voice.save("answer.mp3")
        playsound("answer.mp3")#TODO stop

        #TODO add delay if needed(or in controller)

    def get_user_speech(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
            self.answer("Слухаю Вас ...")
            audio = self.recognizer.listen(source)

        try:
            text = self.recognizer.recognize_google(audio, language=self.lang)
            print("User: " + text)

        except sr.UnknownValueError:
            text = ""
            self.answer("Вибачте, я Вас не розумію. Спробуйте знов.")
            return self.get_user_speech()

        except sr.RequestError as e:
            print("Помилка; {0}. Можливо аудіо задовге, спробуйте, будь ласка, ще раз.".format(e))
            return self.get_user_speech()

        return text

    def unknown_command(self):
        self.answer('Не зрозуміла команда або даних по Вашому запиту немає на сервері. Спробуйте ще раз.')


    def end_conv(self):
        self.answer("Радий був допомогти! До побачення!")
        exit()