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
            i['m'] = 1000*i['m']
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
                self.pfl_mid[n_y+1]['deltaX'] = f*1000/(i['m']*l)
                cir_l += 0.5
                l += 0.5
                n_y += 1

        # debug[1]
        print(self.pfl_mid)
        # 增量法
        if frontfc:
            # 内撑反力
            f1 = (frontfc[1]*(self.pfl_mid[-1]['y']-self.pfl_mid[frontfc[2]]['y'])
                  *0.5
                  /(self.pfl_mid[-1]['y']-frontfc[0]))
            # 增量法导致的下部荷载增加量
            f2 = frontfc[1] - f1
            # debug[3]
            print(f"f2={frontfc[1]}")
            # 处理为均布
            f2 = f2/(self.y_list[-1] - self.y_list[self.index_y])
            # 增量叠加
            for i in self.pfl_mid[self.index_y+1:]:
                i['deltaX'] = i['deltaX']/i['q'] 
                i['q'] += f2
                i['deltaX'] = i['deltaX']*i['q'] 

        # debug[2]
        print(self.pfl_mid)

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

if __name__ == "__main__":
    a = soil([
        {'Es': 30000, 'v': 0.2, 'l': 2, 'c': 20, 'phi': 20, "gama": 19, 'm': 10},
        {'Es': 30000, 'v': 0.2, 'l': 2, 'c': 10, 'phi': 10, "gama": 22, 'm': 10},
    ], 5, frontfc=None)
    b = soil([
        {'Es': 30000, 'v': 0.2, 'l': 1, 'c': 20, 'phi': 20, "gama": 19, 'm': 10},
        {'Es': 30000, 'v': 0.2, 'l': 2, 'c': 10, 'phi': 10, "gama": 22, 'm': 10},
    ], 5, frontfc=[a.ed, a.tf, a.index_y+1])

    [print((pm['y'], pm['q'], pm['deltaX'])) for pm in a.pfl_mid]
    # print(a.d)
    # [print((pm[0], pm[1], pm[2])) for pm in b.pfl_mid]
    # print(a.y_list)
    # print(a.index_y)