# Generated by Django 2.0 on 2022-02-09 07:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_category_tag'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='category',
            table='category',
        ),
        migrations.AlterModelTable(
            name='tag',
            table='tag',
        ),
    ]
