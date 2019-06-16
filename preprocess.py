import os
import json
from tqdm import tqdm

files = []
# file_path = 'C:/Users/bonin/Downloads/baidu/mjdata/mjdata/output2017/MO/'
# files += [os.path.join(file_path, filename) for filename in os.listdir(file_path)]
file_path = 'C:/Users/bonin/Downloads/baidu/mjdata/mjdata/output2017/LIU/'
files += [os.path.join(file_path, filename) for filename in os.listdir(file_path)]

info = {}
info['da'] = {}
info['mo'] = {}
process = 0
for filename in tqdm(files):
	# process += 1
	# if process % 2000 == 0:
	# 	print('processed ', process)
	f = open(filename, encoding='utf-8')

	lines = f.readlines()

	# filename = lines[0]
	state = lines[1]
	hand_init = lines[2:6]
	action = lines[6:]

	# print(json.loads(state.split()[2].replace("'", '"')))
	# print(filename)

	# print(lines)
	players = {}

	# 初始状态
	for line in hand_init:
		split = line.split()
		player_id = split[0]
		players[player_id] = {}
		players[player_id]['hand'] = json.loads(split[1].replace("'", '"'))
		players[player_id]['hua'] = int(split[2])
		players[player_id]['pack'] = []

	# 打牌
	round_cnt = 0
	mo_cnt = 0

	for line in action:
		# print(line)
		split = line.split()
		player_id = split[0]
		cards = json.loads(split[2].replace("'", '"'))
		if split[1] == '打牌':
			players[player_id]['hand'].remove(cards[0])
			round_cnt += 1
		elif split[1] == '摸牌':
			players[player_id]['hand'].append(cards[0])
			mo_cnt += 1
		elif split[1] == '补花后摸牌':
			players[player_id]['hand'].append(cards[0])
			mo_cnt += 1
		elif split[1] == '杠后摸牌':
			players[player_id]['hand'].append(cards[0])
			mo_cnt += 1
		elif split[1] == '补花':
			players[player_id]['hua'] += 1
			mo_cnt -= 1
		elif split[1] == '吃':
			last_card = split[3]
			last_player_id = split[4]
			for card in cards:
				if card != last_card:
					players[player_id]['hand'].remove(card)
		elif split[1] == '碰':
			last_card = split[3]
			last_player_id = split[4]
			players[player_id]['hand'].remove(last_card)
			players[player_id]['hand'].remove(last_card)
		elif split[1] == '明杠' or split[1] == '暗杠':
			last_card = split[3]
			last_player_id = split[4]
			players[player_id]['hand'].remove(last_card)
			players[player_id]['hand'].remove(last_card)
			players[player_id]['hand'].remove(last_card)
		elif split[1] == '补杠' or split[1] == '和牌':
			pass
		else:
			# pass
			print(line)

	if round_cnt in info['da'].keys():
		info['da'][round_cnt] += 1
	else:
		info['da'][round_cnt] = 1
	if mo_cnt > 83:
		print(filename)
	if mo_cnt in info['mo'].keys():
		info['mo'][mo_cnt] += 1
	else:
		info['mo'][mo_cnt] = 1

print(info)