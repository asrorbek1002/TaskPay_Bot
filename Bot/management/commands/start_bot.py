from django.core.management.base import BaseCommand
from telegram.ext import CommandHandler, ChatJoinRequestHandler, ConversationHandler, Updater, MessageHandler, Filters, CallbackQueryHandler
from Config.settings import BOT_TOKEN
from ...handlers.restart import restart
from ...handlers.register_handler import cancel, start, handle_admin_confirmation, ask_last_name, end_registration, ask_user_name
from ...handlers.balance import balance_menu
from ...handlers.add_task import start_add_task, get_task_caption, get_task_name, get_task_price, get_task_url, end_task_add
from ...handlers.earn_money import earn_money_menu, with_task, by_refferal
from ...handlers.chek_task import handle_task_completion, handler_task_chek_with_screnshot, check_notcheck_btn
from ...handlers.request_join import handle_join_request
from ...handlers.add_channel import add_channel_conv_handler
from ...handlers.admin_menu import admin_menu, Bot_Settings_menu
from ...handlers.send_message import handler_send_message
from ...handlers.withdraw_money import choosewithdrawtype, handlerwithdrawtype, endWithdraw, get_withdraw_price, handler_check_paymen
from ...handlers.bot_guide import start_change_guide, save_guide, get_bot_guide
from ...handlers.appeal import start_get_appeal, get_appeal_text, end_appeal, send_reply, reply_appeal_to_user
from ...handlers.botstats import stats_command
from ...handlers.add_admin import admin_conversation_handler
from ...handlers.delete_Task import delete_task_handler
from ...handlers.full_register import passport_handler
from ...handlers.depozite import deposit_handler
from ...handlers.change_card_number import change_card_number_handler
from ...handlers.set_dailiy_limit import set_daily_limit_handler
from ...handlers.delete_admin import delete_admin_handler
from ...handlers.delete_channel import remove_channel_conv_handler
from ...handlers.Usersdepozit import check_depozite, set_user_depozite

token = BOT_TOKEN

# Bosqichlarning holatlari
FIRST_NAME, LAST_NAME, PHONE_NUMBER, PASSPORT_PIC = range(4)
END = ConversationHandler.END

def cancel_appeal(update, context):
    update.callback_query.edit_message_text("<b>Bekor qilindi</b>", parse_mode="HTML")
    return ConversationHandler.END


