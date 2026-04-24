"""Views for the gymweb tracker (server-rendered templates)."""

from __future__ import annotations

import csv
import json
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.db.models import Q

from .i18n_ui import bilingual_line
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .exercise_filters import (
    EQUIPMENT_OPTIONS,
    MUSCLE_OPTIONS,
    equipment_matches,
    muscle_matches,
    normalize_multi_param,
)
from .exercise_library import all_categories, get_category
from .forms import BodyLogForm, KnowledgeNoteForm, ProfileForm, SetEntryForm
from .models import (
    BodyLog,
    Day,
    Exercise,
    KnowledgeNote,
    Profile,
    Program,
    SetEntry,
    WorkoutSession,
)
from .services.exercisedb import ExerciseDbClient, ExerciseDbError


def _get_or_create_singleton_profile() -> Profile:
    """Return the single demo profile (local-first, no auth required)."""
    profile = Profile.objects.order_by("id").first()
    if profile is None:
        profile = Profile.objects.create(display_name="Athlete", height_cm=175.0)
    return profile


def _compute_bmi(weight_kg, height_cm):
    if not weight_kg or not height_cm:
        return None
    try:
        h = float(height_cm) / 100.0
        if h <= 0:
            return None
        return round(float(weight_kg) / (h * h), 2)
    except (TypeError, ValueError):
        return None


def _bmi_category(bmi: float | None) -> str:
    if bmi is None:
        return "—"
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Overweight"
    return "Obese"


def _bmi_category_zh(bmi: float | None) -> str:
    if bmi is None:
        return "—"
    if bmi < 18.5:
        return "過輕"
    if bmi < 25:
        return "正常"
    if bmi < 30:
        return "過重"
    return "肥胖"


# Dashboard ------------------------------------------------------------------

def dashboard(request):
    profile = _get_or_create_singleton_profile()
    latest = profile.body_logs.first()
    bmi = _compute_bmi(latest.weight_kg if latest else None, profile.height_cm)

    since = timezone.now() - timedelta(days=30)
    recent = list(
        profile.body_logs.filter(measured_at__gte=since).order_by("measured_at")
    )

    series = {
        "labels": [b.measured_at.strftime("%Y-%m-%d") for b in recent],
        "weight": [float(b.weight_kg) if b.weight_kg else None for b in recent],
        "fat": [float(b.body_fat_pct) if b.body_fat_pct else None for b in recent],
        "muscle_kg": [float(b.muscle_kg) if b.muscle_kg else None for b in recent],
        "bmi": [
            _compute_bmi(b.weight_kg, profile.height_cm) for b in recent
        ],
    }

    programs = Program.objects.all()[:3]

    return render(
        request,
        "tracker/dashboard.html",
        {
            "profile": profile,
            "latest": latest,
            "bmi": bmi,
            "bmi_category": _bmi_category(bmi),
            "bmi_category_zh": _bmi_category_zh(bmi),
            "series_json": json.dumps(series),
            "programs": programs,
        },
    )


# Profile --------------------------------------------------------------------

def profile_edit(request):
    profile = _get_or_create_singleton_profile()
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                bilingual_line("Profile updated.", "個人資料已更新。"),
            )
            return redirect("tracker:dashboard")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "tracker/profile.html", {"form": form, "profile": profile})


# BodyLog --------------------------------------------------------------------

def log_list(request):
    profile = _get_or_create_singleton_profile()
    logs = profile.body_logs.all()
    enriched = []
    for log in logs:
        enriched.append(
            {
                "log": log,
                "bmi": _compute_bmi(log.weight_kg, profile.height_cm),
            }
        )
    return render(
        request,
        "tracker/log_list.html",
        {"entries": enriched, "profile": profile},
    )


def log_create(request):
    profile = _get_or_create_singleton_profile()
    if request.method == "POST":
        form = BodyLogForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.profile = profile
            entry.save()
            messages.success(
                request,
                bilingual_line("Measurement saved.", "身體數據已儲存。"),
            )
            return redirect("tracker:log")
    else:
        form = BodyLogForm(initial={"measured_at": timezone.now()})
    return render(request, "tracker/log_form.html", {"form": form})


