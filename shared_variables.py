hero_num = 2  # 初始化hero_num变量
hero_skill_num = 1
# skill_path = ""
skill_name_path = "naima.json"
pl_300_message_num = 0


# skill_path = "./default_skill.json"  # 默认的技能路径
if hero_skill_num == 3 or hero_skill_num == 4:
    # skill_path = "./role_skill/naima.json"
    skill_name_path = "naima.json"
elif hero_skill_num == 5:
    # skill_path = "./role_skill/kuangzhanshi.json"
    skill_name_path = "kzs.json"