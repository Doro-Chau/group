# PART I: 該import的library
from vpython import*
import numpy as np
import random
from tkinter import*
from scipy.stats import rankdata

# PART II: 基本畫面設計
N = 38  # 一個邊的格子點數目
h = 0.88  # 每個格子的寬
e = 7*10E-3
phi = np.full(N**2, 1/N**2)  # phi是一個depend on (x,y,t)的函數，會映射到排名，依據排名絕對各點密度
phi = np.reshape(phi, (N, N))
scene = canvas(title = 'Spatial and Pricing Competition', height = 800, width = 900, center = vec(0, 0, 0), background = vec(0, 0, 0))
scene.lights = []  # 背景


def rank(matrix):  # 計算排名
	r = rankdata(matrix, method = 'min').reshape(matrix.shape)
	ranks = (r.max() + 1) - r
	return ranks


points = []  # 在螢幕上畫出格子點，為N*N的list
for i in range(N):
	TempList = []
	for j in range(N):
		point = box(pos = vec(-18+i*(h+e), -3+j*(h+e), 0), length = h, height= h, width = h/4, color = vec(1, 1, 1), emissive = True)
		TempList.append(point)
		if j == N - 1:
			points.append(TempList)

scene.center = points[19][19].pos

# 廠商1的資產負債表圖
BS_1 = graph(width = 600, align = 'left', title = 'Firm 1 Balance Sheet', xtitle = 'time', ytitle = '$', background = vec(0.6, 0.6, 0.6))
A_graph1 = gcurve(color = color.blue, graph = BS_1)  # 資產:藍色線
L_graph1 = gcurve(color = color.red, graph = BS_1)  # 負債:紅色線
E_graph1 = gcurve(color = color.green, graph = BS_1)  # 權益:綠色線
# 廠商2的資產負債表圖
BS_2 = graph(width = 600, align = 'left', title = 'Firm 2 Balance Sheet', xtitle = 'time', ytitle = '$', background = vec(0.6, 0.6, 0.6))
A_graph2 = gcurve(color = color.blue, graph = BS_2)  # 資產:藍色線
L_graph2 = gcurve(color = color.red, graph = BS_2)  # 負債:紅色線
E_graph2 = gcurve(color = color.green, graph = BS_2)  # 權益:綠色線

# PART III: 一些重要的參數、還有存放一些重要訊息的list/variable/numpy array...

v1, v2 = 32, 32  # 消費者認為商品的價值，可能對不同廠商有不同的願付價值
trans_c = 2.0  # 消費者的單位交通成本
p1 ,p2 = 0, 0  # 兩家廠商的定價(user interface)
pf1, pf2 = 0, 0  # 兩家廠商的利潤
marg_c1, marg_c2 = 2.00, 2.00  # 兩家廠商的單位生產成本

Debt1, Debt2 = 0, 0  # 舉債金額(user interface)
AR1, AR2 = 0, 0  # 是否應收帳款(user interface)
ExpandNum1, ExpandNum2 = 1, 1  # 擴廠數目(user interface)
Coop1, Coop2 = False, False  # 是否勾結(user interface)

A1, A2 = 0, 0  # Asset
L1, L2 = 0, 0  # Liability
E1, E2 = 0, 0  # Equity

firm1s, firm2s = [], []  # 存放廠商位置的list

rho = np.zeros((N,N))  # 密度
period = 0  # 時間的計數器
T = 8  # 總期數
loc1, loc2 = [], []  # 紀錄玩家一、玩家二的設廠位置在哪一個格子(i,j)
FirmCnt1, FirmCnt2 = 0, 0  #各玩家個總共有幾家店

# 記錄第幾期有甚麼活動
FirmExpand = [1, 3, 5]
AccountReceive = [0, 2, 4]
DebtRaising = [1, 3, 5]
Collusion = [3, 4, 5]
Pricing = [0, 3, 6]

