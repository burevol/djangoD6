from datetime import datetime, timedelta
from django.db.models.signals import pre_save
from django.dispatch import receiver  # импортируем нужный декоратор
from .models import Post


# в декоратор передаётся первым аргументом сигнал, на который будет реагировать эта функция, и в отправители надо передать также модель
@receiver(pre_save, sender=Post)
def notify_check_post_score(sender, instance, **kwargs):
    current_date = datetime.today()
    previous_date = current_date - timedelta(days=1)
    post_count = Post.objects.filter(author=instance.author, date__gte=previous_date, date__lte=current_date).count()
    if post_count > 3:
        raise Exception('Запрещено отправлять больше 3х статей в сутки!')