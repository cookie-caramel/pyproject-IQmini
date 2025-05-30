'''menu.py'''

import pygame
import game
import json

#菜单列表
options=["USER NAME",
         "SCORE BOARD",
         "CONTINUE",
         "SAVE AND QUIT",
         'QUIT']

#菜单颜色
BRONE = (205, 133, 63)
LBRONE = (222, 184, 135)
DBRONE = (160, 82, 45)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class PopMenu:
    def __init__(self,height,width,options,surface):
        # 窗口变量
        self.height=height
        self.width=width
        self.surface=surface 
        # 可见状态
        self.visible=False 
        # 选项菜单
        self.options=options
        self.option_position = {}
        # 用户绑定
        self.login = False
        self.username = ""
        self.login_input = ""
        self.show_scores = False
        # 排行榜缓存
        self.scoreboard_surface = None
        self.scoreboard_dirty = True  # 标记是否需要重新绘制排行榜

    def draw_overlay(self):
        font = pygame.font.SysFont(None, 30)

        # 创建一个黑色遮罩层
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0,255))
        
        if self.show_scores:
            if not hasattr(self, 'scoreboard_surface') or self.scoreboard_dirty:
                self.draw_scores(overlay)
                self.scoreboard_surface = overlay.copy()  # 保存排行榜的静态图像
                self.scoreboard_dirty = False
            self.surface.blit(self.scoreboard_surface, (0, 0))
            return

        # 计算按钮尺寸与布局
        button_width = self.width - 100
        button_height = (self.height - 200) // len(self.options)
        spacing = 30
        total_height = (button_height * len(self.options)) + (spacing * (len(self.options) - 1))
        start_y = (self.height - total_height) // 2
        adjust_x = (self.width - button_width) // 2

        # 每次绘制前清空旧按钮记录
        self.option_position.clear()
        for index, text in enumerate(self.options):
            rect_y = start_y + index * (button_height + spacing)
            rect = pygame.Rect(adjust_x, rect_y, button_width, button_height)
            pygame.draw.rect(overlay, BRONE, rect)
            pygame.draw.rect(overlay, DBRONE, rect, 2)
            if text=='USER NAME':
                display_text='User : '+ self.username
            else:
                display_text=text
            text_surface = font.render(display_text, True, WHITE)
            text_rect = text_surface.get_rect(center=rect.center)
            overlay.blit(text_surface, text_rect)
            self.option_position[text] = rect  # 保存每个选项的矩形区域

        self.surface.blit(overlay, (0, 0))

    def draw_scores(self, overlay):
        """绘制排行榜"""
        font_title = pygame.font.SysFont(None, 48)
        font_item = pygame.font.SysFont(None, 36)
        
        # 标题
        title = font_title.render("Score Board", True, WHITE)
        overlay.blit(title, (self.width//2 - title.get_width()//2, 30))
        
        # 返回按钮
        back_rect = pygame.Rect(20, 20, 80, 40)
        pygame.draw.rect(overlay, BRONE, back_rect)
        pygame.draw.rect(overlay, DBRONE, back_rect, 2)
        back_text = font_item.render("Back", True, WHITE)
        text_rect=back_text.get_rect(center=back_rect.center)
        overlay.blit(back_text, text_rect)
        self.option_position["BACK"] = back_rect
        
        # 读取分数
        try:
            with open(game.SCORE_FILE, 'r') as f:
                scores = json.load(f)
        except:
            scores = []
            
        # 显示分数
        y_pos = 80
        for i, score in enumerate(scores[:10]):  # 只显示前10名
            score_text = f"{i+1}. {score['username']}: {score['score']} (Time: {score['time']}s)"
            text = font_item.render(score_text, True, WHITE)
            overlay.blit(text, (50, y_pos))
            y_pos += 40

    def handle_click(self, mouse_x, mouse_y): # 按钮点击
        # 遍历所有按钮，判断是否点击到了某个按钮区域
        for option, rect in self.option_position.items():
            if rect.collidepoint(mouse_x, mouse_y):
                if option == "BACK":
                    self.show_scores = False
                    self.scoreboard_dirty = True  # 下次打开排行榜时需要重新绘制
                if option == "CONTINUE":
                    self.visible = False
                return option  # 返回被点击的按钮文字
        return None  # 没有按钮被点击
    
    def draw_login_popup(self): # 绘制登录界面
        font = pygame.font.SysFont(None, 30)
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 255))
        window_width = self.width - 100
        window_height = 180
        enter_width = window_width-100
        enter_height = 60
        rect_y = (self.height - window_height) // 2
        adjust_x = (self.width - window_width) // 2
        enter_x = (self.width - enter_width) // 2
        enter_y = rect_y + 80
        rect_back= pygame.Rect(adjust_x, rect_y, window_width, window_height)
        rect_enter=pygame.Rect(enter_x , enter_y, enter_width, enter_height) # 输入框
        pygame.draw.rect(overlay, WHITE, rect_back)
        pygame.draw.rect(overlay, BLACK, rect_back, 2)
        pygame.draw.rect(overlay, BLACK, rect_enter, 2)
        text_ask=font.render("Enter user's name:", True, BLACK)
        text_answer=font.render(self.login_input, True, BLACK)
        ask_rect = text_ask.get_rect(midtop=(rect_back.centerx , rect_back.top + 50))
        answer_rect=text_answer.get_rect(center=rect_enter.center)
        overlay.blit(text_ask, ask_rect)
        overlay.blit(text_answer, answer_rect)
        self.surface.blit(overlay, (0, 0))

    def handle_login_key(self, event):
        if event.key == pygame.K_RETURN:
            self.username = self.login_input
            self.login = True  # 停止显示输入框
        elif event.key == pygame.K_BACKSPACE:
            self.login_input = self.login_input[:-1]
        else:
            if len(self.login_input)<=14:
                self.login_input += event.unicode  # 加入当前字符
            else:
                pass
    
