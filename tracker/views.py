"""Views for the gymweb tracker (server-rendered templates)."""

from __future__ import annotations

import csv
import json
from datetime import timedelta

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

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
            messages.success(request, "Profile updated.")
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
            messages.success(request, "Measurement saved.")
            return redirect("tracker:log")
    else:
        form = BodyLogForm(initial={"measured_at": timezone.now()})
    return render(request, "tracker/log_form.html", {"form": form})


@require_POST
def log_delete(request, pk: int):
    profile = _get_or_create_singleton_profile()
    entry = get_object_or_404(BodyLog, pk=pk, profile=profile)
    entry.delete()
    messages.success(request, "Measurement deleted.")
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
        messages.success(request, "Set logged.")
    else:
        messages.error(request, "Could not save that set.")
    return redirect("tracker:session_detail", session_id=session.pk)


@require_POST
def session_finish(request, session_id: int):
    session = get_object_or_404(WorkoutSession, pk=session_id)
    session.finished_at = timezone.now()
    session.save(update_fields=["finished_at"])
    messages.success(request, "Session finished. Good work!")
    return redirect("tracker:history")


# History --------------------------------------------------------------------

def history(request):
    profile = _get_or_create_singleton_profile()
    sessions = profile.sessions.select_related("day", "day__program").prefetch_related("sets")
    return render(request, "tracker/history.html", {"sessions": sessions})
