'''main.py'''
import pygame
import game
import menu
import time
import autosolution


pygame.init()

# ---------------------- 界面与棋盘设置 ----------------------
# 定义屏幕尺寸和颜色
SET_WIDTH = 400
SET_HEIGHT = 540
GRID_SIZE = 5            # 棋盘为 5x5
CELL_SIZE = (SET_WIDTH-100)/GRID_SIZE          # 棋盘格大小调整

PANEL_HEIGHT = 80        # 下方拼图块区域高度
MENU_HEIGHT = 100         # 最下方菜单栏高度
SCREEN_WIDTH = SET_WIDTH
SCREEN_HEIGHT = SET_HEIGHT + PANEL_HEIGHT + MENU_HEIGHT
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (30, 144, 255)
GREEN = (0, 195, 92)
LGREEN = (0, 180, 0)
DGRAY=(220, 220, 220)

# 创建游戏窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('5x5 Chessboard')

# 创建一个 5x5 的二维列表，代表棋盘状态
MAP = [[0 for i in range(5)] for j in range(5)]

def draw_map(map):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):           
            x = 50+col * CELL_SIZE# 计算每个单元格的坐标
            y = 50+row * CELL_SIZE            
            if map[row][col] == 0:# 根据 board 数组中的值绘制不同颜色的单元格
                color = WHITE
            elif map[row][col] == 1:
                color = GRAY
            elif map[row][col] == -10:
                color = (50, 50, 50)
            else:
                color = RED
            pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, (0, 0, 0), (x, y, CELL_SIZE, CELL_SIZE), 1)#绘制单元格的边框

#--------------------- 数据初始化 ----------------------

blocs = {k: game.Bloc(k, v, [0, 0], MAP) for k, v in game.blocs_shapes.items()}# 为每个拼图块创建独立 bloc 实例
scoreboard=game.ScoreBoard()

#帧率调整
clock = pygame.time.Clock()

#---------------------- 绘图函数 ----------------------
def draw_buttons(surface, x_offset, y_offset, cell_size, button_texts):    # 绘制拼图块选择按钮，已放置为灰色，未放置为绿色
    font = pygame.font.SysFont(None, 24)
    BUTTONPOSITION={}
    for i in range(2):
        for index, text in enumerate(button_texts[3*i:3*i+3]):
            rect = pygame.Rect(x_offset + index * cell_size, y_offset+i*cell_size, cell_size, cell_size)
            pygame.draw.rect(surface, DGRAY if blocs[text].placed else GREEN, rect)  # 使用类内 placed 属性判断是否已放置
            """if blocs[text][0]== 0:
                pygame.draw.rect(surface, DGRAY, rect)
            else:
                pygame.draw.rect(surface, GREEN, rect)"""
            pygame.draw.rect(surface, (0, 100, 0), rect, 2)
            shape_size = rect.width // 6  # 按钮内每个小方块的大小
            origin_x = rect.x + rect.width // 2 - 17
            origin_y = rect.y + rect.height // 2 -8

            for dx, dy in blocs[text].shape:
                block_x = origin_x + dx * shape_size -4
                block_y = origin_y + dy * shape_size -4
                pygame.draw.rect(surface, WHITE, (block_x, block_y, shape_size, shape_size),2)
            text_surface = font.render(text, True, WHITE)
            surface.blit(text_surface, (rect.x + 10, rect.y + 10))
            BUTTONPOSITION[text]=rect
    return BUTTONPOSITION

def draw_menu(surface, y_offset, menu_texts,scoreboard):    # 绘制底部菜单栏按钮，每个按钮独立放置并增加间隔
    font = pygame.font.SysFont(None, 30)
    button_width = (SCREEN_WIDTH-100) // len(menu_texts)
    spacing = 20  # 按钮之间的间距
    total_width = (button_width * len(menu_texts)) + (spacing * (len(menu_texts) - 1))
    start_x = (SCREEN_WIDTH - total_width) // 2  # 居中排列
    adjusted_y_offset = y_offset +10  # 向下调整菜单栏位置
    MENUPOSITION = {}

    for index, text in enumerate(menu_texts):
        rect_x = start_x + index * (button_width + spacing)
        rect = pygame.Rect(rect_x, adjusted_y_offset, button_width, MENU_HEIGHT-30)
        color = GRAY if text == "START" and not start_enabled else BLUE   # 判断开始与否，开始后标灰
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, (20 , 130 , 255), rect, 2)
        if text=='TIME':    # 计时器位置
            display_text = f"{scoreboard.get_elapsed_time()}s"
        else:
            display_text = text
        text_surface = font.render(display_text, True, WHITE) # 生成带文字图片
        text_rect = text_surface.get_rect(center=rect.center) # pose位置
        surface.blit(text_surface, text_rect) # 贴图（图片，位置）
        MENUPOSITION[text] = rect
    return MENUPOSITION

