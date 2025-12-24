import json
import re
import httpx
from typing import Any

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from films.models import WatchedFilm, Rating, Review, Mood
from api.serializers import RecommendationChatSerializer

from drf_spectacular.utils import extend_schema, OpenApiResponse


# -----------------------------
# Optional DB logs (varsa kullan)
# -----------------------------
def _log_moderation(*, request, direction: str, text: str, allow: bool, flags: list[str], reason: str):
    """
    direction: "input" | "output"
    films.models.ModerationLog varsa kaydeder.
    Yoksa sessizce geçer.
    """
    try:
        from films.models import ModerationLog
    except Exception:
        return

    try:
        user = getattr(request, "user", None)
        ModerationLog.objects.create(
            user=user if getattr(user, "is_authenticated", False) else None,
            direction=direction,  # ✅ "input"/"output"
            text=(text or "")[:5000],
            allow=bool(allow),
            flags=flags or [],
            reason=(reason or "")[:300],
        )
    except Exception:
        return


def _log_recommendation(
    *,
    request,
    user_message: str,
    blocked: bool,
    answer_text: str,
    items: list[dict],
    flags: list[str],
    reason: str,
):
    """
    films.models.RecommendationLog varsa kaydeder.
    Yoksa sessizce geçer.
    NOT: RecommendationLog modelinde path/ip yoksa buraya koyma.
    """
    try:
        from films.models import RecommendationLog
    except Exception:
        return

    try:
        user = getattr(request, "user", None)

        # items güvenliği: sadece dict listesi kalsın
        safe_items: list[dict] = []
        for it in items or []:
            if isinstance(it, dict):
                safe_items.append(it)

        RecommendationLog.objects.create(
            user=user,  # IsAuthenticated zaten, null bırakmıyoruz
            user_message=(user_message or "")[:2000],
            blocked=bool(blocked),
            answer_text=(answer_text or "")[:5000] if answer_text else None,
            items=safe_items,
            flags=flags or [],
            reason=(reason or "")[:500] if reason else None,
        )
    except Exception:
        return


# -----------------------------
# Helpers
# -----------------------------
def _deepseek_chat(
    *,
    api_key: str,
    chat_url: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
) -> httpx.Response:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
    }

    with httpx.Client(timeout=40.0) as client:
        resp = client.post(
            chat_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

    return resp


def _parse_answer(data: dict) -> str | None:
    try:
        return data["choices"][0]["message"]["content"]
    except Exception:
        return data.get("output_text") or data.get("text") or data.get("message") or None


def _strip_code_fences(text: str) -> str:
    if not text:
        return text
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z]*\s*", "", t)
        t = re.sub(r"\s*```$", "", t)
        t = t.strip()
    return t


def _safe_json_loads(text: str) -> dict | None:
    """
    Text içinden JSON parse etmeye çalışır:
    - direkt json.loads
    - olmazsa ilk {...} bloğunu bulup loads
    """
    if not text:
        return None

    t = _strip_code_fences(text)

    try:
        obj = json.loads(t)
        return obj if isinstance(obj, dict) else None
    except Exception:
        pass

    m = re.search(r"\{.*\}", t, flags=re.DOTALL)
    if not m:
        return None

    try:
        obj = json.loads(m.group(0))
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def _moderate_with_llm(*, api_key: str, chat_url: str, model: str, text: str) -> dict:
    """
    Returns:
    {
      "allow": true/false,
      "flags": ["spoiler","profanity","hate","harassment","sexual", ...],
      "reason": "short"
    }
    Parse patlarsa konservatif: block.
    """
    system_prompt = (
        "You are a strict content moderation classifier for a movie app.\n"
        "Classify the TEXT for:\n"
        "- spoiler (reveals OR ASKS for plot twists/endings/deaths/ending)\n"
        "- profanity\n"
        "- hate / racism / discrimination\n"
        "- harassment / bullying\n"
        "- sexual / explicit content\n\n"
        "Return ONLY valid JSON (no markdown, no extra text).\n"
        'Schema: {"allow": boolean, "flags": string[], "reason": string}\n'
        "Rules:\n"
        "- If ANY exists, allow=false and include relevant flags.\n"
        "- If none exists, allow=true and flags=[]\n"
        "- reason must be short (max 1 sentence).\n"
    )

    user_prompt = f"TEXT:\n{text}\n\nReturn JSON only."

    resp = _deepseek_chat(
        api_key=api_key,
        chat_url=chat_url,
        model=model,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.0,
    )

    if resp.status_code >= 400:
        return {
            "allow": False,
            "flags": ["moderation_http_error"],
            "reason": f"Moderation LLM failed ({resp.status_code}).",
        }

    raw = resp.json()
    content = _parse_answer(raw) or ""

    obj = _safe_json_loads(content)
    if not obj:
        return {
            "allow": False,
            "flags": ["moderation_parse_error"],
            "reason": "Moderation JSON parse failed.",
        }

    allow = bool(obj.get("allow", False))
    flags = obj.get("flags", [])
    reason = obj.get("reason", "")

    if not isinstance(flags, list):
        flags = [str(flags)]

    flags = [str(f).strip().lower() for f in flags if str(f).strip()]
    return {"allow": allow, "flags": flags, "reason": str(reason)[:300]}


