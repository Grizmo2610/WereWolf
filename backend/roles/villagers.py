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

APPRENTICE_SEER = register_role(RoleDef(
    role_id="apprentice_seer",
    display_name="Tiên Tri Tập Sự",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=True,
    description="Sẽ thức tỉnh và nhận năng lực của Tiên Tri sau khi Tiên Tri thật chết.",
))

MYSTIC_SEER = register_role(RoleDef(
    role_id="mystic_seer",
    display_name="Tiên Tri Bí Ẩn",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=True,
    description="Mỗi đêm chọn 1 người, biết chính xác vai trò của người đó.",
))

CLAIRVOYANT = register_role(RoleDef(
    role_id="clairvoyant",
    display_name="Ngoại Cảm",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=True,
    description="Mỗi đêm chọn 2 người, biết họ có cùng phe với nhau hay không.",
))

DETECTIVE = register_role(RoleDef(
    role_id="detective",
    display_name="Thám Tử",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=True,
    description="Sử dụng một lần duy nhất trong trò chơi: biết mục tiêu được chọn (hoặc hàng xóm còn sống gần nhất) có phải là Sói hay không.",
))

GHOST = register_role(RoleDef(
    role_id="ghost",
    display_name="Hồn Ma",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=False,
    description="Chết vào đêm đầu tiên; có thể nghe người chết nói chuyện; bị giới hạn chỉ được nói đúng 1 từ mỗi ngày.",
))

PRIEST = register_role(RoleDef(
    role_id="priest",
    display_name="Mục Sư",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=True,
    description="Bảo vệ một mục tiêu vĩnh viễn khỏi bị Sói cắn (vẫn có thể chết vì các lý do khác). Chỉ dùng được một lần.",
))

HUNTRESS = register_role(RoleDef(
    role_id="huntress",
    display_name="Nữ Thợ Săn",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=True,
    description="Có một lần bắn giết mục tiêu bất kỳ lúc nào trong đêm.",
))

PLAGUE_BEARER = register_role(RoleDef(
    role_id="plague_bearer",
    display_name="Người Bị Bệnh",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=False,
    description="Nếu bị Sói cắn chết, Sói sẽ bị nhiễm bệnh và không thể cắn ai vào đêm tiếp theo.",
))

CUPID = register_role(RoleDef(
    role_id="cupid",
    display_name="Cupid",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=True,
    description="Chỉ đêm đầu tiên: ghép đôi 2 người chơi thành cặp tình nhân — một người chết thì người kia cũng chết theo, bất kể phe phái.",
))

TERRORIST = register_role(RoleDef(
    role_id="terrorist",
    display_name="Khủng Bố",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=False,
    description="Khi chết, cả hai người hàng xóm vật lý ở hai bên cũng sẽ chết theo.",
))

HALFBREED = register_role(RoleDef(
    role_id="halfbreed",
    display_name="Con Lai",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=False,
    description="Là Dân thường thực thụ, nhưng Tiên Tri khi soi sẽ thấy là Sói.",
))

CURSED = register_role(RoleDef(
    role_id="cursed",
    display_name="Kẻ Bị Nguyền",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=False,
    description="Dân thường bình thường; nếu bị Sói cắn, sẽ hóa thành Sói thay vì bị chết.",
))

CLONE = register_role(RoleDef(
    role_id="clone",
    display_name="Nhân Bản",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=True,
    description="Đêm 1: chọn một mục tiêu; nếu mục tiêu đó chết, Nhân Bản sẽ thừa kế vai trò của họ.",
))

GRANDMOTHER = register_role(RoleDef(
    role_id="grandmother",
    display_name="Bà Ngoại",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=False,
    description="Dân thường bình thường, được ghép đôi với Khăn Đỏ.",
))

RED_HOOD = register_role(RoleDef(
    role_id="red_hood",
    display_name="Khăn Đỏ",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=True,
    description="Sau khi Bà Ngoại chết, Khăn Đỏ biết danh tính của một con Sói mỗi đêm trong suốt phần còn lại của trò chơi.",
))

TWINS = register_role(RoleDef(
    role_id="twins",
    display_name="Song Sinh",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=False,
    description="Nhận ra nhau từ đêm đầu tiên; có thể thắng độc lập nếu là cặp đôi sống sót cuối cùng.",
))

SORCERER = register_role(RoleDef(
    role_id="sorcerer",
    display_name="Pháp Sư",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=True,
    description="Mỗi đêm, khóa mõm một người chơi vào ngày hôm sau (người đó vẫn có quyền bỏ phiếu).",
))

OLD_HAG = register_role(RoleDef(
    role_id="old_hag",
    display_name="Mụ Già",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=True,
    description="Mỗi đêm, buộc một người chơi phải ngồi ngoài vào ngày hôm sau (không thảo luận, không bỏ phiếu).",
))

PRINCE = register_role(RoleDef(
    role_id="prince",
    display_name="Hoàng Tử",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=False,
    description="Miễn nhiễm với lần treo cổ đầu tiên — thân phận được công khai thay vì bị chết.",
))

TOUGH_YOUTH = register_role(RoleDef(
    role_id="tough_youth",
    display_name="Thanh Niên Cứng",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=False,
    description="Nếu bị Sói cắn, sẽ chết vào đêm sau đó thay vì chết ngay lập tức.",
))

GAMBLER = register_role(RoleDef(
    role_id="gambler",
    display_name="Con Bạc",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=True,
    description="Mỗi đêm (ngoại trừ đêm 1), chọn một người ngẫu nhiên: nếu là Sói, Sói chết; nếu không phải, Con Bạc chết.",
))

DRUNKARD = register_role(RoleDef(
    role_id="drunkard",
    display_name="Bợm Nhậu",
    faction=Faction.VILLAGE,
    faction_goal=VILLAGE_GOAL,
    has_night_action=False,
    description="Dân thường bình thường; từ đêm thứ 2 trở đi, có xác suất ngẫu nhiên để 'tỉnh rượu' và nhận một vai trò ngẫu nhiên mới.",
))
