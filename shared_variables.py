# 英雄顺序
hero_num = 2  # 初始化hero_num变量
# 截取图片路径
current_screen_img = "./current_screen_img.jpg"
# 技能模板
hero_skill_num = 1
# skill_path = ""
# 技能名称
skill_name_path = "naima.json"
# 进入地下城满300疲劳提示
pl_300_message_num = 0
# 选择其他地下城
select_other_dxc = [2078, 240]
# 点击冒险
adventure = []
# 点击冒险奖励
adventure_award = []
# 点击冒险级
adventure_level = []
# 点击区域移动
area_move = []
# 点击布万加地图
bwj_map = []
# 战斗开始
combat_start = []
# 点击返回城镇
return_city = []
# 角色1
role_one = []
# 角色2
role_two = []
# 角色3
role_three = []
# 角色4
role_four = []
# 角色5
role_five = []

select_role_dic = {"别拽了俺tuo": [], "奶到你还想奶": [], "大雷给奶一口": [], "大雷是啥子": [], "貌美似朵如花": []}


# skill_path = "./default_skill.json"  # 默认的技能路径
if hero_skill_num == 3 or hero_skill_num == 4:
    # skill_path = "./role_skill/naima.json"
    skill_name_path = "naima.json"
elif hero_skill_num == 5:
    # skill_path = "./role_skill/kuangzhanshi.json"
    skill_name_path = "kzs.json"