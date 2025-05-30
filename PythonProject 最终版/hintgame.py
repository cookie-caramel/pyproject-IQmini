'''hintgame.py'''
import random
import copy
#place=[[0 for i in range(5)]for j in range(5)]#棋盘

def transfer(dic_bloc,map):
    hintbloc={}
    for i in dic_bloc:
        bloc=dic_bloc[i]
        #name=str()
        hintbloc[bloc.name]=Bloc(bloc.shape,bloc.name)
        board=Board(set_board=copy.deepcopy(map))
    return hintbloc,board


class Bloc:#拼图块函数
    def __init__(self,shape,name):
        self.name=name
        self.shape=shape #[()]
        self.original_shape=shape[:]
        self.position=[0,0] #临时输入，需要被移到地图中处理
        self.placed = False  # 是否已放置标志
        self.rotation_state=0 #0-3
        self.mirrow_state=0   #0-1
        self.rotation_step = self.sythese_rotation()
        self.mirrow_time= self.sythese_mirrow()

    def rotation(self):#顺时针旋转
        self.shape=[(-y,x)for x,y in self.shape]
        if self.rotation_state<3:
            self.rotation_state+=1
        else:
            self.rotation_state=0
        return self.shape
    def mirrow(self):#镜像翻转
        self.shape=[(-x,y)for x,y in self.shape]
        if self.mirrow_state==0:
            self.mirrow_state=1
        else:
            self.mirrow_state=0
        return self.shape
    
    def sythese_mirrow(self):
        def normalize(shape):
            #将最小点移动到(0, 0)，便于比较
            min_x = min(x for x, y in shape)
            min_y = min(y for x, y in shape)
            return sorted([(x - min_x, y - min_y) for x, y in shape])
        bloccopy=copy.deepcopy(self)
        shapetest = normalize(bloccopy.original_shape)
        shape_mirrowed = bloccopy.mirrow()
        if normalize(shape_mirrowed) == shapetest:
            return 1            
        else:
            return 2
    
    def sythese_rotation(self):
        def normalize(shape):
            min_x = min(x for x, y in shape)
            min_y = min(y for x, y in shape)
            return sorted([(x - min_x, y - min_y) for x, y in shape])   
        #original = normalize(self.shape)
        unique_shapes = set()
        shape = copy.deepcopy(self.shape)
        for _ in range(4):
            shape = self.rotation()
            normalized = tuple(normalize(shape))  # tuple for set
            unique_shapes.add(normalized)
        return 4//len(unique_shapes)

    def apply_state(self, rot, mirr,position):
        self.shape = self.original_shape[:]
        for _ in range(rot):
            self.rotation()
        if mirr:
            self.mirrow()
        self.position = position
        self.rotation_state = rot
        self.mirrow_state = mirr
    def reset(self):
        self.shape = self.original_shape
        self.position = [0,0]
        self.rotation_state=0 #0-3
        self.mirrow_state=0   #0-1
        self.right_place = False
        self.placed = False

    def be_posed(self):#放置方块
        self.placed = True

    def be_taken(self): # 移除当前块的放置状态，恢复初始形态
        self.placed = False

#格式：(right,down)
bloc1=[(0,0),(1,0),(2,0)]#111
bloc2=[(0,0),(0,1),(1,0)]#21
bloc3=[(0,0),(1,0),(1,1),(2,1)]#121(Z)
bloc4=[(0,0),(1,0),(1,1),(2,0)]#121(T)
bloc5=[(0,0),(1,0),(0,1),(2,0)]#211(L)
bloc6=[(0,0),(1,0),(0,1),(1,1)]#田

blocs_shapes = {"A": bloc1,"B": bloc2,"C": bloc3,"D": bloc4,"E": bloc5,"F": bloc6}

class Board:
    def __init__(self,set_board=None, random=False):
        self.test_board=set_board
        self.grid = self.create_map() if random else self.load_test_map() 
        self.original_grid=copy.deepcopy(self.grid)
        

    def create_map(self):#地图生成函数
        grid=[[0 for _ in range(5)]for _ in range(5)]
        l1=[(0,0),(1,0),(0,1),(1,1),(2,1),(3,1),(1,2),(1,3)]
        l2=[(3,0),(4,0),(4,1),(4,2),(4,3),(4,4),(3,4)]
        l3=[(0,3),(0,4),(1,4),(2,4),(2,3),(2,2),(3,2)]
        for i in [l1,l2,l3]:
            point=i[random.randint(0,len(i)-1)]
            grid[point[1]][point[0]]+=1
            #print(point)
        #for i in grid:
                #print(i)
        self.grid=grid
        return grid

    def load_test_map(self): # 测试地图
        if self.test_board!=None:
            return self.test_board
        else:
            return [
                [0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1],
                [0, 0, 1, 0, 0]]   

    def full_fill(self): # 判断填满
        for i in self.grid:
            if 0 in i:
                return False
        return True
    
    def clone(self):   # 拷贝地图（可能有用）
        self_copy=copy.deepcopy(self.grid)
        return self_copy

    def inplate(self,bloc):  # 定位拼图在地图位置
        inplat=[]
        for k in bloc.shape:
            result = tuple(map(sum, zip(k,bloc.position)))
            inplat.append(result)
        return inplat
    
    def right_place(self, bloc):  # 判断拼图位置是否合法
        #print(self.inplate(bloc))
        for x,y in self.inplate(bloc):
            #self.display()
            #print(x,',',y)
            #print(self.grid[y][x])
            if x<0 or y<0 or x>4 or y>4:#超出边界
                #print('out of range')
                return False
            elif self.grid[y][x]!=0:
                #print(x,y,"→ 非空格")
                return False
        return True  
       
    def pose(self,bloc):  # 放置拼图（直接修改地图）
        success = self.right_place(bloc)
        if success:
            for x,y in self.inplate(bloc):
                self.grid[y][x]+=1
            bloc.be_posed()
            #print(bloc.placed)
        else:
            pass
            #print('you can not put it here')
        return success   
    
    def take(self,bloc):  # 取下拼图
        for x,y in self.inplate(bloc):
            if bloc.placed :
                #print('take',bloc.placed)
                if self.grid[y][x]==1:
                    self.grid[y][x]-=1
            else:
                pass
                #print(f"can't take {bloc.name} from{bloc.position},it is shaped in {bloc.shape}.")
        bloc.be_taken()

    def display(self):
        for row in self.grid:
            print(row) 

    def show_puzzle(self):
        for row in self.original_grid:
            print(row) 
       

    
    

    