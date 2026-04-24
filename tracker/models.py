"""Domain models for the gymweb tracker.

Core entities:

* ``Profile`` — per-user static data (height, units, sex).
* ``BodyLog`` — dated measurement sample (weight, fat %, muscle).
* ``Program`` / ``Day`` / ``Exercise`` — workout routine structure.
* ``WorkoutSession`` / ``SetEntry`` — history of completed sets.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


UNITS_METRIC = "metric"
UNITS_IMPERIAL = "imperial"
UNITS_CHOICES = [
    (UNITS_METRIC, "Metric (kg / cm)"),
    (UNITS_IMPERIAL, "Imperial (lb / in)"),
]

SEX_CHOICES = [
    ("", "Prefer not to say"),
    ("male", "Male"),
    ("female", "Female"),
    ("other", "Other"),
]


class Profile(models.Model):
    """Static user data. One per auth user; nullable so anonymous demos work."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        null=True,
        blank=True,
    )
    display_name = models.CharField(max_length=80, default="Athlete")
    height_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, blank=True, default="")
    units = models.CharField(max_length=10, choices=UNITS_CHOICES, default=UNITS_METRIC)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.display_name or "Profile"


class BodyLog(models.Model):
    """A dated body composition sample."""

    class Source(models.TextChoices):
        MANUAL = "manual", "Manual entry"
        SCALE = "scale", "Smart scale"
        CALIPER = "caliper", "Calipers"
        DEXA = "dexa", "DEXA / professional"
        OTHER = "other", "Other"

    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="body_logs",
        null=True, blank=True,
    )
    measured_at = models.DateTimeField(default=timezone.now)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    body_fat_pct = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    muscle_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    muscle_pct = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    source = models.CharField(max_length=16, choices=Source.choices, default=Source.MANUAL)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-measured_at"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"BodyLog {self.measured_at:%Y-%m-%d} w={self.weight_kg}"

    @property
    def bmi(self) -> float | None:
        """Derived BMI using the profile height. None when data is missing."""
        if not self.weight_kg or not self.profile or not self.profile.height_cm:
            return None
        h_m = float(self.profile.height_cm) / 100.0
        if h_m <= 0:
            return None
        return round(float(self.weight_kg) / (h_m * h_m), 2)


class Program(models.Model):
    """A named workout program (e.g. "Full Body 3x/week")."""

    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_default", "name"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name


class Day(models.Model):
    """A day inside a program (Day A, Day B, ...)."""

    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="days")
    name = models.CharField(max_length=80)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["program", "order"]
        unique_together = [("program", "order")]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.program.name} — {self.name}"


class Exercise(models.Model):
    """An exercise block inside a day."""

    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name="exercises")
    name = models.CharField(max_length=120)
    order = models.PositiveSmallIntegerField(default=0)
    target_sets = models.PositiveSmallIntegerField(default=3)
    target_reps = models.CharField(max_length=20, default="8-12")
    rest_seconds = models.PositiveSmallIntegerField(default=90)
    setup = models.TextField(blank=True, help_text="How to set up the movement.")
    execution = models.TextField(blank=True, help_text="Step-by-step execution cues.")
    common_mistakes = models.TextField(blank=True)
    coaching_cue = models.CharField(max_length=240, blank=True)
    reference_url = models.URLField(blank=True)

    class Meta:
        ordering = ["day", "order"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name


class WorkoutSession(models.Model):
    """A logged session for a particular program day."""

    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="sessions",
        null=True, blank=True,
    )
    day = models.ForeignKey(Day, on_delete=models.PROTECT, related_name="sessions")
    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Session {self.day} @ {self.started_at:%Y-%m-%d}"


class KnowledgeNote(models.Model):
    """A saved knowledge note with preserved source text and structured sections."""

    class SourceType(models.TextChoices):
        MANUAL = "manual", "Manual note"
        TRANSCRIPT = "transcript", "Transcript import"
        IMPORTED = "imported", "Imported article"

    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="knowledge_notes",
        null=True, blank=True,
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    source_type = models.CharField(
        max_length=20, choices=SourceType.choices, default=SourceType.MANUAL
    )
    source_path = models.CharField(max_length=500, blank=True)
    language_code = models.CharField(max_length=20, default="zh-Hant", blank=True)
    summary = models.TextField(blank=True)
    tags = models.CharField(max_length=240, blank=True, help_text="Comma-separated tags.")
    raw_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-created_at"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            base_slug = slugify(self.title, allow_unicode=True)[:200] or "note"
            slug = base_slug
            suffix = 2
            while KnowledgeNote.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base_slug[:190]}-{suffix}"
                suffix += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def tag_list(self) -> list[str]:
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]


class KnowledgeSection(models.Model):
    """A structured subsection inside a knowledge note."""

    class SectionType(models.TextChoices):
        OVERVIEW = "overview", "Overview"
        TIMELINE = "timeline", "Timeline"
        MECHANISM = "mechanism", "Mechanism"
        BENEFIT = "benefit", "Benefit"
        RISK = "risk", "Risk"
        PRACTICAL = "practical", "Practical takeaway"

    note = models.ForeignKey(
        KnowledgeNote, on_delete=models.CASCADE, related_name="sections"
    )
    heading = models.CharField(max_length=120)
    heading_zh = models.CharField(max_length=120, blank=True)
    section_type = models.CharField(
        max_length=20, choices=SectionType.choices, default=SectionType.OVERVIEW
    )
    sort_order = models.PositiveSmallIntegerField(default=0)
    content = models.TextField()

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.note.title} · {self.heading}"


class SetEntry(models.Model):
    """A single completed set inside a session."""

    session = models.ForeignKey(
        WorkoutSession, on_delete=models.CASCADE, related_name="sets",
    )
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT, related_name="sets")
    set_number = models.PositiveSmallIntegerField(default=1)
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    reps = models.PositiveSmallIntegerField(null=True, blank=True)
    rpe = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    done = models.BooleanField(default=True)

    class Meta:
        ordering = ["session", "exercise", "set_number"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.exercise.name} set {self.set_number}"
