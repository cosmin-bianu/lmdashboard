from django.db import models


#TODO
# Create your models here.
class Chapter(models.Model):
    max_name_length=50 #characters
    
    chapter_id=models.SmallAutoField(primary_key=True)
    name=models.CharField(max_length=max_name_length,default="")

    @classmethod
    def create(cls, name):
        chapter = cls(name=name)
        chapter.save()
        # do something with the book
        return cls(name=name)


class Exercise(models.Model):
    class Meta:
        abstract = True
    max_question_length=100 #characters

    question_id=models.SmallAutoField(primary_key=True)
    question=models.CharField(max_length=max_question_length)


class TwoAnswerExercise(Exercise):
    max_answer_length=100 #characters
    answer1=models.CharField(max_length=max_answer_length)
    answer2=models.CharField(max_length=max_answer_length)
    
    correct_answer_index=models.PositiveSmallIntegerField(choices=(
        (1,"1"),
        (2,"2"),
    ))

class FourAnswerExercise(Exercise):
    max_answer_length=100 #characters
    answer1=models.CharField(max_length=max_answer_length)
    answer2=models.CharField(max_length=max_answer_length)
    answer3=models.CharField(max_length=max_answer_length)
    answer4=models.CharField(max_length=max_answer_length)
    
    correct_answer_index=models.PositiveSmallIntegerField(choices=(
        (1,"1"),
        (2,"2"),
        (3,"3"),
        (4,"4"),
    ))

class Course(models.Model):
    max_question_length=250 #characters

    course_id=models.SmallAutoField(primary_key=True)
    content=models.CharField(max_length=max_question_length)
    
