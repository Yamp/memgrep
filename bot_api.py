import sqlite3

from fuzzysearch import find_near_matches
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes



async def search_memes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Search matching memes in the database and return the bot respons text."""
    args = context.args
    conn = sqlite3.connect('files.db')
    c = conn.cursor()
    table = c.execute("SELECT * FROM files")
    data = table.fetchall()
    msgs = []
    for d in data:
        ocr_text = d[5]
        res = []
        for a in args:
            if ms := find_near_matches(
                a,
                ocr_text,
                # max_l_dist=2,
                max_insertions=0,
                max_deletions=0,
                max_substitutions=2,
            ):
                # msgs += [str(d) + '\n' + str(d[6])]
                m = ms[0]
                match = str(d[5])[m.start:m.end]
                s = match
                res += [s]
        msgs += ['|'.join(res) + str(d[6])]
        msgs = sorted(msgs, key=lambda x: len(x), reverse=True)


    print(f'sending message {msgs}')

    await update.message.reply_text(f'Hello {msgs}')

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


def main():
    app = ApplicationBuilder().token("5725107749:AAGcHhP637ZtTmHQIKPC7bM94yM59ULdbN8").build()
    app.add_handler(CommandHandler("hello", hello))
    app.add_handler(CommandHandler("search", search_memes))
    app.run_polling()

if __name__ == "__main__":
    main()