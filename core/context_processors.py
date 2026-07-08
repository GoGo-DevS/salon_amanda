from django.db.models import Q
from django.utils import timezone
from .models import Promocion


def promocion_activa(request):
    hoy = timezone.now().date()
    promo = (
        Promocion.objects
        .filter(activa=True)
        .filter(Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=hoy))
        .order_by('-id')
        .first()
    )
    return {'promo_activa': promo}
