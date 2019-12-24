from vpython import*
import numpy as np
import random
from tkinter import*
import tkinter.messagebox
from scipy.stats import rankdata
from scipy import stats

# 1,3,5期
window = Tk()
window.title("賒帳")
window.geometry('500x300')
l = Label(window, text='是否接受賒帳?', bg='green', font=('Arial', 12), width=30, height=2)
l.pack()

def quit():
    answer = tkinter.messagebox.askquestion(title='賒帳', message='現在可選擇是否接受應收帳款,若接受,客人可能增加x,倒帳風險為x%,不接受則維持原狀,請問是否接受?')
    print(answer)
    if answer == "no":
        pass
    if answer == "yes":
        v1 = 50
if answer == "yes":
    if T == 1:
        receivable1[0] = pf1
    elif T == 3:
        receivable1[1] = pf1    
    elif T == 5:
        receivable1[2] = pf1
Button(window, text='hit me', command=quit).pack()
window.mainloop()


receivable1 = [200,200,200]
pf1 = 0
period = 6
# period > 0 時歸還receivable
return_rate = [0.96, 0.8, 0.6, 0.4, 0.2, 0.1, 0.05]
base = [0, 2, 4]
if 7 > period > 0:
    for i in range(3):

        pf1 += receivable1[i] * np.random.binomial(100, return_rate[period-base[i]-1])/100
        receivable1[i] -= receivable1[i] * np.random.binomial(100, return_rate[period-base[i]-1])/100
    print(pf1,receivable1)

# 賣掉或賭一把
receivable1, receivable2 = [50,100,100], [0,200,0]
period = 7
if receivable1 == [0,0,0] and receivable2 == [0,0,0]:
    pass
elif receivable1 != [0,0,0]:
    root = tkinter.Tk()
    root.withdraw()
    answer = tkinter.messagebox.askquestion(title='機會:賣掉receivables', message='您所剩的應收帳款還剩x元,現有一折抵賣出機會,請問您是否要購買?')
    if answer == "yes":
        receivable1 == [0,0,0]
        pf1 += 500
    elif answer == "no":
        for i in range(3):
            pf1 += receivable1[i] * np.random.binomial(100, return_rate[period-base[i]-1])/100
            print(pf1)