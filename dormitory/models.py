from django.db import models


class Dormitory(models.Model):
    name = models.CharField(max_length=20)
    desc = models.TextField()
    logo = models.FileField(null=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    question = models.TextField()


class Answer(models.Model):
    answer = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    dormitory = models.ForeignKey(Dormitory, on_delete=models.CASCADE)

