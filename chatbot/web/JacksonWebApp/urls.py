from django.conf.urls import url
from .controllers import ChatController, IndexController, LogsController

app_name = 'JacksonWebApp'

urlpatterns = [
    url(r'^$', IndexController.handle, name='index'),
    url(r'^chat/$', ChatController.handle, name='chat_view'),
    url(r'^job/$', ChatController.get_job_result, name='get_job_result'),
    url(r'^logs/$', LogsController.handle, name='logs_view'),
]