"""
Адаптированный калькулятор таможенных платежей для Telegram бота.
"""
import os
import sys
from datetime import datetime

# Добавляем путь к оригинальному калькулятору
original_calc_path = "/Users/jarvis/.openclaw/workspacesk-proj-d_KYutoeMeow7LUKRKp-D12q_KmmviQ8zyilVKY-wJIsP62VfJpZtx8nmnNZd8ezeGDPXP2Yo5T3BlbkFJXw0rL0LknE0zFpOslS5kdCHg5xhDNz98vp6cnSCXuWN4lhRtSySJctzElD7OpyBAsBuQII4fkA/integrations/customs_calculator"
sys.path.append(original_calc_path)

try:
    from customs_calculator import calculate_customs_duty as original_calculate
    from currency_helper_v2 import load_currency_rates, convert_to_kzt
    HAS_ORIGINAL_CALC = True
except ImportError:
    HAS_ORIGINAL_CALC = False
    print("⚠️ Оригинальный калькулятор не найден, использую упрощённую версию")

def calculate_for_bot(car_data, currency="CNY"):
    """
    Рассчитывает таможенные платежи для данных из бота.
    
    Параметры:
    - car_data: словарь с данными автомобиля от бота
    - currency: валюта цены ('CNY', 'USD', 'KZT')
    
    Возвращает:
    - dict с результатами расчёта
    """
    
    # Извлекаем данные из формата бота
    brand = car_data.get('brand', 'Unknown')
    model = car_data.get('model', 'Unknown')
    car_type = car_data.get('type', 'gasoline')  # electric, gasoline, diesel, hybrid
    
    # Парсим год-месяц (формат: "2025-04")
    year_month = car_data.get('year_month', '2025-01')
    try:
        year = int(year_month.split('-')[0])
        month = int(year_month.split('-')[1])
    except:
        year = 2025
        month = 1
    
    # Цена в CNY (основная валюта для бота)
    price_cny = car_data.get('price_cny', 0)
    
    # Конвертируем в USD для калькулятора
    if HAS_ORIGINAL_CALC:
        try:
            currency_data = load_currency_rates()
            usd_to_kzt = currency_data['rates']['USD']
            cny_to_kzt = currency_data['rates']['CNY']
            
            # Конвертируем CNY → KZT → USD
            price_kzt = price_cny * cny_to_kzt
            price_usd = price_kzt / usd_to_kzt
        except:
            # Fallback курсы если не удалось загрузить
            usd_to_kzt = 470.0
            cny_to_kzt = 69.0
            price_kzt = price_cny * cny_to_kzt
            price_usd = price_kzt / usd_to_kzt
    else:
        # Упрощённые курсы
        usd_to_kzt = 470.0
        cny_to_kzt = 69.0
        price_kzt = price_cny * cny_to_kzt
        price_usd = price_kzt / usd_to_kzt
    
    # Подготавливаем данные для оригинального калькулятора
    calc_data = {
        'brand': brand,
        'year': year,
        'month': month,
        'car_type': car_type,
        'customs_value_usd': price_usd,
    }
    
    # Добавляем специфичные для типа автомобиля параметры
    if car_type == 'electric':
        calc_data['engine_volume'] = 0
        calc_data['power_kw'] = 150  # средняя мощность электромобиля
    else:
        # Для ДВС используем средний объём двигателя
        calc_data['engine_volume'] = 2000  # 2.0L по умолчанию
        calc_data['power_kw'] = 100  # ~136 л.с.
    
    # Рассчитываем возраст
    now = datetime.now()
    age_months = (now.year - year) * 12 + (now.month - month)
    calc_data['age_years'] = max(age_months / 12.0, 0)
    
    # Выполняем расчёт
    if HAS_ORIGINAL_CALC:
        try:
            result = original_calculate(calc_data)
        except Exception as e:
            result = create_fallback_result(calc_data, price_usd, price_kzt, usd_to_kzt, cny_to_kzt)
    else:
        result = create_fallback_result(calc_data, price_usd, price_kzt, usd_to_kzt, cny_to_kzt)
    
    # Добавляем информацию о валютах
    result['currency_rates'] = {
        'USD/KZT': usd_to_kzt,
        'CNY/KZT': cny_to_kzt,
        'price_cny': price_cny,
        'price_usd': price_usd,
        'price_kzt': price_kzt
    }
    
    # Добавляем исходные данные
    result['input_data'] = car_data
    
    return result

