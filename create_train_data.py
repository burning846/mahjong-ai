import os
import json
from tqdm import tqdm
import numpy
import pickle

def tile2index(tile):
	index = -1
	if tile[0] == 'W':
		index += 0
	elif tile[0] == 'T':
		index += 9
	elif tile[0] == 'B':
		index += 18
	elif tile[0] == 'F':
		index += 27
	elif tile[0] == 'J':
		index += 31
	else:
		return 34
	return index + int(tile[1])
label = ["W1","W2","W3","W4","W5","W6","W7","W8","W9",
	"T1","T2","T3","T4","T5","T6","T7","T8","T9",
	"B1","B2","B3","B4","B5","B6","B7","B8","B9",
	"F1","F2","F3","F4","J1","J2","J3","H","unknown"]
files = []


#可调整
#目录
file_path = r'C:\Users\bonin\Downloads\baidu\mjdata\mjdata\output2017\MO'
files += [os.path.join(file_path, filename) for filename in os.listdir(file_path)]

#单个文件内批尺寸
batch_size = 1000
#出牌策略文件数
discard_max = 200
#鸣牌策略文件数
steal_max = 200


discard_train = numpy.zeros((batch_size,51,36,4))
discard_label = numpy.zeros((batch_size,36))
discard_count = 0
discard_file_num = 0

steal_train = numpy.zeros((batch_size,51,36,4))
steal_label = numpy.zeros((batch_size,6))
steal_count = 0
steal_file_num = 0

