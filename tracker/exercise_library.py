"""Curated exercise reference (names + cues). Images are local static SVGs.

This is not a scrape of third-party sites; thumbnails are simple icons shipped
with the repo. Add more entries by extending ``CATEGORIES``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class LibraryExercise:
    slug: str
    name: str
    equipment: str
    primary: str
    notes: str
    thumb: str  # static path under static/, e.g. tracker/img/exercises/abductors.svg


@dataclass(frozen=True)
class MuscleCategory:
    slug: str
    title: str
    summary: str
    exercises: tuple[LibraryExercise, ...]
    thumb: str  # static path for category hero card


CATEGORIES: tuple[MuscleCategory, ...] = (
    MuscleCategory(
        slug="abductors",
        title="Abductors",
        summary="Move the thigh away from the midline — glute med/min and lateral hip stabilizers.",
        thumb="tracker/img/exercises/abductors.svg",
        exercises=(
            LibraryExercise(
                slug="cable-hip-abduction",
                name="Cable hip abduction",
                equipment="Cable / ankle strap",
                primary="Glute medius, hip abductors",
                notes="Stand tall; slight lean away from stack. Control the return; avoid rotating the torso.",
                thumb="tracker/img/exercises/abductors.svg",
            ),
            LibraryExercise(
                slug="machine-hip-abduction",
                name="Seated hip abduction machine",
                equipment="Selectorized abduction",
                primary="Glute medius",
                notes="Back neutral; pause 1s at peak contraction; don’t bounce out of the end range.",
                thumb="tracker/img/exercises/legs.svg",
            ),
            LibraryExercise(
                slug="side-lying-clamshell",
                name="Side-lying clamshell",
                equipment="Bodyweight / mini band",
                primary="Glute medius",
                notes="Heels stacked; open knees without rolling the pelvis backward.",
                thumb="tracker/img/exercises/core.svg",
            ),
            LibraryExercise(
                slug="lateral-band-walk",
                name="Lateral band walk",
                equipment="Mini band",
                primary="Hip abductors",
                notes="Soft knees; small steps; keep tension on the band throughout.",
                thumb="tracker/img/exercises/abductors.svg",
            ),
        ),
    ),
    MuscleCategory(
        slug="chest",
        title="Chest",
        summary="Horizontal and low-incline pressing patterns for pec major emphasis.",
        thumb="tracker/img/exercises/chest.svg",
        exercises=(
            LibraryExercise(
                slug="db-bench-press",
                name="Dumbbell bench press",
                equipment="Dumbbells / bench",
                primary="Pectorals, anterior delt, triceps",
                notes="Scapular retraction; bar path slightly arched; stop short of painful lockout if needed.",
                thumb="tracker/img/exercises/chest.svg",
            ),
            LibraryExercise(
                slug="incline-db-press",
                name="Incline dumbbell press",
                equipment="Dumbbells / incline bench",
                primary="Upper chest, anterior delt",
                notes="15–30° incline is plenty for most; elbows ~45° from ribs.",
                thumb="tracker/img/exercises/chest.svg",
            ),
            LibraryExercise(
                slug="cable-fly",
                name="Cable chest fly (high-to-low)",
                equipment="Cable crossover",
                primary="Pectorals",
                notes="Slight elbow bend fixed; think hugging a barrel, not pressing.",
                thumb="tracker/img/exercises/arms.svg",
            ),
            LibraryExercise(
                slug="push-up",
                name="Push-up",
                equipment="Bodyweight",
                primary="Pectorals, triceps, anterior delt",
                notes="Ribs down; full ROM; elevate hands to regress, feet to progress.",
                thumb="tracker/img/exercises/core.svg",
            ),
        ),
    ),
    MuscleCategory(
        slug="back",
        title="Back (lats & upper back)",
        summary="Rows and vertical pulls for thickness and width.",
        thumb="tracker/img/exercises/back.svg",
        exercises=(
            LibraryExercise(
                slug="lat-pulldown",
                name="Lat pulldown",
                equipment="Cable machine",
                primary="Latissimus dorsi, biceps",
                notes="Lean slightly; drive elbows to pockets; avoid excessive torso swing.",
                thumb="tracker/img/exercises/back.svg",
            ),
            LibraryExercise(
                slug="one-arm-db-row",
                name="One-arm dumbbell row",
                equipment="Dumbbell / bench",
                primary="Lats, rhomboids, mid traps",
                notes="Flat back; pull elbow toward hip; control eccentric.",
                thumb="tracker/img/exercises/back.svg",
            ),
            LibraryExercise(
                slug="seated-cable-row",
                name="Seated cable row",
                equipment="Low cable / row station",
                primary="Mid back, lats, biceps",
                notes="Neutral spine; finish with shoulder blades retracted, not shrugged.",
                thumb="tracker/img/exercises/back.svg",
            ),
            LibraryExercise(
                slug="face-pull",
                name="Face pull",
                equipment="Cable / rope",
                primary="Rear delt, external rotators, mid traps",
                notes="Elbows high; separate rope at end; external rotation without cranking neck.",
                thumb="tracker/img/exercises/shoulders.svg",
            ),
        ),
    ),
    MuscleCategory(
        slug="legs",
        title="Legs (quads & glutes)",
        summary="Squat and knee-dominant patterns for quad and glute development.",
        thumb="tracker/img/exercises/legs.svg",
        exercises=(
            LibraryExercise(
                slug="goblet-squat",
                name="Goblet squat",
                equipment="Dumbbell / kettlebell",
                primary="Quads, glutes",
                notes="Depth you can control; knees track toes; keep torso stacked.",
                thumb="tracker/img/exercises/legs.svg",
            ),
            LibraryExercise(
                slug="leg-press",
                name="Leg press",
                equipment="Leg press machine",
                primary="Quads, glutes",
                notes="Foot placement shifts emphasis; avoid locking out aggressively under heavy load.",
                thumb="tracker/img/exercises/legs.svg",
            ),
            LibraryExercise(
                slug="romanian-deadlift",
                name="Romanian deadlift",
                equipment="Barbell / dumbbells",
                primary="Hamstrings, glutes (hip hinge)",
                notes="Soft knee bend; bar close to legs; feel stretch in hamstrings, not low-back strain.",
                thumb="tracker/img/exercises/legs.svg",
            ),
            LibraryExercise(
                slug="split-squat",
                name="Bulgarian split squat",
                equipment="Bench / dumbbells",
                primary="Quads, glutes",
                notes="Torso angle shifts quad vs glute bias; control the descent.",
                thumb="tracker/img/exercises/legs.svg",
            ),
        ),
    ),
    MuscleCategory(
        slug="shoulders",
        title="Shoulders",
        summary="Overhead pressing and raises for delt development and health.",
        thumb="tracker/img/exercises/shoulders.svg",
        exercises=(
            LibraryExercise(
                slug="ohp",
                name="Overhead press (standing)",
                equipment="Barbell / dumbbells",
                primary="Delts, triceps, upper chest",
                notes="Brace core; ribs down; clear path for the bar without flaring ribs.",
                thumb="tracker/img/exercises/shoulders.svg",
            ),
            LibraryExercise(
                slug="lateral-raise",
                name="Lateral raise",
                equipment="Dumbbells / cables",
                primary="Lateral deltoid",
                notes="Slight bend in elbows; stop at pain-free height; no shrugging.",
                thumb="tracker/img/exercises/shoulders.svg",
            ),
            LibraryExercise(
                slug="rear-delt-fly",
                name="Rear delt fly",
                equipment="Dumbbells / machine / cables",
                primary="Rear delt, mid traps",
                notes="Chest supported reduces cheat; thumbs-down or neutral grip per comfort.",
                thumb="tracker/img/exercises/shoulders.svg",
            ),
            LibraryExercise(
                slug="arnold-press",
                name="Arnold press",
                equipment="Dumbbells",
                primary="Delts (all heads), triceps",
                notes="Rotate palms in-to-out; choose a weight you can control overhead.",
                thumb="tracker/img/exercises/arms.svg",
            ),
        ),
    ),
    MuscleCategory(
        slug="arms",
        title="Arms (biceps & triceps)",
        summary="Isolation work layered after compounds.",
        thumb="tracker/img/exercises/arms.svg",
        exercises=(
            LibraryExercise(
                slug="barbell-curl",
                name="Barbell curl",
                equipment="Barbell / EZ-bar",
                primary="Biceps, brachialis",
                notes="Elbows fixed; avoid excessive hip swing at failure.",
                thumb="tracker/img/exercises/arms.svg",
            ),
            LibraryExercise(
                slug="hammer-curl",
                name="Hammer curl",
                equipment="Dumbbells",
                primary="Brachialis, brachioradialis",
                notes="Neutral grip; keep shoulders packed.",
                thumb="tracker/img/exercises/arms.svg",
            ),
            LibraryExercise(
                slug="rope-pushdown",
                name="Cable rope pushdown",
                equipment="Cable / rope",
                primary="Triceps",
                notes="Split rope at bottom; elbows pinned to sides.",
                thumb="tracker/img/exercises/arms.svg",
            ),
            LibraryExercise(
                slug="skull-crusher",
                name="EZ skull crusher",
                equipment="EZ-bar / bench",
                primary="Triceps (long head bias)",
                notes="Upper arms slightly past vertical; stop before elbow flare pain.",
                thumb="tracker/img/exercises/arms.svg",
            ),
        ),
    ),
    MuscleCategory(
        slug="core",
        title="Core & abs",
        summary="Anti-extension, anti-rotation, and flexion patterns.",
        thumb="tracker/img/exercises/core.svg",
        exercises=(
            LibraryExercise(
                slug="plank",
                name="Front plank",
                equipment="Bodyweight",
                primary="Rectus abdominis, TVA",
                notes="Ribs down; squeeze glutes; breathe behind the brace.",
                thumb="tracker/img/exercises/core.svg",
            ),
            LibraryExercise(
                slug="dead-bug",
                name="Dead bug",
                equipment="Bodyweight",
                primary="Deep core, hip flexors (isometric control)",
                notes="Low back pressed to floor; slow opposite arm/leg.",
                thumb="tracker/img/exercises/core.svg",
            ),
            LibraryExercise(
                slug="cable-crunch",
                name="Kneeling cable crunch",
                equipment="Cable / rope",
                primary="Rectus abdominis",
                notes="Spine flexes from thoracic; hips stay tall; avoid yanking with arms.",
                thumb="tracker/img/exercises/core.svg",
            ),
            LibraryExercise(
                slug="pallof-press",
                name="Pallof press",
                equipment="Cable",
                primary="Obliques, anti-rotation",
                notes="Stand perpendicular to stack; hands mid-sternum; resist rotation.",
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
