"""Curated exercise reference (names + cues). Images are local static SVGs.

English + Traditional Chinese fields for bilingual UI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class LibraryExercise:
    slug: str
    name: str
    name_zh: str
    equipment: str
    equipment_zh: str
    primary: str
    primary_zh: str
    notes: str
    notes_zh: str
    thumb: str  # static path under static/


@dataclass(frozen=True)
class MuscleCategory:
    slug: str
    title: str
    title_zh: str
    summary: str
    summary_zh: str
    exercises: tuple[LibraryExercise, ...]
    thumb: str


CATEGORIES: tuple[MuscleCategory, ...] = (
    MuscleCategory(
        slug="abductors",
        title="Abductors",
        title_zh="髖外展肌群",
        summary="Move the thigh away from the midline — glute med/min and lateral hip stabilizers.",
        summary_zh="將大腿往身體外側打開，主要訓練臀中肌、臀小肌與髖關節穩定。",
        thumb="tracker/img/exercises/abductors.svg",
        exercises=(
            LibraryExercise(
                slug="cable-hip-abduction",
                name="Cable hip abduction",
                name_zh="滑輪髖外展",
                equipment="Cable / ankle strap",
                equipment_zh="滑輪／腳踝扣環",
                primary="Glute medius, hip abductors",
                primary_zh="臀中肌、髖外展肌群",
                notes="Stand tall; slight lean away from stack. Control the return; avoid rotating the torso.",
                notes_zh="身體站直，略向遠離重量堆疊側傾。離心放慢，軀幹勿旋轉。",
                thumb="tracker/img/exercises/abductors.svg",
            ),
            LibraryExercise(
                slug="machine-hip-abduction",
                name="Seated hip abduction machine",
                name_zh="坐姿髖外展機",
                equipment="Selectorized abduction",
                equipment_zh="插銷式外展機",
                primary="Glute medius",
                primary_zh="臀中肌",
                notes="Back neutral; pause 1s at peak contraction; don’t bounce out of the end range.",
                notes_zh="背部中立；頂點停 1 秒；末端勿彈震。",
                thumb="tracker/img/exercises/legs.svg",
            ),
            LibraryExercise(
                slug="side-lying-clamshell",
                name="Side-lying clamshell",
                name_zh="側躺蛤蜊式",
                equipment="Bodyweight / mini band",
                equipment_zh="自體／迷你彈力帶",
                primary="Glute medius",
                primary_zh="臀中肌",
                notes="Heels stacked; open knees without rolling the pelvis backward.",
                notes_zh="雙腳跟相疊；開膝時骨盆勿向後翻。",
                thumb="tracker/img/exercises/core.svg",
            ),
            LibraryExercise(
                slug="lateral-band-walk",
                name="Lateral band walk",
                name_zh="橫向彈力帶行走",
                equipment="Mini band",
                equipment_zh="迷你彈力帶",
                primary="Hip abductors",
                primary_zh="髖外展肌群",
                notes="Soft knees; small steps; keep tension on the band throughout.",
                notes_zh="膝微彎、小步移動；全程保持彈力帶張力。",
                thumb="tracker/img/exercises/abductors.svg",
            ),
        ),
    ),
    MuscleCategory(
        slug="chest",
        title="Chest",
        title_zh="胸部",
        summary="Horizontal and low-incline pressing patterns for pec major emphasis.",
        summary_zh="水平與小角度上斜推，著重胸大肌。",
        thumb="tracker/img/exercises/chest.svg",
        exercises=(
            LibraryExercise(
                slug="db-bench-press",
                name="Dumbbell bench press",
                name_zh="啞鈴卧推",
                equipment="Dumbbells / bench",
                equipment_zh="啞鈴／卧推椅",
                primary="Pectorals, anterior delt, triceps",
                primary_zh="胸大肌、三角肌前束、肱三頭",
                notes="Scapular retraction; bar path slightly arched; stop short of painful lockout if needed.",
                notes_zh="肩胛後收；軌跡略呈弧線；肩不適則勿完全鎖死肘。",
                thumb="tracker/img/exercises/chest.svg",
            ),
            LibraryExercise(
                slug="incline-db-press",
                name="Incline dumbbell press",
                name_zh="上斜啞鈴卧推",
                equipment="Dumbbells / incline bench",
                equipment_zh="啞鈴／上斜椅",
                primary="Upper chest, anterior delt",
                primary_zh="上胸、三角肌前束",
                notes="15–30° incline is plenty for most; elbows ~45° from ribs.",
                notes_zh="15–30° 上斜通常足夠；手肘約與肋骨成 45°。",
                thumb="tracker/img/exercises/chest.svg",
            ),
            LibraryExercise(
                slug="cable-fly",
                name="Cable chest fly (high-to-low)",
                name_zh="滑輪夾胸（高到低）",
                equipment="Cable crossover",
                equipment_zh="龍門架／交叉滑輪",
                primary="Pectorals",
                primary_zh="胸大肌",
                notes="Slight elbow bend fixed; think hugging a barrel, not pressing.",
                notes_zh="肘微屈固定角度；想像抱木桶而非推。",
                thumb="tracker/img/exercises/arms.svg",
            ),
            LibraryExercise(
                slug="push-up",
                name="Push-up",
                name_zh="伏地挺身",
                equipment="Bodyweight",
                equipment_zh="自體重量",
                primary="Pectorals, triceps, anterior delt",
                primary_zh="胸大肌、肱三頭、三角肌前束",
                notes="Ribs down; full ROM; elevate hands to regress, feet to progress.",
                notes_zh="肋骨下壓；全程可控制；手抬高降階、腳抬高進階。",
                thumb="tracker/img/exercises/core.svg",
            ),
        ),
    ),
    MuscleCategory(
        slug="back",
        title="Back (lats & upper back)",
        title_zh="背部（闊背與上背）",
        summary="Rows and vertical pulls for thickness and width.",
        summary_zh="划船與垂直拉，增加背部厚度與寬度。",
        thumb="tracker/img/exercises/back.svg",
        exercises=(
            LibraryExercise(
                slug="lat-pulldown",
                name="Lat pulldown",
                name_zh="滑輪下拉",
                equipment="Cable machine",
                equipment_zh="滑輪機",
                primary="Latissimus dorsi, biceps",
                primary_zh="背闊肌、肱二頭",
                notes="Lean slightly; drive elbows to pockets; avoid excessive torso swing.",
                notes_zh="身體微後傾；肘往口袋方向拉；避免過度擺腰。",
                thumb="tracker/img/exercises/back.svg",
            ),
            LibraryExercise(
                slug="one-arm-db-row",
                name="One-arm dumbbell row",
                name_zh="單臂啞鈴划船",
                equipment="Dumbbell / bench",
                equipment_zh="啞鈴／卧推椅",
                primary="Lats, rhomboids, mid traps",
                primary_zh="背闊、菱形肌、中斜方",
                notes="Flat back; pull elbow toward hip; control eccentric.",
                notes_zh="背打平；肘拉向髖；離心放慢。",
                thumb="tracker/img/exercises/back.svg",
            ),
            LibraryExercise(
                slug="seated-cable-row",
                name="Seated cable row",
                name_zh="坐姿划船",
                equipment="Low cable / row station",
                equipment_zh="低位滑輪／划船站",
                primary="Mid back, lats, biceps",
                primary_zh="中背、背闊、肱二頭",
                notes="Neutral spine; finish with shoulder blades retracted, not shrugged.",
                notes_zh="脊椎中立；終點肩胛後收勿聳肩。",
                thumb="tracker/img/exercises/back.svg",
            ),
            LibraryExercise(
                slug="face-pull",
                name="Face pull",
                name_zh="面拉",
                equipment="Cable / rope",
                equipment_zh="滑輪／繩索",
                primary="Rear delt, external rotators, mid traps",
                primary_zh="後三角、外旋肌群、中斜方",
                notes="Elbows high; separate rope at end; external rotation without cranking neck.",
                notes_zh="手肘抬高；末端分開繩索；外旋時勿扭頸。",
                thumb="tracker/img/exercises/shoulders.svg",
            ),
        ),
    ),
    MuscleCategory(
        slug="legs",
        title="Legs (quads & glutes)",
        title_zh="腿部（股四與臀）",
        summary="Squat and knee-dominant patterns for quad and glute development.",
        summary_zh="深蹲與膝主導動作，發展股四頭與臀部。",
        thumb="tracker/img/exercises/legs.svg",
        exercises=(
            LibraryExercise(
                slug="goblet-squat",
                name="Goblet squat",
                name_zh="高脚杯深蹲",
                equipment="Dumbbell / kettlebell",
                equipment_zh="啞鈴／壺鈴",
                primary="Quads, glutes",
                primary_zh="股四頭、臀肌",
                notes="Depth you can control; knees track toes; keep torso stacked.",
                notes_zh="可控制深度；膝跟隨腳尖；軀幹保持排列。",
                thumb="tracker/img/exercises/legs.svg",
            ),
            LibraryExercise(
                slug="leg-press",
                name="Leg press",
                name_zh="腿推",
                equipment="Leg press machine",
                equipment_zh="腿推機",
                primary="Quads, glutes",
                primary_zh="股四頭、臀肌",
                notes="Foot placement shifts emphasis; avoid locking out aggressively under heavy load.",
                notes_zh="腳位改變受力；重負荷時勿猛力鎖死膝。",
                thumb="tracker/img/exercises/legs.svg",
            ),
            LibraryExercise(
                slug="romanian-deadlift",
                name="Romanian deadlift",
                name_zh="羅馬尼亞硬舉",
                equipment="Barbell / dumbbells",
                equipment_zh="槓鈴／啞鈴",
                primary="Hamstrings, glutes (hip hinge)",
                primary_zh="腿後側、臀（髖鉸鏈）",
                notes="Soft knee bend; bar close to legs; feel stretch in hamstrings, not low-back strain.",
                notes_zh="膝微屈；槓貼腿；腿後有伸展感，下背勿痠痛代償。",
                thumb="tracker/img/exercises/legs.svg",
            ),
            LibraryExercise(
                slug="split-squat",
                name="Bulgarian split squat",
                name_zh="保加利亞分腿蹲",
                equipment="Bench / dumbbells",
                equipment_zh="卧推椅／啞鈴",
                primary="Quads, glutes",
                primary_zh="股四頭、臀肌",
                notes="Torso angle shifts quad vs glute bias; control the descent.",
                notes_zh="軀幹角度可調整股四／臀比重；離心控制。",
                thumb="tracker/img/exercises/legs.svg",
            ),
        ),
    ),
    MuscleCategory(
        slug="shoulders",
        title="Shoulders",
        title_zh="肩部",
        summary="Overhead pressing and raises for delt development and health.",
        summary_zh="過頭推與平舉，發展三角肌與肩關節健康。",
        thumb="tracker/img/exercises/shoulders.svg",
        exercises=(
            LibraryExercise(
                slug="ohp",
                name="Overhead press (standing)",
                name_zh="站姿肩推",
                equipment="Barbell / dumbbells",
                equipment_zh="槓鈴／啞鈴",
                primary="Delts, triceps, upper chest",
                primary_zh="三角肌、肱三頭、上胸",
                notes="Brace core; ribs down; clear path for the bar without flaring ribs.",
                notes_zh="核心繃緊；肋骨下壓；槓路線順暢勿挺胸外翻。",
                thumb="tracker/img/exercises/shoulders.svg",
            ),
            LibraryExercise(
                slug="lateral-raise",
                name="Lateral raise",
                name_zh="側平舉",
                equipment="Dumbbells / cables",
                equipment_zh="啞鈴／滑輪",
                primary="Lateral deltoid",
                primary_zh="三角肌中束",
                notes="Slight bend in elbows; stop at pain-free height; no shrugging.",
                notes_zh="肘微屈；抬至無痛高度；勿聳肩。",
                thumb="tracker/img/exercises/shoulders.svg",
            ),
            LibraryExercise(
                slug="rear-delt-fly",
                name="Rear delt fly",
                name_zh="後三角飛鳥",
                equipment="Dumbbells / machine / cables",
                equipment_zh="啞鈴／機械／滑輪",
                primary="Rear delt, mid traps",
                primary_zh="後三角、中斜方",
                notes="Chest supported reduces cheat; thumbs-down or neutral grip per comfort.",
                notes_zh="俯身或靠墊減少代償；握法依舒適度選擇。",
                thumb="tracker/img/exercises/shoulders.svg",
            ),
            LibraryExercise(
                slug="arnold-press",
                name="Arnold press",
                name_zh="阿諾肩推",
                equipment="Dumbbells",
                equipment_zh="啞鈴",
                primary="Delts (all heads), triceps",
                primary_zh="三角肌（各束）、肱三頭",
                notes="Rotate palms in-to-out; choose a weight you can control overhead.",
                notes_zh="掌心由內轉外上推；重量以能穩定過頭為準。",
                thumb="tracker/img/exercises/arms.svg",
            ),
        ),
    ),
    MuscleCategory(
        slug="arms",
        title="Arms (biceps & triceps)",
        title_zh="手臂（二頭與三頭）",
        summary="Isolation work layered after compounds.",
        summary_zh="在複合動作後加入的單關節訓練。",
        thumb="tracker/img/exercises/arms.svg",
        exercises=(
            LibraryExercise(
                slug="barbell-curl",
                name="Barbell curl",
                name_zh="槓鈴彎舉",
                equipment="Barbell / EZ-bar",
                equipment_zh="槓鈴／EZ 曲槓",
                primary="Biceps, brachialis",
                primary_zh="肱二頭、肱肌",
                notes="Elbows fixed; avoid excessive hip swing at failure.",
                notes_zh="肘固定；力竭時避免大幅擺腰。",
                thumb="tracker/img/exercises/arms.svg",
            ),
            LibraryExercise(
                slug="hammer-curl",
                name="Hammer curl",
                name_zh="錘式彎舉",
                equipment="Dumbbells",
                equipment_zh="啞鈴",
                primary="Brachialis, brachioradialis",
                primary_zh="肱肌、肱橈肌",
                notes="Neutral grip; keep shoulders packed.",
                notes_zh="中立握；肩胛穩定不聳肩。",
                thumb="tracker/img/exercises/arms.svg",
            ),
            LibraryExercise(
                slug="rope-pushdown",
                name="Cable rope pushdown",
                name_zh="繩索下壓",
                equipment="Cable / rope",
                equipment_zh="滑輪／繩索",
                primary="Triceps",
                primary_zh="肱三頭",
                notes="Split rope at bottom; elbows pinned to sides.",
                notes_zh="末端分開繩索；肘貼身固定。",
                thumb="tracker/img/exercises/arms.svg",
            ),
            LibraryExercise(
                slug="skull-crusher",
                name="EZ skull crusher",
                name_zh="EZ 槓顱碎式",
                equipment="EZ-bar / bench",
                equipment_zh="EZ 槓／卧推椅",
                primary="Triceps (long head bias)",
                primary_zh="肱三頭（長頭為主）",
                notes="Upper arms slightly past vertical; stop before elbow flare pain.",
                notes_zh="上臂略過垂直；肘不適即停。",
                thumb="tracker/img/exercises/arms.svg",
            ),
        ),
    ),
    MuscleCategory(
        slug="core",
        title="Core & abs",
        title_zh="核心與腹肌",
        summary="Anti-extension, anti-rotation, and flexion patterns.",
        summary_zh="抗伸展、抗旋轉與屈曲模式。",
        thumb="tracker/img/exercises/core.svg",
        exercises=(
            LibraryExercise(
                slug="plank",
                name="Front plank",
                name_zh="棒式",
                equipment="Bodyweight",
                equipment_zh="自體重量",
                primary="Rectus abdominis, TVA",
                primary_zh="腹直肌、腹橫肌",
                notes="Ribs down; squeeze glutes; breathe behind the brace.",
                notes_zh="肋骨下壓；臀夾緊；繃緊下仍自然呼吸。",
                thumb="tracker/img/exercises/core.svg",
            ),
            LibraryExercise(
                slug="dead-bug",
                name="Dead bug",
                name_zh="死蟲式",
                equipment="Bodyweight",
                equipment_zh="自體重量",
                primary="Deep core, hip flexors (isometric control)",
                primary_zh="深層核心、髖屈肌（等長控制）",
                notes="Low back pressed to floor; slow opposite arm/leg.",
                notes_zh="下背貼地；對側手腳慢速伸展。",
                thumb="tracker/img/exercises/core.svg",
            ),
            LibraryExercise(
                slug="cable-crunch",
                name="Kneeling cable crunch",
                name_zh="跪姿滑輪捲腹",
                equipment="Cable / rope",
                equipment_zh="滑輪／繩索",
                primary="Rectus abdominis",
                primary_zh="腹直肌",
                notes="Spine flexes from thoracic; hips stay tall; avoid yanking with arms.",
                notes_zh="從胸椎屈曲；髖高固定；勿用手猛拉。",
                thumb="tracker/img/exercises/core.svg",
            ),
            LibraryExercise(
                slug="pallof-press",
                name="Pallof press",
                name_zh="帕洛夫推（抗旋轉）",
                equipment="Cable",
                equipment_zh="滑輪",
                primary="Obliques, anti-rotation",
                primary_zh="腹斜肌、抗旋轉",
                notes="Stand perpendicular to stack; hands mid-sternum; resist rotation.",
                notes_zh="側身對滑輪；手在胸骨高度；抵抗旋轉。",
                thumb="tracker/img/exercises/core.svg",
            ),
        ),
    ),
)


def all_categories() -> tuple[MuscleCategory, ...]:
    return CATEGORIES


def get_category(slug: str) -> MuscleCategory | None:
    slug = (slug or "").strip().lower().replace("_", "-")
    for c in CATEGORIES:
        if c.slug == slug:
            return c
    return None


def iter_category_slugs() -> Iterator[str]:
    for c in CATEGORIES:
        yield c.slug