for filename in tqdm(files):
	data = numpy.zeros((51,36,4))
	f = open(filename, encoding='utf-8')

	lines = f.readlines()

	#场风
	state = lines[1]
	if state[0] == '东':
		for i in range(4):
			data[0][27][i] = 1
	elif state[0] == '南':
		for i in range(4):
			data[0][28][i] = 1
	elif state[0] == '西':
		for i in range(4):
			data[0][29][i] = 1
	else:
		for i in range(4):
			data[0][30][i] = 1
	#print('场风')
	#print(pandas.DataFrame(data[0],index = label,dtype = int))
	#胡牌者的自风
	zhuang = int(lines[6][0])
	tmp = int(lines[len(lines)-1][0])
	bias =  4 - zhuang
	winner = (tmp + bias)%4
	for i in range(4):
		data[1][winner + 27][i] = 1
	#print('自风')
	#print(pandas.DataFrame(data[1],index = label,dtype = int))
	#花牌数 最大只记到4
	hand_init = lines[2:6]
	for i in range(4):
		split = hand_init[i].split()
		for j in range(min(int(split[2]),4)):
			data[2+(i+bias)%4][34][j] = 1
	#for i in range(4):
		#print('花',i)
		#print(pandas.DataFrame(data[2+i],index = label,dtype = int))
	#胡牌者的手牌
	hand_init = lines[2 + tmp]
	hand = numpy.zeros(34,dtype = int)
	split = hand_init.split()
	cards = json.loads(split[1].replace("'", '"'))
	for tile in cards:
		index = tile2index(tile)
		if index != 34:
			hand[index] += 1
	for i in range(34):
		for j in range(hand[i]):
			data[6][i][j]  = 1
	#print(pandas.DataFrame(data[6],index = label,dtype = int))
	#更新信息
	action = lines[6:]
	reset = True
	flag = 0 
	for id,line in enumerate(action):
		split = line.split()
		player_id = (int(split[0]) + bias)%4
		cards = json.loads(split[2].replace("'", '"'))
		act = split[1]
		#轮到庄家操作 上一巡结束 信息向后平移
		if player_id == 0 and reset and flag != 0:
			data[15:] = data[6:42]
			reset = False
		if player_id != 0:
			flag = 1
			reset = True
			
		#一个batch装满，存入下一个文件
		if discard_count == batch_size and discard_file_num < discard_max:
			output = open('discard_train/'+str(discard_file_num)+'.pkl','wb')
			pickle.dump(discard_train, output, protocol=pickle.HIGHEST_PROTOCOL)
		
			output = open('discard_label/'+str(discard_file_num)+'.pkl','wb')
			pickle.dump(discard_label, output, protocol=pickle.HIGHEST_PROTOCOL)
			discard_file_num += 1
			discard_count = 0

		if steal_count == batch_size and steal_file_num < steal_max:
			output = open('steal_train/'+str(steal_file_num)+'.pkl','wb')
			pickle.dump(steal_train, output, protocol=pickle.HIGHEST_PROTOCOL)
		
			output = open('steal_label/'+str(steal_file_num)+'.pkl','wb')
			pickle.dump(steal_label, output, protocol=pickle.HIGHEST_PROTOCOL)
			steal_file_num += 1
			steal_count = 0

		#和牌者操作 维护手牌
		if player_id == winner:
			if act == '摸牌' or act == '补花后摸牌' or act == '杠后摸牌':
				index = tile2index(cards[0])
				#摸到花牌自动补花 跳过
				if index != 34:
					hand[index] += 1
			if act == '吃' or act == '碰' or act == '明杠':
				#都减去
				for tile in cards:
					index = tile2index(tile)
					hand[index] -= 1
				#补回一张别人打的
				index = tile2index(split[3])
				hand[index] += 1
			#打牌，需要生成一个决策数据
			if act == '打牌':
				index = tile2index(cards[0])
				if discard_file_num < discard_max:
					discard_train[discard_count,:,:,:] = data
					discard_label[discard_count][index] = 1
					discard_count += 1
				hand[index] -= 1
			#补杠，视为一种出牌策略，需要生成一个决策数据，对应label为34
			if act == '补杠':
				index = tile2index(cards[0])
				if discard_file_num < discard_max:
					discard_train[discard_count,:,:,:] = data
					discard_label[discard_count][34] = 1
					discard_count += 1
				hand[index] -= 1
			#暗杠，视为一种出牌策略，需要生成一个决策数据，对应label为35
			if act == '暗杠':
				if discard_file_num < discard_max:
					discard_train[discard_count,:,:,:] = data
					discard_label[discard_count][35] = 1
					discard_count += 1
				#把四张都减去
				for tile in cards:
					index = tile2index(tile)
					hand[index] -= 1
				#自己的暗杠对自己可见
				act = '明杠'
			#更新手牌信息
			wrong = 0
			data[6] = numpy.zeros((36,4))
			for i in range(34):
				if hand[i] > 4 or hand[i] < 0:
					wrong = 1
				for j in range(hand[i]):
					data[6][i][j]  = 1
			if wrong:
				print(hand)
				print(line)
				flag = 1
				break
		#所有玩家共用操作，
		if act == '打牌':
			index = tile2index(cards[0])
			data[7 + player_id][index][1:4] = data[7 + player_id][index][0:3]
			data[7 + player_id][index][0] = 1
			next_line = action[id + 1]
			split_tmp = next_line.split()
			next_player = (int(split_tmp[0]) + bias) % 4
			next_act = split_tmp[1]
			#非自家打牌且尚未获得足够的吃碰杠数据
			if player_id != winner and steal_file_num < steal_max:
				steal_flag = False
				#可以碰杠
				if hand[index] > 1:
					steal_flag = True
				#是饼条万
				if index < 27:
					tile_num = index % 9 + 1
					#011型
					if tile_num < 8 and hand[index + 1] and hand[index + 2]:
						steal_flag = True
					#110型
					if tile_num > 2 and hand[index - 1] and hand[index - 2]:
						steal_flag = True
					#101型
					if tile_num > 1 and tile_num < 9 and hand[index - 1] and hand[index + 1]:
						steal_flag = True
				if steal_flag:
					steal_train[steal_count,:,:,:] = data
					if next_player != winner:
						steal_label[steal_count][0] = 1
					else:
						if next_act == '碰':
							steal_label[steal_count][4] = 1
						elif next_act == '明杠':
							steal_label[steal_count][5] = 1
						elif next_act == '吃':
							steal_card = split_tmp[3]
							tmp_cards = json.loads(split_tmp[2].replace("'", '"'))
							d = tmp_cards.index(steal_card)
							steal_label[steal_count][d + 1] = 1
						else:
							steal_label[steal_count][0] = 1
					steal_count += 1

		#更新吃碰杠
		if act == '吃' or act == '碰' or act == '明杠' or act == '补杠':
			for tile in cards:
				index = tile2index(tile)
				data[11 + player_id][index][1:4] = data[11 + player_id][index][0:3]
				data[11 + player_id][index][0] = 1
		if act == '暗杠':
			data[11 + player_id][35][1:4] = data[11 + player_id][35][0:3]
			data[11 + player_id][35][0] = 1
		if act == '补花':
			data[2 + player_id][34][1:4] = data[11 + player_id][35][0:3]
			data[2 + player_id][34][0] = 1
	
	#print(pandas.DataFrame(data[6],index = label,dtype = int))
	#break
	if steal_file_num == steal_max and discard_file_num == discard_max:
		print(filename)
		break
