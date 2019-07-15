

class FrameIt(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.relabel, 0.5)
        self.orientation = 'vertical'
        self.l = Label(text='killings!', 
                color=(1.,0.,1.), 
                pos=(10,10))
        # self.l.movable = False
        self.add_widget(self.l)
        self.l.text_size = (Window.width, None)
        self.l.size = self.l.texture_size
    def relabel(self, dt):
        self.l.text = f'{RegisteredMov.t:5.2f}: {RegisteredMov.livings:4d} creatures remain'
    
