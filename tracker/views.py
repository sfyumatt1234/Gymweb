"""Views for the gymweb tracker (server-rendered templates)."""

from __future__ import annotations

import csv
import json
from datetime import timedelta

from django.contrib import messages

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
from .forms import BodyLogForm, ProfileForm, SetEntryForm
from .models import (
    BodyLog,
    Day,
    Exercise,
    Profile,
    Program,
    SetEntry,
    WorkoutSession,
)


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


def planning(request):
    categories = list(all_categories())
    return render(
        request,
        "tracker/planning.html",
        {"categories": categories},
    )


def planning_results(request):
    goal = (request.GET.get("goal") or "gain").strip().lower()
    level = (request.GET.get("level") or "beginner").strip().lower()
    focus = (request.GET.get("focus") or "chest").strip().lower()
    equipment = (request.GET.get("equipment") or "").strip()

    cat = get_category(focus) or get_category("chest")
    assert cat is not None

    # Very simple generator: pick the first N exercises from the category and
    # attach sets/reps based on goal + level.
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
    for ex in cat.exercises[:6]:
        items.append(
            {
                "name": ex.name,
                "name_zh": ex.name_zh,
                "equipment": ex.equipment,
                "equipment_zh": ex.equipment_zh,
                "thumb": ex.thumb,
                "sets": sets,
                "reps": rep_scheme,
                "rest": rest,
                "primary": ex.primary,
                "primary_zh": ex.primary_zh,
            }
        )

    # Coverage is a lightweight proxy; later we can compute real coverage.
    coverage = min(92, 44 + len(items) * 6)
    summary = {
        "coverage": coverage,
        "muscle_groups": 1,
        "goal": goal,
        "level": level,
        "focus": cat,
        "equipment": equipment,
    }

    return render(
        request,
        "tracker/planning_results.html",
        {"items": items, "summary": summary},
    )


def schedule(request):
    return render(request, "tracker/schedule.html")


def tools(request):
    return render(request, "tracker/tools.html")


def body_graph(request):
    return render(request, "tracker/body_graph.html", {"categories": all_categories()})
