# Generated by Django 2.0 on 2017-12-30 16:08

from django.conf import settings
from django.db import migrations, models

import apps.web.validators


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='handler',
            name='allowed',
        ),
        migrations.RemoveField(
            model_name='response',
            name='redirect_to',
        ),
        migrations.AddField(
            model_name='chat',
            name='links_preview',
            field=models.BooleanField(default=False, verbose_name='Show links preview'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='chat',
            name='notifications',
            field=models.BooleanField(default=False, verbose_name='Show notifications'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='chat',
            name='template_context',
            field=models.TextField(blank=True, max_length=3000, null=True, validators=[apps.web.validators.json_field_validator], verbose_name='Template context'),
        ),
        migrations.AddField(
            model_name='handler',
            name='redirects',
            field=models.ManyToManyField(help_text='Users the message redirect to', to=settings.AUTH_USER_MODEL, verbose_name='Redirects'),
        ),
        migrations.AlterField(
            model_name='handler',
            name='ids_expression',
            field=models.CharField(blank=True, help_text='A set of math symbols to construct a particular rule,example: {} + {} > 1; example2: {cond_id} == 0', max_length=500, null=True, validators=[apps.web.validators.condition_validator], verbose_name='Mathematics expression'),
        ),
    ]
