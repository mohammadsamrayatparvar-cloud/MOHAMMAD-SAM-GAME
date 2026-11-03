from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Ellipse, RoundedRectangle, Line

class PlatformGame(Widget):
    WORLD_W = 2600
    GRAVITY = 1850
    MOVE_SPEED = 310
    JUMP_SPEED = 760

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player_x, self.player_y = 70.0, 180.0
        self.vy = 0.0
        self.on_ground = False
        self.camera_x = 0.0
        self.score = 0
        self.coins = [(330,210),(390,210),(650,310),(710,310),(1050,205),
                      (1110,205),(1430,360),(1490,360),(1840,230),(1900,230),(2220,310)]
        self.enemies = [[520,90,1],[900,90,-1],[1320,90,1],[1710,90,-1],[2070,90,1]]
        self.platforms = [
            (0,0,520,70),(600,0,420,70),(1100,0,430,70),
            (1600,0,450,70),(2120,0,480,70),
            (260,180,190,22),(610,280,190,22),(990,180,190,22),
            (1370,330,190,22),(1770,205,190,22),(2160,280,190,22)
        ]
        self.left_down = self.right_down = self.jump_requested = False
        self.won = self.dead = False
        self.hud = Label(text="", font_size="18sp", bold=True, color=(1,1,1,1),
                         size_hint=(None,None))
        self.add_widget(self.hud)
        self.notice = Label(text="", font_size="25sp", bold=True,
                            color=(1,0.92,0.2,1), halign="center", valign="middle")
        self.add_widget(self.notice)
        self.bind(size=self.layout_ui)
        self.layout_ui()
        Clock.schedule_interval(self.update, 1/60)

    def layout_ui(self, *args):
        self.hud.pos, self.hud.size = (12,self.height-48), (270,42)
        self.notice.pos, self.notice.size = (0,self.height*.4), self.size
        self.notice.text_size = self.size

    def restart(self):
        self.player_x,self.player_y=70.0,180.0
        self.vy=0; self.camera_x=0; self.score=0
        self.coins=[(330,210),(390,210),(650,310),(710,310),(1050,205),
                    (1110,205),(1430,360),(1490,360),(1840,230),(1900,230),(2220,310)]
        self.enemies=[[520,90,1],[900,90,-1],[1320,90,1],[1710,90,-1],[2070,90,1]]
        self.won=self.dead=False
        self.notice.text=""

    def on_touch_down(self,touch):
        if self.won or self.dead:
            self.restart()
            return True
        if touch.x < self.width/3: self.left_down=True
        elif touch.x < self.width*2/3: self.right_down=True
        else: self.jump_requested=True
        return True

    def on_touch_up(self,touch):
        self.left_down=self.right_down=False
        return True

    def update(self,dt):
        if self.dead or self.won:
            self.draw_scene()
            return
        dt=min(dt,1/30)
        old_y=self.player_y
        if self.left_down: self.player_x-=self.MOVE_SPEED*dt
        if self.right_down: self.player_x+=self.MOVE_SPEED*dt
        self.player_x=max(0,min(self.WORLD_W-55,self.player_x))
        if self.jump_requested and self.on_ground:
            self.vy=self.JUMP_SPEED
            self.on_ground=False
        self.jump_requested=False
        self.vy-=self.GRAVITY*dt
        self.player_y+=self.vy*dt
        self.on_ground=False
        pw,ph=42,58
        for x,y,w,h in self.platforms:
            if (self.player_x+pw>x and self.player_x<x+w and old_y>=y+h-5
                and self.player_y<=y+h and self.vy<0):
                self.player_y=y+h
                self.vy=0
                self.on_ground=True
        if self.player_y < -100:
            self.dead=True
            self.notice.text="جدی می‌فرماید!\nبازی تمام شد\nبرای شروع دوباره لمس کن"
        for coin in self.coins[:]:
            cx,cy=coin
            if abs(self.player_x+pw/2-cx)<35 and abs(self.player_y+ph/2-cy)<42:
                self.coins.remove(coin); self.score+=10
        for enemy in self.enemies:
            enemy[0]+=enemy[2]*95*dt
            if enemy[0]<80 or enemy[0]>self.WORLD_W-100: enemy[2]*=-1
            if abs(self.player_x+pw/2-enemy[0])<35 and abs(self.player_y+ph/2-enemy[1])<48:
                if self.vy < -100 and self.player_y>enemy[1]:
                    enemy[0]=-500; self.vy=430; self.score+=20
                else:
                    self.dead=True
                    self.notice.text="جدی می‌فرماید!\nبازی تمام شد\nبرای شروع دوباره لمس کن"
        self.camera_x=max(0,min(self.WORLD_W-self.width,self.player_x-self.width*.36))
        if self.player_x>self.WORLD_W-150:
            self.won=True
            self.notice.text="مرحله کامل شد!\nجدی می‌فرماید!\nبرای بازی دوباره لمس کن"
        self.draw_scene()

    def draw_scene(self):
        self.canvas.clear()
        cam=self.camera_x
        with self.canvas:
            Color(.35,.72,.98,1); Rectangle(pos=self.pos,size=self.size)
            Color(.22,.66,.45,1)
            for hx in range(-1,9):
                x=hx*250-(cam*.25)%250
                Ellipse(pos=(x,self.height*.42),size=(330,190))
            for x,y,w,h in self.platforms:
                sx=x-cam
                if sx+w < -20 or sx > self.width+20: continue
                Color(.48,.25,.10,1); Rectangle(pos=(sx,y),size=(w,h))
                Color(.20,.72,.22,1); Rectangle(pos=(sx,y+h-8),size=(w,8))
            for cx,cy in self.coins:
                sx=cx-cam
                if -30<sx<self.width+30:
                    Color(1,.78,.05,1); Ellipse(pos=(sx-13,cy-13),size=(26,26))
                    Color(1,.95,.55,1); Line(circle=(sx,cy,8),width=1.5)
            for ex,ey,direction in self.enemies:
                sx=ex-cam
                if -50<sx<self.width+50 and ex>=0:
                    Color(.55,.12,.18,1)
                    RoundedRectangle(pos=(sx-20,ey),size=(40,34),radius=[10])
                    Color(1,1,1,1)
                    Ellipse(pos=(sx-10,ey+19),size=(7,7))
                    Ellipse(pos=(sx+3,ey+19),size=(7,7))
            fx=self.WORLD_W-110-cam
            Color(.15,.15,.15,1); Rectangle(pos=(fx,70),size=(5,180))
            Color(1,.85,.05,1); Rectangle(pos=(fx+5,205),size=(65,35))
            px,py=self.player_x-cam,self.player_y
            Color(.05,.18,.72,1); RoundedRectangle(pos=(px,py),size=(42,58),radius=[9])
            Color(.98,.78,.55,1); Ellipse(pos=(px+8,py+37),size=(26,19))
            Color(.8,.05,.08,1); Rectangle(pos=(px+4,py+51),size=(34,8))
            Color(1,1,1,1)
            Ellipse(pos=(px+15,py+43),size=(5,5)); Ellipse(pos=(px+26,py+43),size=(5,5))
            Color(.05,.05,.08,.35)
            for bx in (.04,.36,.68):
                RoundedRectangle(pos=(self.width*bx,self.height*.025),
                                 size=(self.width*.28,self.height*.10),radius=[14])
        self.hud.text="MOHAMMAD SAM GAME   COINS: "+str(self.score)
        self.hud.pos=(12,self.height-48)

class MohammadSamGameApp(App):
    def build(self):
        self.title="MOHAMMAD SAM GAME"
        return PlatformGame()

if __name__=="__main__":
    MohammadSamGameApp().run()
