import os
import json
import random
import time

infiles = []
outfiles = []
bots = []

# 设置随机种子，相同随机种子发的牌相同
randseed = time.time()
# randseed = 1234
print('seed: ', randseed)
random.seed(randseed)

for i in range(4):
    infiles.append('in%d.json' % i) # bots输入文件名
    outfiles.append('out%d.json' % i) # bots输出文件名
    bots.append('bot%d.exe' % i) #bots程序文件名

paiku = []

# 构建牌库
for cnt in range(4):
    for num in range(9):
        paiku.append('W%d' % (num + 1))
        paiku.append('B%d' % (num + 1))
        paiku.append('T%d' % (num + 1))
        if num < 4:
            paiku.append('F%d' % (num + 1))
        if num < 3:
            paiku.append('J%d' % (num + 1))

for num in range(8):
    paiku.append('H%d' % (num + 1))

random.shuffle(paiku)
idx_paiku = 0
turn_ID = 0
hand = [] # 手牌
hua = [] # 花牌


inputJson = []
for i in range(4):
    inputJson.append({
        "requests": [],
        "responses": []
        })

# 第一步，随机初始状态
quan = random.randint(0, 3)
for i in range(4):
    inputJson[i]['requests'].append("0 %d %d" % (i, quan))
    inputJson[i]['responses'].append('PASS')
    json.dump(inputJson[i], open(infiles[i], 'w'))
    hand.append([])
    hua.append([])

turn_ID += 1 # 1

# 第二步，随机初始牌
for i in range(4):
    cnt = 0
    max_cnt = 13
    while cnt < max_cnt:
        while paiku[idx_paiku][0] == 'H':
            hua[i].append(paiku[idx_paiku])
            idx_paiku += 1
        hand[i].append(paiku[idx_paiku])
        idx_paiku += 1
        cnt += 1

for i in range(4):
    inputJson[i]['requests'].append("1 %d %d %d %d " % (len(hua[0]), len(hua[1]), len(hua[2]), len(hua[3])) + ' '.join(hand[i]) + ' ' + ' '.join([' '.join(hua[j]) for j in range(4) if len(hua[j]) > 0]))
    inputJson[i]['responses'].append('PASS')
    print(inputJson[i]['requests'][1])

# 庄家摸牌
for i in range(4):
    if i == quan:
        inputJson[i]['requests'].append('2 %s' % paiku[idx_paiku])
    else:
        inputJson[i]['requests'].append('3 %d DRAW' % quan)
    idx_paiku += 1
    print('%d %s' % (i, inputJson[i]['requests'][turn_ID]))