@require_POST
def log_delete(request, pk: int):
    profile = _get_or_create_singleton_profile()
    entry = get_object_or_404(BodyLog, pk=pk, profile=profile)
    entry.delete()
    messages.success(
        request,
        bilingual_line("Measurement deleted.", "已刪除此筆紀錄。"),
    )
    return redirect("tracker:log")


def log_export(request):
    profile = _get_or_create_singleton_profile()
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="body_log.csv"'
    writer = csv.writer(response)
    writer.writerow(
        [
            "measured_at",
            "weight_kg",
            "body_fat_pct",
            "muscle_kg",
            "muscle_pct",
            "bmi",
            "source",
            "notes",
        ]
    )
    for log in profile.body_logs.all():
        writer.writerow(
            [
                log.measured_at.isoformat(),
                log.weight_kg or "",
                log.body_fat_pct or "",
                log.muscle_kg or "",
                log.muscle_pct or "",
                _compute_bmi(log.weight_kg, profile.height_cm) or "",
                log.source,
                log.notes.replace("\n", " ") if log.notes else "",
            ]
        )
    return response


# Routines / programs --------------------------------------------------------

def program_list(request):
    programs = Program.objects.all().prefetch_related("days")
    return render(request, "tracker/routines.html", {"programs": programs})


def program_detail(request, program_id: int):
    program = get_object_or_404(Program, pk=program_id)
    return render(request, "tracker/program_detail.html", {"program": program})


def day_detail(request, day_id: int):
    day = get_object_or_404(Day, pk=day_id)
    return render(request, "tracker/day_detail.html", {"day": day})


# Sessions -------------------------------------------------------------------

def session_start(request, day_id: int):
    day = get_object_or_404(Day, pk=day_id)
    profile = _get_or_create_singleton_profile()
    session = WorkoutSession.objects.create(day=day, profile=profile)
    return redirect("tracker:session_detail", session_id=session.pk)


def session_detail(request, session_id: int):
    session = get_object_or_404(WorkoutSession, pk=session_id)
    set_form = SetEntryForm()
    set_form.fields["exercise"].queryset = session.day.exercises.all()
    return render(
        request,
        "tracker/session_detail.html",
        {"session": session, "set_form": set_form},
    )


@require_POST
def session_add_set(request, session_id: int):
    session = get_object_or_404(WorkoutSession, pk=session_id)
    form = SetEntryForm(request.POST)
    form.fields["exercise"].queryset = session.day.exercises.all()
    if form.is_valid():
        entry = form.save(commit=False)
        entry.session = session
        entry.save()
        messages.success(
            request,
            bilingual_line("Set logged.", "已記錄此組。"),
        )
    else:
        messages.error(
            request,
            bilingual_line("Could not save that set.", "無法儲存此組，請檢查欄位。"),
        )
    return redirect("tracker:session_detail", session_id=session.pk)


@require_POST
def session_finish(request, session_id: int):
    session = get_object_or_404(WorkoutSession, pk=session_id)
    session.finished_at = timezone.now()
    session.save(update_fields=["finished_at"])
    messages.success(
        request,
        bilingual_line("Session finished. Good work!", "訓練已結束，做得好！"),
    )
    return redirect("tracker:history")


# History --------------------------------------------------------------------

def history(request):
    profile = _get_or_create_singleton_profile()
    sessions = profile.sessions.select_related("day", "day__program").prefetch_related("sets")
    return render(request, "tracker/history.html", {"sessions": sessions})


# Knowledge notes -------------------------------------------------------------

def note_list(request):
    profile = _get_or_create_singleton_profile()
    q = (request.GET.get("q") or "").strip()
    notes = profile.knowledge_notes.prefetch_related("sections")
    if q:
        notes = notes.filter(
            Q(title__icontains=q)
            | Q(summary__icontains=q)
            | Q(tags__icontains=q)
            | Q(raw_text__icontains=q)
            | Q(sections__content__icontains=q)
            | Q(sections__heading__icontains=q)
            | Q(sections__heading_zh__icontains=q)
        ).distinct()
    return render(
        request,
        "tracker/note_list.html",
        {"notes": notes, "q": q, "profile": profile},
    )


def note_detail(request, slug: str):
    profile = _get_or_create_singleton_profile()
    note = get_object_or_404(
        KnowledgeNote.objects.prefetch_related("sections"),
        slug=slug,
        profile=profile,
    )
    return render(
        request,
        "tracker/note_detail.html",
        {"note": note, "profile": profile},
    )