# 進入為期8期的迴圈
while period < T:
	print('Period ' + str(period) + ' begins.')

	# 每三期，邊際成本重置至2.00
	if period%3 == 0:
		marg_c1, marg_c2 = 2.00, 2.00

	# 人口密度改變外生衝擊，有8%的機率密度反轉
	DensityShcok = random.random()
	for i in range(N):
		for j in range(N):
			phi[i][j] = exp(0.01*(i+1)*period)*(j+1)  # phi(x,y,t)的值，可以變動，也可以設計contract
			
	if DensityShcok < 0.08:
		for i in range(N):
			for j in range(N):
				phi[i][j] = -phi[i][j]

	# 邊際成本變動外生衝擊(t = 0不出現此衝擊)，本期有pr3機會成本+1，pr2機率成本+3，pr1機率成本+5
	if period > 0:
		pr1, pr2, pr3 = 0.08, 0.12, 0.15
		CostShock = random.random()  # 廠商1
		if CostShock < pr1+pr2+pr3 and CostShock > pr1+pr2:
			marg_c1 += 1
		elif CostShock <= pr1+pr2 and CostShock > pr1:
			marg_c1 += 3
		elif CostShock <= pr1:
			marg_c1 += 5

		CostShock = random.random()  # 廠商2
		if CostShock < pr1+pr2+pr3 and CostShock > pr1+pr2:
			marg_c2 += 1
		elif CostShock <= pr1+pr2 and CostShock > pr1:
			marg_c2 += 3
		elif CostShock <= pr1:
			marg_c2 += 5

	# 討論:邊際成本可不可以變成Private information或出現signal jamming?
	print('Firm 1 marginal cost  $' + str(marg_c1))
	print('Firm 2 marginal cost  $' + str(marg_c2))

			
	R = rank(phi)  # phi mapping到rank
	rho = R // (N**2//100)  # 根據rank決定密度

	for i in range(N):
		for j in range(N):
			a = rho[i][j]
			points[i][j].color = vec(a/100, 0, 1-(a/100))  # 密度越大，越偏向紅色。越小則偏藍色。

# Part IV: Positioning Game(Simultaneous)
	check_ball = 0
	while check_ball < ExpandNum1:
		ev = scene.pause('FIRM 1, CLICK TO PROCEED')  # 廠商1決定位置

		for i in range(N):
			for j in range(N):

				if ev.pos.x <= points[i][j].pos.x+(h/2) and ev.pos.x >= points[i][j].pos.x-(h/2):
					if ev.pos.y <= points[i][j].pos.y+(h/2) and ev.pos.y >= points[i][j].pos.y-(h/2):

						firm1 = sphere(pos = points[i][j].pos, radius = h/2, color = color.cyan, emissive = 'True')  # 放棋子
						loc = []
						loc.append(i)
						loc.append(j)
						loc1.append(loc)
						firm1s.append(firm1)
						check_ball += 1
						FirmCnt1 += 1
						break
	time, dt = 0, 1
	while time < 10:
		rate(1)
		time += dt

	for i in range(FirmCnt1-ExpandNum1, FirmCnt1):
		firm1s[i].visible = False  # 如果positioning session是同時賽局，則玩家一決定後，棋子會短暫不可見。

	check_ball = 0
	while check_ball < ExpandNum2:
		ev = scene.pause('FIRM 2, CLICK TO PROCEED')  # 廠商2決定位置

		for i in range(N):
			for j in range(N):

				if ev.pos.x <= points[i][j].pos.x+(h/2) and ev.pos.x >= points[i][j].pos.x-(h/2):
					if ev.pos.y <= points[i][j].pos.y+(h/2) and ev.pos.y >= points[i][j].pos.y-(h/2):

						firm2 = sphere(pos = points[i][j].pos, radius = h/2, color = color.yellow , emissive = 'True')
						loc = []
						loc.append(i)
						loc.append(j)
						loc2.append(loc)
						firm2s.append(firm2)
						check_ball += 1
						FirmCnt2 += 1
						break

	for i in range(FirmCnt1-ExpandNum2, FirmCnt1):
		firm1s[i].visible = True  #一旦廠商2決定完位置，positioning session結束，公布兩人的決策

	ExpandNum1, ExpandNum2 = 0, 0

