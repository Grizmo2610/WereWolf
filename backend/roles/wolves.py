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

ALPHA_WOLF = register_role(RoleDef(
    role_id="alpha_wolf",
    display_name="Sói Đầu Đàn",
    faction=Faction.WOLF,
    faction_goal=WOLF_GOAL,
    has_night_action=True,
    description="Một lần duy nhất trong cả trận, biến mục tiêu bị cắn thành Sói thay vì giết họ; mất tác dụng nếu mục tiêu được bảo vệ.",
))

WOLF_CUB = register_role(RoleDef(
    role_id="wolf_cub",
    display_name="Sói Con",
    faction=Faction.WOLF,
    faction_goal=WOLF_GOAL,
    has_night_action=False,
    description="Khi Sói Con chết, lượt treo cổ ngày hôm sau cho phép loại bỏ 2 người chơi thay vì 1.",
))

LONE_WOLF = register_role(RoleDef(
    role_id="lone_wolf",
    display_name="Sói Cô Độc",
    faction=Faction.WOLF,
    faction_goal="Là con Sói duy nhất còn sống sót cuối cùng.",
    has_night_action=True,
    description="Hoạt động giống như Sói thường nhưng có điều kiện chiến thắng cá nhân riêng biệt.",
))

VEGETARIAN_WOLF = register_role(RoleDef(
    role_id="vegetarian_wolf",
    display_name="Sói Ăn Chay",
    faction=Faction.WOLF,
    faction_goal=WOLF_GOAL,
    has_night_action=False,
    description="Không tham gia vào việc cắn người mỗi đêm; vẫn chiến thắng cùng phe Sói.",
))

WOLF_SEER = register_role(RoleDef(
    role_id="wolf_seer",
    display_name="Sói Tiên Tri",
    faction=Faction.WOLF,
    faction_goal=WOLF_GOAL,
    has_night_action=True,
    description="Một con Sói sở hữu khả năng soi phe của Tiên Tri mỗi đêm.",
))

MEDIUM = register_role(RoleDef(
    role_id="medium",
    display_name="Bà Đồng",
    faction=Faction.WOLF,
    faction_goal=WOLF_GOAL,
    has_night_action=False,
    description="Không thức dậy cùng đàn sói; bí mật theo dõi Tiên Tri — trở thành Sói Tiên Tri nếu Tiên Tri thật chết.",
))
