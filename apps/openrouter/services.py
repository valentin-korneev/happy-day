import requests

from apps.openrouter.models import AIModel, Message


class OpenRouterService:
    def __init__(self, model: AIModel):
        self.model = model
        self.api_key = model.token.token
        self.base_url = 'https://openrouter.ai/api/v1'
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }

    def generate_birthday_message(self, employees):
        employees_info = []
        for emp in employees:
            add_info = f'{emp.position.name}, {emp.department.name}'
            if emp.telegram_id:
                add_info += f', @{emp.telegram_id}'
            employees_info.append(f'- {emp} ({add_info})')

        employees_list = '\n'.join(employees_info)

        prompt = f'''
Сгенерируй поздравление с Днем Рождения для сотрудников компании.

Список именинников:
{employees_list}

Требования к поздравлению:
- Длина: 5-7 предложений
- Тон: дружелюбный и профессиональный
- Содержание: упомяни каждого сотрудника, пожелай успехов в работе и личной жизни
- Стиль: корпоративный, но теплый
- Начни с общего поздравления, затем перейди к индивидуальным пожеланиям
- Включаем ссылку на телеграмм именинника, если она указана в данных - шаблон вставки `<Имя> (<Ссылка в телеграм>)`, если ссылки нет, то просто имя

Поздравление должно быть готово для отправки в корпоративный чат.
'''

        payload = {
            'model': self.model.model_id,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': 500,
            'temperature': 0.7
        }

        try:
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=self.headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()
            message = data['choices'][0]['message']['content'].strip()

            message_obj = Message.objects.create(
                text=message,
                model=self.model,
            )
            message_obj.employees.set(employees)

            return message_obj.text

        except requests.exceptions.RequestException as e:
            raise Exception(f'Ошибка при генерации сообщения: {e}')
        except KeyError as e:
            raise Exception('Неожиданный формат ответа от AI сервиса')
