from django.db import models

class Location(models.Model):
    directions = models.TextField(blank=True)
    capacity = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=100)
    name_hebrew = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return self.name + (' (' + self.name_hebrew + ')' if self.name_hebrew else '')

class Teacher(models.Model):
    password = models.CharField(max_length=100)
    is_admin = models.BooleanField()
    name = models.CharField(max_length=100)
    name_hebrew = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return self.name + (' (' + self.name_hebrew + ')' if self.name_hebrew else '')

class Level(models.Model):
    as_number = models.FloatField()
    color = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    name_hebrew = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return self.name

class Category(models.Model):
    parent_categories = models.ManyToManyField('self', symmetrical=False)
    name = models.CharField(max_length=100)
    name_hebrew = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return self.name

class TimeSlot(models.Model):
    start = models.DateTimeField()
    stop = models.DateTimeField()
    def __str__(self):
        return '%s Session' % (self.start, )

class Session(models.Model):
    location = models.ForeignKey(Location, models.SET_NULL, blank=True, null=True)
    level = models.ForeignKey(Level, models.SET_NULL, blank=True, null=True)
    when = models.ForeignKey(TimeSlot, models.SET_NULL, blank=True, null=True)
    teachers = models.ManyToManyField(Teacher)
    categories = models.ManyToManyField(Category, blank=True)

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    prereqs = models.TextField(blank=True)

    name_hebrew = models.CharField(max_length=100, blank=True)
    description_hebrew = models.TextField(blank=True)
    prereqs_hebrew = models.TextField(blank=True)
    def __str__(self):
        return '%s: %s level %s with %s' % (
            self.when, self.name if self.name else self.categories, self.level, ' & '.join(str(x) for x in self.teachers.all()))
