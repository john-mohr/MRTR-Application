# Generated by Django 4.1.2 on 2023-08-04 13:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mrtr', '0014_alter_supply_request_notes_and_more'),
        ('custom_user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='assoc_resident',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mrtr.resident'),
        ),
    ]