# Part V: 為跳出視窗準備的一些函數

	def retrieve(firm, tp):
		if tp == 'price' and firm == 1:
			global p1
			InValue = PriceTextBox.get('1.0', 'end-1c')
			p1 = float(InValue)
			PriceBtn.config(state = 'disabled')

		if tp == 'price' and firm == 2:
			global p2
			InValue = PriceTextBox.get('1.0', 'end-1c')
			p2 = float(InValue)
			PriceBtn.config(state = 'disabled')

		if tp == 'debt' and firm == 1:
			global Debt1
			InValue = DebtTextBox.get('1.0', 'end-1c')
			Debt1 = float(InValue)
			DebtBtn.config(state = 'disabled')

		if tp == 'debt' and firm == 2:
			global Debt2
			InValue = DebtTextBox.get('1.0', 'end-1c')
			Debt2 = float(InValue)
			DebtBtn.config(state = 'disabled')

	def ChangeValue(firm, evt, cond):
		if firm == 1:

			if evt == 'collusion':
				global Coop1
				collBtn1.config(state = 'disabled')
				collBtn0.config(state = 'disabled')
				if cond == 'coop':
					Coop1 = True
				if cond == 'devi':
					Coop1 = False

			if evt == 'expand':
				global ExpandNum1
				ExpandBtn1.config(state = 'disabled')
				ExpandBtn2.config(state = 'disabled')
				ExpandBtn0.config(state = 'disabled')
				if cond == 0:
					ExpandNum1 = 0
				if cond == 1:
					ExpandNum1 = 1
				if cond == 2:
					ExpandNum1 = 2

			if evt == 'AR':
				global AR1
				ARBtn1.config(state = 'disabled')
				ARBtn0.config(state = 'disabled')
				if cond == 'yes':
					AR1 = 1
				if cond == 'no':
					AR1 = 0
		else:

			if evt == 'collusion':
				global Coop2
				collBtn1.config(state = 'disabled')
				collBtn0.config(state = 'disabled')
				if cond == 'coop':
					Coop2 = True
				if cond == 'devi':
					Coop2 = False

			if evt == 'expand':
				global ExpandNum2
				ExpandBtn1.config(state = 'disabled')
				ExpandBtn2.config(state = 'disabled')
				ExpandBtn0.config(state = 'disabled')
				if cond == 0:
					ExpandNum2 = 0
				if cond == 1:
					ExpandNum2 = 1
				if cond == 2:
					ExpandNum2 = 2

			if evt == 'AR':
				global AR2
				ARBtn1.config(state = 'disabled')
				ARBtn0.config(state = 'disabled')
				if cond == 'yes':
					AR2 = 1
				if cond == 'no':
					AR2 = 0
