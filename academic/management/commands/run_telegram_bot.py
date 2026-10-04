import os
from django.core.management.base import BaseCommand
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from academic.models import Task, WeekendPlan, DebugLog, Subject, Project
from dotenv import load_dotenv

load_dotenv()


class Command(BaseCommand):
    help = 'Pornește botul de Telegram conectat la Django'

    def handle(self, *args, **kwargs):
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            self.stdout.write(self.style.ERROR("TELEGRAM_BOT_TOKEN nu este setat în fișierul .env!"))
            return

        self.stdout.write(self.style.SUCCESS("Botul de Telegram a pornit și ascultă comenzi..."))

        app = ApplicationBuilder().token(token).build()

        # Înregistrare comenzi
        app.add_handler(CommandHandler("start", self.cmd_start))
        app.add_handler(CommandHandler("sprint", self.cmd_sprint))
        app.add_handler(CommandHandler("done", self.cmd_done))
        app.add_handler(CommandHandler("raport", self.cmd_raport))

        app.run_polling()

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = (
            "🎓 *Academic Hub Telegram Bot*\n\n"
            "Comenzi disponibile:\n"
            "• /raport - Raportul detaliat al zilei\n"
            "• /sprint - Vezi task-urile din sprintul de weekend\n"
            "• /done <id> - Bifează un task ca fiind completat\n"
        )
        await update.message.reply_text(msg, parse_mode='Markdown')

    async def cmd_sprint(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        plan = WeekendPlan.objects.filter(is_active=True).first()
        if not plan:
            await update.message.reply_text("Nu există niciun plan de weekend activ momentan.")
            return

        tasks = plan.tasks.all()
        msg = f"⚡ *{plan.title}*\nProgres: *{plan.progress_percentage}%*\n\n"
        
        for task in tasks:
            status = "✅" if task.is_completed else "❌"
            msg += f"{status} `[{task.id}]` *{task.title}* ({task.subject.code})\n"

        await update.message.reply_text(msg, parse_mode='Markdown')

    async def cmd_done(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Folosește comanda așa: `/done <id_task>` (ex: `/done 3`)", parse_mode='Markdown')
            return

        try:
            task_id = int(context.args[0])
            task = Task.objects.get(id=task_id)
            task.is_completed = True
            task.save()
            await update.message.reply_text(f"🎉 Task-ul *'{task.title}'* a fost marcat ca finalizat!", parse_mode='Markdown')
        except Task.DoesNotExist:
            await update.message.reply_text("❌ Nu am găsit niciun task cu acest ID.")
        except ValueError:
            await update.message.reply_text("❌ ID-ul trebuie să fie un număr.")

    async def cmd_raport(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generează și trimite raportul detaliat al zilei direct în chat"""
        active_plan = WeekendPlan.objects.filter(is_active=True).first()
        urgent_tasks = Task.objects.filter(is_completed=False).order_by('due_date', '-priority')[:5]
        active_projects = Project.objects.all().order_by('deadline')[:3]

        msg = "☀️ *Raport Academic Hub*\n\n"

        if active_plan:
            msg += f"⚡ *Sprint Activ:* {active_plan.title}\n"
            msg += f"📊 Progres: *{active_plan.progress_percentage}%* ({active_plan.completed_tasks_count}/{active_plan.total_tasks})\n\n"

        if urgent_tasks.exists():
            msg += "🔥 *Task-uri Urgente:*\n"
            for t in urgent_tasks:
                msg += f"• `[{t.id}]` {t.title} ({t.subject.code})\n"
            msg += "\n"

        if active_projects.exists():
            msg += "📁 *Proiecte Active:*\n"
            for p in active_projects:
                msg += f"• *{p.title}* ({p.subject.code}) - {p.progress_percentage}% gata\n"

        await update.message.reply_text(msg, parse_mode='Markdown')