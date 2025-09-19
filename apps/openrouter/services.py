import requests
from apps.openrouter.models import Service, Message


class OpenRouterService:
    def __init__(self, service: Service):
        self.service = service
        self.api_key = service.api_key.value
        self.model_id = service.model.get_model_id()
        self.prompt = service.prompt

    def generate_message(self, extra_info=None):
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        prompt = self.prompt.format(extra_info=extra_info)

        payload = {
            'model': self.model_id,
            'messages': [{
                'role': 'user',
                'content': prompt,
            }],
            'max_tokens': 500,
            'temperature': 0.7
        }
        try:
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()
            message = data['choices'][0]['message']['content'].strip()

            if '</think>' in message:
                message = message[message.index('</think>') + len('</think>'):].strip()

            message_obj = Message.objects.create(
                text=message,
                service=self.service,
            )

            return message_obj.text

        except requests.exceptions.RequestException as e:
            raise Exception(f'Ошибка при генерации сообщения: {e}')
        except KeyError as e:
            raise Exception('Неожиданный формат ответа от AI сервиса')
