from vkbottle import Bot
from vkbottle.bot import Message
import json
import random

# === НАСТРОЙКИ ===
TOKEN = "vk1.a.ТВОЙ_ТОКЕН_ЗДЕСЬ"  # Вставь токен из настроек сообщества
GROUP_ID = 123456789  # ID твоего сообщества (цифры из URL)

# Загружаем вопросы из JSON-файла (создали ранее)
with open('questions/history/medinskiy/paragraph_10.json', 'r', encoding='utf-8') as f:
    questions_data = json.load(f)
    QUESTIONS = questions_data['questions']

# Хранилище состояния пользователей (в памяти)
user_state = {}

bot = Bot(token=TOKEN)

# Главное меню
@bot.on.message(text=["/start", "Начать", "Меню"])
async def start_handler(message: Message):
    keyboard = [
        ["📚 История 7 класс"],
        ["📊 Моя статистика"],
        ["ℹ️ Помощь"]
    ]
    await message.answer(
        "Привет! 👋 Я бот ИзиЗачёт.\n\n"
        "Выбери предмет:",
        keyboard=keyboard
    )

# Выбор параграфа
@bot.on.message(text="📚 История 7 класс")
async def history_handler(message: Message):
    keyboard = [["📖 Параграф 10: Абсолютизм во Франции"]]
    await message.answer(
        "📚 История Нового времени (Мединский)\n\n"
        "Выбери параграф:",
        keyboard=keyboard
    )

# Старт теста
@bot.on.message(text="📖 Параграф 10: Абсолютизм во Франции")
async def start_quiz(message: Message):
    user_id = message.from_id
    # Берем 5 случайных вопросов
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
    
    # Если вопросы закончились — показываем результат
    if state['current_question'] >= len(state['questions']):
        await show_results(message, user_id)
        return
    
    q = state['questions'][state['current_question']]
    # Создаем кнопки с вариантами ответов
    keyboard = [[opt] for opt in q['options']]
    
    await message.answer(
        f"❓ Вопрос {state['current_question'] + 1}/{len(state['questions'])}:\n\n"
        f"{q['question']}",
        keyboard=keyboard
    )

# Обработка ответа
@bot.on.message()
async def answer_handler(message: Message):
    user_id = message.from_id
    state = user_state.get(user_id)
    
    # Если пользователь не в режиме теста — игнорируем
    if not state:
        return
    
    selected_answer = message.text
    q = state['questions'][state['current_question']]
    
    # Проверяем ответ
    if selected_answer == q['options'][q['correct_answer']]:
        state['score'] += 1
        await message.answer(f"✅ Правильно!\n\n{q['explanation']}")
    else:
        await message.answer(
            f"❌ Неправильно.\n\n"
            f"Правильный ответ: {q['options'][q['correct_answer']]}\n\n"
            f"{q['explanation']}"
        )
    
    # Переходим к следующему вопросу
    state['current_question'] += 1
    await show_question(message, user_id)

# Показ результатов
async def show_results(message: Message, user_id: int):
    state = user_state[user_id]
    score = state['score']
    total = len(state['questions'])
    percentage = (score / total) * 100
    
    if percentage >= 80:
        emoji, msg = "🎉", "Отлично! Ты готов к уроку!"
    elif percentage >= 60:
        emoji, msg = "👍", "Хорошо, но можно лучше!"
    else:
        emoji, msg = "📚", "Стоит повторить параграф"
    
    keyboard = [["🔄 Пройти ещё раз"], [" В меню"]]
    
    await message.answer(
        f"{emoji} Тест завершен!\n\n"
        f"Результат: {score}/{total} ({percentage:.0f}%)\n"
        f"{msg}",
        keyboard=keyboard
    )
    
    # Очищаем состояние
    del user_state[user_id]

# Запуск бота
if __name__ == "__main__":
    print(" Бот ИзиЗачёт запущен! Жду сообщений...")
    bot.run_forever()