# Generated by Django 3.0.7 on 2020-08-07 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LVR', '0014_blog_crew'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog_post',
            name='slug',
            field=models.SlugField(editable=False, unique=True),
        ),
    ]