class Command(BaseCommand):
    help = 'Starts the Telegram bot'

    def handle(self, *args, **kwargs):
        updater = Updater(token, use_context=True)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", set_user_depozite, Filters.regex("setuserd_")))

        conversation_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],  # /start buyrug'i orqali jarayonni boshlash
            states={
                FIRST_NAME: [MessageHandler(Filters.text & ~Filters.command, ask_user_name)],
                LAST_NAME: [MessageHandler(Filters.text & ~Filters.command, ask_last_name)],
                PHONE_NUMBER: [MessageHandler(Filters.contact, end_registration)],
            },
            fallbacks=[CommandHandler('cancel', cancel)],  # /cancel buyrug'i orqali jarayonni bekor qilish
        )
        dp.add_handler(CallbackQueryHandler(handle_admin_confirmation, pattern='^(confirm|cancel)'))
        dp.add_handler(CallbackQueryHandler(check_notcheck_btn, pattern='^(chkad_|ntchkd_)'))
        dp.add_handler(ChatJoinRequestHandler(handle_join_request))
        dp.add_handler(conversation_handler)
        dp.add_handler(MessageHandler(Filters.regex(r"^💰 Hisobim$"), balance_menu))
        dp.add_handler(MessageHandler(Filters.regex(r"^💵 Pul ishlash$"), earn_money_menu))
        dp.add_handler(CallbackQueryHandler(with_task, pattern="^with_task$"))
        dp.add_handler(CallbackQueryHandler(by_refferal, pattern="^by_referral$"))
        dp.add_handler(handler_send_message())
        task_hand = ConversationHandler(
            entry_points=[CallbackQueryHandler(start_add_task, pattern='^add_task$')],
            states={
                'START_ADD_TASK': [MessageHandler(Filters.text & ~Filters.command, get_task_name)],
                'GET_TASK_NAME': [MessageHandler(Filters.text & ~Filters.command, get_task_url)], 
                'GET_TASK_URL': [MessageHandler(Filters.text & ~Filters.command, get_task_caption)],
                'GET_TASK_CAPTION': [MessageHandler(Filters.text & ~Filters.command, get_task_price,)],
                'GET_TASK_PRICE': [CallbackQueryHandler(end_task_add)] #end_task_add
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
        dp.add_handler(task_hand)
        dp.add_handler(add_channel_conv_handler)
        task_chek_hand = ConversationHandler(
            entry_points=[CallbackQueryHandler(handle_task_completion, pattern="^cht_")],
            states={
                'TGCHEKSCREEN': [MessageHandler(Filters.photo, handler_task_chek_with_screnshot)]
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
        dp.add_handler(task_chek_hand)
        dp.add_handler(CommandHandler('admin', admin_menu))
        dp.add_handler(MessageHandler(Filters.regex(r"^🏦 Pulni yechish$"), choosewithdrawtype))
        guide_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(start_change_guide, pattern='^change_guide$')],
            states={
                'START_CHANGE_GUIDE': [MessageHandler(Filters.text & ~Filters.command, save_guide)]
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
        dp.add_handler(guide_handler)
        dp.add_handler(MessageHandler(Filters.regex(r"^📚 Qo'llanma$"), get_bot_guide))
        hand_apeal = ConversationHandler(
            entry_points=[MessageHandler(Filters.regex(r"^📨 Murojaat$"), start_get_appeal)],
            states={
                'START_GET_APPEAL': [MessageHandler(Filters.text & ~Filters.command, get_appeal_text)],
                'GET_APPEAL_TEXT': [MessageHandler(Filters.text & ~Filters.command, end_appeal)]

            },
            fallbacks=[CallbackQueryHandler(cancel_appeal, pattern='back_appeal')]
        )
        dp.add_handler(hand_apeal)
        reply_hand = ConversationHandler(
            entry_points=[CallbackQueryHandler(reply_appeal_to_user, pattern="^replyappeal_")],
            states={
                "START_REPLY": [MessageHandler(Filters.text & ~Filters.command, send_reply)]
                },
            fallbacks=[]
        )
        dp.add_handler(reply_hand)
        dp.add_handler(CallbackQueryHandler(stats_command, pattern=r'^botstats$'))
        handler_withdraw = ConversationHandler(
            entry_points=[CallbackQueryHandler(handlerwithdrawtype, pattern="^wto_")],
            states={
                'START_WITHDRAW': [MessageHandler(Filters.text & ~Filters.command, get_withdraw_price)],
                'GET_WITHDRAW_PRICE': [MessageHandler(Filters.text & ~Filters.command, endWithdraw)]
            },
            fallbacks=[]
        )
        dp.add_handler(handler_withdraw)
        dp.add_handler(CallbackQueryHandler(handler_check_paymen, pattern=r"^(okm|nokm)"))
        dp.add_handler(admin_conversation_handler)
        dp.add_handler(delete_task_handler)
        dp.add_handler(passport_handler)
        dp.add_handler(deposit_handler)
        dp.add_handler(change_card_number_handler)
        dp.add_handler(CallbackQueryHandler(Bot_Settings_menu, pattern=r"^bot_settings$"))
        dp.add_handler(set_daily_limit_handler)
        dp.add_handler(delete_admin_handler)
        dp.add_handler(remove_channel_conv_handler)
        dp.add_handler(CallbackQueryHandler(check_depozite, pattern=r'^(depocheck_|deponotcheck_)'))
        MessageHandler(Filters.regex("^🏠Asosiy menyu🏠$"), restart)
        dp.add_handler(MessageHandler(Filters.all, restart))
        print("The bot is running...")
        updater.start_polling()
        updater.idle()