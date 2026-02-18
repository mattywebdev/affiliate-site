from django import template

register = template.Library()

@register.simple_tag
def star_states(rating):
    """
    rating: Decimal/float (0..5) with halves.
    returns: list like ["full","full","full","half","empty"]
    """
    try:
        r = float(rating)
    except (TypeError, ValueError):
        r = 0.0

    r = max(0.0, min(5.0, r))
    full = int(r)
    half = 1 if (r - full) >= 0.5 else 0
    empty = 5 - full - half

    return (["full"] * full) + (["half"] * half) + (["empty"] * empty)
