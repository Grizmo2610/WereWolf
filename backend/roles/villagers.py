from enums import Faction
from roles.base import RoleDef, register_role

VILLAGE_GOAL = "Tìm ra và loại bỏ hết phe Sói trước khi bị Sói tiêu diệt hết."

VILLAGER = register_role(RoleDef(
    role_id="villager",
    display_name="Dân thường",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=False,
    description="Không có khả năng đặc biệt, chỉ có quyền thảo luận và vote.",
))

SEER = register_role(RoleDef(
    role_id="seer",
    display_name="Tiên Tri",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=True,
    description="Mỗi đêm BẮT BUỘC chọn 1 người, biết họ thuộc phe nào.",
))

GUARD = register_role(RoleDef(
    role_id="guard",
    display_name="Bảo Vệ",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=True,
    description="Mỗi đêm BẮT BUỘC PHẢI chọn 1 người để bảo vệ khỏi Sói cắn. Không được bảo vệ trùng người 2 đêm liên tiếp.",
))

WITCH = register_role(RoleDef(
    role_id="witch",
    display_name="Phù Thủy",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=True,
    description="Có 1 lọ cứu + 1 lọ độc, dùng cả game, mỗi loại 1 lần.",
))

HUNTER = register_role(RoleDef(
    role_id="hunter",
    display_name="Thợ Săn",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=False,
    description="Nếu Thợ Săn chết, được bắn theo 1 người bất kỳ ngay lập tức.",
))
