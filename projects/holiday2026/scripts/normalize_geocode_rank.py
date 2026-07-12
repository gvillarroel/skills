#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests>=2.32.0"]
# ///
"""Normalize research, geocode it, estimate routes, score it, and apply selection rules."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import time
import unicodedata
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote_plus

import requests


HOME_ADDRESS = "7010 Brassfield Dr, Cumming, GA 30041"
HOME_LAT = 34.079099895469
HOME_LON = -84.183167025532
CHECKED_DATE = "2026-07-11"
VACATION_START = date(2026, 7, 11)
VACATION_END = date(2026, 7, 20)

CATEGORY_ALIASES = {
    "restaurants": "family-restaurants",
    "family restaurants": "family-restaurants",
    "restaurant": "family-restaurants",
    "bakeries": "bakeries-cafes-desserts",
    "bakeries cafes desserts": "bakeries-cafes-desserts",
    "bakeries, cafes, and desserts": "bakeries-cafes-desserts",
    "museums": "museums-science-history",
    "museums science history": "museums-science-history",
    "museums, science, and history": "museums-science-history",
    "arts culture spiritual heritage": "arts-culture-spiritual-heritage",
    "arts, culture, spiritual sites, and heritage": "arts-culture-spiritual-heritage",
    "family attractions indoor play": "family-attractions-indoor-play",
    "family attractions and indoor play": "family-attractions-indoor-play",
    "geek tech anime games comics vinyl": "geek-tech-anime-games-comics-vinyl",
    "geek, technology, anime, games, comics, and vinyl": "geek-tech-anime-games-comics-vinyl",
    "parks hiking lakes nature": "parks-hiking-lakes-nature",
    "parks, hiking, lakes, and nature": "parks-hiking-lakes-nature",
    "adventure water animals farms": "adventure-water-animals-farms",
    "adventure, water activities, animals, and farms": "adventure-water-animals-farms",
    "shopping markets outlets": "shopping-markets-outlets",
    "shopping, markets, and outlets": "shopping-markets-outlets",
    "sports": "sports-live-games",
    "sports and live games": "sports-live-games",
    "events": "events-festivals-live-shows",
    "events, festivals, and live shows": "events-festivals-live-shows",
    "day trips": "day-trips-unusual-experiences",
    "day trips and unusual experiences": "day-trips-unusual-experiences",
}

LEXICOGRAPHIC_BASE = 51

EVERGREEN_SECONDARY_WEIGHTS = {
    "family": 0.30,
    "evidence": 0.25,
    "proximity": 0.20,
    "rating": 0.15,
    "uniqueness": 0.10,
    "urgency": 0.00,
}

TIMED_SECONDARY_WEIGHTS = {
    "family": 0.25,
    "evidence": 0.20,
    "proximity": 0.15,
    "rating": 0.10,
    "uniqueness": 0.10,
    "urgency": 0.20,
}

CULTURE_BASELINES = {
    "family-restaurants": 2.0,
    "bakeries-cafes-desserts": 2.0,
    "museums-science-history": 5.0,
    "arts-culture-spiritual-heritage": 5.0,
    "family-attractions-indoor-play": 1.5,
    "geek-tech-anime-games-comics-vinyl": 2.2,
    "parks-hiking-lakes-nature": 2.0,
    "adventure-water-animals-farms": 1.8,
    "shopping-markets-outlets": 2.0,
    "sports-live-games": 1.8,
    "events-festivals-live-shows": 3.0,
    "day-trips-unusual-experiences": 3.0,
}

NATION_CULTURE_PATTERNS = [
    ("India", 5.0, ("indian", "hindu", "mandir", "swaminarayan", "shirdi sai", "baps")),
    ("Korea", 5.0, ("korean", "korea", "k pop", "kpop", "h mart")),
    ("Japan", 5.0, ("japanese", "japan", "anime", "manga", "kinokuniya", "otaku", "kura sushi")),
    ("China", 5.0, ("chinese", "china", "dim sum", "sichuan", "szechuan")),
    ("Thailand", 5.0, ("thai", "thailand")),
    ("Vietnam", 5.0, ("vietnamese", "vietnam", "pho", "banh mi")),
    ("Persia / Iran", 5.0, ("persian", "iranian", "rumi s kitchen")),
    ("Mexico / Latin America", 5.0, ("mexican", "latin", "taqueria", "plaza fiesta", "mariachi")),
    ("France", 4.8, ("french", "france", "patisserie", "macaron", "crepe", "croissant")),
    ("Italy", 4.5, ("italian", "italy", "gelato", "venetian")),
    ("Germany / Bavaria", 5.0, ("german", "germany", "bavarian", "bavaria")),
    ("Greece / Mediterranean", 4.7, ("greek", "greece", "mediterranean")),
    ("Middle East", 4.7, ("middle eastern", "levant", "arabic", "halal")),
    ("Africa", 4.8, ("ethiopian", "african diaspora", "pan african")),
    ("Caribbean", 4.8, ("caribbean", "jamaican", "cuban", "puerto rican")),
    ("Brazil", 5.0, ("brazilian", "brazil", "churrascaria")),
    ("Tibet / Buddhism", 5.0, ("tibetan", "buddhist", "buddhism", "drepung")),
    ("Jewish heritage", 4.6, ("jewish", "synagogue", "holocaust")),
    ("Cherokee Nation", 4.7, ("cherokee", "new echota")),
    ("Indigenous nations", 4.8, ("native american", "indigenous", "mississippian", "indian mounds", "etowah mounds")),
    ("Global cultures", 4.5, ("international", "world cultures", "global culture", "global village", "world cup", "fifa")),
]

CHILD_EXCLUSION_PATTERNS = (
    "adult only",
    "adults only",
    "21 and over only",
    "21 plus only",
    "21 only",
    "ages 21 and older only",
    "must be 21 to enter",
    "no minors",
    "18 and over only",
    "18 plus only",
    "18 only",
)

CHILD_CONDITIONAL_PATTERNS = (
    "with a parent",
    "with parent",
    "guardian",
    "supervision",
    "older children",
    "mature upper elementary",
    "teens and adults",
    "best for ages 12",
    "recommended around 13",
    "alcohol is served",
    "alcohol is present",
    "height rule",
    "height requirement",
    "must be at least 5 feet",
    "film ratings",
    "may be scary",
    "sensory sensitive",
)


def slug_text(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def category_id(value: Any) -> str:
    raw = str(value or "").strip()
    if raw in set(CATEGORY_ALIASES.values()):
        return raw
    key = slug_text(raw)
    if key in CATEGORY_ALIASES:
        return CATEGORY_ALIASES[key]
    for alias, canonical in CATEGORY_ALIASES.items():
        if alias in key or key in alias:
            return canonical
    return re.sub(r"[^a-z0-9]+", "-", key).strip("-")


def flatten_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("candidates", "places", "items", "entries"):
        if isinstance(payload.get(key), list):
            return [row for row in payload[key] if isinstance(row, dict)]
    rows: list[dict[str, Any]] = []
    categories = payload.get("categories")
    if isinstance(categories, dict):
        for cat, values in categories.items():
            if isinstance(values, list):
                for row in values:
                    if isinstance(row, dict):
                        row = dict(row)
                        row.setdefault("category_id", cat)
                        rows.append(row)
    if rows:
        return rows
    for key, values in payload.items():
        if key == "metadata" or not isinstance(values, list):
            continue
        for row in values:
            if isinstance(row, dict):
                row = dict(row)
                row.setdefault("category_id", key)
                rows.append(row)
    return rows


def first(row: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        value = row.get(key)
        if value not in (None, "", []):
            return value
    return default


def as_float(value: Any, default: float | None = None) -> float | None:
    if value in (None, ""):
        return default
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return default


def as_int(value: Any, default: int | None = None) -> int | None:
    number = as_float(value)
    return int(number) if number is not None else default


def as_bool(value: Any, default: bool = True) -> bool:
    if value in (None, ""):
        return default
    if isinstance(value, bool):
        return value
    return slug_text(value) not in {"false", "no", "0", "excluded", "ineligible"}


def clamp(value: Any, low: float = 1.0, high: float = 5.0, default: float = 3.0) -> float:
    number = as_float(value, default)
    assert number is not None
    return max(low, min(high, number))


def parse_date(value: Any) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def normalize_images(value: Any) -> list[dict[str, str]]:
    if not value:
        return []
    if isinstance(value, str):
        return [{"page_url": value, "method": "Provided visual source", "rights_note": "Verify before reuse."}]
    result: list[dict[str, str]] = []
    if isinstance(value, list):
        for item in value[:3]:
            if isinstance(item, str):
                result.append({"page_url": item, "method": "Provided visual source", "rights_note": "Verify before reuse."})
            elif isinstance(item, dict):
                page = first(item, "page_url", "url", "source_url", "image_url", default="")
                if page:
                    result.append({
                        "page_url": str(page),
                        "method": str(first(item, "method", "provenance", default="Provided visual source")),
                        "rights_note": str(first(item, "rights_note", "rights", default="Verify before reuse.")),
                    })
    return result


def normalize_row(raw: dict[str, Any], source_file: str) -> dict[str, Any] | None:
    name = str(first(raw, "name", "title", "venue_name", "place", default="")).strip()
    cat = category_id(first(raw, "category_id", "category", "category_name", default=""))
    if not name or not cat:
        return None
    address = str(first(raw, "address", "street_address", "location", default="")).strip()
    city = str(first(raw, "city", "locality", default="")).strip()
    state = str(first(raw, "state", default="GA")).strip() or "GA"
    zip_code = str(first(raw, "zip", "zip_code", "postal_code", default="")).strip()
    official_url = str(first(raw, "official_url", "website", "url", "source_url", default="")).strip()
    corroborating_url = str(first(raw, "corroborating_url", "secondary_source_url", "secondary_url", default=official_url)).strip()
    price_level = str(first(raw, "price_level", "price", "cost", default="unknown")).strip()
    why_good = str(first(raw, "why_good", "why", "summary", "description", default="Worth considering based on the linked source.")).strip()
    caveat = str(first(raw, "caveat", "limitations", "notes", default="Recheck hours, tickets and age rules before travel.")).strip()
    age_notes = str(first(raw, "age_notes", "ages", "difficulty_or_age_notes", default="Confirm age-specific rules.")).strip()
    subtype = str(first(raw, "subtype", "cuisine_or_specialty", "specialty", "type", default="family activity")).strip()
    indoor_outdoor = str(first(raw, "indoor_outdoor", "setting", default="mixed")).strip().lower()
    start_date = str(first(raw, "start_date", "date", default="")).strip()
    end_date = str(first(raw, "end_date", default=start_date)).strip()
    rating = as_float(first(raw, "rating", "google_rating"))
    if rating is not None and rating > 5:
        rating = rating / 2 if rating <= 10 else None
    review_count = as_int(first(raw, "review_count", "reviews", "rating_count"))
    lat = as_float(first(raw, "latitude", "lat"))
    lon = as_float(first(raw, "longitude", "lon", "lng"))
    source_date = str(first(raw, "checked_date", "source_checked_date", default=CHECKED_DATE)).strip()
    return {
        "id": hashlib.sha1(f"{cat}|{slug_text(name)}|{slug_text(city)}".encode()).hexdigest()[:14],
        "category_id": cat,
        "name": name,
        "venue": str(first(raw, "venue", default=name)).strip(),
        "address": address,
        "city": city,
        "state": state,
        "zip": zip_code,
        "latitude": lat,
        "longitude": lon,
        "official_url": official_url,
        "corroborating_url": corroborating_url,
        "checked_date": source_date,
        "source_eligible": as_bool(first(raw, "eligible", default=True)),
        "operational_status": str(first(raw, "operational_status", "operation_status", default="active-or-unverified")).strip(),
        "start_date": start_date,
        "end_date": end_date,
        "start_time": str(first(raw, "start_time", default="")).strip(),
        "rating": rating,
        "review_count": review_count,
        "price_level": price_level,
        "subtype": subtype,
        "family_fit_1_5": clamp(first(raw, "family_fit_1_5", "family_fit", default=4)),
        "uniqueness_1_5": clamp(first(raw, "uniqueness_1_5", "uniqueness", default=3)),
        "evidence_quality_1_5": clamp(first(raw, "evidence_quality_1_5", "evidence_quality", default=3)),
        "value_1_5": clamp(first(raw, "value_1_5", "value", default=infer_value(price_level))),
        "time_urgency_1_5": clamp(first(raw, "time_urgency_1_5", "urgency", default=infer_urgency(start_date, end_date))),
        "estimated_visit_hours": as_float(first(raw, "estimated_visit_hours", "visit_hours", default=2.5), 2.5),
        "cost_note": str(first(raw, "cost_note", default="Check current pricing before leaving.")).strip(),
        "why_good": why_good,
        "caveat": caveat,
        "age_notes": age_notes,
        "indoor_outdoor": indoor_outdoor,
        "image_candidates": normalize_images(first(raw, "image_candidates", "images", default=[])),
        "research_source_file": source_file,
    }


def infer_value(price: str) -> int:
    raw = str(price or "").strip().lower()
    text = slug_text(raw)
    if "free" in text:
        return 5
    if "premium" in text or "expensive" in text or "high" in text:
        return 2
    if raw == "$":
        return 5
    if raw == "$-$$":
        return 4
    if raw in {"$$", "$/$$"}:
        return 3
    if raw in {"$$$", "$$/$$$"}:
        return 2
    if "unknown" in text:
        return 3
    return 4


def infer_urgency(start: str, end: str) -> int:
    d1, d2 = parse_date(start), parse_date(end)
    if not d1:
        return 3
    d2 = d2 or d1
    if d1 <= VACATION_END and d2 >= VACATION_START:
        return 5
    if d1 <= date(2026, 7, 31):
        return 4
    if d1 <= date(2026, 9, 30):
        return 3
    return 2


def preference_text(row: dict[str, Any]) -> str:
    return slug_text(" ".join(str(row.get(key) or "") for key in (
        "name", "subtype", "why_good", "caveat", "age_notes", "cost_note",
    )))


def child_access_profile(row: dict[str, Any]) -> tuple[bool, str, str]:
    text = preference_text(row)
    age_text = slug_text(row.get("age_notes"))
    for phrase in CHILD_EXCLUSION_PATTERNS:
        if phrase in text:
            return False, "Excluded — adult-only", f"Explicit restriction detected: {phrase}."
    conditional = [phrase for phrase in CHILD_CONDITIONAL_PATTERNS if phrase in text]
    if conditional:
        return (
            True,
            "Children allowed with conditions",
            f"Children are permitted, but review this condition: {conditional[0]}.",
        )
    if age_text and age_text != "confirm age specific rules" and any(
        marker in age_text for marker in ("all ages", "children", "kids", "family", "ages", "younger", "toddler")
    ):
        return True, "Children allowed", "The research record includes an affirmative child or all-ages note."
    if row.get("category_id") in {"family-restaurants", "bakeries-cafes-desserts"}:
        return (
            True,
            "Children allowed — venue-type inference",
            "Retained as a normal food-service venue with no adult-only restriction; verify unusual late-night policies.",
        )
    return (
        True,
        "Children allowed — no restriction found",
        "Family research record contains no adult-only restriction; review the age note and official page before leaving.",
    )


def nation_culture_tags(row: dict[str, Any]) -> tuple[list[str], float]:
    text = preference_text(row)
    padded = f" {text} "
    tags: list[str] = []
    score = 1.0
    for label, strength, phrases in NATION_CULTURE_PATTERNS:
        filtered_phrases = phrases
        if label == "India" and row.get("category_id") not in {"family-restaurants", "bakeries-cafes-desserts"}:
            filtered_phrases = tuple(phrase for phrase in phrases if phrase != "indian")
        if label == "Greece / Mediterranean" and "greek revival" in text:
            filtered_phrases = tuple(phrase for phrase in phrases if phrase != "greek")
        if label in {"Cherokee Nation", "Indigenous nations"} and row.get("category_id") not in {
            "museums-science-history",
            "arts-culture-spiritual-heritage",
            "parks-hiking-lakes-nature",
            "events-festivals-live-shows",
            "day-trips-unusual-experiences",
        }:
            filtered_phrases = ()
        if any(f" {phrase.strip()} " in padded for phrase in filtered_phrases):
            tags.append(label)
            score = max(score, strength)
    if slug_text(row.get("name")) == "the temple" and "Jewish heritage" not in tags:
        tags.append("Jewish heritage")
        score = max(score, 4.6)
    return tags, score


def infer_cultural_priority(row: dict[str, Any], international_score: float) -> float:
    category = str(row.get("category_id") or "")
    text = preference_text(row)
    name_subtype = slug_text(f"{row.get('name', '')} {row.get('subtype', '')}")
    score = CULTURE_BASELINES.get(category, 2.0)
    if category in {"museums-science-history", "arts-culture-spiritual-heritage"}:
        score = 5.0
    elif category == "day-trips-unusual-experiences":
        if any(marker in text for marker in (
            "museum", "historic", "heritage", "archaeolog", "indigenous", "cherokee",
            "folk art", "living history", "battlefield", "presidential", "monastery",
        )):
            score = 5.0
        elif any(marker in text for marker in ("puppetry", "theater", "theatre", "art center", "railway")):
            score = 4.6
    elif category == "family-attractions-indoor-play":
        if "museum" in name_subtype:
            score = 5.0
        elif "themed dinner" in name_subtype:
            score = 3.5
    elif category == "geek-tech-anime-games-comics-vinyl":
        if "museum" in name_subtype:
            score = 5.0
        elif international_score >= 4.5:
            score = 4.2
        elif any(marker in name_subtype for marker in ("historic", "record store", "comic", "vinyl")):
            score = 3.8
    elif category == "parks-hiking-lakes-nature":
        if any(marker in text for marker in ("heritage area", "battlefield", "historic ruins", "mill ruins", "heritage center")):
            score = 4.5
        elif any(marker in name_subtype for marker in ("nature center", "botanical garden")):
            score = 2.8
    elif category == "adventure-water-animals-farms":
        if any(marker in name_subtype for marker in ("historic", "museum", "heritage")):
            score = 4.2
        elif "festival" in text:
            score = 3.8
    elif category == "shopping-markets-outlets":
        if international_score >= 4.5:
            score = 4.5
        elif any(marker in text for marker in ("historic downtown", "artisan market", "antiques", "folk art")):
            score = 4.0
    elif category == "sports-live-games":
        if international_score >= 4.5:
            score = 4.5
        elif any(marker in name_subtype for marker in ("museum", "hall of fame", "stadium tour", "ballpark tour")):
            score = 4.0
        elif "festival" in text:
            score = 3.5
    elif category == "events-festivals-live-shows":
        if any(marker in text for marker in (
            "museum special exhibition", "native american", "pow wow", "cultural festival",
            "arts festival", "book festival", "film festival", "heritage festival",
        )):
            score = 5.0
        elif any(marker in text for marker in ("puppet", "theater", "theatre", "orchestra", "performing arts")):
            score = 4.6
        elif international_score >= 4.5:
            score = 4.6
        elif "festival" in text:
            score = 3.8
    if international_score >= 4.5 and category in {"family-restaurants", "bakeries-cafes-desserts"}:
        score = max(score, 4.3)
    return round(max(1.0, min(5.0, score)), 2)


def infer_affordability(price_level: str, value_score: float) -> float:
    price = str(price_level or "unknown").strip().lower()
    if "premium" in price:
        return 1.2
    if price in {"free", "free-entry", "free-registration"}:
        return 5.0
    if "free" in price:
        return 4.7
    if price == "$":
        return 4.6
    if price == "$-$$":
        return 4.1
    if price in {"$/$$", "free/$/$$"}:
        return 3.8
    if price == "$$":
        return 3.3
    if price == "$$/$$$":
        return 2.4
    if price == "$$$":
        return 1.8
    if price in {"promotion", "free-or-program"}:
        return 4.6
    if price in {"paid", "registration", "event-dependent", "parking-or-entry", "unknown"}:
        return round(max(2.4, min(4.2, 3.0 + (value_score - 3.0) * 0.4)), 2)
    return round(max(1.0, min(5.0, value_score)), 2)


def annotate_preferences(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    eligible: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for row in rows:
        children_allowed, access_level, policy_basis = child_access_profile(row)
        tags, international_score = nation_culture_tags(row)
        cultural_score = infer_cultural_priority(row, international_score)
        affordability_score = infer_affordability(row.get("price_level", "unknown"), row["value_1_5"])
        secondary_quality = (
            0.30 * row["family_fit_1_5"]
            + 0.25 * row["evidence_quality_1_5"]
            + 0.25 * row["uniqueness_1_5"]
            + 0.20 * row["value_1_5"]
        )
        row.update({
            "children_allowed": children_allowed,
            "child_access_level": access_level,
            "child_policy_basis": policy_basis,
            "cultural_priority_1_5": cultural_score,
            "cultural_priority_basis": f"Category/type classification for {row['category_id']} with source-description markers.",
            "international_experience_1_5": round(international_score, 2),
            "international_experience_basis": "; ".join(tags) if tags else "No explicit nation, diaspora, faith, or global-culture tag detected.",
            "affordability_1_5": affordability_score,
            "affordability_basis": f"Mapped from price level '{row.get('price_level', 'unknown')}', separate from subjective value.",
            "nation_culture_tags": tags,
            "secondary_quality_1_5": round(secondary_quality, 2),
            "preference_order": "1 Culture • 2 International cultures • 3 Low price",
        })
        if children_allowed:
            eligible.append(row)
        else:
            excluded.append(row)
    return eligible, excluded


def geocode_query(row: dict[str, Any]) -> str:
    parts = [row.get("address"), row.get("city"), row.get("state"), row.get("zip")]
    text = ", ".join(str(part) for part in parts if part)
    if not row.get("address"):
        text = ", ".join(part for part in [row.get("venue"), row.get("city"), row.get("state")] if part)
    return text


def geocode_rows(rows: list[dict[str, Any]], cache_path: Path, session: requests.Session) -> None:
    cache: dict[str, Any] = {}
    if cache_path.exists():
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
    changed = False
    for index, row in enumerate(rows, 1):
        if row.get("latitude") is not None and row.get("longitude") is not None:
            continue
        query = geocode_query(row)
        if not query:
            row["geocode_status"] = "missing-address"
            continue
        key = slug_text(query)
        result = cache.get(key)
        if result is None:
            params = {
                "SingleLine": query,
                "f": "json",
                "maxLocations": 1,
                "outFields": "Match_addr,Addr_type",
            }
            response = session.get(
                "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates",
                params=params,
                timeout=25,
            )
            response.raise_for_status()
            candidates = response.json().get("candidates", [])
            if candidates:
                top = candidates[0]
                result = {
                    "lat": top.get("location", {}).get("y"),
                    "lon": top.get("location", {}).get("x"),
                    "score": top.get("score", 0),
                    "match": top.get("address", ""),
                }
            else:
                result = {"lat": None, "lon": None, "score": 0, "match": ""}
            cache[key] = result
            changed = True
            time.sleep(0.08)
        if result.get("lat") is not None and result.get("score", 0) >= 70:
            row["latitude"] = float(result["lat"])
            row["longitude"] = float(result["lon"])
            row["geocode_status"] = "matched"
            row["geocode_match"] = result.get("match", "")
            row["geocode_score"] = result.get("score", 0)
        else:
            row["geocode_status"] = "unmatched"
    if changed:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(cache, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def haversine_miles(lat: float, lon: float) -> float:
    radius = 3958.7613
    phi1, phi2 = math.radians(HOME_LAT), math.radians(lat)
    dphi = phi2 - phi1
    dlambda = math.radians(lon - HOME_LON)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


def route_rows(rows: list[dict[str, Any]], session: requests.Session) -> None:
    routed = [row for row in rows if row.get("latitude") is not None and row.get("longitude") is not None]
    for start in range(0, len(routed), 70):
        batch = routed[start : start + 70]
        coords = [f"{HOME_LON:.6f},{HOME_LAT:.6f}"] + [f"{r['longitude']:.6f},{r['latitude']:.6f}" for r in batch]
        url = "https://router.project-osrm.org/table/v1/driving/" + ";".join(coords)
        params = {"sources": "0", "annotations": "distance,duration"}
        try:
            response = session.get(url, params=params, timeout=90)
            response.raise_for_status()
            data = response.json()
            distances = data.get("distances", [[]])[0]
            durations = data.get("durations", [[]])[0]
        except (requests.RequestException, ValueError, IndexError):
            distances, durations = [], []
        for offset, row in enumerate(batch, 1):
            straight = haversine_miles(row["latitude"], row["longitude"])
            route_m = distances[offset] if offset < len(distances) else None
            route_s = durations[offset] if offset < len(durations) else None
            if route_m is not None:
                row["distance_miles"] = round(route_m / 1609.344, 1)
                row["drive_minutes"] = round(route_s / 60) if route_s is not None else None
                row["distance_method"] = "OSRM driving route"
            else:
                row["distance_miles"] = round(straight * 1.22 + 1.5, 1)
                row["drive_minutes"] = round(row["distance_miles"] * 1.45)
                row["distance_method"] = "Haversine fallback with road factor"
    for row in rows:
        if row.get("distance_miles") is None:
            row["distance_method"] = "Unavailable"
        destination = ", ".join(part for part in [row.get("address"), row.get("city"), row.get("state"), row.get("zip")] if part)
        row["directions_url"] = (
            "https://www.google.com/maps/dir/?api=1&origin="
            + quote_plus(HOME_ADDRESS)
            + "&destination="
            + quote_plus(destination or row["name"])
        )


def proximity_score(miles: float | None) -> float:
    if miles is None:
        return 1.0
    if miles <= 5:
        return 5.0
    if miles <= 15:
        return 4.7
    if miles <= 25:
        return 4.3
    if miles <= 40:
        return 3.7
    if miles <= 60:
        return 3.0
    if miles <= 90:
        return 2.2
    if miles <= 150:
        return 1.4
    return 0.5


def rating_score(rating: float | None, count: int | None) -> float:
    if rating is None:
        return 3.8
    count = max(0, count or 0)
    prior, strength = 4.1, 120
    return (rating * count + prior * strength) / (count + strength)


def preference_key(culture: float, international: float, affordability: float, secondary: float) -> int:
    digits = [int(round(value * 10)) for value in (culture, international, affordability, secondary)]
    key = digits[0]
    for digit in digits[1:]:
        key = key * LEXICOGRAPHIC_BASE + digit
    return key


def preference_score_100(key: int) -> float:
    minimum = preference_key(1.0, 1.0, 1.0, 1.0)
    maximum = preference_key(5.0, 5.0, 5.0, 5.0)
    return round(20.0 + 80.0 * (key - minimum) / (maximum - minimum), 1)


def score_rows(rows: list[dict[str, Any]]) -> None:
    timed = {"events-festivals-live-shows", "sports-live-games"}
    for row in rows:
        p = proximity_score(row.get("distance_miles"))
        r = rating_score(row.get("rating"), row.get("review_count"))
        row["proximity_score_1_5"] = round(p, 2)
        row["rating_score_1_5"] = round(r, 2)
        is_timed = row["category_id"] in timed
        d1, d2 = parse_date(row.get("start_date")), parse_date(row.get("end_date"))
        row["vacation_window"] = bool(d1 and d1 <= VACATION_END and (d2 or d1) >= VACATION_START)
        row["available_during_vacation"] = bool(not d1 or row["vacation_window"])
        row["availability_priority"] = 1 if (not is_timed or row["available_during_vacation"]) else 0
        components = {
            "family": row["family_fit_1_5"],
            "evidence": row["evidence_quality_1_5"],
            "proximity": p,
            "rating": r,
            "uniqueness": row["uniqueness_1_5"],
            "urgency": row["time_urgency_1_5"],
        }
        secondary_weights = TIMED_SECONDARY_WEIGHTS if is_timed else EVERGREEN_SECONDARY_WEIGHTS
        secondary_quality = sum(secondary_weights[key] * components[key] for key in secondary_weights)
        row["secondary_quality_1_5"] = round(secondary_quality, 2)
        row["preference_key"] = preference_key(
            row["cultural_priority_1_5"],
            row["international_experience_1_5"],
            row["affordability_1_5"],
            row["secondary_quality_1_5"],
        )
        row["ranking_key"] = row["availability_priority"] * (LEXICOGRAPHIC_BASE ** 4) + row["preference_key"]
        row["score_100"] = preference_score_100(row["preference_key"])
        miles = row.get("distance_miles")
        if miles is None:
            row["distance_tier"] = "Unknown"
        elif miles <= 25:
            row["distance_tier"] = "Local"
        elif miles <= 60:
            row["distance_tier"] = "Metro"
        elif miles <= 150:
            row["distance_tier"] = "Day trip"
        else:
            row["distance_tier"] = "Exceptional overnight"


def dedupe(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str]] = set()
    result: list[dict[str, Any]] = []
    for row in rows:
        key = (row["category_id"], slug_text(row["name"]), slug_text(row.get("city")))
        if key in seen:
            continue
        seen.add(key)
        result.append(row)
    return result


def apply_selection(rows: list[dict[str, Any]], category_order: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["category_id"]].append(row)
    selected: list[dict[str, Any]] = []
    summary: list[dict[str, Any]] = []
    for cat in category_order:
        pool = sorted(
            grouped.get(cat, []),
            key=lambda r: (
                -r["availability_priority"],
                -r["cultural_priority_1_5"],
                -r["international_experience_1_5"],
                -r["affordability_1_5"],
                -r["secondary_quality_1_5"],
                r.get("distance_miles") if r.get("distance_miles") is not None else 9999,
                r["name"],
            ),
        )
        pool_size = len(pool)
        publish_count = min(50, pool_size) if pool_size >= 50 else math.ceil(pool_size * 0.5)
        rule = "Top 50" if pool_size >= 50 else "Top 50% of verified pool (rounded up)"
        for rank, row in enumerate(pool, 1):
            row["pool_rank"] = rank
            row["pool_size"] = pool_size
            row["selection_rule"] = rule
            row["selected"] = rank <= publish_count
            if row["selected"]:
                row["rank"] = rank
                selected.append(row)
        selected_pool = pool[:publish_count]
        summary.append({
            "category_id": cat,
            "eligible_pool_size": pool_size,
            "published_count": publish_count,
            "selection_rule": rule,
            "geocoded_count": sum(1 for row in pool if row.get("latitude") is not None),
            "vacation_window_count": sum(1 for row in pool if row.get("vacation_window")),
            "children_allowed_count": sum(1 for row in pool if row.get("children_allowed")),
            "conditional_child_access_count": sum(1 for row in pool if row.get("child_access_level") == "Children allowed with conditions"),
            "cultural_priority_count": sum(1 for row in selected_pool if row.get("cultural_priority_1_5", 0) >= 4.0),
            "international_experience_count": sum(1 for row in selected_pool if row.get("international_experience_1_5", 0) >= 4.0),
            "affordable_count": sum(1 for row in selected_pool if row.get("affordability_1_5", 0) >= 4.0),
            "average_score": round(sum(row["score_100"] for row in selected_pool) / publish_count, 1) if publish_count else None,
            "average_distance_miles": round(sum(row.get("distance_miles", 0) for row in selected_pool if row.get("distance_miles") is not None) / max(1, sum(1 for row in selected_pool if row.get("distance_miles") is not None)), 1) if selected_pool else None,
        })
    return selected, summary


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "category_id", "rank", "name", "subtype", "score_100", "distance_miles", "drive_minutes",
        "distance_tier", "address", "city", "state", "zip", "start_date", "end_date", "start_time",
        "vacation_window", "children_allowed", "child_access_level", "child_policy_basis", "age_notes",
        "cultural_priority_1_5", "cultural_priority_basis", "international_experience_1_5", "international_experience_basis",
        "affordability_1_5", "affordability_basis", "nation_culture_tags",
        "secondary_quality_1_5", "preference_key", "ranking_key", "preference_order", "price_level", "rating", "review_count", "family_fit_1_5", "uniqueness_1_5",
        "evidence_quality_1_5", "value_1_5", "proximity_score_1_5", "rating_score_1_5",
        "estimated_visit_hours", "indoor_outdoor", "why_good", "caveat", "cost_note",
        "official_url", "corroborating_url", "directions_url", "checked_date", "selection_rule", "pool_size",
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--skip-geocode", action="store_true")
    parser.add_argument("--skip-routes", action="store_true")
    args = parser.parse_args()
    project = args.project_root.resolve()
    categories = json.loads((project / "source" / "categories.json").read_text(encoding="utf-8"))
    category_order = [item["id"] for item in sorted(categories, key=lambda item: item["order"])]
    raw_files = sorted((project / "research" / "raw").glob("*.json"))
    normalized: list[dict[str, Any]] = []
    excluded_out_of_state: list[dict[str, str]] = []
    excluded_source_status: list[dict[str, str]] = []
    source_metadata: list[dict[str, Any]] = []
    for path in raw_files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        source_metadata.append({"file": str(path.relative_to(project)), "metadata": payload.get("metadata", {}) if isinstance(payload, dict) else {}})
        for raw in flatten_payload(payload):
            row = normalize_row(raw, str(path.relative_to(project)))
            if row and row["category_id"] in category_order:
                status = slug_text(row.get("operational_status"))
                if not row.get("source_eligible", True) or status in {
                    "closed", "inactive", "permanently closed", "cancelled", "canceled", "ineligible",
                }:
                    excluded_source_status.append({
                        "name": row["name"],
                        "status": str(row.get("operational_status") or "source-ineligible"),
                        "category_id": row["category_id"],
                    })
                    continue
                normalized_state = str(row.get("state") or "GA").strip().upper()
                if normalized_state not in {"GA", "GEORGIA"}:
                    excluded_out_of_state.append({
                        "name": row["name"],
                        "state": str(row.get("state") or ""),
                        "category_id": row["category_id"],
                    })
                    continue
                normalized.append(row)
    rows = dedupe(normalized)
    rows, excluded_child_access = annotate_preferences(rows)
    session = requests.Session()
    session.headers.update({"User-Agent": "holiday2026-family-guide/1.0 local research"})
    cache_path = project / "research" / "cache" / "arcgis-geocode.json"
    if not args.skip_geocode:
        geocode_rows(rows, cache_path, session)
    if not args.skip_routes:
        route_rows(rows, session)
    else:
        for row in rows:
            if row.get("latitude") is not None:
                row["distance_miles"] = round(haversine_miles(row["latitude"], row["longitude"]) * 1.22 + 1.5, 1)
                row["drive_minutes"] = round(row["distance_miles"] * 1.45)
                row["distance_method"] = "Haversine fallback with road factor"
    score_rows(rows)
    selected, summary = apply_selection(rows, category_order)
    output_dir = project / "artifacts" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "all-eligible-candidates.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "ranked-places.json").write_text(json.dumps(selected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "category-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "research-sources.json").write_text(json.dumps(source_metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(output_dir / "ranked-places.csv", selected)
    report = {
        "ok": True,
        "checked_date": CHECKED_DATE,
        "raw_files": len(raw_files),
        "eligible_candidates": len(rows),
        "selected_candidates": len(selected),
        "category_counts": dict(Counter(row["category_id"] for row in selected)),
        "child_access_filter": {
            "required": True,
            "eligible": len(rows),
            "excluded": len(excluded_child_access),
            "conditional_eligible": sum(1 for row in rows if row.get("child_access_level") == "Children allowed with conditions"),
            "excluded_rows": [
                {
                    "name": row["name"],
                    "category_id": row["category_id"],
                    "basis": row["child_policy_basis"],
                }
                for row in excluded_child_access
            ],
        },
        "preference_ranking": {
            "mode": "strict lexicographic",
            "timed_feasibility_precondition": "Dated events and games usable during July 11-20 rank before later dates; evergreen activities remain usable.",
            "priority_order": ["culture", "international cultures", "low price", "secondary quality"],
            "evergreen_secondary_weights": EVERGREEN_SECONDARY_WEIGHTS,
            "timed_secondary_weights": TIMED_SECONDARY_WEIGHTS,
        },
        "unmatched_geocodes": sum(1 for row in rows if row.get("latitude") is None),
        "out_of_state_excluded": excluded_out_of_state,
        "source_status_excluded": excluded_source_status,
        "outputs": [
            "artifacts/data/all-eligible-candidates.json",
            "artifacts/data/ranked-places.json",
            "artifacts/data/ranked-places.csv",
            "artifacts/data/category-summary.json",
            "artifacts/data/research-sources.json",
        ],
    }
    (output_dir / "dataset-build-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
