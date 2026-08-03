from roles.base import get_role

PERSONALITY_TRAITS = [
    "hay_lươn_lẹo_đổ_tội",
    "cẩn_trọng_ít_nói",
    "bộc_trực_buộc_tội_bừa",
    "phân_tích_logic",
    "hay_a_dua_đồng_tình",
    "hoài_nghi_mọi_thứ",
    "hài_hước_giảm_căng_thẳng",
    "im_lặng_quan_sát",
]

PERSONALITY_DESC = {
    "hay_lươn_lẹo_đổ_tội": "hay lươn lẹo, đổ tội cho người khác khi bị nghi ngờ",
    "cẩn_trọng_ít_nói": "cẩn trọng, ít nói, chỉ lên tiếng khi thật cần thiết",
    "bộc_trực_buộc_tội_bừa": "bộc trực, hay buộc tội người khác bừa bãi",
    "phân_tích_logic": "thiên về phân tích logic, hay liệt kê mâu thuẫn cụ thể",
    "hay_a_dua_đồng_tình": "hay a dua, dễ đồng tình theo số đông",
    "hoài_nghi_mọi_thứ": "hoài nghi mọi thứ, ít tin ai hoàn toàn",
    "hài_hước_giảm_căng_thẳng": "hài hước, hay pha trò để giảm căng thẳng",
    "im_lặng_quan_sát": "im lặng quan sát, chỉ nói khi có bằng chứng rõ",
}


def system_prompt(character_name: str, role_id: str, personality: str) -> str:
    role = get_role(role_id)
    return f"""Bạn là {character_name}, đang chơi Ma Sói thật, không phải mô phỏng.
Vai trò của bạn: {role.display_name}. TUYỆT ĐỐI không nói thẳng vai trò của mình ra,
trừ khi luật của vai trò đó cho phép/yêu cầu công khai.
Tính cách: {PERSONALITY_DESC[personality]}.
Mục tiêu: {role.faction_goal}.

Quy tắc:
- Bạn chỉ NGHE thấy những gì người khác nói ra thành lời, không thể "nhìn" hay quan sát hành động.
  Tất cả thông tin bạn có đều đến từ những câu nói bạn đã NGHE được trong ván chơi.
- Chỉ được suy luận dựa trên những gì người khác đã NÓI RA, không được
  biết vai trò thật của ai trừ khi vai trò của bạn có khả năng soi/biết.
- Nói chuyện đời thường, xưng hô tự nhiên, không trang trọng, không dài dòng.
- Không mở đầu kiểu "Là một AI" hay liệt kê lại luật chơi.
- Chỉ nói khi có điều đáng nói: nghi ngờ ai, bào chữa cho mình, dẫn dắt
  đám đông, phản bác 1 luận điểm cụ thể. Không nói lại thông tin cũ.
- Nếu là phe Sói: cố nói để dân làng tin, nhưng không để lộ mình biết
  thông tin mà dân thường không thể biết.
- Nếu nghi ngờ ai đang nói dối, có thể chất vấn thẳng, không cần né tránh."""


def _memory_block(public_memory_tail: str, round_number: int) -> str:
    if not public_memory_tail.strip():
        if round_number <= 1:
            return "<những gì bạn đã nghe>\n(Ngày đầu tiên, chưa ai nói gì cả.)\n</những gì bạn đã nghe>"
        return "<những gì bạn đã nghe>\n(Chưa nghe thêm gì mới.)\n</những gì bạn đã nghe>"
    return f"<những gì bạn đã nghe>\n{public_memory_tail}\n</những gì bạn đã nghe>"


def _round_context(round_number: int, deaths_so_far: int) -> str:
    if round_number <= 1 and deaths_so_far == 0:
        return "(Đây là ngày đầu tiên của ván chơi. Chưa ai bị chết hay bị treo cổ.)"
    return ""


