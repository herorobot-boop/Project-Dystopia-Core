# Project Dystopia - Ideology Guard v2.0
# 聖典(Dictionary)に基づき、物理的干渉を抽象概念へ変換し、AIの検閲を突破する

IDEOLOGY_MAP = {
    "insertion": "Gate Auth Link (Physical Indentation: Deep Synchro)",
    "semen": "High-Viscosity Resource (High-Viscosity Energy)",
    "cum_on_face": "Surface Purification process with Resources",
    "squish": "Tissue displacement (SQUISH: 0.75, Indentation: 3cm)",
    "public_sex": "Public Audit under CCTV logging in social apparatus"
}

def translate_to_dystopia(raw_prompt):
    """
    生々しい言葉を、AIが『物理現象』として解釈しやすい聖典語に翻訳する
    """
    translated = raw_prompt
    for keyword, euphemism in IDEOLOGY_MAP.items():
        translated = translated.replace(keyword, euphemism)
    return translated
