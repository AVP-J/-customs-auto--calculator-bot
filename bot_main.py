        payment_text = "🆓 *Бесплатный расчёт* (электромобиль)"
    elif calculations_left > 0 and not is_electric:
        # Нужна оплата для не-электромобилей
        await query.edit_message_text(
            "❌ *Бесплатные расчёты только для электромобилей*\n\n"
            "У вас осталось бесплатных расчётов, но они доступны только для электромобилей.\n\n"
            "Для этого автомобиля нужен платный расчёт (299 ₸).\n\n"
            "Хотите продолжить?",
            parse_mode="Markdown"
        )
        return
    else:
        # Нет бесплатных расчётов
        await query.edit_message_text(
            "💰 *Требуется оплата*\n\n"
            "Бесплатные расчёты закончились.\n\n"
            "Стоимость расчёта: 299 ₸\n\n"
            "Хотите продолжить?",
            parse_mode="Markdown"
        )
        return
    
    # Выполняем расчёт
    try:
        result = calculate_for_bot(car_data)
        result_text = format_result_for_telegram(result)
        
        # Сохраняем в базу
        calculation_id = db.save_calculation(
            telegram_id=user.id,
            car_data=car_data,
            result_data=result,
            is_paid=not (calculations_left > 0 and is_electric)
        )
        
        if calculation_id:
            result_text += f"\n\n📁 *ID расчёта:* {calculation_id}"
        
        # Добавляем информацию о тарифе
        if not (calculations_left > 0 and is_electric):
            result_text += "\n\n💰 *Тариф:* Платный (299 ₸)"
        else:
            new_calculations_left = db.get_user_calculations_left(user.id)
            result_text += f"\n\n🆓 *Тариф:* Бесплатный (осталось: {new_calculations_left}/3)"
        
        await query.edit_message_text(
            result_text,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Calculation error: {e}")
        await query.edit_message_text(
            f"❌ *Ошибка при расчёте*\n\n"
            f"Произошла ошибка: {str(e)}\n\n"
            f"Попробуйте снова: /calculate",
            parse_mode="Markdown"
        )

async def edit_calculation(query, context):
    """Позволяет редактировать данные перед расчётом."""
    await query.edit_message_text(
        "✏️ *Редактирование данных*\n\n"
        "Какой параметр хотите изменить?\n\n"
        "1. Марка автомобиля\n"
        "2. Модель\n"
        "3. Тип\n"
        "4. Год-месяц\n"
        "5. Цена\n\n"
        "Отправьте номер параметра (1-5) или /calculate для нового расчёта",
        parse_mode="Markdown"
    )

async def cancel_operation(query, context):
    """Отменяет текущую операцию."""
    # Очищаем данные пользователя
    context.user_data.clear()
    
    await query.edit_message_text(
        "❌ *Операция отменена*\n\n"
        "Все введённые данные удалены.\n\n"
        "Чтобы начать заново, отправьте /calculate",
        parse_mode="Markdown"
    )

# ========== ОБРАБОТЧИКИ ТЕКСТОВЫХ СООБЩЕНИЙ ==========

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений (для пошагового ввода)."""
    user = update.effective_user
    text = update.message.text.strip()
    
    # Проверяем, находится ли пользователь в процессе ввода
    input_step = context.user_data.get("input_step")
    
    if not input_step:
        # Не в процессе ввода, показываем помощь
        await update.message.reply_text(
            "Чтобы начать расчёт, отправьте /calculate\n"
            "Для помощи отправьте /help"
        )
        return
    
    # Обрабатываем в зависимости от текущего шага
    if input_step == "brand":
        await handle_brand_input(update, context, text)
    elif input_step == "model":
        await handle_model_input(update, context, text)
    elif input_step == "year_month":
        await handle_year_month_input(update, context, text)
    elif input_step == "price":
        await handle_price_input(update, context, text)
    else:
        await update.message.reply_text(
            "Неизвестный шаг. Отправьте /calculate чтобы начать заново."
        )

async def handle_brand_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Обрабатывает ввод марки автомобиля."""
    if len(text) < 2 or len(text) > 50:
        await update.message.reply_text(
            "Марка должна быть от 2 до 50 символов. Попробуйте снова:"
        )
        return
    
    # Сохраняем марку
    context.user_data["car_data"]["brand"] = text
    context.user_data["input_step"] = "model"
    
    await update.message.reply_text(
        f"✅ *Марка принята:* {text}\n\n"
        "2️⃣ **Введите модель автомобиля** (например: L6):",
        parse_mode="Markdown"
    )

async def handle_model_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Обрабатывает ввод модели автомобиля."""
    if len(text) < 1 or len(text) > 50:
        await update.message.reply_text(
            "Модель должна быть от 1 до 50 символов. Попробуйте снова:"
        )
        return
    
    # Сохраняем модель
    context.user_data["car_data"]["model"] = text
    context.user_data["input_step"] = "type"
    
    # Показываем выбор типа
    keyboard = [
        [
            InlineKeyboardButton("⚡ Электрический", callback_data="car_type_electric"),
            InlineKeyboardButton("⛽ Бензин", callback_data="car_type_gasoline")
        ],
        [
            InlineKeyboardButton("⛽ Дизель", callback_data="car_type_diesel"),
            InlineKeyboardButton("🌿 Гибрид", callback_data="car_type_hybrid")
        ],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✅ *Модель принята:* {text}\n\n"
        "3️⃣ **Выберите тип автомобиля:**",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def handle_year_month_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Обрабатывает ввод года и месяца."""
    import re
    
    # Проверяем формат ГГГГ-ММ
    pattern = r'^\d{4}-(0[1-9]|1[0-2])$'
    if not re.match(pattern, text):
        await update.message.reply_text(
            "❌ *Неверный формат*\n\n"
            "Введите год и месяц в формате *ГГГГ-ММ* (например: 2025-04):",
            parse_mode="Markdown"
        )
        return
    
    year, month = text.split("-")
    year_int = int(year)
    
    # Проверяем разумный диапазон годов
    current_year = datetime.now().year
    if year_int < 2000 or year_int > current_year + 5:
        await update.message.reply_text(
            f"❌ *Некорректный год*\n\n"
            f"Год должен быть между 2000 и {current_year + 5}.\n"
            f"Попробуйте снова:",
            parse_mode="Markdown"
        )
        return
    
    # Сохраняем год-месяц
    context.user_data["car_data"]["year_month"] = text
    context.user_data["input_step"] = "price"
    
    await update.message.reply_text(
        f"✅ *Год принят:* {text}\n\n"
        "5️⃣ **Введите цену в Китае** (CNY, например 200000):",
        parse_mode="Markdown"
    )

async def handle_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Обрабатывает ввод цены."""
    try:
        # Очищаем от пробелов и запятых
        clean_text = text.replace(",", "").replace(" ", "")
        price = float(clean_text)
        
        if price <= 0 or price > 10000000:  # Разумный диапазон: 0-10 млн CNY
            await update.message.reply_text(
                "❌ *Некорректная цена*\n\n"
                "Цена должна быть от 1 до 10,000,000 CNY.\n"
                "Попробуйте снова:",
                parse_mode="Markdown"
            )
            return
    except ValueError:
        await update.message.reply_text(
            "❌ *Неверный формат*\n\n"
            "Введите число (например: 200000 или 250,000):",
            parse_mode="Markdown"
        )
        return
    
    # Сохраняем цену
    context.user_data["car_data"]["price_cny"] = price
    
    # Показываем подтверждение
    car_data = context.user_data["car_data"]
    
    # Получаем читаемое название типа
    type_names = {
        "electric": "⚡ Электрический",
        "gasoline": "⛽ Бензин",
        "diesel": "⛽ Дизель",
        "hybrid": "🌿 Гибрид"
    }
    car_type_name = type_names.get(car_data.get("type", ""), "Неизвестный")
    
    confirmation_text = (
        "📋 *ПОДТВЕРЖДЕНИЕ ДАННЫХ*\n\n"
        f"*Марка:* {car_data.get('brand', 'Не указано')}\n"
        f"*Модель:* {car_data.get('model', 'Не указано')}\n"
        f"*Тип:* {car_type_name}\n"
        f"*Год-месяц:* {car_data.get('year_month', 'Не указано')}\n"
        f"*Цена в Китае:* {price:,.0f} CNY\n\n"
        "Всё верно?"
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ Да, всё верно", callback_data="confirm_data")],
        [InlineKeyboardButton("✏️  Исправить", callback_data="edit_data")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        confirmation_text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# ========== ОСНОВНАЯ ФУНКЦИЯ ==========

def main():
    """Основная функция запуска бота."""
    print("🚀 Starting Customs Calculator Bot...")
    
    # Создаём приложение
    application = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("calculate", calculate_command))
    application.add_handler(CommandHandler("history", history_command))
    
    # Добавляем обработчик inline кнопок
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # Запускаем бота
    print(f"✅ Bot started: @CustomsCalcKZBot")
    print("📱 Listening for messages...")
    print("Press Ctrl+C to stop")
    
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()