# Part VI: 跳出視窗出現(決定一下哪些是Simultaneous,哪些可以做Sequential)
	FirmPlaying = 1
	z = 40
	s = 20
	while FirmPlaying <= 2:

		root = Tk()
		root.title('Firm '+ str(FirmPlaying) +' Decision Making')
		if FirmPlaying == 1:
			root.configure(background = 'cyan')
		else:
			root.configure(background = 'yellow')
		root.geometry('500x500')

		if period in Pricing:
			price_frame = Frame(root)
			price_frame.pack(side = TOP)
			price_label = Label(price_frame, text = '定價($)')
			price_label.pack(side = LEFT)
			PriceTextBox = Text(root, height = 2, width = s)
			PriceTextBox.pack()
			PriceBtn = Button(root, height = 1, width = z, text = 'pricing confirmed!', command = lambda: retrieve(FirmPlaying, 'price'))
			PriceBtn.pack()

		if period in FirmExpand:
			expand_frame = Frame(root)
			expand_frame.pack(side = TOP)
			expand_label = Label(expand_frame, text = '擴廠數目(按鈕)')
			expand_label.pack(side = LEFT)
			ExpandBtn1 = Button(root, height = 1, width = z, bg = 'Purple' , fg = 'White', text = 'Expand 1 firm.', command = lambda: ChangeValue(FirmPlaying, 'expand', 1))
			ExpandBtn2 = Button(root, height = 1, width = z, bg = 'Purple' , fg = 'White', text = 'Expand 2 firms.', command = lambda: ChangeValue(FirmPlaying, 'expand', 2))
			ExpandBtn0 = Button(root, height = 1, width = z, bg = 'Purple' , fg = 'White', text = 'No firm expansion.', command = lambda: ChangeValue(FirmPlaying, 'expand', 0))
			ExpandBtn2.pack()
			ExpandBtn1.pack()
			ExpandBtn0.pack()

		if period in AccountReceive:
			AR_frame = Frame(root)
			AR_frame.pack(side = TOP)
			AR_label = Label(AR_frame, text = '賒帳服務(按鈕)')
			AR_label.pack(side = LEFT)
			ARBtn1 = Button(root, height = 1, width = z, bg = 'Green', fg = 'White', text = 'Accept both cash and payment on account.', command = lambda: ChangeValue(FirmPlaying, 'AR', 'yes'))
			ARBtn0 = Button(root, height = 1, width = z, bg = 'Red', fg = 'White', text = 'Only accept cash.', command = lambda: ChangeValue(FirmPlaying, 'AR', 'no'))
			ARBtn1.pack()
			ARBtn0.pack()

		if period in Collusion:
			coll_frame = Frame(root)
			coll_frame.pack(side = TOP)
			coll_label = Label(coll_frame, text = '勾結//背叛(按鈕)')
			coll_label.pack(side = LEFT)
			collBtn1 = Button(root, height = 1, width = z, text = 'Collude with opponent.', bg = 'Green', fg = 'White', command = lambda: ChangeValue(FirmPlaying, 'collusion', 'coop'))
			collBtn0 = Button(root, height = 1, width = z, text = 'Deviate.', bg = 'Red', fg = 'White', command = lambda: ChangeValue(FirmPlaying, 'collusion', 'devi'))
			collBtn1.pack()
			collBtn0.pack()

		if period in DebtRaising:
			debt_frame = Frame(root)
			debt_frame.pack(side = TOP)
			debt_label = Label(debt_frame, text='舉債($)')
			debt_label.pack(side = LEFT)
			DebtTextBox = Text(root, height = 2, width = s)
			DebtTextBox.pack()
			DebtBtn = Button(root, height = 1, width = z, text = 'debt confirmed!', command = lambda: retrieve(FirmPlaying, 'debt'))
			DebtBtn.pack()

		QuitBtn = Button(root, text = 'Quit', command = root.destroy)
		QuitBtn.pack()
		mainloop()

		FirmPlaying += 1


# Part VII: 檢查每個格子點上的消費者到底會買廠商1、廠商2、還是都不買
	for i in range(N):
		for j in range(N):

			CS1, CS2 = -1, -1
			for num in range(len(loc1)):
				dist1 = mag(vec(i, j, 0)-vec(loc1[num][0], loc1[num][1], 0))  # 廠商1跟該格子消費者的距離
				CS1 = max(v1-p1-trans_c*dist1, CS1)  # 消費者買廠商1的消費者剩餘
			for num in range(len(loc2)):
				dist2 = mag(vec(i, j, 0)-vec(loc2[num][0], loc2[num][1], 0))  # 廠商1跟該格子消費者的距離
				CS2 = max(v2-p2-trans_c*dist2, CS2)  # 消費者買廠商1的消費者剩餘

			if CS1 > CS2 and CS1 >= 0:
				pf1 += rho[i][j]*(p1-marg_c1)
			if CS1 < CS2 and CS2 >= 0:
				pf2 += rho[i][j]*(p2-marg_c2) 
			if CS1 == CS2 and CS1 >= 0:
				r = random.random()
				if r < 0.50:
					pf1 = rho[i][j]*(p1-marg_c1)
				else:
					pf2 = rho[i][j]*(p2-marg_c2)
					
# Part VIII: 結算本期損益，畫圖在財報上

	A2 = A2 + pf2 + Debt2
	L2 += Debt2
	E2 += pf2
	A1 = A1 + pf1 + Debt1
	L1 += Debt1
	E1 += pf1						

	print('Period ' + str(period) + ' ends.')  # 一期就這樣結束了~

	A_graph1.plot(pos = (period, A1))
	L_graph1.plot(pos = (period, L1))
	E_graph1.plot(pos = (period, E1))	

	A_graph2.plot(pos = (period, A2))
	L_graph2.plot(pos = (period, L2))
	E_graph2.plot(pos = (period, E2))
	
	print('Firm 1 Profit:  $ ', pf1)
	print('Firm 2 Profit:  $ ', pf2)
	pf1, pf2 = 0, 0
	Debt1, Debt2 = 0, 0

	period += 1