# 第三步，仿真打牌
turn = quan
type = 2
while idx_paiku < len(paiku):
    # 1、传给bot得到response
    for i in range(4):
        json.dump(inputJson[i], open(infiles[i], 'w'))
        # print("./%s < %s > %s" % (bots[i], infiles[i], outfiles[i]))
        os.system("%s < %s > %s" % (bots[i], infiles[i], outfiles[i]))

    # 2、获得response并处理
    for i in range(4):
        response = json.load(open('out%d.json' % i, 'r'))['response']
        inputJson[i]['responses'].append(response)
        # print(response)

    priority = -1
    for i in range(4):
        response = inputJson[i]['responses'][-1]
        if response != 'PASS':
            response = response.split()
            if response[0] == 'HU': #有人胡了，直接结束
                flag_hu = 1
                print('%d HU!' % i)
                exit(0)

            elif response[0] == 'CHI' and priority < 1:
                turn = i
                priority = 1

            elif response[0] == 'PENG' and priority < 2:
                turn = i
                priority = 2

            elif response[0] == 'GANG' and priority < 3:
                turn = i
                priority = 3

            elif response[0] == 'BUGANG' and priority < 4:
                turn = i
                priority = 4
                break
            elif response[0] == 'PLAY':
                turn = i
                priority = 0
                break

    turn_ID += 1  # 一次交互一次ID增加，当前turn_ID代表最后一次

    # 根据response构造新的输入
    if priority == -1: # 大家都PASS，下一步该摸牌了

        turn = (turn + 1) % 4
        while idx_paiku < len(paiku) and paiku[idx_paiku][0] == 'H':
            hua[turn].append(paiku[idx_paiku])
            for i in range(4):
                inputJson[i]['requests'].append('3 %d BUHUA %s' % (turn, paiku[idx_paiku]))
                inputJson[i]['responses'].append('PASS')
            turn_ID += 1
            idx_paiku += 1

        if idx_paiku == len(paiku):
            break

        print(idx_paiku, '/', len(paiku), '  ', paiku[idx_paiku])  # 打印下一张牌以显示进程

        curr_pai = paiku[idx_paiku]
        idx_paiku += 1
        for i in range(4):
            if i == turn:
                inputJson[i]['requests'].append('2 %s' % curr_pai)
            else:
                inputJson[i]['requests'].append('3 %d DRAW' % turn)

    elif priority == 0: # 有人打牌
        response = inputJson[turn]['responses'][turn_ID].split()
        # print(inputJson[turn]['responses'], turn, turn_ID)
        for i in range(4):
            inputJson[i]['requests'].append('3 %d PLAY %s' % (turn, response[1]))

    elif priority == 1: # 有人吃了
        response = inputJson[turn]['responses'][turn_ID].split()
        for i in range(4):
            inputJson[i]['requests'].append('3 %d CHI %s %s' % (turn, response[1], response[2]))

    elif priority == 2: # 有人碰
        response = inputJson[turn]['responses'][turn_ID].split()
        # print(inputJson[turn]['responses'], turn, turn_ID)
        for i in range(4):
            inputJson[i]['requests'].append('3 %d PENG %s' % (turn, response[1]))

    # 杠和补杠额外摸一张牌
    elif priority == 3: # 有人杠
        response = inputJson[turn]['responses'][turn_ID].split()

        for i in range(4):
            inputJson[i]['requests'].append('3 %d GANG' % (turn))
            inputJson[i]['responses'].append('PASS')
        turn_ID += 1

        while idx_paiku < len(paiku) and paiku[idx_paiku][0] == 'H':
            hua[turn].append(paiku[idx_paiku])
            for i in range(4):
                inputJson[i]['requests'].append('3 %d BUHUA %s' % (turn, paiku[idx_paiku]))
                inputJson[i]['responses'].append('PASS')
            turn_ID += 1
            idx_paiku += 1

        if idx_paiku == len(paiku):
            break

        print(idx_paiku, '/', len(paiku), '  ', paiku[idx_paiku])  # 打印下一张牌以显示进程

        curr_pai = paiku[idx_paiku]
        idx_paiku += 1
        for i in range(4):
            if i == turn:
                inputJson[i]['requests'].append('2 %s' % curr_pai)
            else:
                inputJson[i]['requests'].append('3 %d DRAW' % turn)

    elif priority == 4: # 有人补杠
        response = inputJson[turn]['responses'][turn_ID].split()

        for i in range(4):
            inputJson[i]['requests'].append('3 %d BUGANG %s' % (turn, response[1]))
            inputJson[i]['responses'].append('PASS')
        turn_ID += 1

        while idx_paiku < len(paiku) and paiku[idx_paiku][0] == 'H':
            hua[turn].append(paiku[idx_paiku])
            for i in range(4):
                inputJson[i]['requests'].append('3 %d BUHUA %s' % (turn, paiku[idx_paiku]))
                inputJson[i]['responses'].append('PASS')
            turn_ID += 1
            idx_paiku += 1

        if idx_paiku == len(paiku):
            break

        print(idx_paiku, '/', len(paiku), '  ', paiku[idx_paiku])  # 打印下一张牌以显示进程

        curr_pai = paiku[idx_paiku]
        idx_paiku += 1
        for i in range(4):
            if i == turn:
                inputJson[i]['requests'].append('2 %s' % curr_pai)
            else:
                inputJson[i]['requests'].append('3 %d DRAW' % turn)

print('LIU') # 流局