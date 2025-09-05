from django.conf import settings
from .models import Route, Upstream




def bootstrap_env_upstreams():
    """Ensure env-defined upstreams exist in DB so admin can tweak them."""
    for cfg in getattr(settings, "UPSTREAMS", []):
        up, _ = Upstream.objects.get_or_create(name=cfg["name"], defaults={
        "kind": cfg["kind"],
        "base_url": cfg["base_url"],
        "token": cfg.get("token") or "",
        "tps": cfg.get("tps") or 20,
        })
        # Create default route for DEFAULT_COUNTRY if none exists
        Route.objects.get_or_create(country=settings.DEFAULT_COUNTRY, upstream=up)




def select_route(country: str | None = None) -> Route:
    """Pick a route. For MVP: one route per country; fallback to DEFAULT_COUNTRY."""
    country = (country or settings.DEFAULT_COUNTRY).upper()
    try:
        return Route.objects.select_related("upstream").get(country=country)
    except Route.DoesNotExist:
        # fallback to ANY route
        return Route.objects.select_related("upstream").first()