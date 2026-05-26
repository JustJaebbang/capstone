LABEL_MAP = {
    ("연기", "positive"): "연기가 좋아요",
    ("연기", "negative"): "연기가 아쉬워요",
    ("캐릭터", "positive"): "캐릭터가 매력적이에요",
    ("캐릭터", "negative"): "캐릭터가 아쉬워요",
    ("스토리", "positive"): "스토리가 좋아요",
    ("스토리", "negative"): "스토리가 아쉬워요",
    ("연출", "positive"): "연출이 좋아요",
    ("연출", "negative"): "연출이 아쉬워요",
    ("영상미", "positive"): "영상미가 좋아요",
    ("영상미", "negative"): "영상미가 아쉬워요",
    ("음향", "positive"): "음향이 좋아요",
    ("음향", "negative"): "음향이 아쉬워요",
    ("속도감", "positive"): "전개 속도감이 좋아요",
    ("속도감", "negative"): "전개가 늘어져요",
    ("재미", "positive"): "재미있어요",
    ("재미", "negative"): "재미가 아쉬워요",
    ("몰입감", "positive"): "몰입감이 높아요",
    ("몰입감", "negative"): "몰입감이 떨어져요",
    ("감정", "positive"): "감정적으로 와닿아요",
    ("감정", "negative"): "감정선이 아쉬워요",
    ("메시지", "positive"): "메시지가 인상적이에요",
    ("메시지", "negative"): "메시지가 아쉬워요",
    ("기타", "positive"): "긍정적인 반응이 있어요",
    ("기타", "negative"): "아쉬운 반응이 있어요",
}


def make_label(topic: str, sentiment: str) -> str:
    return LABEL_MAP.get((topic, sentiment), f"{topic} ({sentiment})")
