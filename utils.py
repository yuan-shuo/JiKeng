import math

class soil:
    def __init__(self, clist, totalDeep, frontfc, exdeep=0.5):
        # 基坑深度
        self.td = totalDeep
        # y轴坐标系
        self.y_list = [i * 0.5 for i in range(2 * self.td + 1)]
        # 本工况开挖深度
        self.d = totalDeep

        # 参数列表
        for i in clist:
            i["Ki"] = ki(v=i['v'], es=i['Es'])
            i["Kp"] = kp(phi=i['phi'])
            self.d -= i['l']
        self.cl = clist

        # 利用超挖深度反算内撑高度
        self.ed = self.d - exdeep

        # 计算起始y坐标(的索引)
        self.index_y = ind(self.y_list, self.d)

        # 被动土压力中点力
        n_y = self.index_y
        l = self.y_list[self.index_y] - self.d + 0.5
        self.pfl_mid = [{'y': i, 'q': 0, 'deltaX':0} for i in self.y_list]
        # self.pfl_mid = [(0,0,0), (l+self.d-1,0,0)]
        # 每个土层
        for i in self.cl:
            cir_l = 0.5
            frontValue = self.pfl_mid[n_y-1]['q']
            # 从0开始的range
            for j in range(math.floor(i['l']*2)):
                j = j*0.5
                f = (frontValue + i['gama']*cir_l + 2*i['c'])*math.sqrt(i['Kp'])*0.5
                # self.pfl_mid[i][0]是y轴坐标
                # self.pfl_mid[i][1]是力的值
                # self.pfl_mid[i][2]是位移
                # self.pfl_mid.append((l + self.d, f, f*1000/(i['m']*l)))
                self.pfl_mid[n_y+1]['q'] = f
                # debug[4]
                # print(f"f={f}")
                # print(f"m={i['m']*l}")
                self.pfl_mid[n_y+1]['deltaX'] = f/(i['m']*l)
                # debug[5]
                # print(self.pfl_mid[n_y+1]['deltaX'])
                cir_l += 0.5
                l += 0.5
                n_y += 1

        # debug[1]
        # print(self.pfl_mid)
        # 增量法
        if frontfc:
            # 内撑反力
            f1 = (frontfc[1]*(self.pfl_mid[-1]['y']-self.pfl_mid[frontfc[2]]['y'])
                  *0.5
                  /(self.pfl_mid[-1]['y']-frontfc[0]))
            for i in self.pfl_mid:
                if frontfc[0] <= i['y']:
                    i['deltaX'] = f1/frontfc[3]
                    break
            # 增量法导致的下部荷载增加量
            f2 = frontfc[1] - f1
            # debug[3]
            # print(f"f2={frontfc[1]}")
            # 处理为均布
            f2 = f2/(self.y_list[-1] - self.y_list[self.index_y])
            # 增量叠加
            for i in self.pfl_mid[self.index_y+1:]:
                i['deltaX'] = i['deltaX']/i['q'] 
                # print(i['deltaX'])
                i['q'] += f2
                i['deltaX'] = i['deltaX']*i['q']

        # debug[2]
        # print(self.pfl_mid)

        # 计算梯形的合力
        self.tf = ((self.pfl_mid[self.index_y+1]['q'] + self.pfl_mid[-1]['q'])
                   *
                   (self.pfl_mid[-1]['y'] - self.pfl_mid[self.index_y+1]['y'])
                   *0.5)
        # debug
        # print((self.pfl_mid[self.index_y+1]['q'] + self.pfl_mid[-1]['q']),
        #       self.pfl_mid[-1]['y'] - self.pfl_mid[self.index_y+1]['y'])


# 1.弹簧刚度系数Ki的计算函数
# ps:不用单位换算,m*N/mm2 = mm* kN/mm2
def ki(v, es,b=1, d=1):
    if b/d == 1:
        w = 0.8
    elif b/d == 1.5:
        w = 1.08
    elif b/d == 2:
        w = 1.22
    else:
        w = 0.8
    fz = b*es
    fm = w*(1-v**2)
    return fz/fm

# 2.被动土压力系数Kp的计算函数
def kp(phi):
    return (math.tan(math.pi*(45+phi/2)/180))**2

# 3.确定index
def ind(list, value):
    n=0
    for i in list:
        if i >= value: return n
        n += 1
    return 0

