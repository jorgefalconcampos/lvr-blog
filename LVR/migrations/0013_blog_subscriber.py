# Generated by Django 3.0.7 on 2020-07-11 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LVR', '0012_auto_20200703_1451'),
    ]

    operations = [
        migrations.CreateModel(
            name='blog_subscriber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('conf_num', models.CharField(max_length=15)),
                ('confirmed', models.BooleanField(default=False)),
            ],
        ),
    ]
