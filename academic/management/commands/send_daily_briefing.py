import os
import asyncio
from django.core.management.base import BaseCommand
from django.utils import timezone
from telegram import Bot
from academic.models import Task, WeekendPlan, Project
from dotenv import load_dotenv

load_dotenv()


class Command(BaseCommand):
    help = 'Trimite un raport automat pe Telegram cu task-urile și sprintul curent'

    def handle(self, *args, **kwargs):
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')

        if not token or not chat_id:
            self.stdout.write(self.style.ERROR("Token-ul sau Chat ID-ul de Telegram lipsesc din .env!"))
            return

        bot = Bot(token=token)

        # Pregătire date
        active_plan = WeekendPlan.objects.filter(is_active=True).first()
        urgent_tasks = Task.objects.filter(is_completed=False).order_by('due_date', '-priority')[:5]
        active_projects = Project.objects.all().order_by('deadline')[:3]

        message = "☀️ *Bună dimineața! Raportul tău zilnic - Academic Hub*\n\n"

        if active_plan:
            message += f"⚡ *Sprint Activ:* {active_plan.title}\n"
            message += f"📊 Progres Sprint: *{active_plan.progress_percentage}%* ({active_plan.completed_tasks_count}/{active_plan.total_tasks})\n\n"

        if urgent_tasks.exists():
            message += "🔥 *Task-uri Pripritare / Urgente:*\n"
            for t in urgent_tasks:
                message += f"• `[{t.id}]` {t.title} ({t.subject.code})\n"
            message += "\n"

        if active_projects.exists():
            message += "📁 *Următoarele Deadline-uri Proiecte:*\n"
            for p in active_projects:
                message += f"• *{p.title}* ({p.subject.code}) - {p.progress_percentage}% gata\n"

        message += "\n💪 Spor la lucru azi!"

        # Trimitere mesaj asincron
        asyncio.run(bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown'))
        self.stdout.write(self.style.SUCCESS("Raportul zilnic a fost trimis pe Telegram!"))