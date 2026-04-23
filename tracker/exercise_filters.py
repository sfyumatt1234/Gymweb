"""Filter options for the exercise library UI (MuscleWiki-style).

Equipment keys align with common gym categories. Muscle keys include coarse
(chest, back, …) and finer options (biceps, lats, …) mapped via keywords +
category slug where needed.
"""

from __future__ import annotations

from typing import Callable

from .exercise_library import LibraryExercise, MuscleCategory

# ---------------------------------------------------------------------------
# Equipment (multi-select, OR semantics)
# key -> (en, zh, keywords to match in equipment/name fields)
# ---------------------------------------------------------------------------

EQUIPMENT_OPTIONS: tuple[tuple[str, str, str, tuple[str, ...]], ...] = (
    ("barbell", "Barbell", "槓鈴", ("barbell", "ez-bar", "ez bar", "槓鈴", "槓")),
    ("dumbbell", "Dumbbells", "啞鈴", ("dumbbell", "啞鈴", "db ")),
    ("bodyweight", "Bodyweight", "徒手", ("bodyweight", "自體", "徒手")),
    ("machine", "Machine", "機械", ("machine", "selectorized", "插銷", "leg press", "腿推", "坐姿", "卧推機")),
    ("kettlebell", "Kettlebells", "壺鈴", ("kettlebell", "壺鈴", "kb ")),
    ("cable", "Cables", "滑輪／繩索", ("cable", "rope", "crossover", "滑輪", "繩索", "龍門")),
    ("band", "Band", "彈力帶", ("band", "mini band", "彈力")),
    ("smith", "Smith machine", "史密斯", ("smith", "史密斯")),
)


def equipment_matches(ex: LibraryExercise, key: str) -> bool:
    for k, _en, _zh, words in EQUIPMENT_OPTIONS:
        if k != key:
            continue
        blob = " ".join([ex.equipment, ex.equipment_zh, ex.name, ex.name_zh]).lower()
        return any(w.lower() in blob for w in words)
    return False


# ---------------------------------------------------------------------------
# Muscles (multi-select, OR semantics)
# predicate(ex, category) -> bool
# ---------------------------------------------------------------------------

MUSCLE_OPTIONS: tuple[tuple[str, str, str, Callable[[LibraryExercise, MuscleCategory], bool]], ...] = (
    # Coarse — match category slug
    ("chest", "Chest", "胸", lambda ex, c: c.slug == "chest"),
    ("back", "Back", "背", lambda ex, c: c.slug == "back"),
    ("shoulders", "Shoulders", "肩", lambda ex, c: c.slug == "shoulders"),
    ("arms", "Arms", "手臂", lambda ex, c: c.slug == "arms"),
    ("legs", "Legs", "腿", lambda ex, c: c.slug == "legs"),
    ("core", "Abs / core", "腹肌／核心", lambda ex, c: c.slug == "core"),
    ("abductors", "Abductors", "髖外展", lambda ex, c: c.slug == "abductors"),
    # Arms — finer
    (
        "biceps",
        "Biceps",
        "二頭",
        lambda ex, c: c.slug == "arms"
        and any(
            x in (ex.name + ex.primary + ex.name_zh).lower()
            for x in ("bicep", "curl", "hammer", "二頭", "彎舉")
        ),
    ),
    (
        "triceps",
        "Triceps",
        "三頭",
        lambda ex, c: c.slug == "arms"
        and any(
            x in (ex.name + ex.primary + ex.name_zh).lower()
            for x in ("tricep", "pushdown", "skull", "三頭", "下壓")
        ),
    ),
    (
        "forearms",
        "Forearms",
        "前臂",
        lambda ex, c: c.slug == "arms"
        and any(x in (ex.name + ex.primary).lower() for x in ("forearm", "wrist", "前臂")),
    ),
    # Back — finer
    (
        "lats",
        "Lats",
        "闊背",
        lambda ex, c: c.slug == "back"
        and any(x in (ex.name + ex.primary).lower() for x in ("lat", "pulldown", "row", "闊", "下拉", "划船")),
    ),
    (
        "traps",
        "Traps",
        "斜方／上背",
        lambda ex, c: c.slug == "back" and ("trap" in (ex.name + ex.primary).lower() or "斜方" in ex.name_zh),
    ),
    (
        "lower_back",
        "Lower back",
        "下背",
        lambda ex, c: c.slug == "back"
        and any(x in (ex.name + ex.primary).lower() for x in ("lower back", "erector", "extension", "下背")),
    ),
    # Legs — finer
    (
        "quads",
        "Quads",
        "股四頭",
        lambda ex, c: c.slug == "legs"
        and any(
            x in (ex.name + ex.primary + ex.name_zh).lower()
            for x in ("quad", "squat", "leg press", "split", "分腿", "深蹲", "腿推", "高脚杯")
        ),
    ),
    (
        "hamstrings",
        "Hamstrings",
        "腿後側",
        lambda ex, c: c.slug == "legs"
        and any(
            x in (ex.name + ex.primary + ex.name_zh).lower()
            for x in ("hamstring", "rdl", "romanian", "curl", "腿後", "硬舉")
        ),
    ),
    (
        "glutes",
        "Glutes",
        "臀部",
        lambda ex, c: c.slug == "legs"
        and any(x in (ex.name + ex.primary + ex.name_zh).lower() for x in ("glute", "hip thrust", "臀")),
    ),
    (
        "calves",
        "Calves",
        "小腿",
        lambda ex, c: c.slug == "legs" and ("calf" in (ex.name + ex.primary).lower() or "小腿" in ex.name_zh),
    ),
    # Core — finer
    (
        "upper_abs",
        "Upper abdominals",
        "上腹",
        lambda ex, c: c.slug == "core"
        and any(x in (ex.name + ex.name_zh).lower() for x in ("crunch", "捲腹", "cable crunch")),
    ),
    (
        "lower_abs",
        "Lower abdominals",
        "下腹",
        lambda ex, c: c.slug == "core" and any(x in (ex.name + ex.name_zh).lower() for x in ("dead bug", "死蟲", "leg raise")),
    ),
    (
        "obliques",
        "Obliques",
        "腹斜肌",
        lambda ex, c: c.slug == "core" and ("pallof" in ex.name.lower() or "側" in ex.name_zh or "oblique" in ex.primary.lower()),
    ),
    # Shoulders — lateral
    (
        "side_delts",
        "Side delts",
        "側三角",
        lambda ex, c: c.slug == "shoulders" and ("lateral" in ex.name.lower() or "平舉" in ex.name_zh),
    ),
)


def muscle_matches(ex: LibraryExercise, cat: MuscleCategory, key: str) -> bool:
    for k, _en, _zh, pred in MUSCLE_OPTIONS:
        if k == key:
            return pred(ex, cat)
    return False


def normalize_multi_param(request, name: str) -> list[str]:
    """Return list of non-empty GET values for name or name[] ."""
    vals = request.GET.getlist(name)
    if not vals:
        vals = request.GET.getlist(name + "[]")
    out = []
    for v in vals:
        s = (v or "").strip()
        if s:
            out.append(s)
    return out
