# Generated by Django 3.1.4 on 2020-12-11 19:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('password_hash', models.CharField(blank=True, max_length=300)),
                ('role', models.CharField(choices=[('admin', 'admin'), ('customer', 'customer'), ('agent', 'agent')], default='customer', max_length=10)),
                ('is_active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_approved', models.BooleanField(default=False)),
                ('principal_amount', models.IntegerField(default=0)),
                ('interest_rate', models.FloatField(default=0.0)),
                ('tenure_months', models.IntegerField(default=0)),
                ('emi', models.FloatField(default=0.0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('new', 'new'), ('rejected', 'rejected'), ('approved', 'approved')], default='new', max_length=10)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='admin', to='lms.user')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agent', to='lms.user')),
                ('created_for', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customer', to='lms.user')),
            ],
        ),
        migrations.CreateModel(
            name='EditLoanHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_approved', models.BooleanField(default=False)),
                ('principal_amount', models.IntegerField(default=0)),
                ('interest_rate', models.FloatField(default=0.0)),
                ('tenure_months', models.IntegerField(default=0)),
                ('emi', models.FloatField(default=0.0)),
                ('created_at', models.DateTimeField()),
                ('status', models.CharField(choices=[('new', 'new'), ('rejected', 'rejected'), ('approved', 'approved')], default='new', max_length=10)),
                ('instance_created_at', models.DateTimeField(auto_now_add=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='admin_edit_loan', to='lms.user')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agent_edit_loan', to='lms.user')),
                ('created_for', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customer_edit_loan', to='lms.user')),
                ('edit_history_of', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='lms.loan')),
            ],
        ),
    ]
