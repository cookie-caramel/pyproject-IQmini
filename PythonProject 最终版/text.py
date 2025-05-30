DGRAY=(100, 100, 100)
INFO_BOX_COLOR = (240, 240, 240)  # 信息框背景色
TEXT_COLOR = (0, 0, 0)            # 文字颜色
info_font = pygame.font.SysFont("simhei", 20)

# 在初始化部分添加字体
info_font = pygame.font.SysFont("simhei", 20)  # 使用黑体

# 添加信息提示框绘制函数
def draw_info_box(surface, messages):
    box_height = 50
    pygame.draw.rect(surface, INFO_BOX_COLOR, (0, 0, SCREEN_WIDTH, box_height))
    y_offset = 5
    for msg in messages[-2:]:  # 只显示最新两条信息
        text_surface = info_font.render(msg, True, TEXT_COLOR)
        surface.blit(text_surface, (10, y_offset))
        y_offset += 20

# 添加全局状态变量（主循环前添加）
game_status = {
    "last_action": "等待操作",
    "error_msg": None,
    "win": False
}

# 修改主循环中的事件处理部分（示例）
if event.key == pygame.K_RIGHT:
    game_status["last_action"] = "向右移动"
elif event.key == pygame.K_r:
    game_status["last_action"] = "旋转方块"
elif event.key == pygame.K_RETURN:
    if not bloc_now.right_place:
        game_status["error_msg"] = "无法放置：与其他方块重叠或超出边界！"

# 修改胜利判断部分
if WIN(MAP):
    game_status["win"] = True

# 在主循环渲染部分添加信息框绘制
messages = []
if game_status["win"]:
    messages.append("游戏胜利！请重置游戏继续")
else:
    messages.append(f"最新操作：{game_status['last_action']}")
    if game_status["error_msg"]:
        messages.append(f"错误：{game_status['error_msg']}")

draw_info_box(screen, messages)  # 在pygame.display.flip()前调用