'''autosolution.py'''
import hintgame
import copy


def impossible(map): # 孤岛地图 non soloution map
    for i in range(5):
        for j in range(5):
            if map[i][j] == 0:
                zero_neighbors = []
                for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < 5 and 0 <= nj < 5:
                        if map[ni][nj] == 0:
                            zero_neighbors.append([ni,nj])
                if len(zero_neighbors) == 0:
                    return True
                elif len(zero_neighbors) == 1:
                    zero_neighbors_neibor = 0
                    i,j=zero_neighbors[0][0],zero_neighbors[0][1]                 
                    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                        ni, nj = i + dx, j + dy
                        if 0 <= ni < 5 and 0 <= nj < 5:
                            if map[ni][nj] == 0:
                                zero_neighbors_neibor+=1
                    if zero_neighbors_neibor<=1:
                        return True
    return False

def advance_state(bloc): #下一个状态 prochain etat
    #print('下一步')
    rot = bloc.rotation_state
    mirr = bloc.mirrow_state
    x, y = bloc.position

    # 先推进 x 坐标（最小单位）
    if x < 4:
        bloc.position[0] += 1
        return True
    elif y < 4:
        bloc.position[0] = 0
        bloc.position[1] += 1
        return True
    elif rot < 3:
        bloc.position = [0, 0]
        bloc.rotation_state += 1
        return True
    elif mirr < bloc.mirrow_time - 1:
        bloc.position = [0, 0]
        bloc.rotation_state = 0
        bloc.mirrow_state += 1
        return True
    else:
        return False  # 所有状态都试过了

def can_pose(broad,bloc): #当前位置能否放置 possible position?
    new_broad=copy.deepcopy(broad) # 不影响原broad
    testbloc=copy.deepcopy(bloc)
    #new_broad.pose(testbloc)  
    if new_broad.pose(testbloc) and not impossible(new_broad.grid):
        #print(f"可放置于 {bloc.position}")
        #new_broad.display()
        return True
    #new_broad.display()
    #print(f"{bloc.name}不可放置于 {bloc.position}",bloc.mirrow_state,bloc.rotation_state,new_broad.pose(testbloc))
    return False

def find_position_from(broad,bloc,mirror_s,rotat_s,position): #从特定位置开始 commencer a cet position et etat
    #bloc.take()  
    for mirrow in range(mirror_s,bloc.mirrow_time):
        #print('镜像',mirrow)
        rotat=rotat_s  
        for _ in range(rotat_s,4,bloc.rotation_step):
            #print('旋转',rotat)
            #判断边界
            bloc.apply_state(rotat, mirrow, position)  # 首先确定当前形态
            #print(position)            
            # 获取形态范围
            xs = [x for x, y in bloc.shape]
            ys = [y for x, y in bloc.shape]
            wm, hm = min(xs), min(ys)
            wM, hM = max(xs), max(ys)
            
            # 确保不会出负坐标
            if 5 - wM < position[0]:
                position[0]=0
                position[1]+=1
            elif 5 - hM < position[1]:
                broad.take(bloc) 
                bloc.reset()  # 下一行全部超出范围则等价于无解
                return False
            y_start = max(position[1], 0, -hm)
            y_end = 5 - hM
            x_start = max(0, -wm,position[0])
            x_end = 5 - wM
            for y in range(y_start, y_end):
                for x in range(x_start , x_end):
                    #print(rotat, mirrow)
                    bloc.apply_state(rotat, mirrow, [x, y])
                    if can_pose(broad, bloc):
                        broad.pose(bloc)
                        return True
            position=[0,0]
            rotat+=1
        rotat_s=0
    broad.take(bloc) 
    bloc.reset()  # 如果全部遍历后无解，则初始化
    #print('初始化')
    return False

def find_a_solution(broad,blocs): #求解函数 trouver les solution
    wrong_place=False
    path=copy.deepcopy(blocs)
    tried_times=0
    bloc_key=list(path.keys())
    blocs_index=0
    for _ in range(len(path)):        
        while tried_times<1000 and not broad.full_fill():
            tried_times+=1
            bloc_analysing=path[bloc_key[blocs_index]]
            #print(bloc_key[blocs_index]) #当前操作对象
            #print(bloc_analysing.mirrow_state,bloc_analysing.rotation_state,bloc_analysing.position)
            placed=find_position_from(broad,
                                    bloc_analysing,
                                    bloc_analysing.mirrow_state,
                                    bloc_analysing.rotation_state,
                                    bloc_analysing.position)        
            #print(path[bloc_key[blocs_index]].position)
            if placed and blocs_index<5:
                blocs_index+=1
            elif not placed and blocs_index>=0:            
                blocs_index-=1
                bloc_analysing=path[bloc_key[blocs_index]]
                #print(f"❗退回索引 {blocs_index}, 当前处理块: {bloc_key[blocs_index]}, placed: {path[bloc_key[blocs_index]].placed}")
                broad.take(path[bloc_key[blocs_index]])
                #print(bloc_analysing.mirrow_state,bloc_analysing.rotation_state,bloc_analysing.position)
                advance_state(path[bloc_key[blocs_index]])
            elif blocs_index>=5 or blocs_index<0:
                wrong_place=True
                break
            elif broad.full_fill():
                break
        first_key = next(iter(path))
        first_value = path[first_key]
        # 删除第一项
        del path[first_key]
        # 重新插入第一项到最后
        path[first_key] = first_value
        #print('换顺序')
        tried_times=0
    if broad.full_fill():
        print('I find a solution.')
        print(list(path.keys()))
        #broad.show_puzzle()
    else:
        if not wrong_place:
            print('too hard for me')
        else:
            print('there is a wrong bloc.')
        #broad.show_puzzle()
    return path,wrong_place

def check(puzzle,solution): #justifier
    test=copy.deepcopy(puzzle)
    for i in solution:
        bloc=solution[i]
        check_broad=hintgame.Board(set_board=test)
        check_broad.pose(bloc)
    return check_broad.full_fill()

def test(): # 测试程序
    BOARD = hintgame.Board(random=True)
    BLOCS = {k: hintgame.Bloc(v,k) for k, v in hintgame.blocs_shapes.items()}

    solution,tryed=find_a_solution(BOARD,BLOCS)

    #print(tryed)

    if check(BOARD.original_grid,solution):
        print('True')
        return True, BOARD.original_grid
    else:
        print('False')
        return False, None
#----------------------solution------------------

def answer(dic_bloc,map):
    blocs,board=hintgame.transfer(dic_bloc,map)
    solution,wrong_place=find_a_solution(board,blocs)
    print(wrong_place)
    if check(board.original_grid,solution):
        return True,solution
    else:
        return False,wrong_place
'''
BOARD = hintgame.Board(random=False)
BLOCS = {k: hintgame.Bloc(v,k) for k, v in hintgame.blocs_shapes.items()}

solution,tryed=find_a_solution(BOARD,BLOCS)

print(tryed)
for i in solution:
    print(i,solution[i].position,solution[i].shape)'''