'''game.py'''
import random
import pygame
import time
import json
import os

# 保存文件路径
SAVE_DIR = "save"
SCORE_FILE = os.path.join(SAVE_DIR, "scores.json")
SAVE_FILE = os.path.join(SAVE_DIR, "user_saves.json")

class Bloc:#拼图块函数
    # 所有 bloc 共用的按键行为映射表
    key_action = {
        pygame.K_RIGHT: lambda b: b.go_right(),
        pygame.K_LEFT:  lambda b: b.go_left(),
        pygame.K_DOWN:  lambda b: b.go_down(),
        pygame.K_UP:    lambda b: b.go_up(),
        pygame.K_r:     lambda b: b.rotation(),
        pygame.K_m:     lambda b: b.mirrow(),
    }
    def __init__(self,name,shape,position,place):
        self.name=name
        self.shape=shape #[()]
        self.original_shape=shape[:]
        self.position=position #[]
        self.showplace=[[0 for i in range(5)]for j in range(5)]
        self.right_place=False
        self.place=place
        self.placed = False  # 是否已放置标志 sur le plat?
        self.rotation_state=0 #0-3
        self.mirrow_state=0   #0-1
    def inplat(self):#求最终位置 les final position sur la plat
        inplat=[]
        for k in self.shape:
            result = tuple(map(sum, zip(k,self.position)))
            inplat.append(result)
        return inplat
    def rotation(self):#顺时针旋转 
        self.shape=[(-y,x)for x,y in self.shape]
        if self.rotation_state<3:
            self.rotation_state+=1
        else:
            self.rotation_state=0
        #print(self.shape)
    def mirrow(self):#镜像翻转
        self.shape=[(-x,y)for x,y in self.shape]
        if self.mirrow_state==0:
            self.mirrow_state=1
        else:
            self.mirrow_state=0
    def go_right(self):#以下4条为移动函数
        for x,y in self.inplat():
            if x>=4:
                return
        self.position[0]+=1
    def go_left(self):
        for x,y in self.inplat():
            if x<=0:
                return
        self.position[0]+=-1
    def go_up(self):
        for x,y in self.inplat():
            if y<=0:
                return
        self.position[1]+=-1
    def go_down(self):
        for x,y in self.inplat():
            if y>=4:
                return
        self.position[1]+=1
    def apply_state(self, rot, mirr):
        self.shape = self.original_shape[:]
        for _ in range(rot):
            self.rotation()
        if mirr:
            self.mirrow()
        self.rotation_state = rot
        self.mirrow_state = mirr
    def show(self):#效果预览 pour voir le bloc sur le plat
        self.showplace=list(map(list, self.place))#二维列表的副本需要嵌套两次 deep copy
        #print(self.inplat())
        outofmap=False
        for x,y in self.inplat():
            if x<0 or y<0 or x>4 or y>4:#超出边界 out of range
                outofmap=True
                pass
            else:
                self.showplace[y][x]+=1
        self.right_place = True  # 假设一开始是合法的
        for i in self.showplace:#判断是否可放
            if max(i) > 1 or (-9 in i) or outofmap:
                self.right_place = False
                break
        '''for i in self.showplace:
            if max(i)>1 or (-9 in i) or outofmap:
                #print(min(i))
                self.right_place=False
                break
            else:
                self.right_place=True'''
        #for i in self.showplace:#效果预览
            #1print(i)
        return self.showplace              
    def pose(self):
        if self.right_place:
            for y in range(5):
                for x in range(5):
                    # 只更新为1，保留原始障碍物(-10)
                    if self.showplace[y][x] > 0:
                        self.place[y][x] = self.showplace[y][x]
            self.placed = True
            return self.place
        else:
            print('you can not put it here')
            return None
    def take(self): # 移除当前块的放置状态，恢复初始形态 take the blocs from the plat,initiale
        for x,y in self.inplat():
            #print(x,y)
            self.place[y][x]-=1
            self.placed = False
        return self.place
    def reset(self):
        self.shape = self.original_shape
        self.position = [0,0]
        self.rotation_state=0 #0-3
        self.mirrow_state=0   #0-1
        self.right_place = False
        self.placed = False


bloc1=[(0,0),(1,0),(2,0)]#111
bloc2=[(0,0),(0,1),(1,0)]#21
bloc3=[(0,0),(1,0),(1,1),(2,1)]#121(Z)
bloc4=[(0,0),(1,0),(1,1),(2,0)]#121(T)
bloc5=[(0,0),(1,0),(0,1),(2,0)]#211(L)
bloc6=[(0,0),(1,0),(0,1),(1,1)]#田

blocs_shapes = {"A": bloc1,"B": bloc2,"C": bloc3,"D": bloc4,"E": bloc5,"F": bloc6}