def draw_loading(surface, text,size,bgcolor): # 弹窗字样
    font = pygame.font.SysFont(None, size)
    loading_surface = font.render(text, True, (255, 255, 255))
    rect = loading_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    pygame.draw.rect(surface, bgcolor, rect)
    # 半透明背景（可选）
    overlay = pygame.Surface((SCREEN_WIDTH-80, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((255,255,255,0))
    surface.blit(overlay, (0,0))   
    surface.blit(loading_surface, rect)
    pygame.display.flip()

#---------------------- 控制函数 ----------------------
def bloc_show(bloc_now):    # 预览方块移动
    showtime = True
    bloc_now.show()  
    draw_map(bloc_now.showplace)
    pygame.display.flip()
    while showtime:
        update=False #做出操作才进行渲染，否则不渲染                              
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN :
                print(f"按下了键: {pygame.key.name(event.key)}")                
                if event.key == pygame.K_RETURN:#确认方块位置
                    print('ok')
                    bloc_now.show()
                    update=True
                    showtime = False
                elif event.key in game.Bloc.key_action:
                    game.Bloc.key_action[event.key](bloc_now)
                update = True
                
        if update:
            bloc_now.show()
            draw_map(bloc_now.showplace)
            pygame.display.flip()

def handle_button_click(button):   # 拼图块按钮函数
    global MAP
    if not blocs[button].placed:#拼图块不在棋盘上 放置
        #bloc_now = game.bloc(blocs[button].shape, [0, 0], MAP)
        bloc_now = blocs[button]
        bloc_now.position = [0, 0]
        bloc_show(bloc_now)#预览方块
        if bloc_now.right_place:
            MAP=bloc_now.pose() #放置方块
        else:
            pass
        #if bloc_now.right_place:
            #blocs[button].placed=True #放置后标灰该按钮 储存拼图位置
    else:#拼图块在棋盘上 取回
        blocs[button].show()
        MAP = blocs[button].take()
        blocs[button].reset()
        #blocs[button]=game.Bloc(game.blocs_shapes[button], [0, 0], MAP)#重新将拼图与按钮绑定
    return MAP

def login(pop_menu): # 用户登录函数
    pop_menu.draw_login_popup()
    pygame.display.flip()
    while not pop_menu.login:
        update=False     
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN :
                pop_menu.handle_login_key(event)
                update = True
        if update:
            pop_menu.draw_login_popup()
            pygame.display.flip()


def WIN(MAP): #判断胜利
    for i in MAP:
        if 0 in i:
            return False
    return True

def hint():
    """
    求“下一块可放置方案”，
    再把形状 + 坐标同步到 game.Bloc。
    """
    global blocs, MAP
    draw_loading(screen, "Loading...",40,BLACK) # 显示“loading”
    pygame.display.flip()  # 强制刷新屏幕
    unposed = {k: v for k, v in blocs.items() if not v.placed}
    hintgrade=len(unposed)
    #print(unposed)
    if not unposed:          # 已无未放置块
        return

    ok, solution = autosolution.answer(unposed, MAP)
    if not ok:
        if solution:
            draw_loading(screen, "WRONG BLOC",40,BLACK)
            pygame.display.flip()
            print("无可行提示")
            time.sleep(1)
            return
        draw_loading(screen, "CAN'T FIND ANSWER",40,BLACK)
        pygame.display.flip()
        print("无可行提示")
        time.sleep(1)
        return
    print(solution)
    name, hb = next(iter(solution.items()))   # 只放第一块
    gb = blocs[name]

    gb.shape = hb.shape[:]  # 深拷贝以防联动
    # 同步旋转/镜像状态计数（仅用于后续判断）
    gb.rotation_state = hb.rotation_state
    gb.mirrow_state  = hb.mirrow_state
    
    gb.position = hb.position[:] # 同步坐标
    gb.right_place = True   # 标记可放
    gb.show() #正式放置并更新棋盘
    MAP = gb.pose()
    print(f"HINT：已放置 {name} 于 {gb.position}")
    scoreboard.hint_score(hintgrade)


def save_state(map,blocs):
    blocs_state = {} # 保存当前游戏状态
    for name, bloc in blocs.items():
        blocs_state[name] = {
            "position": bloc.position,
            "rotation_state": bloc.rotation_state,
            "mirrow_state": bloc.mirrow_state,
            "placed": bloc.placed}
    scoreboard.save_game(map, blocs_state)

button_texts1 = ["A","B","C","D","E","F"]  # 代表不同拼图块的按钮
BOTTON_SIZE = (SCREEN_WIDTH-100)/3
menu_texts = ["START", "TIME", "HINT", "MENU"]  # 底部菜单栏按钮


# ---------------------- Main ----------------------
running = True #主游戏循环
button_positions={}
#blocs=game.blocs.copy()#拷贝字典而非引用
menu_positions = {}
start_enabled = True
score_saved = False
pop_menu = menu.PopMenu(SCREEN_HEIGHT,SCREEN_WIDTH,menu.options,screen) # 弹出菜单对象

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:   # 退出 quit
            running = False
        if not pop_menu.login: # 若未登录需先登录 if not loging, log
            login(pop_menu)
            if pop_menu.login:# 登录成功后尝试加载存档 loading the savefile
                scoreboard.username = pop_menu.username
                saved_data = scoreboard.load_game()
                if saved_data:
                    MAP = saved_data["map"]
                    for bloc_name, bloc_data in saved_data["blocs"].items():#恢复方块状态 reload the blocs
                        if bloc_name in blocs:
                            blocs[bloc_name].apply_state(bloc_data["rotation_state"], bloc_data["mirrow_state"])
                            blocs[bloc_name].position = bloc_data["position"]
                            blocs[bloc_name].placed = bloc_data["placed"]
                            blocs[bloc_name].place = MAP
                    scoreboard.time_start = time.time() - saved_data["time_elapsed"]
                    scoreboard.time_running = True
                    start_enabled = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos  # 获取鼠标点击位置 get the mause clic pos
            if pop_menu.visible and not pop_menu.show_scores: #先判断菜单是否打开 Menu est ouvert ou pas
                result = pop_menu.handle_click(*event.pos)
                if result:
                    print(f"点击了按钮：{result}")
                if result=="USER NAME": # 点击用户名重新登录 relogging et change le user(sans loading the save file)
                    pop_menu.username=''
                    pop_menu.login=False
                    start_enabled = True
                    scoreboard.stop_timer()

                if result=="SAVE AND QUIT":
                    '''blocs_state = {} # 保存当前游戏状态
                    for name, bloc in blocs.items():
                        blocs_state[name] = {
                            "position": bloc.position,
                            "rotation_state": bloc.rotation_state,
                            "mirrow_state": bloc.mirrow_state,
                            "placed": bloc.placed}
                    scoreboard.save_game(MAP, blocs_state)'''
                    save_state(MAP,blocs)
                    running=False
                if result == "SCORE BOARD":
                    pop_menu.show_scores = True
                    print(pop_menu.show_scores)
                if result=="CONTINUE":
                    scoreboard.continue_timer()
                if result=="QUIT":
                    running=False
            elif pop_menu.show_scores:
                pop_menu.handle_click(*event.pos)
            else:
                # start 按钮
                if menu_positions.get("START") and menu_positions["START"].collidepoint(mouse_x, mouse_y) and start_enabled:
                    print("START 被点击，生成新地图")
                    MAP = game.create_map()
                    blocs = {k: game.Bloc(k, v, [0, 0], MAP) for k, v in game.blocs_shapes.items()}
                    start_enabled = False
                    score_saved = False
                    scoreboard.start_timer()
                # menu 按钮
                if menu_positions.get("MENU") and menu_positions["MENU"].collidepoint(mouse_x, mouse_y):
                    scoreboard.pause_timer()
                    pop_menu.visible = True
                    print("MENU 被点击，弹出菜单栏")

                if not start_enabled:#点击开始后才可以操作 ciic start pour remove le blocs
                    for button, rect in button_positions.items():    # 鼠标点在矩形里
                        if rect.collidepoint(mouse_x, mouse_y):
                            pygame.draw.rect(screen, GRAY, rect)
                            print(f"按钮 {button} 被点击！")
                            MAP=handle_button_click(button)
                # hint 按钮
                if menu_positions.get('HINT') and menu_positions["HINT"].collidepoint(mouse_x, mouse_y):
                    print("HINT 被点击")
                    scoreboard.pause_timer()
                    hint()
                    scoreboard.continue_timer()
                    
            
    
    # 填充背景 绘制棋盘
    screen.fill((200, 200, 200))
    draw_map(MAP)   

    #判断菜单是否打开： le menu est-il ouvert?
    if pop_menu.visible:
        pop_menu.draw_overlay()
    else:  
        # 绘制拼图块存放区域 le blocs
        pygame.draw.rect(screen, GRAY, (0, SCREEN_HEIGHT, SCREEN_WIDTH, PANEL_HEIGHT))
        button_positions = draw_buttons(screen, 50, SCREEN_WIDTH-20 , BOTTON_SIZE, button_texts1)

        # 绘制菜单栏 le sous menu
        pygame.draw.rect(screen, WHITE, (0, SCREEN_HEIGHT - MENU_HEIGHT, SCREEN_WIDTH, MENU_HEIGHT))
        menu_positions = draw_menu(screen, SCREEN_HEIGHT - MENU_HEIGHT, menu_texts,scoreboard)
        #print(menu_positions)
    if WIN(MAP) and not score_saved:
        #print('you win!')
        scoreboard.calculate_score()  # 计算分数
        scoreboard.save_score()
        save_state(MAP,blocs)
        scoreboard.stop_timer()
        start_enabled = True
        score_saved = True
        draw_loading(screen, f"You Win!  Score : {scoreboard.score}",40,RED) # 显示“Win”
        time.sleep(1)
        pygame.display.flip()  # 强制刷新屏幕
    pygame.display.flip()    # 更新显示
    clock.tick(30)     #帧率限制

# 退出 Pygame
pygame.quit()

