from enums import Faction
from roles.base import RoleDef, register_role

FOOL = register_role(RoleDef(
    role_id="fool",
    display_name="Kẻ Chán Đời",
    faction=Faction.NEUTRAL,
    faction_goal="Được bình chọn treo cổ vào ban ngày.",
    has_night_action=False,
    description="Thắng độc lập nếu bị treo cổ bằng hình thức bỏ phiếu ban ngày (chỉ tính nguyên nhân cái chết này).",
))

SOLO_KILLER = register_role(RoleDef(
    role_id="solo_killer",
    display_name="Sát Nhân Đơn Độc",
    faction=Faction.NEUTRAL,
    faction_goal="Trở thành người sống sót duy nhất.",
    has_night_action=True,
    description="Mỗi đêm giết một người chơi (không phải Sói); chiến thắng khi là người duy nhất còn sống sót.",
))

CULT_LEADER = register_role(RoleDef(
    role_id="cult_leader",
    display_name="Chủ Giáo Phái",
    faction=Faction.NEUTRAL,
    faction_goal="Thu nạp tất cả người chơi còn sống vào giáo phái.",
    has_night_action=True,
    description="Mỗi đêm thu nạp một người chơi vào giáo phái; chiến thắng khi tất cả người chơi còn sống đều là thành viên giáo phái.",
))

VAMPIRE = register_role(RoleDef(
    role_id="vampire",
    display_name="Ma Cà Rồng",
    faction=Faction.NEUTRAL,
    faction_goal="Tiêu diệt tất cả những người khác.",
    has_night_action=True,
    description="Hút máu một người chơi mỗi đêm — cái chết của nạn nhân chỉ được công bố sau khi cuộc họp ngày hôm sau kết thúc; nạn nhân vẫn có thể được cứu trước đó.",
))

SABOTEUR = register_role(RoleDef(
    role_id="saboteur",
    display_name="Kẻ Phá Rối",
    faction=Faction.NEUTRAL,
    faction_goal="Phá hoại trò chơi bằng cách hoán đổi vai trò.",
    has_night_action=True,
    description="Sử dụng một lần duy nhất: hoán đổi vai trò của hai người chơi ngẫu nhiên.",
))
