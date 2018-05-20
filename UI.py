from Tkinter import *
import ttk
import tkMessageBox
import tkFont
import RPi.GPIO as GPIO
import Queue
import threading
import thread
import time
import random
from datetime import datetime

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
#left right
stepPinMotor1=26 	#yellow
dirPinMotor1=24 	#white
#up down
stepPinMotor2=10 	#brown
dirPinMotor2=8		#orange
#front back
stepPinMotor3=16	#pink	
dirPinMotor3=12		#purple
#glass2 left right
stepPinMotor4=33	#blue
dirPinMotor4=31		#green

#glass3 left right
stepPinMotor5=22
dirPinMotor5=18

#shake	
shakeMotor2B=29	
#lid
lidMotor2A=7		
lidMotor2B=11		
#glass1 left right
dcMotor1A=13     	
dcMotor1B=15    	
#water
waterPump1=3 		
waterPump2=5		
#ice
iceMotorA=23		
		
irSensor1=19		   	#glass1
irSensor2=21 			#glass3
#left right 
limitSwitchMotor1=32 #black
#up down
limitSwitchMotor2=38 #white
#front back
limitSwitchMotor3=36 #red
#glass2 left right 
limitSwitchMotor4=37 #orange
#lid 
limitSwitchLid=35	 #yellow
#shake
limitSwitchGlass2=40 #blue

GPIO.setup(stepPinMotor1,GPIO.OUT) #left right
GPIO.setup(dirPinMotor1,GPIO.OUT)
GPIO.setup(stepPinMotor2,GPIO.OUT) #up down
GPIO.setup(dirPinMotor2,GPIO.OUT)
GPIO.setup(stepPinMotor3,GPIO.OUT) #forward back
GPIO.setup(dirPinMotor3,GPIO.OUT)
GPIO.setup(stepPinMotor4,GPIO.OUT) # shake left right
GPIO.setup(dirPinMotor4,GPIO.OUT)
GPIO.setup(stepPinMotor5,GPIO.OUT) # glass3 left right
GPIO.setup(dirPinMotor5,GPIO.OUT)

GPIO.setup(shakeMotor2B,GPIO.OUT)
sm2B = GPIO.PWM(29,1000)

GPIO.setup(lidMotor2A,GPIO.OUT)
GPIO.setup(lidMotor2B,GPIO.OUT)

GPIO.setup(dcMotor1A,GPIO.OUT)
GPIO.setup(dcMotor1B,GPIO.OUT)

GPIO.setup(waterPump1,GPIO.OUT)
GPIO.setup(waterPump2,GPIO.OUT)

GPIO.setup(iceMotorA,GPIO.OUT)

GPIO.setup(irSensor1,GPIO.IN)
GPIO.setup(irSensor2,GPIO.IN)

GPIO.setup(limitSwitchMotor1,GPIO.IN)
GPIO.setup(limitSwitchMotor2,GPIO.IN)
GPIO.setup(limitSwitchMotor3,GPIO.IN)
GPIO.setup(limitSwitchMotor4,GPIO.IN)
GPIO.setup(limitSwitchLid,GPIO.IN)
GPIO.setup(limitSwitchGlass2,GPIO.IN)


#/*Motor1 1rev=2cm* 1/16 6400 blue yellow green white */  	#LOW right HIGH left
#/*Motor2 1rev=0.8cm 1/32  3200 green blue black red */		#HIGH up LOW down

class MyFrame(ttk.Frame):
	def __init__(self, master, name):
		ttk.Frame.__init__(self, master)
		self.name = name
		self.pack()

	def update(self):
		print "Updating %s" % self.name


