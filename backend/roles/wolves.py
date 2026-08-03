from enums import Faction
from roles.base import RoleDef, register_role

WOLF_GOAL = """Che giấu thân phận, cắn chết dân làng mỗi đêm cho tới khi số Sói còn sống >= số người còn lại. 
Vào buổi đêm, sói không thảo luận gì mà trực tiếp vote chọn người muốn cắn 
(Suy nghĩ và vote chứ không cần nói)"""

WEREWOLF = register_role(RoleDef(
    role_id="werewolf",
    display_name="Sói",
    faction=Faction.WOLF,
    faction_goal=WOLF_GOAL,
    has_night_action=True,
    description="Cả đàn cùng thức, thống nhất cắn 1 người mỗi đêm.",
))