def create_map():#地图生成函数
    map=[[0 for i in range(5)]for j in range(5)]
    l1=[(0,0),(1,0),(0,1),(1,1),(2,1),(3,1),(1,2),(1,3)]
    l2=[(3,0),(4,0),(4,1),(4,2),(4,3),(4,4),(3,4)]
    l3=[(0,3),(0,4),(1,4),(2,4),(2,3),(2,2),(3,2)]
    for i in [l1,l2,l3]:
        point=i[random.randint(0,len(i)-1)]
        map[point[1]][point[0]]-=10
        #print(point)
    for i in map:
            print(i)
    return map

class ScoreBoard:#计分模块 score
    def __init__(self):
        self.time_start=0.0
        self.time_pass=0.0
        self.time_get_paused=0.0
        self.time_pause=0.0
        self.time_running=False
        self.score=0
        self.username = ""
        self.hint_times=0
    def start_timer(self): #timer
        self.time_start=time.time()
        self.time_pause=0.0
        self.time_running=True
        self.hint_times=0
    def pause_timer(self):
        self.time_get_paused = time.time()
    def continue_timer(self):
        self.time_pause += time.time()-self.time_get_paused
    def get_elapsed_time(self):
        if self.time_running:
            self.time_pass=round(time.time()-self.time_start-self.time_pause,1)            
        else:
            self.time_pass=0.00
        return self.time_pass
    def stop_timer(self):
        if self.time_running:
            self.time_pass = round(time.time() - self.time_start, 1)
            self.time_running = False
        
    def hint_score(self,n):
        self.hint_times+=n
        print('hintgrade:',self.hint_times)

    def calculate_score(self):
        self.score = max(0, 5000 - int(self.get_elapsed_time() * 10)-int(self.hint_times*200))
        return self.score


    def save_score(self):  # 保存分数到排行榜 save scores
        print(f"尝试保存分数 - 用户名: {self.username}, 时间: {self.time_pass}, 分数: {self.score}")
        
        if not self.username or not self.time_pass:
            print("保存失败: 缺少用户名或时间数据")
            return False

        try:
            # 读取现有分数 read scores
            score_data = []
            if os.path.exists(SCORE_FILE):
                print("找到分数文件，尝试读取...")
                with open(SCORE_FILE, 'r') as f:
                    try:
                        score_data = json.load(f)
                        print(f"成功读取 {len(score_data)} 条记录")
                    except json.JSONDecodeError:
                        print("分数文件格式错误，将创建新记录")
                        score_data = []
            else:
                print("分数文件不存在，将创建新文件")

            # 检查是否已有该用户的记录 trouver le data deja ecrit
            user_exists = False
            for record in score_data:
                if record["username"] == self.username:
                    print(f"找到现有记录: {record}")
                    user_exists = True
                    if self.score > record["score"]:
                        print("新分数更高，更新记录")
                        record.update({
                            "score": self.score,
                            "time": self.time_pass,
                            "date": time.strftime("%Y-%m-%d %H:%M:%S")
                        })
                    break

            if not user_exists:
                print("添加新用户记录")
                score_data.append({
                    "username": self.username,
                    "score": self.score,
                    "time": self.time_pass,
                    "date": time.strftime("%Y-%m-%d %H:%M:%S")
                })

            # 按分数排序并保留前10名 order
            score_data.sort(key=lambda x: x["score"], reverse=True)
            score_data = score_data[:10]
            print(f"最终保存 {len(score_data)} 条记录")

            # 保存分数
            if not os.path.exists(SAVE_DIR):
                os.makedirs(SAVE_DIR)
                
            with open(SCORE_FILE, 'w') as f:
                json.dump(score_data, f, indent=4)
            print("分数保存成功")
            return True

        except Exception as e:
            print(f"保存分数时出错: {str(e)}")
            return False

    def save_game(self, map_state, blocs_state):
        """保存当前游戏状态"""
        if not self.username:
            return False
            
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)
            
        save_data = {}
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'r') as f:
                save_data = json.load(f)
                
        # 保存完整地图状态（包括原始地图和当前地图）
        save_data[self.username] = {
            "map": map_state,
            "blocs": blocs_state,
            "time_elapsed": self.get_elapsed_time(),
            "save_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(SAVE_FILE, 'w') as f:
            json.dump(save_data, f, indent=4)
        return True

    def load_game(self):
        """加载用户保存的游戏"""
        if not self.username or not os.path.exists(SAVE_FILE):
            return None
            
        with open(SAVE_FILE, 'r') as f:
            save_data = json.load(f)
            
        if self.username in save_data:
            user_data = save_data[self.username]
            # 返回完整数据
            return {
                "map": user_data["map"],
                "blocs": user_data["blocs"],
                "time_elapsed": user_data["time_elapsed"]
            }
        return None
