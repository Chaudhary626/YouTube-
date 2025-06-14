from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def register(bot):
    from database import get_proofs_for_owner, verify_proof

    @bot.message_handler(commands=["verify"])
    def handle_verify(message):
        proofs = get_proofs_for_owner(message.from_user.id)
        if not proofs:
            bot.send_message(message.chat.id, "No proofs awaiting your verification.")
            return
        for v in proofs:
            markup = InlineKeyboardMarkup()
            markup.row(
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_proof_{v[0]}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_proof_{v[0]}")
            )
            bot.send_message(message.chat.id, f"Proof for video: <b>{v[2]}</b>", reply_markup=markup)
            if v[10]:  # proof file id
                bot.send_video(message.chat.id, v[10])

    @bot.callback_query_handler(func=lambda call: call.data.startswith("approve_proof_") or call.data.startswith("reject_proof_"))
    def verify_cb(call):
        vid = int(call.data.split("_")[-1])
        if call.data.startswith("approve"):
            verify_proof(vid, True)
            bot.answer_callback_query(call.id, "Proof approved!")
            bot.send_message(call.message.chat.id, "Proof approved. Both users are now eligible for next tasks.")
        else:
            verify_proof(vid, False)
            bot.answer_callback_query(call.id, "Proof rejected!")
            bot.send_message(call.message.chat.id, "Proof rejected. The helper must redo the task and resubmit proof.")