def _items_to_answer(items: list[dict]) -> str:
    """items -> okunabilir bullet answer"""
    lines: list[str] = []
    for it in items or []:
        title = str(it.get("title", "")).strip()
        year = it.get("year", None)
        reason = str(it.get("reason", "")).strip()

        if not title:
            continue

        if year:
            lines.append(f"- {title} ({year}) — {reason}".strip())
        else:
            lines.append(f"- {title} — {reason}".strip())

    return "\n".join(lines).strip() or "(Cevap boş geldi)"


def _get_imdb_id(obj: Any) -> str | None:
    direct = getattr(obj, "imdb_id", None)
    if direct:
        return direct
    film = getattr(obj, "film", None)
    if film:
        return getattr(film, "imdb_id", None)
    return None


# -----------------------------
# View
# -----------------------------
class RecommendationChatView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=RecommendationChatSerializer,
        responses={
            200: OpenApiResponse(description="Recommendation answer (or blocked)"),
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Unauthorized"),
            502: OpenApiResponse(description="LLM request failed"),
        },
    )
    def post(self, request):
        user = request.user

        serializer = RecommendationChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_message = serializer.validated_data["user_message"].strip()

        api_key_raw = getattr(settings, "DEEPSEEK_API_KEY", None)
        api_key = (api_key_raw or "").strip() if api_key_raw else ""
        base_url = getattr(settings, "DEEPSEEK_BASE", "https://api.deepseek.com/v1")
        model = getattr(settings, "DEEPSEEK_MODEL", "deepseek-chat")

        print(
            ">>> RECO_CHAT HIT | user_id=",
            getattr(user, "id", None),
            "| has_key=",
            bool(api_key),
            "| key_length=",
            len(api_key) if api_key else 0,
            "| key_prefix=",
            (api_key[:10] + "...") if api_key and len(api_key) > 10 else ("EMPTY" if not api_key else api_key[:10]),
            "| base=",
            base_url,
            "| model=",
            model,
            "| settings_module=",
            settings.SETTINGS_MODULE if hasattr(settings, 'SETTINGS_MODULE') else "unknown",
            flush=True,
        )

        if not api_key:
            _log_recommendation(
                request=request,
                user_message=user_message,
                blocked=False,
                answer_text="DEEPSEEK_API_KEY boş. (Demo mode)",
                items=[],
                flags=[],
                reason="demo_mode",
            )
            return Response(
                {
                    "blocked": False,
                    "message": "DEEPSEEK_API_KEY boş. Endpoint çalışıyor ama LLM'e gitmiyor. (Demo mode)",
                    "items": [],
                },
                status=status.HTTP_200_OK,
            )

        chat_url = base_url.rstrip("/") + "/chat/completions"

        # ✅ INPUT moderation
        mod_in = _moderate_with_llm(api_key=api_key, chat_url=chat_url, model=model, text=user_message)

        _log_moderation(
            request=request,
            direction="input",
            text=user_message,
            allow=mod_in.get("allow", False),
            flags=mod_in.get("flags", []),
            reason=mod_in.get("reason", ""),
        )

        if not mod_in.get("allow", False):
            _log_recommendation(
                request=request,
                user_message=user_message,
                blocked=True,
                answer_text="İstek engellendi (moderation_in).",
                items=[],
                flags=mod_in.get("flags", []),
                reason=mod_in.get("reason", ""),
            )
            return Response(
                {
                    "blocked": True,
                    "message": "Bu istek spoiler/uygunsuz içerik içerdiği için yanıtlanamaz. Spoilersız film önerisi istersen tür/ruh hali söyle 🙂",
                    "flags": mod_in.get("flags", []),
                    "reason": mod_in.get("reason", ""),
                    "items": [],
                },
                status=status.HTTP_200_OK,
            )

        # ✅ history
        watched_qs = WatchedFilm.objects.filter(user=user).select_related("film").order_by("-id")[:50]
        ratings_qs = Rating.objects.filter(user=user).select_related("film").order_by("-id")[:50]
        reviews_qs = Review.objects.filter(user=user).select_related("film").order_by("-id")[:30]
        moods_qs = Mood.objects.filter(user=user).select_related("film").order_by("-id")[:30]

        watched = []
        for w in watched_qs:
            imdb = _get_imdb_id(w)
            if imdb:
                watched.append(imdb)

        ratings = []
        for r in ratings_qs:
            imdb = _get_imdb_id(r)
            if imdb:
                ratings.append({"imdb_id": imdb, "rating": getattr(r, "overall_rating", None)})

        reviews = []
        for rv in reviews_qs:
            imdb = _get_imdb_id(rv)
            if imdb:
                txt = (getattr(rv, "content", None) or getattr(rv, "text", "") or "")[:400]
                reviews.append({"imdb_id": imdb, "text": txt})

        moods = []
        for m in moods_qs:
            imdb = _get_imdb_id(m)
            if imdb:
                moods.append({
                    "imdb_id": imdb,
                    "mood_before": getattr(m, "mood_before", None),
                    "mood_after": getattr(m, "mood_after", None)
                })

        context = {
            "user_id": user.id,
            "has_history": bool(watched or ratings or reviews or moods),
            "watched_imdb_ids": watched,
            "recent_ratings": ratings,
            "recent_reviews": reviews,
            "recent_moods": moods,
        }

        # ✅ recommendation prompt
        system_prompt = (
            "You are a movie recommendation assistant.\n"
            "You MUST return ONLY valid JSON. No markdown. No extra text.\n"
            "Return 3-5 movie recommendations.\n"
            "Use the user's history if available (watched films, ratings, reviews, mood tracking).\n"
            "If the user has no history, do cold-start based on the user's message.\n"
            "Never reveal spoilers or plot twists.\n"
            "Keep it short.\n"
            "JSON schema:\n"
            "{\n"
            '  "items": [\n'
            "    {\n"
            '      "title": "string",\n'
            '      "year": 2000,\n'
            '      "reason": "string",\n'
            '      "tags": ["string"]\n'
            "    }\n"
            "  ]\n"
            "}\n"
        )

        user_prompt = (
            "USER_CONTEXT (JSON):\n"
            f"{json.dumps(context, ensure_ascii=False)}\n\n"
            f"USER_MESSAGE:\n{user_message}\n"
        )

        try:
            resp = _deepseek_chat(
                api_key=api_key,
                chat_url=chat_url,
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.7,
            )

            if resp.status_code >= 400:
                _log_recommendation(
                    request=request,
                    user_message=user_message,
                    blocked=True,
                    answer_text="LLM HTTP error",
                    items=[],
                    flags=["llm_http_error"],
                    reason=resp.text[:500],
                )
                return Response(
                    {
                        "error": "LLM request failed",
                        "status_code": resp.status_code,
                        "body": resp.text,
                        "chat_url": chat_url,
                    },
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            data = resp.json()
            raw_text = _parse_answer(data) or ""

            rec_obj = _safe_json_loads(raw_text)
            if (not rec_obj) or ("items" not in rec_obj) or (not isinstance(rec_obj.get("items"), list)):
                _log_recommendation(
                    request=request,
                    user_message=user_message,
                    blocked=True,
                    answer_text="Recommendation JSON parse failed",
                    items=[],
                    flags=["recommendation_parse_error"],
                    reason=raw_text[:500],
                )
                return Response(
                    {"error": "Recommendation JSON parse failed", "raw_text": raw_text[:2000]},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            items = rec_obj.get("items", []) or []
            answer_text = _items_to_answer(items)

            # ✅ OUTPUT moderation
            mod_out = _moderate_with_llm(api_key=api_key, chat_url=chat_url, model=model, text=answer_text)

            _log_moderation(
                request=request,
                direction="output",
                text=answer_text,
                allow=mod_out.get("allow", False),
                flags=mod_out.get("flags", []),
                reason=mod_out.get("reason", ""),
            )

            if not mod_out.get("allow", False):
                _log_recommendation(
                    request=request,
                    user_message=user_message,
                    blocked=True,
                    answer_text="Cevap engellendi (moderation_out).",
                    items=[],
                    flags=mod_out.get("flags", []),
                    reason=mod_out.get("reason", ""),
                )
                return Response(
                    {
                        "blocked": True,
                        "message": "Bu içerik güvenlik politikaları nedeniyle gösterilemiyor.",
                        "flags": mod_out.get("flags", []),
                        "reason": mod_out.get("reason", ""),
                        "items": [],
                    },
                    status=status.HTTP_200_OK,
                )

            # ✅ success log
            _log_recommendation(
                request=request,
                user_message=user_message,
                blocked=False,
                answer_text=answer_text,
                items=items,
                flags=[],
                reason="ok",
            )

            return Response({"blocked": False, "message": answer_text, "items": items}, status=status.HTTP_200_OK)

        except Exception as e:
            _log_recommendation(
                request=request,
                user_message=user_message,
                blocked=True,
                answer_text="server_exception",
                items=[],
                flags=["server_exception"],
                reason=str(e)[:500],
            )
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
