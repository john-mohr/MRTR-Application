# Generated by Django 4.1.2 on 2023-07-22 03:49

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mrtr', '0013_shopping_trip_supply_request'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='method',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='type',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.CreateModel(
            name='Site_visit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('issues', models.TextField(null=True)),
                ('explanation', models.TextField(null=True)),
                ('submission_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_update', models.DateTimeField(null=True)),
                ('house', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mrtr.house')),
                ('manager', models.ForeignKey(db_column='manager_id', on_delete=django.db.models.deletion.CASCADE, to='mrtr.resident')),
            ],
        ),
        migrations.CreateModel(
            name='House_meeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('issues', models.TextField(null=True)),
                ('submission_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_update', models.DateTimeField(null=True)),
                ('house', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mrtr.house')),
                ('manager', models.ForeignKey(db_column='manager_id', on_delete=django.db.models.deletion.CASCADE, to='mrtr.resident')),
            ],
        ),
        migrations.CreateModel(
            name='Drug_test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, default=django.utils.timezone.now)),
                ('result', models.CharField(choices=[('Negative', 'Negative'), ('Positive', 'Positive'), ('Positive (meds)', 'Positive (meds)'), ('Invalid', 'Invalid'), ('Other (specify)', 'Other (specify)')], max_length=17)),
                ('substances', models.TextField(null=True)),
                ('notes', models.CharField(max_length=50, null=True)),
                ('submission_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_update', models.DateTimeField(null=True)),
                ('resident', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mrtr.resident')),
            ],
        ),
        migrations.CreateModel(
            name='Check_in',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('method', models.CharField(choices=[('In person', 'In person'), ('Phone call', 'Phone call'), ('Text', 'Text')], max_length=12)),
                ('notes', models.TextField(null=True)),
                ('submission_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_update', models.DateTimeField(null=True)),
                ('manager', models.ForeignKey(blank=True, db_column='manager_id', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='manager', to='mrtr.resident')),
                ('resident', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mrtr.resident')),
            ],
        ),
        migrations.CreateModel(
            name='Absentee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meeting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mrtr.house_meeting')),
                ('resident', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mrtr.resident')),
            ],
        ),
    ]