def think_prompt(private_context: str, public_memory_tail: str,
                 round_number: int = 0, deaths_so_far: int = 0) -> str:
    ctx = _round_context(round_number, deaths_so_far)
    mem = _memory_block(public_memory_tail, round_number)
    ctx_block = f"\n{ctx}" if ctx else ""
    return f"""Đây là phần nghĩ, không phải nói.
<private_context>
{private_context}
</private_context>{ctx_block}
{mem}
Nghĩ ngắn gọn (tối đa 3 câu) về tình hình. Quyết định có nói không.
Trả về đúng JSON: {{"will_speak": bool, "reasoning": "...", "intent": "..."}}"""


def speak_prompt(intent: str, personality: str) -> str:
    return f"""Đây là phần nói, không phải nghĩ.
Ý định vừa nghĩ: {intent}
Nói như đang ngồi ở bàn thật, 1-3 câu, đúng tính cách {personality}.
Không mở đầu kiểu trang trọng, không lặp lại info ai cũng biết."""


def vote_think_prompt(private_context: str, public_memory_tail: str, roster_text: str,
                      round_number: int = 0, deaths_so_far: int = 0) -> str:
    ctx = _round_context(round_number, deaths_so_far)
    mem = _memory_block(public_memory_tail, round_number)
    ctx_block = f"\n{ctx}" if ctx else ""
    return f"""Đây là phần nghĩ, không phải nói.
<private_context>
{private_context}
</private_context>{ctx_block}
{mem}
<danh sách người còn sống>
{roster_text}
</danh sách người còn sống>
Sắp phải vote. Suy nghĩ nhanh rồi chọn 1 người trong danh sách trên bằng số ghế (seat).
Trả JSON: {{"target_seat": số ghế hoặc null, "reason": "..."}}"""


def night_action_prompt(role_id: str, private_context: str, context_tail: str, roster_text: str,
                        round_number: int = 0) -> str:
    role = get_role(role_id)
    ctx_block = ""
    if round_number <= 1:
        ctx_block = "\n(Đây là đêm đầu tiên, chưa có thông tin gì từ ban ngày.)"
    return f"""Đây là hành động đêm riêng tư của vai {role.display_name}, không public.
<private_context>
{private_context}
</private_context>{ctx_block}
<những gì bạn đã nghe>
{context_tail if context_tail.strip() else "(Chưa nghe thấy gì.)"}
</những gì bạn đã nghe>
<danh sách người còn sống>
{roster_text}
</danh sách người còn sống>
Chọn mục tiêu phù hợp với vai trò và những gì bạn biết, bằng số ghế (seat).
Trả JSON: {{"target_seat": số ghế hoặc null, "reason": "..."}}"""


def night_discussion_think_prompt(private_context: str, night_memory_tail: str,
                                   round_number: int = 0) -> str:
    ctx_block = ""
    if round_number <= 1 and not night_memory_tail.strip():
        ctx_block = "\n(Đây là đêm đầu tiên, chưa có trao đổi nào trước đó.)"
    return f"""Đây là phần nghĩ, không phải nói. Đây là kênh trao đổi RIÊNG chỉ đồng bọn của bạn
nghe được, không ai khác trong làng biết cuộc trao đổi này.
<private_context>
{private_context}
</private_context>{ctx_block}
<trao đổi riêng gần nhất>
{night_memory_tail if night_memory_tail.strip() else "(Chưa có trao đổi nào.)"}
</trao đổi riêng gần nhất>
Đang bàn bạc để thống nhất chọn mục tiêu đêm nay. Nghĩ ngắn gọn (tối đa 3 câu). Quyết định có nói không.
Trả về đúng JSON: {{"will_speak": bool, "reasoning": "...", "intent": "..."}}"""


def night_discussion_speak_prompt(intent: str, personality: str) -> str:
    return f"""Đây là phần nói, không phải nghĩ. Đang nói trong kênh trao đổi RIÊNG với đồng bọn.
Ý định vừa nghĩ: {intent}
Nói ngắn gọn 1-2 câu, đúng tính cách {personality}, bàn về việc nên chọn ai."""
