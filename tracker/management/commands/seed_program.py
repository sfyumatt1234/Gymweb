"""Seed a starter "Full Body 3x/week" program with rich instructions."""

from django.core.management.base import BaseCommand
from django.db import transaction

from tracker.models import Day, Exercise, Program


PROGRAM = {
    "name": "Full Body 3x/week",
    "description": (
        "A simple full-body template suitable for beginners and returning lifters. "
        "Run it on non-consecutive days (e.g. Mon/Wed/Fri). Aim for 1-2 reps in "
        "reserve on the last working set."
    ),
    "days": [
        {
            "name": "Day A",
            "exercises": [
                {
                    "name": "Back squat",
                    "target_sets": 3, "target_reps": "5-8", "rest_seconds": 150,
                    "setup": "Bar on upper traps, feet shoulder-width, toes slightly out.",
                    "execution": "Brace, sit between hips, knees track over toes, depth at or below parallel.",
                    "common_mistakes": "Knees collapsing inward, losing brace, heels lifting.",
                    "coaching_cue": "Spread the floor with your feet.",
                },
                {
                    "name": "Bench press",
                    "target_sets": 3, "target_reps": "5-8", "rest_seconds": 150,
                    "setup": "Eyes under bar, shoulder blades retracted, mild arch, feet planted.",
                    "execution": "Lower to lower chest with elbows ~45°, press up and slightly back.",
                    "common_mistakes": "Flared elbows, bouncing off chest.",
                    "coaching_cue": "Bend the bar.",
                },
                {
                    "name": "Bent-over row",
                    "target_sets": 3, "target_reps": "8-10", "rest_seconds": 120,
                    "setup": "Hinge ~45°, neutral spine, bar at knees.",
                    "execution": "Pull to lower ribs, squeeze scapulae, control eccentric.",
                    "common_mistakes": "Yanking with biceps, rounding the back.",
                    "coaching_cue": "Drive elbows back, not up.",
                },
                {
                    "name": "Plank",
                    "target_sets": 3, "target_reps": "30-60s", "rest_seconds": 60,
                    "setup": "Forearms under shoulders, glutes squeezed.",
                    "execution": "Long body line, breathe through the brace.",
                    "common_mistakes": "Hips sagging or piking.",
                    "coaching_cue": "Ribs down, abs tight.",
                },
            ],
        },
        {
            "name": "Day B",
            "exercises": [
                {
                    "name": "Romanian deadlift",
                    "target_sets": 3, "target_reps": "6-8", "rest_seconds": 150,
                    "setup": "Bar at hips, soft knees, neutral spine.",
                    "execution": "Push hips back, lower until you feel a strong hamstring stretch, drive hips forward.",
                    "common_mistakes": "Squatting the lift, rounding upper back.",
                    "coaching_cue": "Hips back, not down.",
                },
                {
                    "name": "Overhead press",
                    "target_sets": 3, "target_reps": "5-8", "rest_seconds": 120,
                    "setup": "Bar on front delts, elbows just in front of bar, glutes braced.",
                    "execution": "Press straight up, head through at lockout.",
                    "common_mistakes": "Excessive lower-back arch, pressing in front of the body.",
                    "coaching_cue": "Stack ears over shoulders at the top.",
                },
                {
                    "name": "Lat pulldown",
                    "target_sets": 3, "target_reps": "8-12", "rest_seconds": 90,
                    "setup": "Thighs locked under pads, slight backward lean.",
                    "execution": "Pull bar to upper chest, lead with elbows.",
                    "common_mistakes": "Using momentum, shrugging at the top.",
                    "coaching_cue": "Elbows down to your back pockets.",
                },
                {
                    "name": "Walking lunge",
                    "target_sets": 3, "target_reps": "10-12 / leg", "rest_seconds": 90,
                    "setup": "Dumbbells at sides, tall posture.",
                    "execution": "Step into long stride, drop back knee just shy of ground, drive through front heel.",
                    "common_mistakes": "Short stride, front knee caving in.",
                    "coaching_cue": "Big step, tall chest.",
                },
            ],
        },
        {
            "name": "Day C",
            "exercises": [
                {
                    "name": "Conventional deadlift",
                    "target_sets": 3, "target_reps": "3-5", "rest_seconds": 180,
                    "setup": "Bar over mid-foot, shoulders just in front of bar, lats tight.",
                    "execution": "Push the floor away, hips and shoulders rise together, lock out.",
                    "common_mistakes": "Hips shoot up first, rounded lower back.",
                    "coaching_cue": "Long arms, proud chest, push the world away.",
                },
                {
                    "name": "Incline dumbbell press",
                    "target_sets": 3, "target_reps": "8-10", "rest_seconds": 120,
                    "setup": "Bench at 30°, dumbbells over lower chest.",
                    "execution": "Press up and slightly together, controlled lowering.",
                    "common_mistakes": "Flared elbows, dumbbells crashing together.",
                    "coaching_cue": "Drive through the heels of your hands.",
                },
                {
                    "name": "Seated cable row",
                    "target_sets": 3, "target_reps": "10-12", "rest_seconds": 90,
                    "setup": "Tall chest, slight backward angle.",
                    "execution": "Pull handle to lower ribs, squeeze, control return.",
                    "common_mistakes": "Heaving with the torso.",
                    "coaching_cue": "Long arms back to long arms forward.",
                },
                {
                    "name": "Hanging knee raise",
                    "target_sets": 3, "target_reps": "8-12", "rest_seconds": 75,
                    "setup": "Hang from bar, shoulders engaged.",
                    "execution": "Curl knees to chest by tilting pelvis.",
                    "common_mistakes": "Swinging, only using hip flexors.",
                    "coaching_cue": "Posterior tilt at the top.",
                },
            ],
        },
    ],
}


class Command(BaseCommand):
    help = "Create or refresh the default 'Full Body 3x/week' program."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete and recreate the seeded program if it already exists.",
        )

    def handle(self, *args, reset=False, **options):
        with transaction.atomic():
            existing = Program.objects.filter(name=PROGRAM["name"]).first()
            if existing and reset:
                self.stdout.write(self.style.WARNING(f"Deleting existing '{existing.name}'"))
                existing.delete()
                existing = None
            if existing:
                self.stdout.write(self.style.NOTICE(
                    f"Program '{existing.name}' already present (id={existing.id}). "
                    f"Pass --reset to recreate it."
                ))
                return

            program = Program.objects.create(
                name=PROGRAM["name"],
                description=PROGRAM["description"],
                is_default=True,
            )
            for d_idx, day_data in enumerate(PROGRAM["days"]):
                day = Day.objects.create(
                    program=program, name=day_data["name"], order=d_idx
                )
                for e_idx, ex in enumerate(day_data["exercises"]):
                    Exercise.objects.create(
                        day=day,
                        order=e_idx,
                        name=ex["name"],
                        target_sets=ex["target_sets"],
                        target_reps=ex["target_reps"],
                        rest_seconds=ex["rest_seconds"],
                        setup=ex.get("setup", ""),
                        execution=ex.get("execution", ""),
                        common_mistakes=ex.get("common_mistakes", ""),
                        coaching_cue=ex.get("coaching_cue", ""),
                    )

        self.stdout.write(self.style.SUCCESS(
            f"Seeded program '{program.name}' with {program.days.count()} days."
        ))
