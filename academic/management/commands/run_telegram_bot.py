import os 
import django
from django.core.management.base import BaseCommand
from telegram import Update
from telegram.ext import ApplicationBuilder,CommandHandler,ContextTypes
from academic.models import Task,WeekendPlan,DebugLog,Subject
from dotenv import load_dotenv
load_dotenv()

class Command(BaseCommand):
    help='Porneste botul de telegram conectat la Django'
    
    def handle(self,*args, **kwargs):
        token=os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            self.stdout.write(self.style.ERROR("Telegram nu este setat"))
            return
        self.stdout.write(self.style.SUCCESS("Botul de telegram  a pornit si asculta"))
        app=ApplicationBuilder().token(token).build()
        
        app.add_handler(CommandHandler("start",self.cmd_start))
        app.add_handler(CommandHandler("sprint", self.cmd_sprint))
        app.add_handler(CommandHandler("done", self.cmd_done))
        app.add_handler(CommandHandler("raport", self.cmd_raport))
        
        app.run_polling()
        
    async def cmd_start(self,update:Update,context:ContextTypes.DEFAULT_TYPE):
        msg=(
            "🎓 *Academic Hub Telegram Bot*\n\n"
            "Comenzi disponibile:\n"
            "• /sprint - Vezi task-urile din sprintul de weekend\n"
            "• /done <id> - Bifează un task ca fiind completat\n"
        )
        await update.message.reply_text(msg,parse_mode='Markdown')
        
    async def cmd_sprint(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Preluăm planul activ direct din ORM-ul Django
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