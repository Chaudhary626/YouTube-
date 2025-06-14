def register(bot):
    from database import get_proofs_for_owner, report_proof

    @bot.message_handler(commands=["report"])
    def handle_report(message):
        proofs = get_proofs_for_owner(message.from_user.id)
        if not proofs:
            bot.send_message(message.chat.id, "No proofs to report.")
            return
        for v in proofs:
            bot.send_message(
                message.chat.id,
                f"Reply to this message with reason for reporting proof for video <b>{v[2]}</b>."
            )
            bot.register_next_step_handler(message, lambda m: finish_report(m, v))

    def finish_report(message, v):
        reason = message.text.strip()
        report_proof(v[0], message.from_user.id, reason, v[10])
        bot.send_message(message.chat.id, "Report submitted to admins. Thank you!")