# 4.根据总土层和开挖深度计算对象及基坑外侧主动土压力
def soil_cal(obj, totalDeep, digDeep, frontfc=[]):
    detect_deepth = 0
    obj_1 = []
    for i in obj:
        obj_1.append(i.copy())
    for i in range(len(obj_1)):
        if i:
            obj_1[i]['l'] += obj_1[i-1]['l']
    cor_index = 0
    de_deep = 0
    for i in obj_1:
        if digDeep <= i['l']:
            de_deep = i['l'] - digDeep
            break
        cor_index += 1

    # 计算开挖面一下土层信息
    obj_down = obj[cor_index:]
    obj_down[0]['l'] = de_deep
    return obj_down, totalDeep, frontfc

# 5.总位移统计
def total_delta(sum, list_pfl):
    for i in range(len(sum)):
        sum[i]['deltaX'] += list_pfl[i]['deltaX']
    return sum


if __name__ == "__main__":
    
    # 总体土层
    solid=[
        {'Es': 30000, 'v': 0.2, 'l': 3, 'c': 20, 'phi': 20, "gama": 19, 'm': 10},
        {'Es': 30000, 'v': 0.2, 'l': 2, 'c': 10, 'phi': 10, "gama": 22, 'm': 10},
    ]
    # 桩体总长度
    deep = 0
    for i in solid:
        deep += i['l']

    y_list = [i * 0.5 for i in range(2 * deep + 1)]
    total_f = [{'y': i, 'deltaX':0, 'shear':0, 'moment':0} for i in y_list]
    # c = soil(*soil_cal(solid, deep, 1))
    # a = soil(*soil_cal(solid, deep, 1))
    
    # a = soil([
    #     {'Es': 30000, 'v': 0.2, 'l': 2, 'c': 20, 'phi': 20, "gama": 19, 'm': 10},
    #     {'Es': 30000, 'v': 0.2, 'l': 2, 'c': 10, 'phi': 10, "gama": 22, 'm': 10},
    # ], deep, frontfc=None)

    # (solid总土层, deep总深度, 1此工况开挖深度, 
    # frontfc=[a.ed前一工况内撑高度, a.tf前一工况集中力, a.index_y+1前一工况开挖起始坐标索引, 409内撑刚度MN/m]
    # b = soil(*soil_cal(solid, deep, 1, frontfc=[a.ed, a.tf, a.index_y+1, 409]))
    # b = soil([
    #     {'Es': 30000, 'v': 0.2, 'l': 1, 'c': 20, 'phi': 20, "gama": 19, 'm': 10},
    #     {'Es': 30000, 'v': 0.2, 'l': 2, 'c': 10, 'phi': 10, "gama": 22, 'm': 10},
    # ], deep, frontfc=[a.ed, a.tf, a.index_y+1])

    all_process = [
        {"digDeepth": 1, "frontEI": None},
        {"digDeepth": 1, "frontEI": 409},
        ]
    setSolid = []
    
    for i in range(len(all_process)):
        if all_process[i]["frontEI"]:
            setSolid.append(soil(*soil_cal(solid,
                                            deep, 
                                            all_process[i]['digDeepth'], 
                                            frontfc=[setSolid[i-1].ed, 
                                                     setSolid[i-1].tf, 
                                                     setSolid[i-1].index_y+1, 
                                                     all_process[i]['frontEI']])))
        else:
            setSolid.append(soil(*soil_cal(solid,
                                            deep, 
                                            all_process[i]['digDeepth'], 
                                            )))
            
    # 总位移初始化
    total_deltaX = [{'y': i, 'deltaX':0} for i in y_list]
    print("forResult:")
    for i in setSolid:
        print("di=")
        [print((pm['y'], pm['q'], pm['deltaX'])) for pm in i.pfl_mid]
        total_deltaX = total_delta(total_deltaX, i.pfl_mid)
        print("td=")
        [print((td['y'], td['deltaX'])) for td in total_deltaX]

    # print("a:")

    # [print((pm['y'], pm['q'], pm['deltaX'])) for pm in a.pfl_mid]

    # print("b:")

    # [print((pm['y'], pm['q'], pm['deltaX'])) for pm in b.pfl_mid]
    # total_deltaX = total_delta(total_deltaX, b.pfl_mid)
    # print("td=")
    # [print((td['y'], td['deltaX'])) for td in total_deltaX]

    

    # print(a.d)
    # [print((pm[0], pm[1], pm[2])) for pm in b.pfl_mid]
    # print(a.y_list)
    # print(a.index_y)