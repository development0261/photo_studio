# Generated by Django 4.0 on 2022-01-21 05:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_alter_application_data_total_time_spent'),
    ]

    operations = [
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('pid', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('status', models.CharField(max_length=20)),
                ('auto_renew_status', models.BooleanField(default=False)),
                ('is_in_billing_retry_period', models.BooleanField(default=False)),
                ('is_in_intro_offer_period', models.BooleanField(default=False)),
                ('is_trial_period', models.BooleanField(default=False)),
                ('username', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]