class GUI():
	Menu=[]
	Recipe=[]
	orderNumber=1
	def __init__(self,master):		
		self.master=master
		master.title("Mocktail Making Machine")
		master.geometry("800x480") 
		myFont=tkFont.Font(family='THSarabun',size=10)
		myFontBig=tkFont.Font(family='THSarabun',size=16)
		self.myFont=tkFont.Font(family='THSarabun',size=12)
		self.myFontBig=tkFont.Font(family='THSarabun',size=16)
		style = ttk.Style()
		style.theme_create( "MyStyle", parent="alt",settings={"TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0] } },"TNotebook.Tab": {"configure": {"padding": [3, 3] },}})
		style.theme_use("MyStyle")
		self.nb = ttk.Notebook(self.master,width=200,height=200)
		master.attributes('-fullscreen', True)
		#master.configure(background='white')
		
		self.f1_name = "Home"
		self.f2_name = "Manual"
		self.f3_name = "Setting"
		self.f1 = MyFrame(self.nb, self.f1_name)
		self.f2 = MyFrame(self.nb, self.f2_name)
		
		self.nb.add(self.f1,text=self.f1_name)
		self.nb.add(self.f2,text=self.f2_name)
		self.nb.pack(fill="both", expand=True)

		self.readFile()
		 
		#F1
		self.dashBoard = Frame(self.f1,width=600,height=300)
		self.dashBoard.place(x=195,y=160)
		
		self.recommend = Frame(self.f1,width=600,height=160)
		self.recommend.place(x=195,y=0)
#1E90FF		
		self.butPanel = Frame(self.f1,width=195,height=460,bg='#ffb400')
		self.butPanel.place(x=0,y=0)
		
		self.dashList=Listbox(self.dashBoard,width=50,height=11,font=self.myFont)
		self.dashList.grid(padx=(45,0),pady=20,row=0,column=0)
		self.scrollbar = Scrollbar(self.dashBoard, orient="vertical",width=11)
		self.scrollbar.config(command=self.dashList.yview)
		self.scrollbar.grid(row=0,column=1,sticky='ns',pady=20,padx=(0,50))
		self.dashList.config(yscrollcommand=self.scrollbar.set)
		
		self.logoPic=Label(self.butPanel)
		self.logo=PhotoImage(file="ffb400.png")
		self.logoPic.config(image=self.logo,width="173",height="64")
		self.logoPic.place(x=10,y=20)
		self.orderButton=Button(self.butPanel,text="Order Drinks",width=12,command=lambda:self.orderClick())
		self.orderButton.place(x=10,y=110)
		#self.favButton=Button(self.butPanel,text="Favourite",width=18,command=lambda:self.orderClick())
		#self.favButton.place(x=10,y=70)
		self.settingButton=Button(self.butPanel,command=lambda:self.settingClick())
		self.photo=PhotoImage(file="setting.png")
		self.settingButton.config(image=self.photo,width="30",height="30")
		self.settingButton.place(x=150,y=100)
		self.qLabel=Label(self.butPanel,text="%d Queue in progress"%q4.qsize(),font=self.myFont)
		self.qLabel.place(x=15,y=150)
		self.qList=Listbox(self.butPanel,width=10,height=9,font=self.myFont,relief='sunken')
		self.qList.place(x=40,y=190)
		
		self.waterPic1=Label(self.recommend)
		self.waterPic2=Label(self.recommend)
		self.waterPic3=Label(self.recommend)
		self.waterPic4=Label(self.recommend)
		self.waterPic5=Label(self.recommend)
		self.waterPic6=Label(self.recommend)
		self.waterPic7=Label(self.recommend)
		self.waterPic8=Label(self.recommend)
		self.waterPic9=Label(self.recommend)
		self.waterPic10=Label(self.recommend)
		self.wp0=PhotoImage(file="bot0r.png")
		self.wp1=PhotoImage(file="bot25r.png")
		self.wp2=PhotoImage(file="bot50r.png")
		self.wp3=PhotoImage(file="bot75r.png")
		self.wp4=PhotoImage(file="bot100r.png")
		self.waterPic1.config(image=self.wp1,width="64",height="64")
		self.waterPic1.place(x=-5,y=70)
		self.waterPic2.config(image=self.wp1,width="64",height="64")
		self.waterPic2.place(x=54,y=70)
		self.waterPic3.config(image=self.wp1,width="64",height="64")
		self.waterPic3.place(x=118,y=70)
		self.waterPic4.config(image=self.wp1,width="64",height="64")
		self.waterPic4.place(x=178,y=70)
		self.waterPic5.config(image=self.wp1,width="64",height="64")
		self.waterPic5.place(x=236,y=70)
		self.waterPic6.config(image=self.wp1,width="64",height="64")
		self.waterPic6.place(x=296,y=70)
		self.waterPic7.config(image=self.wp1,width="64",height="64")
		self.waterPic7.place(x=356,y=70)
		self.waterPic8.config(image=self.wp1,width="64",height="64")
		self.waterPic8.place(x=416,y=70)
		self.waterPic9.config(image=self.wp1,width="64",height="64")
		self.waterPic9.place(x=476,y=70)
		self.waterPic10.config(image=self.wp1,width="64",height="64")
		self.waterPic10.place(x=536,y=70)
		self.calWater(0,0,0,0,0,0,0,0,0,0)
		
		self.Level1=Label(self.recommend,textvariable=self.Water1,font=self.myFont,bd=2,relief='groove').place(x=10,y=25)
		self.Level2=Label(self.recommend,textvariable=self.Water2,font=self.myFont,bd=2,relief='groove').place(x=70,y=25)
		self.Level3=Label(self.recommend,textvariable=self.Water3,font=self.myFont,bd=2,relief='groove').place(x=130,y=25)
		self.Level4=Label(self.recommend,textvariable=self.Water4,font=self.myFont,bd=2,relief='groove').place(x=190,y=25)
		self.Level5=Label(self.recommend,textvariable=self.Water5,font=self.myFont,bd=2,relief='groove').place(x=250,y=25)
		self.Level6=Label(self.recommend,textvariable=self.Water6,font=self.myFont,bd=2,relief='groove').place(x=310,y=25)
		self.Level7=Label(self.recommend,textvariable=self.Water7,font=self.myFont,bd=2,relief='groove').place(x=370,y=25)
		self.Level8=Label(self.recommend,textvariable=self.Water8,font=self.myFont,bd=2,relief='groove').place(x=430,y=25)
		self.Level9=Label(self.recommend,textvariable=self.Water9,font=self.myFont,bd=2,relief='groove').place(x=490,y=25)
		self.Level10=Label(self.recommend,textvariable=self.Water10,font=self.myFont,bd=2,relief='groove').place(x=550,y=25)
		
		#F2
		self.l1=Label(self.f2,text="Bottle1",font=myFont).place(x=10,y=10)
		self.s1=Spinbox(self.f2,width=3,from_=0,to=10,font=myFont)
		self.s1.place(x=90,y=10)
		self.l2=Label(self.f2,text="Bottle2",font=myFont).place(x=10,y=40)
		self.s2=Spinbox(self.f2,width=3,from_=0,to=10,font=myFont)
		self.s2.place(x=90,y=40)
		self.l3=Label(self.f2,text="Bottle3",font=myFont).place(x=10,y=70)
		self.s3=Spinbox(self.f2,width=3,from_=0,to=10,font=myFont)
		self.s3.place(x=90,y=70)
		self.l4=Label(self.f2,text="Bottle4",font=myFont).place(x=10,y=100)
		self.s4=Spinbox(self.f2,width=3,from_=0,to=10,font=myFont)
		self.s4.place(x=90,y=100)
		self.l5=Label(self.f2,text="Bottle5",font=myFont).place(x=10,y=130)
		self.s5=Spinbox(self.f2,width=3,from_=0,to=10,font=myFont)
		self.s5.place(x=90,y=130)
		self.l6=Label(self.f2,text="Bottle6",font=myFont).place(x=150,y=10)
		self.s6=Spinbox(self.f2,width=3,from_=0,to=10,font=myFont)
		self.s6.place(x=230,y=10)
		self.l7=Label(self.f2,text="Bottle7",font=myFont).place(x=150,y=40)
		self.s7=Spinbox(self.f2,width=3,from_=0,to=10,font=myFont)
		self.s7.place(x=230,y=40)
		self.l8=Label(self.f2,text="Bottle8",font=myFont).place(x=150,y=70)
		self.s8=Spinbox(self.f2,width=3,from_=0,to=10,font=myFont)
		self.s8.place(x=230,y=70)
		self.l9=Label(self.f2,text="Bottle9",font=myFont).place(x=150,y=100)
		self.s9=Spinbox(self.f2,width=3,from_=0,to=10,font=myFont)
		self.s9.place(x=230,y=100)
		self.l10=Label(self.f2,text="Bottle10",font=myFont).place(x=150,y=130)
		self.s10=Spinbox(self.f2,width=3,from_=0,to=10,font=myFont)
		self.s10.place(x=230,y=130)
		self.l11=Label(self.f2,text="Max shot=10",font=myFontBig).place(x=300,y=20)
		self.b1=Button(self.f2,text="Order",font=myFontBig,command=lambda:self.manOrderMenu()).place(x=330,y=50)
		
		self.manIce = IntVar()
		self.manIceCheck = Checkbutton(self.f2, text="ICE", variable=self.manIce,height=1,font=myFont)
		self.manIceCheck.place(x=300,y=100)
		
		self.manShake = IntVar()
		self.manShakeCheck = Checkbutton(self.f2, text="SHAKE", variable=self.manShake,height=1,font=myFont)
		self.manShakeCheck.place(x=300,y=130)
		
		self.l12=Label(self.f2,text="Manual",font=myFontBig,fg="red").place(x=10,y=165)
		
		self.gu=Button(self.f2,width=6,text="Go Up",font=myFont,command=lambda:q.put("pro.moveMotor2Up(10000,1,4)")).place(x=95,y=205)
		self.gl=Button(self.f2,width=6,text="Go Left",font=myFont,command=lambda:q.put("pro.moveMotor1Left(8000,1,200)")).place(x=50,y=235)
		self.gr=Button(self.f2,width=6,text="Go Right",font=myFont,command=lambda:q.put("pro.moveMotor1Right(8000,1,200)")).place(x=140,y=235)
		self.gf=Button(self.f2,width=6,text="Go Down",font=myFont,command=lambda:q.put("pro.moveMotor2Down(10000,1,4)")).place(x=95,y=265)
		
		self.mgu=Button(self.f2,width=8,text="M Go Up",font=myFont,command=lambda:q.put("pro.moveMotor2Up(%s,1,5)"%(self.s11.get()))).place(x=335,y=205)
		self.mgl=Button(self.f2,width=8,text="M Go Left",font=myFont,command=lambda:q.put("pro.moveMotor1Left(%s,1,200)"%(self.s11.get()))).place(x=250,y=235)
		self.mgr=Button(self.f2,width=8,text="M Go Right",font=myFont,command=lambda:q.put("pro.moveMotor1Right(%s,1,200)"%(self.s11.get()))).place(x=420,y=235)
		self.mgd=Button(self.f2,width=8,text="M Go Down",font=myFont,command=lambda:q.put("pro.moveMotor2Down(%s,1,4)"%(self.s11.get()))).place(x=335,y=265)
		self.s11=Spinbox(self.f2,width=6,from_=0,to=50000,font=myFont)
		self.s11.place(x=350,y=240)
		
		self.g2l=Button(self.f2,width=5,text="G2 Left",font=myFont,command=lambda:q2.put("pro.moveMotor4Left(5000,1,50)")).place(x=540,y=205)
		self.g2r=Button(self.f2,width=5,text="G2 Right",font=myFont,command=lambda:q2.put("pro.moveMotor4Right(5000,1,50)")).place(x=700,y=205)
		self.g2ml=Button(self.f2,width=5,text="G2 MLeft",font=myFont,command=lambda:q2.put("pro.moveMotor4Left(%s,1,50)"%(self.s12.get()))).place(x=540,y=235)
		self.s12=Spinbox(self.f2,width=6,from_=0,to=50000,font=myFont)
		self.s12.place(x=620,y=240)
		self.g2mr=Button(self.f2,width=5,text="G2 MRight",font=myFont,command=lambda:q2.put("pro.moveMotor4Right(%s,1,50)"%(self.s12.get()))).place(x=700,y=235)		
		
		self.gf=Button(self.f2,width=5,text="Go Front",font=myFont,command=lambda:q.put("pro.moveMotor3Front(7500,1,50)")).place(x=540,y=265)
		self.gb=Button(self.f2,width=5,text="Go Back",font=myFont,command=lambda:q.put("pro.moveMotor3Back(7500,1,50)")).place(x=700,y=265)
		self.mgf=Button(self.f2,width=5,text="Go MFront",font=myFont,command=lambda:q.put("pro.moveMotor3Front(%s,1,50)"%(self.s13.get()))).place(x=540,y=295)
		self.s13=Spinbox(self.f2,width=6,from_=0,to=50000,font=myFont)
		self.s13.place(x=620,y=300)
		self.mgb=Button(self.f2,width=5,text="Go MBack",font=myFont,command=lambda:q.put("pro.moveMotor3Back(%s,1,50)"%(self.s13.get()))).place(x=700,y=295)		
		
		self.g1l=Button(self.f2,width=5,text="G1 Left",font=myFont,command=lambda:q.put("pro.dcMotor1Control(1)")).place(x=50,y=335)
		self.g1s=Button(self.f2,width=5,text="G1 Stop",font=myFont,command=lambda:q.put("pro.dcMotor1Control(0)")).place(x=120,y=335)
		self.g1r=Button(self.f2,width=5,text="G1 Right",font=myFont,command=lambda:q.put("pro.dcMotor1Control(-1)")).place(x=190,y=335)
		self.g1cl=Button(self.f2,width=5,text="G1ConL",font=myFont,command=lambda:q.put("pro.glass1Control(1)")).place(x=260,y=335)
		self.g1cr=Button(self.f2,width=5,text="G1ConR",font=myFont,command=lambda:q.put("pro.glass1Control(-1)")).place(x=330,y=335)
		
		self.g2cl=Button(self.f2,width=5,text="G2ConL",font=myFont,command=lambda:q2.put("pro.glass2Control(1)")).place(x=410,y=335)
		self.g2cr=Button(self.f2,width=5,text="G2ConR",font=myFont,command=lambda:q2.put("pro.glass2Control(-1)")).place(x=480,y=335)
		self.lo=Button(self.f2,width=6,text="G2LidOpen",font=myFont,command=lambda:q2.put("pro.glass2LidOpen()")).place(x=550,y=335)
		self.lc=Button(self.f2,width=6,text="G2LidClose",font=myFont,command=lambda:q2.put("pro.glass2LidClose()")).place(x=630,y=335)
		self.shake=Button(self.f2,width=5,text="G2Shake",font=myFont,command=lambda:q2.put("pro.glass2Shake(4)")).place(x=710,y=335)
		
		self.g3l=Button(self.f2,width=5,text="G3 Left",font=myFont,command=lambda:q2.put("pro.moveMotor5Left(5000,1,50)")).place(x=50,y=385)
		self.g3r=Button(self.f2,width=5,text="G3 Right",font=myFont,command=lambda:q2.put("pro.moveMotor5Right(5000,1,50)")).place(x=120,y=385)
		self.g3ml=Button(self.f2,width=5,text="G3 MLeft",font=myFont,command=lambda:q2.put("pro.moveMotor5Left(%s,1,50)"%(self.g3s.get()))).place(x=190,y=385)
		self.g3s=Spinbox(self.f2,width=6,from_=0,to=50000,font=myFont)
		self.g3s.place(x=260,y=390)
		self.g3mr=Button(self.f2,width=5,text="G3 MRight",font=myFont,command=lambda:q2.put("pro.moveMotor5Right(%s,1,50)"%(self.g3s.get()))).place(x=330,y=385)		
		
		self.ib=Button(self.f2,width=5,text="ICE",font=myFont,command=lambda:q2.put("pro.iceControl()")).place(x=410,y=385)
		self.p1=Button(self.f2,width=5,text="PUMP1",font=myFont,command=lambda:q2.put("pro.waterPump1Control()")).place(x=480,y=385)
		self.p2=Button(self.f2,width=5,text="PUMP2",font=myFont,command=lambda:q2.put("pro.waterPump2Control()")).place(x=550,y=385)

		
		self.initM1=Button(self.f2,width=6,text="init M1",font=myFont,command=lambda:q.put("pro.motor1Init()")).place(x=610,y=10)
		self.initM2=Button(self.f2,width=6,text="init M2",font=myFont,command=lambda:q2.put("pro.motor2Init()")).place(x=700,y=10)
		self.initM3=Button(self.f2,width=6,text="init M3",font=myFont,command=lambda:q.put("pro.motor3Init()")).place(x=610,y=50)
		self.shakeInit=Button(self.f2,width=6,text="init Shake",font=myFont,command=lambda:q2.put("pro.shakeInit()")).place(x=700,y=50)
		self.lidInit=Button(self.f2,width=6,text="init Lid",font=myFont,command=lambda:q2.put("pro.lidInit()")).place(x=610,y=90)
		self.glass1Init=Button(self.f2,width=6,text="init G1",font=myFont,command=lambda:q.put("pro.glass1Init()")).place(x=700,y=90)
		self.glass2Init=Button(self.f2,width=6,text="init G2",font=myFont,command=lambda:q2.put("pro.glass2Init()")).place(x=610,y=130)
		self.glass3Init=Button(self.f2,width=6,text="init G3",font=myFont,command=lambda:q2.put("pro.glass3Init()")).place(x=700,y=130)\
		
		self.testBut=Button(self.f2,width=5,text="TEST SW",font=myFont,command=lambda:pro.testSW()).place(x=620,y=385)
		self.thread=Button(self.f2,width=5,text="Boom",font=myFont,command=lambda:q.put("pro.glass2ToGlass3()")).place(x=690,y=385)
		
		
		
	def menuFinished(self):
		name=str(q4.get())
		num=str(q4.get())
		self.dashFeed(str(name)+" Finished(Order Number: "+str(num)+")")
		self.qList.delete(0)
		self.qLabel.config(text="%d queue in progress"%(q4.qsize()/2))
		
	def boom(self):
		q.put("while True: print self.name")
		q2.put("while True: print self.name")
	
	def settingClick(self):
		self.settingTop = Toplevel()
		self.settingTop.geometry("500x350")
		
		self.temp1=self.Bottle1.get()
		self.temp2=self.Bottle2.get()
		self.temp3=self.Bottle3.get()
		self.temp4=self.Bottle4.get()
		self.temp5=self.Bottle5.get()
		self.temp6=self.Bottle6.get()
		self.temp7=self.Bottle7.get()
		self.temp8=self.Bottle8.get()
		self.temp9=self.Bottle9.get()
		self.temp10=self.Bottle10.get()
		
		self.tempw1=self.Water1.get()
		self.tempw2=self.Water2.get()
		self.tempw3=self.Water3.get()
		self.tempw4=self.Water4.get()
		self.tempw5=self.Water5.get()
		self.tempw6=self.Water6.get()
		self.tempw7=self.Water7.get()
		self.tempw8=self.Water8.get()
		self.tempw9=self.Water9.get()
		self.tempw10=self.Water10.get()
	
		self.text1=Label(self.settingTop,text="Bottle1").place(x=50,y=10)
		self.text2=Label(self.settingTop,text="Bottle2").place(x=50,y=60)
		self.text3=Label(self.settingTop,text="Bottle3").place(x=50,y=110)
		self.text4=Label(self.settingTop,text="Bottle4").place(x=50,y=160)
		self.text5=Label(self.settingTop,text="Bottle5").place(x=50,y=210)
		self.text6=Label(self.settingTop,text="Bottle6").place(x=250,y=10)
		self.text7=Label(self.settingTop,text="Bottle7").place(x=250,y=60)
		self.text8=Label(self.settingTop,text="Bottle8").place(x=250,y=110)
		self.text9=Label(self.settingTop,text="Bottle9").place(x=250,y=160)
		self.text10=Label(self.settingTop,text="Bottle10").place(x=250,y=210)

		self.entry1 = Entry(self.settingTop, textvariable=self.Bottle1, width=10)
		self.entry1.place(x=100,y=10)
		self.entryw1 = Entry(self.settingTop,justify='right', textvariable=self.Water1, width=4)
		self.entryw1.place(x=100,y=30)
		self.text11=Label(self.settingTop,text="Ml").place(x=153,y=30)
		
		self.entry2 = Entry(self.settingTop, textvariable=self.Bottle2, width=10)
		self.entry2.place(x=100,y=60)
		self.entryw2 = Entry(self.settingTop,justify='right', textvariable=self.Water2, width=4)
		self.entryw2.place(x=100,y=80)
		self.text12=Label(self.settingTop,text="Ml").place(x=153,y=80)
		
		self.entry3 = Entry(self.settingTop, textvariable=self.Bottle3, width=10)
		self.entry3.place(x=100,y=110)
		self.entryw3 = Entry(self.settingTop,justify='right', textvariable=self.Water3, width=4)
		self.entryw3.place(x=100,y=130)
		self.text13=Label(self.settingTop,text="Ml").place(x=153,y=130)
		
		self.entry4 = Entry(self.settingTop, textvariable=self.Bottle4, width=10)
		self.entry4.place(x=100,y=160)
		self.entryw4 = Entry(self.settingTop,justify='right', textvariable=self.Water4, width=4)
		self.entryw4.place(x=100,y=180)
		self.text14=Label(self.settingTop,text="Ml").place(x=153,y=180)
			
		self.entry5 = Entry(self.settingTop, textvariable=self.Bottle5, width=10)
		self.entry5.place(x=100,y=210)
		self.entryw5 = Entry(self.settingTop,justify='right', textvariable=self.Water5, width=4)
		self.entryw5.place(x=100,y=230)
		self.text15=Label(self.settingTop,text="Ml").place(x=153,y=230)
					
		self.entry6 = Entry(self.settingTop, textvariable=self.Bottle6, width=10)
		self.entry6.place(x=310,y=10)
		self.entryw6 = Entry(self.settingTop,justify='right', textvariable=self.Water6, width=4)
		self.entryw6.place(x=310,y=30)
		self.text16=Label(self.settingTop,text="Ml").place(x=363,y=30)
		
		self.entry7 = Entry(self.settingTop, textvariable=self.Bottle7, width=10)
		self.entry7.place(x=310,y=60)
		self.entryw7 = Entry(self.settingTop,justify='right', textvariable=self.Water7, width=4)
		self.entryw7.place(x=310,y=80)
		self.text17=Label(self.settingTop,text="Ml").place(x=363,y=80)
		
		self.entry8 = Entry(self.settingTop, textvariable=self.Bottle8, width=10)
		self.entry8.place(x=310,y=110)
		self.entryw8 = Entry(self.settingTop,justify='right', textvariable=self.Water8, width=4)
		self.entryw8.place(x=310,y=130)
		self.text18=Label(self.settingTop,text="Ml").place(x=363,y=130)
		
		self.entry9 = Entry(self.settingTop, textvariable=self.Bottle9, width=10)
		self.entry9.place(x=310,y=160)
		self.entryw9 = Entry(self.settingTop,justify='right', textvariable=self.Water9, width=4)
		self.entryw9.place(x=310,y=180)
		self.text19=Label(self.settingTop,text="Ml").place(x=363,y=180)
		
		self.entry10 = Entry(self.settingTop, textvariable=self.Bottle10, width=10)
		self.entry10.place(x=310,y=210)
		self.entryw10 = Entry(self.settingTop,justify='right', textvariable=self.Water10,width=4)
		self.entryw10.place(x=310,y=230)
		self.text20=Label(self.settingTop,text="Ml").place(x=363,y=230)
		
		self.b = Button(self.settingTop,bd=2, text="Update", width=10, command=lambda:self.updateMenu()).place(x=130,y=270)
		self.b2 = Button(self.settingTop,bd=2, text="Cancel", width=10, command=lambda:self.updateCancel()).place(x=260,y=270)
		
	def readFile(self):
		self.myFile = open('FS.txt','r')
		self.Menu=self.myFile.read().splitlines()
		self.Bottle1 = StringVar()
		self.Bottle1.set(self.Menu[0])
		self.Bottle2 = StringVar()
		self.Bottle2.set(self.Menu[1])
		self.Bottle3 = StringVar()
		self.Bottle3.set(self.Menu[2])
		self.Bottle4 = StringVar()
		self.Bottle4.set(self.Menu[3])
		self.Bottle5 = StringVar()
		self.Bottle5.set(self.Menu[4])
		self.Bottle6 = StringVar()
		self.Bottle6.set(self.Menu[5])
		self.Bottle7 = StringVar()
		self.Bottle7.set(self.Menu[6])
		self.Bottle8 = StringVar()
		self.Bottle8.set(self.Menu[7])
		self.Bottle9 = StringVar()
		self.Bottle9.set(self.Menu[8])
		self.Bottle10 = StringVar()
		self.Bottle10.set(self.Menu[9])
		
		self.Water1=StringVar()
		self.Water1.set(self.Menu[10])
		self.Water2=StringVar()
		self.Water2.set(self.Menu[11])
		self.Water3=StringVar()
		self.Water3.set(self.Menu[12])
		self.Water4=StringVar()
		self.Water4.set(self.Menu[13])
		self.Water5=StringVar()
		self.Water5.set(self.Menu[14])
		self.Water6=StringVar()
		self.Water6.set(self.Menu[15])
		self.Water7=StringVar()
		self.Water7.set(self.Menu[16])
		self.Water8=StringVar()
		self.Water8.set(self.Menu[17])
		self.Water9=StringVar()
		self.Water9.set(self.Menu[18])
		self.Water10=StringVar()
		self.Water10.set(self.Menu[19])		
		
		self.myFile.close()
			
	def updateCancel(self):
		self.Bottle1.set(self.temp1)
		self.Bottle2.set(self.temp2)
		self.Bottle3.set(self.temp3)
		self.Bottle4.set(self.temp4)
		self.Bottle5.set(self.temp5)
		self.Bottle6.set(self.temp6)
		self.Bottle7.set(self.temp7)
		self.Bottle8.set(self.temp8)
		self.Bottle9.set(self.temp9)
		self.Bottle10.set(self.temp10)
		
		self.Water1.set(self.tempw1)
		self.Water2.set(self.tempw2)
		self.Water3.set(self.tempw3)
		self.Water4.set(self.tempw4)
		self.Water5.set(self.tempw5)
		self.Water6.set(self.tempw6)
		self.Water7.set(self.tempw7)
		self.Water8.set(self.tempw8)
		self.Water9.set(self.tempw9)
		self.Water10.set(self.tempw10)
		
		self.settingTop.destroy()
				
	def updateMenu(self):
		self.Menu[0]=self.entry1.get()
		self.Menu[1]=self.entry2.get()
		self.Menu[2]=self.entry3.get()
		self.Menu[3]=self.entry4.get()
		self.Menu[4]=self.entry5.get()
		self.Menu[5]=self.entry6.get()
		self.Menu[6]=self.entry7.get()
		self.Menu[7]=self.entry8.get()
		self.Menu[8]=self.entry9.get()
		self.Menu[9]=self.entry10.get()
		self.Menu[10]=self.entryw1.get()
		self.Menu[11]=self.entryw2.get()
		self.Menu[12]=self.entryw3.get()
		self.Menu[13]=self.entryw4.get()
		self.Menu[14]=self.entryw5.get()
		self.Menu[15]=self.entryw6.get()
		self.Menu[16]=self.entryw7.get()
		self.Menu[17]=self.entryw8.get()
		self.Menu[18]=self.entryw9.get()
		self.Menu[19]=self.entryw10.get()
		self.writeMenu()
		self.calWater(0,0,0,0,0,0,0,0,0,0)
		self.settingTop.destroy()
		
	def writeMenu(self):
		self.update=open("FS.txt","w")
		for i in range (20):
			self.update.write(self.Menu[i]+"\n")
		self.update.close()
	
	def manOrderMenu(self):
		self.bot1=int(self.s1.get())
		self.bot2=int(self.s2.get())
		self.bot3=int(self.s3.get())
		self.bot4=int(self.s4.get())
		self.bot5=int(self.s5.get())
		self.bot6=int(self.s6.get())
		self.bot7=int(self.s7.get())
		self.bot8=int(self.s8.get())
		self.bot9=int(self.s9.get())
		self.bot10=int(self.s10.get())
		self.sum=self.bot1+self.bot2+self.bot3+self.bot4+self.bot5+self.bot6+self.bot7+self.bot8+self.bot9+self.bot10
		if self.sum>10 or self.sum<=0:
			tkMessageBox.showwarning("Too much shot","All shot must not more than 10 shots \nPlease Try again")
			print "%d %d %d %d %d %d %d %d %d %d"%(self.bot1,self.bot2,self.bot3,self.bot4,self.bot5,self.bot6,self.bot7,self.bot8,self.bot9,self.bot10)
			print "sum=%d"%self.sum
		else:
			print "%d %d %d %d %d %d %d %d %d %d"%(self.bot1,self.bot2,self.bot3,self.bot4,self.bot5,self.bot6,self.bot7,self.bot8,self.bot9,self.bot10)
			print "Total Shot =%d"%self.sum
			if self.calWater(self.bot1,self.bot2,self.bot3,self.bot4,self.bot5,self.bot6,self.bot7,self.bot8,self.bot9,self.bot10)==1:
				q4.put("Manual")
				q4.put(self.orderNumber)
				self.dashFeed("Manual Ordered(Order Number: "+str(self.orderNumber)+")")
				self.qFeed(self.orderNumber)
				print 'pro.order('+str(self.bot1)+','+str(self.bot2)+','+str(self.bot3)+','+str(self.bot4)+','+str(self.bot5)+','+str(self.bot6)+','+str(self.bot7)+','+str(self.bot8)+','+str(self.bot9)+','+str(self.bot10)+','+str(self.manShake.get())+','+str(self.manIce.get())+')'
				q.put("pro.order("+str(self.bot1)+','+str(self.bot2)+','+str(self.bot3)+','+str(self.bot4)+','+str(self.bot5)+','+str(self.bot6)+','+str(self.bot7)+','+str(self.bot8)+','+str(self.bot9)+','+str(self.bot10)+','+str(self.manShake.get())+','+str(self.manIce.get())+')')
			else:
				tkMessageBox.showwarning("Warning","Material is not enough.\nPlease Try again.")	
		
			
	
	def orderClick(self):
		self.orderTop = Toplevel()
		self.orderTop.geometry("500x600")
		self.showRecipe=StringVar()
		self.showRecipe.set("Recipe\n")
		self.myFile = open('favourite.txt','r')
		self.fav=self.myFile.read().splitlines()
		self.myFile.close()
		self.Lb1 = Listbox(self.orderTop,font=self.myFont,bd=2,relief='solid',width=25,height=15)
		self.recipeLabel = Label(self.orderTop,textvariable=self.showRecipe,justify='left',font=self.myFont).place(x=275,y=10)

		for i in range (len(self.fav)):
			asd=self.fav[i].split(" ")
			self.Lb1.insert(END,asd[0])
		
		def CurSelect(evt):
			self.active = self.Lb1.curselection()
			a=str(self.active)
			self.selected=self.Lb1.get(self.active)
		
			string = "Recipe\n"
			b=a.split("(")
			c=b[1].split(",")
			self.pos=int(c[0])
					
			self.showed = self.fav[self.pos].split(" ")
			#print self.showed
			for i in range (1,11):
				#print self.showed[i]
				if int(self.showed[i])>0:
					string+=self.Menu[i-1]+"  "+self.showed[i]+" shot\n"
			if int(self.showed[11])==1:
				string+="Add Shake\n"				
			if int(self.showed[12])==1:		
				string+="Add Ice\n"
			self.showRecipe.set(string)
			
		self.Lb1.bind('<<ListboxSelect>>',CurSelect)
		self.Lb1.place(x=10,y=10)
		self.selectButton=Button(self.orderTop,width=8,text="Order",font=self.myFont,command=lambda:self.selectMenu()).place(x=330,y=270)
		self.orderPhoto=PhotoImage(file="order.png")
		self.orderPic=Label(self.orderTop)
		self.orderPic.config(image=self.orderPhoto,width="30",height="30")
		self.orderPic.place(x=290,y=270)
		
		self.addButton=Button(self.orderTop,width=8,text="Add",font=self.myFont,command=lambda:self.addMenu()).place(x=330,y=320)
		self.addPhoto=PhotoImage(file="add.png")
		self.addPic=Label(self.orderTop)
		self.addPic.config(image=self.addPhoto,width="30",height="30")
		self.addPic.place(x=290,y=320)
		
		self.deleteButton=Button(self.orderTop,width=8,text="Delete",font=self.myFont,command=lambda:self.deleteMenu(self.showed,self.pos)).place(x=330,y=370)
		self.deletePhoto=PhotoImage(file="delete.png")
		self.deletePic=Label(self.orderTop)
		self.deletePic.config(image=self.deletePhoto,width="30",height="30")
		self.deletePic.place(x=290,y=370)
		
		self.randomButton=Button(self.orderTop,width=8,text="Random",font=self.myFont,command=lambda:self.randomMenu()).place(x=130,y=320)
		self.randomPhoto=PhotoImage(file="random.png")
		self.randomPic=Label(self.orderTop)
		self.randomPic.config(image=self.randomPhoto,width="30",height="30")
		self.randomPic.place(x=110,y=320)
		
		self.randomSpin=Spinbox(self.orderTop,width=3,from_=1,to=10,font=self.myFont)
		self.randomSpin.place(x=125,y=355)
		self.Shot=Label(self.orderTop,text="Shot",font=self.myFont).place(x=175,y=355)
		
	def selectMenu(self):
		result=tkMessageBox.askquestion("Order","Order Selected Menu?", icon='question',parent=self.orderTop)
		if result=='yes':
			self.active = self.Lb1.curselection()
			self.selected=self.Lb1.get(self.active)
			for i in range (len(self.fav)):
				split=self.fav[i].split(" ")
				if self.selected==split[0]:
					self.pos=i			
			self.showed = self.fav[self.pos].split(" ")		
			if(self.calWater(self.showed[1],self.showed[2],self.showed[3],self.showed[4],self.showed[5],self.showed[6],self.showed[7],self.showed[8],self.showed[9],self.showed[10]))==1:
				q4.put(self.showed[0])
				q4.put(self.orderNumber)
				self.dashFeed(str(self.showed[0])+" Ordered(Order Number: "+str(self.orderNumber)+")")
				self.qFeed(self.orderNumber)
				print 'pro.order('+str(self.showed[1])+','+str(self.showed[2])+','+str(self.showed[3])+','+str(self.showed[4])+','+str(self.showed[5])+','+str(self.showed[6])+','+str(self.showed[7])+','+str(self.showed[8])+','+str(self.showed[9])+','+str(self.showed[10])+','+str(self.showed[11])+','+str(self.showed[12])+')'
				q.put('pro.order('+str(self.showed[1])+','+str(self.showed[2])+','+str(self.showed[3])+','+str(self.showed[4])+','+str(self.showed[5])+','+str(self.showed[6])+','+str(self.showed[7])+','+str(self.showed[8])+','+str(self.showed[9])+','+str(self.showed[10])+','+str(self.showed[11])+','+str(self.showed[12])+')')

				self.orderTop.destroy()
			else:
				tkMessageBox.showwarning("Warning","Material is not enough.\nPlease Try again.",parent=self.orderTop)	
			#self.orderTop.destroy()	

		else:
			print "Cancel"	
			
	def calWater(self,w1,w2,w3,w4,w5,w6,w7,w8,w9,w10):
		enough=0
		self.Water1.set(int(self.Water1.get())-(30*int(w1)))
		self.Water2.set(int(self.Water2.get())-(30*int(w2)))
		self.Water3.set(int(self.Water3.get())-(30*int(w3)))
		self.Water4.set(int(self.Water4.get())-(30*int(w4)))
		self.Water5.set(int(self.Water5.get())-(30*int(w5)))
		self.Water6.set(int(self.Water6.get())-(30*int(w6)))
		self.Water7.set(int(self.Water7.get())-(30*int(w7)))
		self.Water8.set(int(self.Water8.get())-(30*int(w8)))
		self.Water9.set(int(self.Water9.get())-(30*int(w9)))
		self.Water10.set(int(self.Water10.get())-(30*int(w10)))
		if int(self.Water1.get())>=0:
			if int(self.Water2.get())>=0:
				if int(self.Water3.get())>=0:
					if int(self.Water4.get())>=0:
						if int(self.Water5.get())>=0:
							if int(self.Water6.get())>=0:
								if int(self.Water7.get())>=0:
									if int(self.Water8.get())>=0:
										if int(self.Water9.get())>=0:
											if int(self.Water10.get())>=0:
												enough=1
		if enough==1:
			self.Menu[10]=self.Water1.get()
			self.Menu[11]=self.Water2.get()
			self.Menu[12]=self.Water3.get()
			self.Menu[13]=self.Water4.get()
			self.Menu[14]=self.Water5.get()
			self.Menu[15]=self.Water6.get()
			self.Menu[16]=self.Water7.get()
			self.Menu[17]=self.Water8.get()
			self.Menu[18]=self.Water9.get()
			self.Menu[19]=self.Water10.get()
			self.writeMenu()
			#wp0 0	  0<w<75
			#wp1 25	  150>w>75	
			#wp2 50   300>w>150
			#wp3 75	  450>w>300	
			#wp4 100  w>45
			self.int1=int(self.Water1.get())
			self.int2=int(self.Water2.get())
			self.int3=int(self.Water3.get())
			self.int4=int(self.Water4.get())
			self.int5=int(self.Water5.get())
			self.int6=int(self.Water6.get())
			self.int7=int(self.Water7.get())
			self.int8=int(self.Water8.get())
			self.int9=int(self.Water9.get())
			self.int10=int(self.Water10.get())
			if self.int1>900:
				self.waterPic1.config(image=self.wp4)
			elif self.int1>600 and self.int1<=900:
				self.waterPic1.config(image=self.wp3)
			elif self.int1>300 and self.int1<=600:
				self.waterPic1.config(image=self.wp2)
			elif self.int1>120 and self.int1<=300:
				self.waterPic1.config(image=self.wp1)
			elif self.int1<=120:
				self.waterPic1.config(image=self.wp0)
				
			
			if self.int2>900:
				self.waterPic2.config(image=self.wp4)
			elif  self.int2>600 and  self.int2<=900:
				self.waterPic2.config(image=self.wp3)
			elif  self.int2>300 and  self.int2<=600:
				self.waterPic2.config(image=self.wp2)		
			elif  self.int2>120 and  self.int12<=300:
				self.waterPic2.config(image=self.wp1)
			elif  self.int2<=120:
				self.waterPic2.config(image=self.wp0)
				
			if self.int3>900:
				self.waterPic3.config(image=self.wp4)
			elif self.int3>600 and self.int3<=900:
				self.waterPic3.config(image=self.wp3)
			elif self.int3>300 and self.int3<=600:
				self.waterPic3.config(image=self.wp2)
			elif self.int3>120 and self.int3<=300:
				self.waterPic3.config(image=self.wp1)
			elif self.int3<=120:
				self.waterPic3.config(image=self.wp0)
				
			if self.int4>900:
				self.waterPic4.config(image=self.wp4)
			elif self.int4>600 and self.int4<=900:
				self.waterPic4.config(image=self.wp3)
			elif self.int4>300 and self.int4<=600:
				self.waterPic4.config(image=self.wp2)
			elif self.int4>120 and self.int4<=300:
				self.waterPic4.config(image=self.wp1)
			elif self.int4<=120:
				self.waterPic4.config(image=self.wp0)
				
			if self.int5>900:
				self.waterPic5.config(image=self.wp4)
			elif self.int5>600 and self.int5<=900:
				self.waterPic5.config(image=self.wp3)
			elif self.int5>300 and self.int5<=600:
				self.waterPic5.config(image=self.wp2)
			elif self.int5>120 and self.int5<=300:
				self.waterPic5.config(image=self.wp1)
			elif self.int5<=120:
				self.waterPic5.config(image=self.wp0)
				
			if self.int6>900:
				self.waterPic6.config(image=self.wp4)
			elif self.int6>600 and self.int6<=900:
				self.waterPic6.config(image=self.wp3)
			elif self.int6>300 and self.int6<=600:
				self.waterPic6.config(image=self.wp2)
			elif self.int6>120 and self.int6<=300:
				self.waterPic6.config(image=self.wp1)
			elif self.int6<=120:
				self.waterPic6.config(image=self.wp0)
				
			if self.int7>900:
				self.waterPic7.config(image=self.wp4)
			elif self.int7>600 and self.int7<=900:
				self.waterPic7.config(image=self.wp3)
			elif self.int7>300 and self.int7<=600:
				self.waterPic7.config(image=self.wp2)
			elif self.int7>120 and self.int7<=300:
				self.waterPic7.config(image=self.wp1)
			elif self.int7<=120:
				self.waterPic7.config(image=self.wp0)
				
			if self.int8>900:
				self.waterPic8.config(image=self.wp4)
			elif self.int8>600 and self.int8<=900:
				self.waterPic8.config(image=self.wp3)
			elif self.int8>300 and self.int8<=600:
				self.waterPic8.config(image=self.wp2)
			elif self.int8>120 and self.int8<=300:
				self.waterPic8.config(image=self.wp1)
			elif self.int8<=120:
				self.waterPic8.config(image=self.wp0)
				
			if self.int9>900:
				self.waterPic9.config(image=self.wp4)
			elif self.int9>600 and self.int9<=900:
				self.waterPic9.config(image=self.wp3)
			elif self.int9>300 and self.int9<=600:
				self.waterPic9.config(image=self.wp2)
			elif self.int9>120 and self.int9<=300:
				self.waterPic9.config(image=self.wp1)
			elif self.int9<=120:
				self.waterPic9.config(image=self.wp0)
				
			if self.int10>900:
				self.waterPic10.config(image=self.wp4)
			elif self.int10>600 and self.int10<=900:
				self.waterPic10.config(image=self.wp3)
			elif self.int10>300 and self.int10<=600:
				self.waterPic10.config(image=self.wp2)
			elif self.int10>120 and self.int10<=300:
				self.waterPic10.config(image=self.wp1)
			elif self.int10<=120:
				self.waterPic10.config(image=self.wp0)
				
			return 1
		else:
			self.Water1.set(int(self.Water1.get())+(30*int(w1)))
			self.Water2.set(int(self.Water2.get())+(30*int(w2)))
			self.Water3.set(int(self.Water3.get())+(30*int(w3)))
			self.Water4.set(int(self.Water4.get())+(30*int(w4)))
			self.Water5.set(int(self.Water5.get())+(30*int(w5)))
			self.Water6.set(int(self.Water6.get())+(30*int(w6)))
			self.Water7.set(int(self.Water7.get())+(30*int(w7)))
			self.Water8.set(int(self.Water8.get())+(30*int(w8)))
			self.Water9.set(int(self.Water9.get())+(30*int(w9)))
			self.Water10.set(int(self.Water10.get())+(30*int(w10)))
			
			return 0
				
	def addMenu(self):
		self.addTop = Toplevel()
		self.addTop.geometry("300x300")

		self.addl1=Label(self.addTop,textvariable=self.Bottle1,font=self.myFont).place(x=10,y=10)
		self.addsp1=Spinbox(self.addTop,width=3,from_=0,to=10,font=self.myFont)
		self.addsp1.place(x=100,y=10)
		self.addl2=Label(self.addTop,textvariable=self.Bottle2,font=self.myFont).place(x=10,y=40)
		self.addsp2=Spinbox(self.addTop,width=3,from_=0,to=10,font=self.myFont)
		self.addsp2.place(x=100,y=40)
		self.addl3=Label(self.addTop,textvariable=self.Bottle3,font=self.myFont).place(x=10,y=70)
		self.addsp3=Spinbox(self.addTop,width=3,from_=0,to=10,font=self.myFont)
		self.addsp3.place(x=100,y=70)
		self.addl4=Label(self.addTop,textvariable=self.Bottle4,font=self.myFont).place(x=10,y=100)
		self.addsp4=Spinbox(self.addTop,width=3,from_=0,to=10,font=self.myFont)
		self.addsp4.place(x=100,y=100)
		self.addl5=Label(self.addTop,textvariable=self.Bottle5,font=self.myFont).place(x=10,y=130)
		self.addsp5=Spinbox(self.addTop,width=3,from_=0,to=10,font=self.myFont)
		self.addsp5.place(x=100,y=130)
		self.addl6=Label(self.addTop,textvariable=self.Bottle6,font=self.myFont).place(x=150,y=10)
		self.addsp6=Spinbox(self.addTop,width=3,from_=0,to=10,font=self.myFont)
		self.addsp6.place(x=240,y=10)
		self.addl7=Label(self.addTop,textvariable=self.Bottle7,font=self.myFont).place(x=150,y=40)
		self.addsp7=Spinbox(self.addTop,width=3,from_=0,to=10,font=self.myFont)
		self.addsp7.place(x=240,y=40)
		self.addl8=Label(self.addTop,textvariable=self.Bottle8,font=self.myFont).place(x=150,y=70)
		self.addsp8=Spinbox(self.addTop,width=3,from_=0,to=10,font=self.myFont)
		self.addsp8.place(x=240,y=70)
		self.addl9=Label(self.addTop,textvariable=self.Bottle9,font=self.myFont).place(x=150,y=100)
		self.addsp9=Spinbox(self.addTop,width=3,from_=0,to=10,font=self.myFont)
		self.addsp9.place(x=240,y=100)
		self.addl10=Label(self.addTop,textvariable=self.Bottle10,font=self.myFont).place(x=150,y=130)
		self.addsp10=Spinbox(self.addTop,width=3,from_=0,to=10,font=self.myFont)
		self.addsp10.place(x=240,y=130)
		self.ice = IntVar()
		self.iceCheck = Checkbutton(self.addTop, text="ICE", variable=self.ice,height=1,font=self.myFont)
		self.iceCheck.place(x=20,y=170)
		
		self.shake = IntVar()
		self.shakeCheck = Checkbutton(self.addTop, text="SHAKE", variable=self.shake,height=1,font=self.myFont)
		self.shakeCheck.place(x=90,y=170)
		
		self.add=Button(self.addTop,width=6,text="Add",font=self.myFont,command=lambda:self.writeRecipe()).place(x=90,y=250)
		self.cancel=Button(self.addTop,width=6,text="Cancel",font=self.myFont,command=lambda:self.addTop.destroy()).place(x=190,y=250)
		self.nameLabel=Label(self.addTop,width=10,font=self.myFont,text="Name").place(x=10,y=210)
		self.addentry1 = Entry(self.addTop, width=10,font=self.myFont)
		self.addentry1.place(x=90,y=210)
		
	def writeRecipe(self):
		self.addBot1=int(self.addsp1.get())
		self.addBot2=int(self.addsp2.get())
		self.addBot3=int(self.addsp3.get())
		self.addBot4=int(self.addsp4.get())
		self.addBot5=int(self.addsp5.get())
		self.addBot6=int(self.addsp6.get())
		self.addBot7=int(self.addsp7.get())
		self.addBot8=int(self.addsp8.get())
		self.addBot9=int(self.addsp9.get())
		self.addBot10=int(self.addsp10.get())
		#self.shakeRecipe=int(self.shake.get())
		#self.iceRecipe=int(self.ice.get())
				
		self.addSum=self.addBot1+self.addBot2+self.addBot3+self.addBot4+self.addBot5+self.addBot6+self.addBot7+self.addBot8+self.addBot9+self.addBot10
		if self.addSum>10 or self.addSum<=0:
			tkMessageBox.showwarning("Too much shot","All shot must not more than 10 shots \nPlease Try again",parent=self.orderTop)
			self.addTop.destroy()
		else:
			self.myRecipe = open('favourite.txt','a')
			self.myRecipe.write(self.addentry1.get()+" "+self.addsp1.get()+" "+self.addsp2.get()+" "+self.addsp3.get()+" "+self.addsp4.get()+" "+self.addsp5.get()+" "+self.addsp6.get()+" "+self.addsp7.get()+" "+self.addsp8.get()+" "+self.addsp9.get()+" "+self.addsp10.get()+" "+str(self.shake.get())+" "+str(self.ice.get())+"\n")
			self.myRecipe.close()
			self.dashFeed("Menu "+str(self.addentry1.get())+" added")
			self.addTop.destroy()
			self.orderTop.destroy()
			self.orderClick()
		
	def deleteMenu(self,Name,ind):
		result=tkMessageBox.askquestion("Delete","Delete Selected Menu?", icon='question',parent=self.orderTop)
		if result=="yes":
			self.myFile = open('favourite.txt','r')
			self.fav=self.myFile.read().splitlines()
			self.myFile.close()
			
			self.myFile = open('favourite.txt','w')
			for line in self.fav:
				s=line.split(" ")
				if s!=Name:
					self.myFile.write(line+"\n")
			self.myFile.close()
			self.dashFeed("Menu "+str(Name[0])+" deleted")
			self.Lb1.delete(ind)
			self.orderTop.destroy()
			self.orderClick()
		else:
			print "closed"
			
	def randomMenu(self):
		check=0
		maxshot=int(self.randomSpin.get())
		while check==0:
			remain=maxshot
			a=[0,0,0,0,0,0,0,0,0,0]
			for i in range(10):
				a[i]=random.randint(0,remain)
				remain=remain-a[i]
			random.shuffle(a)		
			ice=random.randint(0,1)
			shake=random.randint(0,1)
			check=self.randomCheck(a[0],a[1],a[2],a[3],a[4],a[5],a[6],a[7],a[8],a[9])
			print a
		result=tkMessageBox.askquestion("Random","Are You Sure?", icon='question',parent=self.orderTop)
		if result=="yes":
			self.calWater(a[0],a[1],a[2],a[3],a[4],a[5],a[6],a[7],a[8],a[9])
			
			temp=""
			for i in range(10):
				if a[i]>0:
					temp+=str(self.Menu[i])+" "+str(a[i])+" "
			
			q4.put("RANDOM")
			q4.put(self.orderNumber)
			self.dashFeed("Random(Order Number: "+str(self.orderNumber)+")")
			self.dashFeed(temp)
			self.qFeed(self.orderNumber)
			print "pro.order("+str(a[0])+","+str(a[1])+","+str(a[2])+","+str(a[3])+","+str(a[4])+","+str(a[5])+","+str(a[6])+","+str(a[7])+","+str(a[8])+","+str(a[9])+","+str(shake)+","+str(ice)+")"	
			q.put("pro.order("+str(a[0])+","+str(a[1])+","+str(a[2])+","+str(a[3])+","+str(a[4])+","+str(a[5])+","+str(a[6])+","+str(a[7])+","+str(a[8])+","+str(a[9])+","+str(shake)+","+str(ice)+")")
			self.orderTop.destroy()
			self.orderClick()
		else:
			print "closed"

	def randomCheck(self,w1,w2,w3,w4,w5,w6,w7,w8,w9,w10):
		enough=0
		self.Water1.set(int(self.Water1.get())-(30*int(w1)))
		self.Water2.set(int(self.Water2.get())-(30*int(w2)))
		self.Water3.set(int(self.Water3.get())-(30*int(w3)))
		self.Water4.set(int(self.Water4.get())-(30*int(w4)))
		self.Water5.set(int(self.Water5.get())-(30*int(w5)))
		self.Water6.set(int(self.Water6.get())-(30*int(w6)))
		self.Water7.set(int(self.Water7.get())-(30*int(w7)))
		self.Water8.set(int(self.Water8.get())-(30*int(w8)))
		self.Water9.set(int(self.Water9.get())-(30*int(w9)))
		self.Water10.set(int(self.Water10.get())-(30*int(w10)))
		if int(self.Water1.get())>0:
			if int(self.Water2.get())>0:
				if int(self.Water3.get())>0:
					if int(self.Water4.get())>0:
						if int(self.Water5.get())>0:
							if int(self.Water6.get())>0:
								if int(self.Water7.get())>0:
									if int(self.Water8.get())>0:
										if int(self.Water9.get())>0:
											if int(self.Water10.get())>0:
												enough=1
		
			self.Water1.set(int(self.Water1.get())+(30*int(w1)))
			self.Water2.set(int(self.Water2.get())+(30*int(w2)))
			self.Water3.set(int(self.Water3.get())+(30*int(w3)))
			self.Water4.set(int(self.Water4.get())+(30*int(w4)))
			self.Water5.set(int(self.Water5.get())+(30*int(w5)))
			self.Water6.set(int(self.Water6.get())+(30*int(w6)))
			self.Water7.set(int(self.Water7.get())+(30*int(w7)))
			self.Water8.set(int(self.Water8.get())+(30*int(w8)))
			self.Water9.set(int(self.Water9.get())+(30*int(w9)))
			self.Water10.set(int(self.Water10.get())+(30*int(w10)))										
		return enough
		
	def dashFeed(self,word):
		self.dashList.insert(0,str(datetime.now().strftime('%H:%M:%S'))+":   "+word)
	
	def qFeed(self,word):
		self.qList.insert(END,"Order:  "+str(word))
		self.orderNumber +=1
		self.qLabel.config(text="%d queue in progress"%(q4.qsize()/2))

class myThread (threading.Thread):
	def __init__(self,name,queue):
		threading.Thread.__init__(self)
		self.name = name
		self.glass1Status=-1 #-1washed 0used 1ready
		self.glass2Status=-1 #-1washed 0used 1ready
		self.lidStatus=0 # 0close 1open
		self.queue=queue
		self.test=0
		self.dead=True
		self.drinkStatus=0 #0not done 1done
	def run(self):
		if self.name=="dead":
			while self.dead==True:
				time.sleep(0.1)
				
		else:
			print "Starting " + self.name
			while True:
				exec(self.queue.get())
				#print str(self.name)+"is Running"
				#time.sleep(0.3)
				
			print "Exiting " + self.name

class machine:
	dc=10
	def __init__(self):
		my_gui.dashFeed("Start")
		my_gui.dashFeed("Initialize Motors")
		self. machineInit()
		my_gui.dashFeed("Ready")

	def machineInit(self):
		print "INIT"
		GPIO.output(waterPump1,True)
		GPIO.output(waterPump2,True)
		GPIO.output(iceMotorA,True)
		#self.motor1Init()
		#self.motor2Init()
		#self.motor3Init()
		#self.shakeInit()
		#self.lidInit()
		#self.glass1Init()
		#self.glass2Init()	
		#self.glass3Init()
		
	def motor1Init(self):
		sdelays=40/1000000.0
		GPIO.output(dirPinMotor1,True)
		while GPIO.input(limitSwitchMotor1)==True:
			GPIO.output(stepPinMotor1,True)
			time.sleep(sdelays)
			GPIO.output(stepPinMotor1,False)
			time.sleep(sdelays)
		self.moveMotor1Right(800,1,200)
		print "Motor 1 Initialize complete"
		
	def motor2Init(self):
		s2delays=5/1000000.0
		GPIO.output(dirPinMotor2,True)
		while GPIO.input(limitSwitchMotor2)==True:
			GPIO.output(stepPinMotor2,True)
			time.sleep(s2delays)
			GPIO.output(stepPinMotor2,False)
			time.sleep(s2delays)
		#self.moveMotor2Up(500,1,5)
		print "Motor 2 Initialize complete"
		
	def motor3Init(self):
		s2delays=15/1000000.0
		GPIO.output(dirPinMotor3,False)
		while GPIO.input(limitSwitchMotor3)==True:
			GPIO.output(stepPinMotor3,True)
			time.sleep(s2delays)
			GPIO.output(stepPinMotor3,False)
			time.sleep(s2delays)
		self.moveMotor3Front(9000,1,50)
		print "Motor 3 Initialize complete"
					
	def lidInit(self):
		self.glass2LidClose()
		print "Lid Initialize complete"
		
	def glass1Init(self):
		self.glass1Control(1)
		print "Glass 1 Initialize complete"
		
	def glass2Init(self):
		sdelays=55/1000000.0
		GPIO.output(dirPinMotor4,False)
		while GPIO.input(limitSwitchMotor4)==True:
			GPIO.output(stepPinMotor4,True)
			time.sleep(sdelays)
			GPIO.output(stepPinMotor4,False)
			time.sleep(sdelays)
		self.moveMotor4Left(6700,1,55)
		print "Glass 2 Initialize complete"
	
	
	def glass3Init(self):
		sdelays=55/1000000.0
		GPIO.output(dirPinMotor5,True)
		while GPIO.input(irSensor2)==True:
			GPIO.output(stepPinMotor5,True)
			time.sleep(sdelays)
			GPIO.output(stepPinMotor5,False)
			time.sleep(sdelays)
		self.moveMotor5Left(15000,1,55)
	
	def shakeInit(self):
		count=0
		state=0
		laststate=0
		print "start shake"
		sm2B.start(10)
		sm2B.ChangeDutyCycle(10)
		while count<1:
			state= GPIO.input(limitSwitchGlass2)
			if state != laststate:
				if state==False:
					count +=1
			time.sleep(0.05)
			laststate=state
		time.sleep(1)
		sm2B.stop()
		print "Shake Initialize complete"
		
	def glass1Control(self,di):
		print"start glass1 control"
		if di==-1: #right
			self.dcMotor1Control(-1)
			time.sleep(2)
			self.dcMotor1Control(0)
			time.sleep(2.5)
			self.sensorValue=GPIO.input(irSensor1)
			while self.sensorValue== False:
				self.dcMotor1Control(1)
				self.sensorValue=GPIO.input(irSensor1)
	
			self.dcMotor1Control(0)

		if di==1: #left
			self.dcMotor1Control(1)
			time.sleep(2.2)
			self.dcMotor1Control(0)
			time.sleep(2.5)
			self.sensorValue=GPIO.input(irSensor1)
			while self.sensorValue== False:
				self.dcMotor1Control(-1)
				self.sensorValue=GPIO.input(irSensor1)
			#time.sleep(0.1)
			self.dcMotor1Control(0)
		print "glass 1 control finished"

	def glass2Control(self,di):
		print"start glass2 control"
		if di==-1: #right
			self.moveMotor4Right(4500,1,300)
			time.sleep(2)
			self.moveMotor4Left(4500,1,50)
			
		if di==1: #left
			self.moveMotor4Left(5000,1,300)
			time.sleep(2)
			self.moveMotor4Right(5000,1,50)
			
		print "glass 2 control finished"

	def glass2Shake(self,times):
		count=0
		state=0
		laststate=0
		print "start shake"
		self.shakeMotor2Control(1)
		while count<times:
			state= GPIO.input(limitSwitchGlass2)
			if state != laststate:
				if state==False:
					count +=1
					print count
			time.sleep(0.05)
			laststate=state
		time.sleep(1.07)
		self.shakeMotor2Control(0)
		print "shake finished"

	def glass2LidOpen(self):
		while GPIO.input(limitSwitchLid)==True:
			self.lidMotor2Control(-1)
		self.lidMotor2Control(1)
		time.sleep(0.25)
		self.lidMotor2Control(0)
		print "open lid"
		qthread2.lidStatus=1

	def glass2LidClose(self):
		self.lidMotor2Control(1)
		time.sleep(3.5)
		self.lidMotor2Control(0)
		print "close lid"
		qthread2.lidStatus=0

	def dcMotor1Control(self,di):
		if di==-1:
			GPIO.output(dcMotor1A,True)
			GPIO.output(dcMotor1B,False)
			#print"DC motor1  1"
		if di==1:
			GPIO.output(dcMotor1A,False)
			GPIO.output(dcMotor1B,True)
			#print"DC motor1 -1"
		if di==0:
			GPIO.output(dcMotor1A,False)
			GPIO.output(dcMotor1B,False)
			#print"DC motor1  0"
				
	def iceControl(self):
		GPIO.output(iceMotorA,False)
		time.sleep(3)
		GPIO.output(iceMotorA,True)
		print "ICE complete"

	def shakeMotor2Control(self,di):
		if di==1:
			sm2B.start(self.dc)
			while(self.dc<50):
				self.dc += 10
				print self.dc
				sm2B.ChangeDutyCycle(self.dc)
				time.sleep(0.2)
		if di==0:
			while(self.dc>0):
				self.dc -= 10
				print self.dc
				sm2B.ChangeDutyCycle(self.dc)
				time.sleep(0.2)
			sm2B.stop()

	def lidMotor2Control(self,di):
		if di==1:
			GPIO.output(lidMotor2A,True)
			GPIO.output(lidMotor2B,False)
			#print"lid motor2  1"
		if di==-1:
			GPIO.output(lidMotor2A,False)
			GPIO.output(lidMotor2B,True)
			#print"lid motor2 -1"
		if di==0:
			GPIO.output(lidMotor2A,False)
			GPIO.output(lidMotor2B,False)
			#print"lid motor2  0"

	def waterPump1Control(self):
		GPIO.output(waterPump1,False)
		time.sleep(2)
		GPIO.output(waterPump1,True)
		print "Pump1"

	def waterPump2Control(self):
		GPIO.output(waterPump2,False)
		time.sleep(2)
		GPIO.output(waterPump2,True)
		print "Pump2"
				
	def moveMotor1Right(self,step,times,delays):
		GPIO.output(dirPinMotor1,False)
		mindelays=10
		dec=(mindelays-delays)/600000000.0
		inc=(delays-mindelays)/600000000.0
		#print dec,inc
		delays =delays/1000000.0
		default=mindelays/1000000.0
		for i in range (times):
			for j in range (step):
				if j<600:
					delays += dec
				elif j>step-600:
					delays += inc
				else:
					delays=default

				#if GPIO.input(limitSwitchMotor1)==True:
				GPIO.output(stepPinMotor1,True)
				time.sleep(delays)
				GPIO.output(stepPinMotor1,False)
				time.sleep(delays)
			time.sleep(1)
		print"moveRight %d %d times"%(step,times)

	def moveMotor1Left(self,step,times,delays):
		GPIO.output(dirPinMotor1,True)
		mindelays=10
		dec=(mindelays-delays)/600000000.0
		inc=(delays-mindelays)/600000000.0
		#print dec,inc
		delays =delays/1000000.0
		default=mindelays/1000000.0
		for i in range (times):
			for j in range (step):
				if j<600:
					delays += dec
				elif j>step-600:
					delays += inc
				else:
					delays=default

				#if GPIO.input(limitSwitchMotor1)==True:
				GPIO.output(stepPinMotor1,True)
				time.sleep(delays)
				GPIO.output(stepPinMotor1,False)
				time.sleep(delays)
			time.sleep(1)
		print"moveRight %d %d times"%(step,times)

	def moveMotor2Up(self,step,times,delays):
		GPIO.output(dirPinMotor2,False)
		delays = delays/1000000.0
		for i in range (times):
			for j in range (step):
				#if GPIO.input(limitSwitchMotor2)==True:
				GPIO.output(stepPinMotor2,True)
				time.sleep(delays)
				GPIO.output(stepPinMotor2,False)
				time.sleep(delays)
			time.sleep(1)
		print"moveUp %d %d times"%(step,times)

	def moveMotor2Down(self,step,times,delays):
		GPIO.output(dirPinMotor2,True)
		delays = delays/1000000.0
		for i in range (times):
			for j in range (step):
				#if GPIO.input(limitSwitchMotor2)==True:
				GPIO.output(stepPinMotor2,True)
				time.sleep(delays)
				GPIO.output(stepPinMotor2,False)
				time.sleep(delays)
			time.sleep(1)
		print"moveDown %d %d times"%(step,times)
		
	def moveMotor3Front(self,step,times,delays):
		mindelays=15
		dec=(mindelays-delays)/600000000.0
		inc=(delays-mindelays)/600000000.0
		GPIO.output(dirPinMotor3,True)
		delays = delays/1000000.0
		default=mindelays/1000000.0
		for i in range (times):
			for j in range (step):
				if j<600:
					delays += dec
				elif j>step-600:
					delays += inc
				else:
					delays=default
				#if GPIO.input(limitSwitchMotor3)==True:
				GPIO.output(stepPinMotor3,True)
				time.sleep(delays)
				GPIO.output(stepPinMotor3,False)
				time.sleep(delays)
		print"moveFront %d %d times"%(step,times)
		
	def moveMotor3Back(self,step,times,delays):
		mindelays=15
		dec=(mindelays-delays)/600000000.0
		inc=(delays-mindelays)/600000000.0
		GPIO.output(dirPinMotor3,False)
		delays = delays/1000000.0
		default=mindelays/1000000.0
		for i in range (times):
			for j in range (step):
				if j<600:
					delays += dec
				elif j>step-600:
					delays += inc
				else:
					delays=default

				#if GPIO.input(limitSwitchMotor1)==True:
				GPIO.output(stepPinMotor3,True)
				time.sleep(delays)
				GPIO.output(stepPinMotor3,False)
				time.sleep(delays)
		print"moveBack %d %d times"%(step,times)
		
	def moveMotor4Right(self,step,times,delays):
		GPIO.output(dirPinMotor4,False)
		delays = delays/1000000.0
		for i in range (times):
			for j in range (step):
				#if GPIO.input(limitSwitchMotor3)==True:
				GPIO.output(stepPinMotor4,True)
				time.sleep(delays)
				GPIO.output(stepPinMotor4,False)
				time.sleep(delays)
			time.sleep(1)
		print"moveShakeRight %d %d times"%(step,times)
		
	def moveMotor4Left(self,step,times,delays):
		GPIO.output(dirPinMotor4,True)
		delays = delays/1000000.0
		for i in range (times):
			for j in range (step):
				#if GPIO.input(limitSwitchMotor3)==True:
				GPIO.output(stepPinMotor4,True)
				time.sleep(delays)
				GPIO.output(stepPinMotor4,False)
				time.sleep(delays)
			time.sleep(1)
		print"moveShakeLeft %d %d times"%(step,times)
		
	def moveMotor5Right(self,step,times,delays):
		GPIO.output(dirPinMotor5,True)
		delays = delays/1000000.0
		for i in range (times):
			for j in range (step):
				#if GPIO.input(limitSwitchMotor3)==True:
				GPIO.output(stepPinMotor5,True)
				time.sleep(delays)
				GPIO.output(stepPinMotor5,False)
				time.sleep(delays)
			time.sleep(1)
		print"moveShakeRight %d %d times"%(step,times)
		
	def moveMotor5Left(self,step,times,delays):
		GPIO.output(dirPinMotor5,False)
		delays = delays/1000000.0
		for i in range (times):
			for j in range (step):
				#if GPIO.input(limitSwitchMotor3)==True:
				GPIO.output(stepPinMotor5,True)
				time.sleep(delays)
				GPIO.output(stepPinMotor5,False)
				time.sleep(delays)
			time.sleep(1)
		print"moveShakeLeft %d %d times"%(step,times)
			
	def order(self,bot1,bot2,bot3,bot4,bot5,bot6,bot7,bot8,bot9,bot10,shake,ice):
		print "order"
		q.put("pro.glass1DrinkControl("+str(bot1)+","+str(bot2)+","+str(bot3)+","+str(bot4)+","+str(bot5)+","+str(bot6)+","+str(bot7)+","+str(bot8)+","+str(bot9)+","+str(bot10)+")")
		q2.put("pro.glass2WaitandShake("+str(shake)+","+str(ice)+")")
	 	q.put("pro.glass1ToGlass2()")
		q.put("pro.glass1Wash()")
		q2.put("pro.glass2ToGlass3()")
		q2.put("pro.glass2Wash()")

	def glass1DrinkControl(self,bot1,bot2,bot3,bot4,bot5,bot6,bot7,bot8,bot9,bot10):
		print "Glass 1 Drink Control"
		while qthread.glass1Status!=1:
			if qthread.glass1Status==-1:
				pos=1
				if bot1 !=0:
					self.moveMotor3Back(7500,1,50)
					for i in range (bot1):
						self.moveMotor2Up(17000,1,5)
						time.sleep(3)
						self.moveMotor2Down(17000,1,5)
					self.moveMotor3Front(7500,1,50)
				
				if bot6!=0:
					self.moveMotor3Front(7500,1,50)			
					for i in range (bot6):
						self.moveMotor2Up(15000,1,5)
						time.sleep(3)
						self.moveMotor2Down(15000,1,5)	
					self.moveMotor3Back(7500,1,50)	
					
				ns=8000
				pos=2
				if bot2==0 and bot7==0:
					ns=16000
					pos=3
					if bot3==0 and bot8==0:
						ns=24000
						pos=4
						if bot4==0 and bot9==0:
							ns=32000
							pos=5
				self.moveMotor1Right(ns,1,200)

				if bot2!=0:
					self.moveMotor3Back(7500,1,50)
					for i in range (bot2):
						self.moveMotor2Up(17000,1,5)
						time.sleep(3)
						self.moveMotor2Down(17000,1,5)
					self.moveMotor3Front(7500,1,50)
				
				if bot7!=0:
					self.moveMotor3Front(7500,1,50)			
					for i in range (bot7):
						self.moveMotor2Up(15000,1,5)
						time.sleep(3)
						self.moveMotor2Down(15000,1,5)	
					self.moveMotor3Back(7500,1,50)
				
				if pos==2:
					ns=8000
					pos=3
					if bot3==0 and bot8==0:
						ns=16000
						pos=4
						if bot4==0 and bot9==0:
							ns=24000
							pos=5
					self.moveMotor1Right(ns,1,200)

				if bot3!=0:
					self.moveMotor3Back(7500,1,50)
					for i in range (bot3):
						self.moveMotor2Up(17000,1,5)
						time.sleep(3)
						self.moveMotor2Down(17000,1,5)
					self.moveMotor3Front(7500,1,50)
				
				if bot8!=0:
					self.moveMotor3Front(7500,1,50)			
					for i in range (bot8):
						self.moveMotor2Up(15000,1,5)
						time.sleep(3)
						self.moveMotor2Down(15000,1,5)	
					self.moveMotor3Back(7500,1,50)

				if pos==3:
					ns=8000
					pos=4
					if bot4==0 and bot9==0:
						ns=16000
						pos=5
					self.moveMotor1Right(ns,1,200)

				if bot4!=0:
					self.moveMotor3Back(7500,1,50)
					for i in range (bot4):
						self.moveMotor2Up(17000,1,5)
						time.sleep(3)
						self.moveMotor2Down(17000,1,5)
					self.moveMotor3Front(7500,1,50)
				
				if bot9!=0:
					self.moveMotor3Front(7500,1,50)
					for i in range (bot9):
						self.moveMotor2Up(15000,1,5)
						time.sleep(3)
						self.moveMotor2Down(15000,1,5)	
					self.moveMotor3Back(7500,1,50)
				
				if pos==4:
					ns=8000
					pos=5
					self.moveMotor1Right(ns,1,200)

				if bot5!=0:
					self.moveMotor3Back(7500,1,50)
					for i in range (bot5):
						self.moveMotor2Up(17000,1,5)
						time.sleep(3)
						self.moveMotor2Down(17000,1,5)
					self.moveMotor3Front(7500,1,50)
				
				if bot10!=0:
					self.moveMotor3Front(7500,1,50)
					for i in range (bot10):
						self.moveMotor2Up(15000,1,5)
						time.sleep(3)
						self.moveMotor2Down(15000,1,5)	
					self.moveMotor3Back(7500,1,50)	
			
				qthread.glass1Status=1
				print "glass 1 ready"

	def glass1ToGlass2(self):
		print "Glass1 to Glass2"
		while qthread.glass1Status!=0:
			if qthread2.glass2Status==-1:
				if qthread.glass1Status==1:
					if qthread2.lidStatus==1:
						self.moveMotor1Right(7000,1,200)
						self.moveMotor4Left(1500,1,50)
						self.moveMotor3Back(500,1,50)
						self.glass1Control(-1)
						self.moveMotor3Front(500,1,50)
						self.moveMotor1Left(7000,1,200)
						qthread2.glass2Status=1
						qthread.glass1Status=0
						print "glass 2 ready"
	
	def glass2WaitandShake(self,shake,ice):
		print "Glass 2 wait and Shake"
		self.glass2LidOpen()
		if ice==1:
			print "ADD ICE"
			self.iceControl()
		while qthread2.glass2Status!=0:
			if qthread.glass1Status==0:
				if qthread2.glass2Status==1:
					if qthread2.lidStatus==1:
						self.moveMotor4Right(1500,1,50)
						self.glass2LidClose()
						if shake==1:
							self.glass2Shake(1)
							print "Shake"
						qthread2.drinkStatus=1
						qthread2.glass2Status=0
						print "drink ready"
			time.sleep(0.1)

	def glass1Wash(self):
		while qthread.glass1Status!=-1:
			if qthread.glass1Status==0:
				print "washing glass1"
				self.moveMotor1Left(24000,1,200)
				self.moveMotor3Front(500,1,50)
				self.moveMotor2Up(12500,1,5)
				self.waterPump1Control()
				self.moveMotor2Down(12500,1,5)
				self.moveMotor3Back(500,1,50)
				self.moveMotor1Left(4000,1,200)
				self.moveMotor2Up(12500,1,5)
				self.glass1Control(1)  
				self.moveMotor2Down(12500,1,5)
				self.motor1Init()
				qthread.glass1Status=-1
				print "glass 1 washed"

	
	def glass2ToGlass3(self):
		while GPIO.input(irSensor2)==False:
			print "Glass 3 is missing!!"
			gui.dashFeed("Glass 3 is missing!")
			time.sleep(3)
		if qthread2.drinkStatus==1:
			self.moveMotor5Right(12000,1,50)
			self.glass2LidOpen()
			q5.put("time.sleep(1)")
			q5.put("pro.moveMotor5Right(3000,1,150)")
			self.glass2Control(1)
			self.moveMotor5Left(15000,1,50)
			qthread2.glass2Status=0
			print "glass3 ready"
			name=str(q4.get())
			num=str(q4.get())
			my_gui.dashFeed(str(name)+" Finished(Order Number: "+str(num)+")")
			my_gui.qList.delete(0)
			my_gui.qLabel.config(text="%d queue in progress"%(q4.qsize()/2))
		
	def glass2Wash(self):
		while qthread2.glass2Status!=-1:
			if qthread2.glass2Status==0:
				if qthread2.lidStatus==1:
					print "washing glass2"
					self.waterPump2Control()
					self.glass2LidClose()
					self.glass2Shake(1)
					self.glass2LidOpen()
					self.glass2Control(-1)
					self.glass2LidClose()
					self.shakeInit()
					print"glass 2 washed"
					qthread2.glass2Status=-1

	def testSW(self):
		print "TEST"
		print "MOTOR1    "+str(GPIO.input(limitSwitchMotor1))
		print "MOTOR2    "+ str(GPIO.input(limitSwitchMotor2))
		print "MOTOR3    "+ str(GPIO.input(limitSwitchMotor3))
		print "MOTOR4    "+ str(GPIO.input(limitSwitchMotor4))
		print "LID       "+ str(GPIO.input(limitSwitchLid))
		print "Glass2    "+ str(GPIO.input(limitSwitchGlass2))
		print "IR Glass1 "+ str(GPIO.input(irSensor1))
		print "Glass3    "+ str(GPIO.input(irSensor2))
		
	def testSleep(self,dlay):
		dlay1=dlay/1000000.0
		while True:
			t1=time.time()
			time.sleep(dlay1)
			t0=time.time()
			print "dlay %.6f"%(t0-t1)
			time.sleep(1)
		


q=Queue.Queue()
q2=Queue.Queue()
q3=Queue.Queue()
q4=Queue.Queue()
q5=Queue.Queue()
MainQueue=Queue.Queue()

qthread = myThread("Queue Thread",q)
qthread2 = myThread("Queue Thread 2",q2)
qthread3 = myThread("dead",q3)
qthread4 = myThread("Queue Thread 3",q5)

qthread.daemon=True
qthread2.daemon=True
qthread4.daemon=True

qthread.start()
qthread2.start()
qthread3.start()
qthread4.start()
while(True):
    try:
        root = Tk()
        break
    except:
        print 'display not ready'
        time.sleep(1)
        
my_gui = GUI(root)
pro = machine()


def on_closing():
	q.queue.clear()
	q2.queue.clear()
	qthread3.dead=False
	GPIO.output(stepPinMotor1,False)
	GPIO.output(dirPinMotor1,False)
	GPIO.output(stepPinMotor2,False)
	GPIO.output(dirPinMotor2,False)
	GPIO.output(stepPinMotor3,False)
	GPIO.output(dirPinMotor3,False)
	GPIO.output(stepPinMotor4,False)
	GPIO.output(dirPinMotor4,False)
	sm2B.stop()
	GPIO.output(shakeMotor2B,False)
	GPIO.output(lidMotor2A,False)
	GPIO.output(lidMotor2B,False)
	GPIO.output(dcMotor1A,False)
	GPIO.output(dcMotor1B,False)
	GPIO.output(waterPump1,True)
	GPIO.output(waterPump2,True)
	GPIO.output(iceMotorA,True)
	root.destroy()
            
def main():
	root.protocol("WM_DELETE_WINDOW", on_closing)
	root.mainloop()

if __name__ == "__main__":
	main()

