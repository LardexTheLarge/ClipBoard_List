from kivy.app import App
from kivy.uix.label import Label
from backend import setup_channel  # Import the setup_channel function

class MyApp(App):
    def build(self):
        setup_channel()  # Initialize the platform channel
        return Label(text='Python backend is running')

if __name__ == '__main__':
    MyApp().run()