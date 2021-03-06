from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from apps.web.api.serializers import UpdateModelSerializer
from apps.web.models import AppUser, CallbackQuery, Chat, Message, Update
from apps.web.models.message import Photo
from apps.web.utils import allowed_hooks

from ..tasks import handle_message_task


class ProcessWebHookAPIView(CreateAPIView):
    """View to retrieve and handle all user's request, i.e webhook

    Steps:
        1) Got request with ``hook_id`` param to determine the bot
        2) Extract message or callback_query.message
        3) Handle this message by celery task creation

    """
    serializer_class = UpdateModelSerializer
    queryset = Update.objects.all()

    @allowed_hooks
    def post(self, request, *args, **kwargs):
        bot_id = kwargs.get('hook_id', None)
        self.request.data['hook_id'] = bot_id

        serializer = self.get_serializer(data=request.data)
        is_valid = serializer.is_valid()

        if is_valid:
            update = self.perform_create(serializer)
        else:
            # TODO: implement errors handling
            print("Error has been occurred. Format is not valid.")
            return Response(status=status.HTTP_204_NO_CONTENT)

        headers = self.get_success_headers(serializer.data)

        # handle_message_task.delay(update.id)

        handle_message_task(update.id)

        return Response(
            serializer.data,
            headers=headers,
            status=status.HTTP_201_CREATED,
        )

    def handle_message(self, data):
        bot = data['bot']
        user, _ = AppUser.objects.get_or_create(**data['message']['from_user'])
        chat, _ = Chat.objects.get_or_create(**data['message']['chat'])
        message, _ = Message.objects.get_or_create(
            from_user=user,
            chat=chat,
            date=data['message']['date'],
            text=data['message'].get('text'),
            message_id=data['message']['message_id'],
        )

        self.attach_photo_to_message(data=data['message'], message=message)

        update, _ = Update.objects.get_or_create(
            bot=bot,
            message=message,
            update_id=data['update_id'],
        )
        return update

    @staticmethod
    def extract_callback_message(callback):
        user, _ = AppUser.objects.get_or_create(
            **callback['message']['from_user']
        )
        chat, _ = Chat.objects.get_or_create(
            **callback['message']['chat']
        )

        message, _ = Message.objects.get_or_create(
            message_id=callback['message']['message_id'],
            from_user=user,
            chat=chat,
            date=callback['message']['date'],
            text=callback['message'].get('text'),
        )
        return message

    @staticmethod
    def attach_photo_to_message(data, message):
        photos = data.get('photo', [])
        for photo in photos:
            photo.pop('message', None)
            Photo.objects.get_or_create(**photo, message=message)

    def handle_callback(self, data):
        bot = data['bot']
        user, _ = AppUser.objects.get_or_create(
            **data['callback_query']['from_user']
        )
        chat, _ = Chat.objects.get_or_create(
            **data['callback_query']['message']['chat']
        )

        message = data['callback_query'].get('message')
        if message:
            message = self.extract_callback_message(data['callback_query'])
            self.attach_photo_to_message(
                data=data['callback_query']['message'],
                message=message
            )

        callback_query, _ = CallbackQuery.objects.get_or_create(
            from_user=user,
            message=message,
            data=data['callback_query']['data'],
            id=data['callback_query']['id'],
        )

        update, _ = Update.objects.get_or_create(
            bot=bot,
            callback_query=callback_query,
            update_id=data['update_id'],
        )
        return update

    def perform_create(self, serializer):
        data = serializer.validated_data

        if 'message' in data:
            update = self.handle_message(data)
        else:
            update = self.handle_callback(data)

        return update
