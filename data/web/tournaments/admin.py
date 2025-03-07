from django.contrib import admin
from django.db import models
from .models import Tournament

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
	def __init__(self, model, admin_site):
		super().__init__(model, admin_site)
		self.list_display = [field.name for field in model._meta.fields]
		self.list_filter = ('status', 'max_players')
		self.search_fields = [
			field.name for field in model._meta.fields 
			if isinstance(field, models.CharField)
		]
