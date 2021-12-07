import logging

from datetime import datetime, timedelta
from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


from newsportal.models import Post, Category

logger = logging.getLogger(__name__)


def my_job():
    current_date = datetime.today()
    previous_date = current_date - timedelta(days=7)
    messages = []
    text_body = []
    users = User.objects.all()
    for user in users:
        posts = Post.objects.filter(category__in=user.category_set.all(), date__gte=previous_date, date__lte=current_date)
        for post in posts:
            message = {'header': post.header, 'text': post.text, 'id': post.id}
            messages.append(message)
            text_body.append(post.text[:50])

        html_content = render_to_string('weekly_mail.html',
                                        {'username': user.username, 'messages': messages})
        msg = EmailMultiAlternatives(
            subject='Новые статьи за неделю в твоих любимых разделах!',
            from_email='appointment@silicon-chronicles.ru',
            body='\n'.join(text_body),
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()




# функция, которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day_of_week="sun", hour="00", minute="00"),
            # То же, что и интервал, но задача тригера таким образом более понятна django
            id="my_job",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="sat", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")