def note_create(request):
    profile = _get_or_create_singleton_profile()
    if request.method == "POST":
        form = KnowledgeNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.profile = profile
            note.save()
            messages.success(
                request,
                bilingual_line("Note saved.", "筆記已儲存。"),
            )
            return redirect("tracker:note_detail", slug=note.slug)
    else:
        form = KnowledgeNoteForm(
            initial={
                "language_code": "zh-Hant",
                "source_type": KnowledgeNote.SourceType.MANUAL,
            }
        )
    return render(
        request,
        "tracker/note_form.html",
        {"form": form, "profile": profile},
    )


# Exercise library (curated reference + local thumbnails) ----------------------


def exercise_index(request):
    q_raw = request.GET.get("q") or ""
    q = q_raw.strip().lower()
    equipment_legacy = (request.GET.get("equipment") or "").strip().lower()
    equip_keys = normalize_multi_param(request, "equip")
    muscle_keys = normalize_multi_param(request, "muscle")

    categories = list(all_categories())

    def exercise_passes_filters(ex, cat) -> bool:
        hay = " ".join(
            [
                ex.name,
                ex.name_zh,
                ex.equipment,
                ex.equipment_zh,
                ex.primary,
                ex.primary_zh,
            ]
        ).lower()
        if q and q not in hay:
            return False
        if equipment_legacy and equipment_legacy not in ex.equipment.lower() and equipment_legacy not in ex.equipment_zh.lower():
            return False
        if equip_keys:
            if not any(equipment_matches(ex, k) for k in equip_keys):
                return False
        if muscle_keys:
            if not any(muscle_matches(ex, cat, k) for k in muscle_keys):
                return False
        return True

    if q or equipment_legacy or equip_keys or muscle_keys:
        filtered = []
        for c in categories:
            exs = [ex for ex in c.exercises if exercise_passes_filters(ex, c)]
            if exs:
                filtered.append(
                    type(c)(
                        slug=c.slug,
                        title=c.title,
                        title_zh=c.title_zh,
                        summary=c.summary,
                        summary_zh=c.summary_zh,
                        exercises=tuple(exs),
                        thumb=c.thumb,
                    )
                )
        categories = filtered

    return render(
        request,
        "tracker/exercise_index.html",
        {
            "categories": categories,
            "q": q_raw.strip(),
            "equipment": equipment_legacy,
            "equip_keys": equip_keys,
            "muscle_keys": muscle_keys,
            "equipment_options": EQUIPMENT_OPTIONS,
            "muscle_options": MUSCLE_OPTIONS,
        },
    )


def exercise_category(request, slug: str):
    category = get_category(slug)
    if category is None:
        raise Http404("Unknown muscle group")
    return render(
        request,
        "tracker/exercise_category.html",
        {"category": category},
    )


# MuscleWiki-like navigation stubs -------------------------------------------


def _exercise_db_bodypart_for_focus(focus: str) -> str | None:
    return {
        "chest": "Chest",
        "back": "Back",
        "legs": "Upper Legs",
        "shoulders": "Shoulders",
        "arms": "Upper Arms",
        "core": "Waist",
        "abductors": "Upper Legs",
    }.get(focus)


def _exercise_db_equipment_value(equipment: str) -> str | None:
    return {
        "any": None,
        "cable": "Cable",
        "dumbbell": "Dumbbell",
        "barbell": "Barbell",
        "bodyweight": "Body Weight",
    }.get((equipment or "").strip().lower())


def _remote_plan_items(focus: str, equipment: str, sets: int, rep_scheme: str, rest: str) -> list[dict]:
    body_part = _exercise_db_bodypart_for_focus(focus)
    if not body_part:
        return []

    client = ExerciseDbClient.from_settings()
    response = client.list_exercises(
        bodyParts=body_part,
        equipments=_exercise_db_equipment_value(equipment),
        limit=6,
    )

    items = []
    for ex in response.get("data", []):
        items.append(
            {
                "name": ex.get("name", ""),
                "name_zh": "",
                "equipment": ", ".join(ex.get("equipments") or []),
                "equipment_zh": "",
                "thumb": "",
                "image_url": ex.get("imageUrl", ""),
                "sets": sets,
                "reps": rep_scheme,
                "rest": rest,
                "primary": ", ".join(ex.get("targetMuscles") or ex.get("bodyParts") or []),
                "primary_zh": "",
                "notes": (ex.get("overview") or "")[:220],
                "notes_zh": "",
                "category_slug": focus or "chest",
            }
        )
    return items


