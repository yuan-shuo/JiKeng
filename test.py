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

# 总体土层
solid=[
    {'Es': 30000, 'v': 0.2, 'l': 3, 'c': 20, 'phi': 20, "gama": 19, 'm': 10},
    {'Es': 30000, 'v': 0.2, 'l': 2, 'c': 10, 'phi': 10, "gama": 22, 'm': 10},
]
# 桩体总长度
deep = 0
for i in solid:
    deep += i['l']

a = soil_cal(solid, deep, 1)
print(a)