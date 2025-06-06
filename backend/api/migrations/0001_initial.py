# Generated by Django 5.2.1 on 2025-05-29 14:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Athlete',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('date_of_birth', models.DateField()),
                ('address', models.TextField(blank=True, null=True)),
                ('mobile_number', models.CharField(blank=True, max_length=15, null=True)),
                ('registered_date', models.DateField(blank=True, null=True)),
                ('expiration_date', models.DateField(blank=True, null=True)),
                ('is_coach', models.BooleanField(default=False)),
                ('is_referee', models.BooleanField(default=False)),
                ('profile_image', models.ImageField(blank=True, default='profile_images/default.png', null=True, upload_to='profile_images/')),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('place', models.CharField(blank=True, max_length=100, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FederationRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('rank_order', models.IntegerField(default=0)),
                ('grade_type', models.CharField(choices=[('inferior', 'Inferior Grade'), ('superior', 'Superior Grade')], default='inferior', max_length=10)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Title',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='AnnualVisa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issued_date', models.DateField(blank=True, null=True)),
                ('visa_status', models.CharField(choices=[('approved', 'Approved'), ('denied', 'Denied')], default='denied', max_length=10)),
                ('athlete', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='annual_visas', to='api.athlete')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('solo', 'Solo'), ('teams', 'Teams'), ('fight', 'Fight')], default='solo', max_length=20)),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('mixt', 'Mixt')], default='mixt', max_length=20)),
                ('athletes', models.ManyToManyField(blank=True, related_name='categories', to='api.athlete')),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='api.competition')),
            ],
        ),
        migrations.CreateModel(
            name='AthleteCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_weight', models.FloatField(blank=True, null=True)),
                ('athlete', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='athlete_categories', to='api.athlete')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='athlete_categories', to='api.category')),
            ],
        ),
        migrations.AddField(
            model_name='athlete',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='athletes', to='api.city'),
        ),
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='club_logos/')),
                ('address', models.TextField(blank=True, null=True)),
                ('mobile_number', models.CharField(blank=True, max_length=15, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='clubs', to='api.city')),
                ('coaches', models.ManyToManyField(blank=True, related_name='coached_clubs', to='api.athlete')),
            ],
        ),
        migrations.AddField(
            model_name='athlete',
            name='club',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='athletes', to='api.club'),
        ),
        migrations.AddField(
            model_name='athlete',
            name='federation_role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='athletes', to='api.federationrole'),
        ),
        migrations.AddField(
            model_name='athlete',
            name='current_grade',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='current_athletes', to='api.grade'),
        ),
        migrations.CreateModel(
            name='GradeHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('obtained_date', models.DateField(auto_now_add=True)),
                ('level', models.CharField(choices=[('good', 'Good'), ('bad', 'Bad')], default='good', max_length=10)),
                ('exam_date', models.DateField(blank=True, null=True)),
                ('exam_place', models.CharField(blank=True, max_length=100, null=True)),
                ('technical_director', models.CharField(blank=True, max_length=100, null=True)),
                ('president', models.CharField(blank=True, max_length=100, null=True)),
                ('athlete', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grade_history', to='api.athlete')),
                ('grade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.grade')),
            ],
        ),
        migrations.CreateModel(
            name='MedicalVisa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issued_date', models.DateField(blank=True, null=True)),
                ('health_status', models.CharField(choices=[('approved', 'Approved'), ('denied', 'Denied')], default='denied', max_length=10)),
                ('athlete', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medical_visas', to='api.athlete')),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255)),
                ('athletes', models.ManyToManyField(related_name='teams', to='api.athlete')),
            ],
        ),
        migrations.CreateModel(
            name='CategoryTeam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.category')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.team')),
            ],
        ),
        migrations.AddField(
            model_name='category',
            name='teams',
            field=models.ManyToManyField(blank=True, related_name='new_categories', through='api.CategoryTeam', to='api.team'),
        ),
        migrations.AddField(
            model_name='athlete',
            name='title',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='athletes', to='api.title'),
        ),
        migrations.CreateModel(
            name='TrainingSeminar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('place', models.CharField(max_length=100)),
                ('athletes', models.ManyToManyField(blank=True, related_name='training_seminars', to='api.athlete')),
            ],
        ),
    ]