def _local_plan_items(cat, sets: int, rep_scheme: str, rest: str) -> list[dict]:
    items = []
    for ex in cat.exercises[:6]:
        items.append(
            {
                "name": ex.name,
                "name_zh": ex.name_zh,
                "equipment": ex.equipment,
                "equipment_zh": ex.equipment_zh,
                "thumb": ex.thumb,
                "image_url": "",
                "sets": sets,
                "reps": rep_scheme,
                "rest": rest,
                "primary": ex.primary,
                "primary_zh": ex.primary_zh,
                "notes": ex.notes,
                "notes_zh": ex.notes_zh,
                "category_slug": cat.slug,
            }
        )
    return items


def planning(request):
    categories = list(all_categories())
    return render(
        request,
        "tracker/planning.html",
        {
            "categories": categories,
            "exercisedb_enabled": settings.EXERCISEDB_ENABLED,
        },
    )


def planning_results(request):
    goal = (request.GET.get("goal") or "gain").strip().lower()
    level = (request.GET.get("level") or "beginner").strip().lower()
    focus = (request.GET.get("focus") or "chest").strip().lower()
    equipment = (request.GET.get("equipment") or "").strip()

    cat = get_category(focus) or get_category("chest")
    assert cat is not None

    if goal in ("strength",):
        rep_scheme = "3–5"
        sets = 4 if level in ("intermediate", "advanced") else 3
        rest = "2–4 min"
    elif goal in ("lose", "fatloss", "cut"):
        rep_scheme = "10–15"
        sets = 3
        rest = "60–90s"
    else:  # gain muscle
        rep_scheme = "8–12"
        sets = 3 if level == "beginner" else 4
        rest = "90–150s"

    items = []
    source_label = bilingual_line("Gymweb curated library", "Gymweb 內建動作庫")
    remote_error = ""
    try:
        items = _remote_plan_items(cat.slug, equipment, sets, rep_scheme, rest)
        if items:
            source_label = bilingual_line("ExerciseDB suggestions", "ExerciseDB 建議結果")
    except ExerciseDbError:
        remote_error = bilingual_line(
            "ExerciseDB was unavailable, so Gymweb used the built-in exercise library.",
            "ExerciseDB 暫時不可用，已改用 Gymweb 內建動作庫。",
        )

    if not items:
        items = _local_plan_items(cat, sets, rep_scheme, rest)

    coverage = min(92, 44 + len(items) * 6)
    goal_labels = {
        "gain": bilingual_line("Gain muscle", "增肌"),
        "strength": bilingual_line("Strength", "力量"),
        "fatloss": bilingual_line("Lose fat", "減脂"),
        "lose": bilingual_line("Lose fat", "減脂"),
        "cut": bilingual_line("Lose fat", "減脂"),
    }
    level_labels = {
        "beginner": bilingual_line("Beginner", "初學"),
        "intermediate": bilingual_line("Intermediate", "中級"),
        "advanced": bilingual_line("Advanced", "進階"),
    }

    return render(
        request,
        "tracker/planning_results.html",
        {
            "items": items,
            "plan_title": bilingual_line(f"{cat.title} workout plan", f"{cat.title_zh} 訓練計畫"),
            "plan_subtitle": bilingual_line(
                f"{source_label} tuned for {goal_labels.get(goal, goal)} and {level_labels.get(level, level)}.",
                f"{source_label}，已依 {goal_labels.get(goal, goal)} 與 {level_labels.get(level, level)} 調整。",
            ),
            "goal_label": goal_labels.get(goal, goal),
            "level_label": level_labels.get(level, level),
            "exercise_count": len(items),
            "muscle_group_count": 1,
            "coverage_pct": coverage,
            "targeted_slugs": [cat.slug],
            "targeted_categories": [cat],
            "source_label": source_label,
            "remote_error": remote_error,
        },
    )


def schedule(request):
    return render(request, "tracker/schedule.html")


def tools(request):
    return render(request, "tracker/tools.html")


def body_graph(request):
    return render(request, "tracker/body_graph.html", {"categories": all_categories()})