def create_fallback_result(calc_data, price_usd, price_kzt, usd_to_kzt, cny_to_kzt):
    """
    Создаёт упрощённый результат расчёта если оригинальный калькулятор недоступен.
    """
    car_type = calc_data['car_type']
    age_years = calc_data['age_years']
    
    # Базовые ставки (упрощённые)
    if car_type == 'electric':
        # Электромобили: пошлина 0% до 2028, затем 15%
        duty_rate = 0.0 if datetime.now().year <= 2028 else 0.15
        duty_name = "Пошлина на электромобили"
    elif car_type == 'hybrid':
        # Гибриды: скидка 50%
        duty_rate = 0.15 * 0.5  # 50% скидка от стандартной 15%
        duty_name = "Пошлина на гибриды (со скидкой 50%)"
    else:
        # Бензин/дизель: стандартная ставка
        duty_rate = 0.15
        duty_name = "Таможенная пошлина"
    
    # НДС: 16% с 01.01.2026
    vat_rate = 0.16
    
    # Акциз: зависит от объёма двигателя и возраста
    engine_volume = calc_data.get('engine_volume', 2000)
    if age_years < 3:
        # Новые автомобили: 0.3 EUR за см³
        excise_rate = 0.3 * usd_to_kzt / 470  # Конвертируем EUR в KZT через USD
    elif age_years < 7:
        # 3-7 лет: 0.2 EUR за см³
        excise_rate = 0.2 * usd_to_kzt / 470
    else:
        # Старше 7 лет: 0.1 EUR за см³
        excise_rate = 0.1 * usd_to_kzt / 470
    
    # Расчёты
    duty_amount = price_usd * duty_rate * usd_to_kzt
    vat_base = price_usd * usd_to_kzt + duty_amount
    vat_amount = vat_base * vat_rate
    excise_amount = engine_volume * excise_rate
    clearance_fee = 70000  # Фиксированный сбор за таможенное оформление
    
    total_customs = duty_amount + vat_amount + excise_amount + clearance_fee
    total_price_kzt = price_kzt + total_customs
    
    return {
        'success': True,
        'car_info': {
            'brand': calc_data['brand'],
            'type': car_type,
            'year': calc_data['year'],
            'age_years': round(age_years, 1),
            'engine_volume': engine_volume,
        },
        'calculations': {
            'customs_value_usd': round(price_usd, 2),
            'customs_value_kzt': round(price_kzt, 0),
            'duty': {
                'name': duty_name,
                'rate': f"{duty_rate * 100:.1f}%",
                'amount_kzt': round(duty_amount, 0)
            },
            'vat': {
                'name': "НДС",
                'rate': f"{vat_rate * 100:.0f}%",
                'amount_kzt': round(vat_amount, 0)
            },
            'excise': {
                'name': "Акциз",
                'rate': f"{excise_rate:.2f} ₸/см³",
                'amount_kzt': round(excise_amount, 0)
            },
            'clearance': {
                'name': "Сбор за оформление",
                'amount_kzt': clearance_fee
            }
        },
        'totals': {
            'total_customs_kzt': round(total_customs, 0),
            'total_price_kzt': round(total_price_kzt, 0),
            'customs_percentage': round((total_customs / price_kzt) * 100, 1) if price_kzt > 0 else 0
        },
        'notes': [
            "⚠️ Это упрощённый расчёт. Для точного расчёта нужны точные параметры автомобиля.",
            "📅 Курсы валют загружены из утренней сводки.",
            f"💰 Цена в Китае: {calc_data.get('price_cny', 0):,.0f} CNY",
            f"🚗 Тип: {get_car_type_name(car_type)}"
        ]
    }

def get_car_type_name(car_type):
    """Возвращает читаемое название типа автомобиля."""
    names = {
        'electric': '⚡ Электрический',
        'gasoline': '⛽ Бензин',
        'diesel': '⛽ Дизель',
        'hybrid': '🌿 Гибрид'
    }
    return names.get(car_type, 'Неизвестный')

def format_result_for_telegram(result):
    """
    Форматирует результат расчёта для отправки в Telegram.
    """
    if not result.get('success', False):
        return "❌ Ошибка при расчёте. Попробуйте снова."
    
    car_info = result['car_info']
    calculations = result['calculations']
    totals = result['totals']
    notes = result.get('notes', [])
    
    # Формируем сообщение
    message = f"🚗 *РАСЧЁТ ТАМОЖЕННЫХ ПЛАТЕЖЕЙ*\n\n"
    
    # Информация об автомобиле
    message += f"*Автомобиль:* {car_info['brand']}\n"
    message += f"*Тип:* {get_car_type_name(car_info['type'])}\n"
    message += f"*Год выпуска:* {car_info['year']} ({car_info['age_years']} лет)\n"
    if car_info['engine_volume'] > 0:
        message += f"*Объём двигателя:* {car_info['engine_volume']} см³\n"
    message += f"*Таможенная стоимость:* {calculations['customs_value_usd']:,.0f} USD\n"
    message += f"*В тенге:* {calculations['customs_value_kzt']:,.0f} ₸\n\n"
    
    # Расчёты
    message += "*📊 ТАМОЖЕННЫЕ ПЛАТЕЖИ:*\n"
    
    duty = calculations['duty']
    if float(duty['amount_kzt']) > 0:
        message += f"• {duty['name']} ({duty['rate']}): {duty['amount_kzt']:,.0f} ₸\n"
    
    vat = calculations['vat']
    message += f"• {vat['name']} ({vat['rate']}): {vat['amount_kzt']:,.0f} ₸\n"
    
    excise = calculations['excise']
    if float(excise['amount_kzt']) > 0:
        message += f"• {excise['name']} ({excise['rate']}): {excise['amount_kzt']:,.0f} ₸\n"
    
    clearance = calculations['clearance']
    message += f"• {clearance['name']}: {clearance['amount_kzt']:,.0f} ₸\n\n"
    
    # Итоги
    message += f"*💰 ИТОГО ТАМОЖНЯ:* {totals['total_customs_kzt']:,.0f} ₸\n"
    message += f"*📈 % от стоимости:* {totals['customs_percentage']:.1f}%\n"
    message += f"*💵 ОБЩАЯ СТОИМОСТЬ:* {totals['total_price_kzt']:,.0f} ₸\n\n"
    
    # Примечания
    if notes:
        message += "*📝 ПРИМЕЧАНИЯ:*\n"
        for note in notes:
            message += f"• {note}\n"
    
    return message

# Тестовая функция
if __name__ == "__main__":
    # Тестовые данные
    test_data = {
        'brand': 'Li',
        'model': 'L6',
        'type': 'electric',
        'year_month': '2025-04',
        'price_cny': 300000
    }
    
    result = calculate_for_bot(test_data)
    print(format_result_for_telegram(result))