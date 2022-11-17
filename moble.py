import kivy  
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

from kivy.uix.floatlayout import FloatLayout 
from kivy.uix.scatter import Scatter
from kivy.uix.boxlayout import BoxLayout

import random

import ytmusicdl

red = [1,0,0,1]
green = [0,1,0,1]
blue =  [0,0,1,1]
purple = [1,0,1,1]

input_data = ytmusicdl.REQUESTED_INPUT_DATA
input_data['playlist_url'] = 'https://music.youtube.com/playlist?list=OLAK5uy_nbu8EUmXmbBb24DoOx_H7NBV_PKlo3Ku8'
input_data['cover_art'] = 'https://lh3.googleusercontent.com/5zD1MULLvF5bvatvjcyAyBHJZyvql_yrnrPfW2g5Sp6a5kRoMxVUlQp9iK6j8YHoIl03ZGwmN4NFW7M=w544-h544-l90-rj'
input_data['cutoff'] = 0

current_key = 'cutoff'

class HBoxLayoutExample(App):
    def build(self):
        global input_data

        layout = BoxLayout(padding=10, orientation='vertical')
        colors = [red, green, blue, purple]
        
        print(input_data)

        textinpts = []
        for i in ytmusicdl.REQUESTED_INPUT_DATA:
            layout.add_widget(Label(text=i))
            textinput = TextInput(text=str(input_data[i]))
            layout.add_widget(textinput)
            
            if i == 'playlist_url':
                textinput.bind(text=self.uid_playlist_url)
            elif i == 'album':
                textinput.bind(text=self.uid_album)
            elif i == 'artist':
                textinput.bind(text=self.uid_artist)
            elif i == 'cover_art':
                textinput.bind(text=self.uid_art)
            elif i == 'cutoff':
                textinput.bind(text=self.uid_cutoff)
            

        submit = Button(text='submit')
        submit.bind(on_press=self.submit)
        layout.add_widget(submit)

        return layout

    def uid_playlist_url(self, instance, value): self.update_input_dict('playlist_url', value)
    def uid_album(self, instance, value): self.update_input_dict('album', value)
    def uid_artist(self, instance, value): self.update_input_dict('artist', value)
    def uid_art(self, instance, value): self.update_input_dict('cover_art', value)
    def uid_cutoff(self, instance, value): self.update_input_dict('cutoff', value)
        
    def update_input_dict(self, key, value):
        global input_data

        input_data[key] = value
    
    def submit(self, instance):
        global input_data

        print(instance.text)
        print('Sumbit')
        print(input_data)
        ytmusicdl.download_content(input_data)

if __name__ == "__main__":
    app = HBoxLayoutExample()
    run = app.run()
    print(run)
