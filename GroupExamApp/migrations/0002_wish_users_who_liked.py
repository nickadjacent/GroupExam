# Generated by Django 3.0.3 on 2020-02-25 00:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GroupExamApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='wish',
            name='users_who_liked',
            field=models.ManyToManyField(related_name='liked_wish', to='GroupExamApp.User'),
        ),
    ]
