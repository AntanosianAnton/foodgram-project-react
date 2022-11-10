# Generated by Django 2.2.16 on 2022-11-06 09:35

import django.contrib.auth.models
import django.core.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(db_index=True, help_text='Введите имя пользователя', max_length=150, unique=True, validators=[django.core.validators.RegexValidator(message='Допустимые символы: буквы, цифры, +, @, ., -,_', regex='^[\\w.@+-]+$')], verbose_name='Уникальное имя')),
                ('email', models.EmailField(db_index=True, help_text='Введите адрес электронной почты', max_length=254, unique=True, verbose_name='Электронная почта')),
                ('first_name', models.CharField(blank=True, help_text='Введите имя пользователя', max_length=150, null=True, verbose_name='Имя')),
                ('last_name', models.CharField(blank=True, help_text='Введите фамилию пользователя', max_length=150, null=True, verbose_name='Фамилия')),
                ('password', models.CharField(help_text='Введите пароль', max_length=150, verbose_name='Пароль')),
                ('role', models.CharField(blank=True, choices=[('user', 'Пользователь'), ('guest', 'Гость'), ('admin', 'Администратор')], default='user', max_length=16, null=True)),
                ('is_subscribed', models.BooleanField(default=False, help_text='Подписаться', verbose_name='Подписка на данного пользователя')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
