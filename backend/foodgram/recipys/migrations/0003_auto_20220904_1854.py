# Generated by Django 3.2.15 on 2022-09-04 15:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipys', '0002_auto_20220903_1513'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='basket',
            options={'verbose_name': 'рецепт в корзине', 'verbose_name_plural': 'рецепты в корзине'},
        ),
        migrations.AlterModelOptions(
            name='favorite',
            options={'verbose_name': 'избранный рецепт', 'verbose_name_plural': 'избранные рецепты'},
        ),
        migrations.AlterModelOptions(
            name='ingredientsforrecipy',
            options={'verbose_name': 'ингредиент для рецепта', 'verbose_name_plural': 'ингредиенты для рецепта'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'verbose_name': 'Тег', 'verbose_name_plural': 'Теги'},
        ),
    ]