from django.db import models

class Location(models.Model):
    name = models.CharField(max_length=100)
    directions = models.TextField(blank=True)
    capacity = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return self.name

class Teacher(models.Model):
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    is_admin = models.BooleanField()
    def __str__(self):
        return self.name

class Level(models.Model):
    as_number = models.FloatField()
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    parent_categories = models.ManyToManyField('self', symmetrical=False)
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
    prereqs = models.TextField(blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    def __str__(self):
        return '%s: %s level %s with %s' % (
            self.when, self.name if self.name else self.categories, self.level, ' & '.join(str(x) for x in self.teachers.all()))
