import os
from vkbottle import Bot, Keyboard, Text
from vkbottle.bot import Message
import json
import random

# === НАСТРОЙКИ ===
TOKEN = os.environ.get("VK_TOKEN")
GROUP_ID = int(os.environ.get("GROUP_ID"))

if not TOKEN or not GROUP_ID:
    raise ValueError("Не настроены переменные VK_TOKEN и GROUP_ID")

# Загружаем вопросы
with open('questions/history/medinskiy/paragraph_10.json', 'r', encoding='utf-8') as f:
    questions_data = json.load(f)
    QUESTIONS = questions_data['questions']

user_state = {}
bot = Bot(token=TOKEN)

# Главное меню
@bot.on.message(text=["/start", "Начать", "Меню"])
async def start_handler(message: Message):
    kb = Keyboard(one_time=False)
    kb.add(Text("📚 История 7 класс"))
    kb.row()
    kb.add(Text(" Моя статистика"))
    kb.row()
    kb.add(Text("ℹ️ Помощь"))
    
    await message.answer(
        "Привет! 👋 Я бот ИзиЗачёт.\n\nВыбери предмет:",
        keyboard=kb
    )

# Выбор параграфа
@bot.on.message(text="📚 История 7 класс")
async def history_handler(message: Message):
    kb = Keyboard(one_time=False)
    kb.add(Text("📖 Параграф 10: Абсолютизм во Франции"))
    
    await message.answer(
        "📚 История Нового времени (Мединский)\n\nВыбери параграф:",
        keyboard=kb
    )

# Старт теста
@bot.on.message(text=" Параграф 10: Абсолютизм во Франции")
async def start_quiz(message: Message):
    user_id = message.from_id
    selected_questions = random.sample(QUESTIONS, min(5, len(QUESTIONS)))
    
    user_state[user_id] = {
        'current_question': 0,
        'score': 0,
        'questions': selected_questions
    }
    await show_question(message, user_id)

# Показ вопроса
async def show_question(message: Message, user_id: int):
    state = user_state[user_id]
    
    if state['current_question'] >= len(state['questions']):
        await show_results(message, user_id)
        return
    
    q = state['questions'][state['current_question']]
    kb = Keyboard(one_time=True)
    
    for opt in q['options']:
        kb.add(Text(opt))
        kb.row()
    
    await message.answer(
        f" Вопрос {state['current_question'] + 1}/{len(state['questions'])}:\n\n{q['question']}",
        keyboard=kb
    )

# Обработка ответа
@bot.on.message()
async def answer_handler(message: Message):
    user_id = message.from_id
    state = user_state.get(user_id)
    
    if not state:
        return
    
    selected_answer = message.text
    q = state['questions'][state['current_question']]
    
    if selected_answer == q['options'][q['correct_answer']]:
        state['score'] += 1
        await message.answer(f"✅ Правильно!\n\n{q['explanation']}")
    else:
        await message.answer(
            f"❌ Неправильно.\n\nПравильный ответ: {q['options'][q['correct_answer']]}\n\n{q['explanation']}"
        )
    
    state['current_question'] += 1
    await show_question(message, user_id)

# Результаты
async def show_results(message: Message, user_id: int):
    state = user_state[user_id]
    score = state['score']
    total = len(state['questions'])
    percentage = (score / total) * 100
    
    if percentage >= 80:
        emoji, msg = "🎉", "Отлично! Ты готов к уроку!"
    elif percentage >= 60:
        emoji, msg = "", "Хорошо, но можно лучше!"
    else:
        emoji, msg = "", "Стоит повторить параграф"
    
    kb = Keyboard(one_time=False)
    kb.add(Text("🔄 Пройти ещё раз"))
    kb.row()
    kb.add(Text(" В меню"))
    
    await message.answer(
        f"{emoji} Тест завершен!\n\nРезультат: {score}/{total} ({percentage:.0f}%)\n{msg}",
        keyboard=kb
    )
    
    del user_state[user_id]

if __name__ == "__main__":
    print("🤖 Бот ИзиЗачёт запущен!")
    bot.run_forever()