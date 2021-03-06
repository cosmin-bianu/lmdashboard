from django.shortcuts import render
from django.views.generic import TemplateView
from .forms import LoginForm,ChapterCreationForm,CourseCreationForm,ExerciseCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from data_management.models import FourAnswerExercise,Course,Chapter
from django.views.decorators.http import require_http_methods
import logging
import urllib.parse



# Create your views here.
logger = logging.getLogger(__name__)
MAX_ORDER_NUMBER = 32767

@require_http_methods(["GET"])
def login_view(request):

    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        context = {
            "form":LoginForm,
        }
        return render(request, "login.html", context=context)

#TODO Session timeout
@require_http_methods(["POST"])
def authenticate_redirect_view(request):
    if request.method == "POST":
        username=request.POST['username']
        password=request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            logger.error('Invalid credentials.')
            return redirect('login')
    else:    
        logger.error('Not a POST request. Request method: ' + request.method)


@require_http_methods(["GET"])
@login_required(login_url='login')
def logout_redirect_view(request):
    logout(request)
    return redirect('login')

@require_http_methods(["GET"])
@login_required(login_url='login')
def dashboard_view(request):
    context = {
        "chapters_count": Chapter.objects.count(), 
        "question_count":  FourAnswerExercise.objects.count(),
        "course_count": Course.objects.count(),
        'disable_column':True,
    }
    return render(request, "dashboard.html", context)
    

#View pages

@require_http_methods(["GET"])
@login_required(login_url='login')
def manage_questions_view_general(request):
    chapters={}
    for chapter in Chapter.objects.all():
        count=FourAnswerExercise.objects.filter(chapter__chapter_id=chapter.chapter_id).count()
        chapters[chapter]=count
        
    breadcrumbs = [
        {"name":"Pagina principală", "link":"/"},
        {"name":"Întrebări", "link":"#", "current_page":True}
    ]
    context = {
        "page_title": "Întrebări",
        "breadcrumbs":breadcrumbs,
        "chapters":chapters,
    }
    return render(request, "view_questions_general.html", context)


@require_http_methods(["GET"])
@login_required(login_url='login')
def manage_questions_view_detailed(request):
    source_chapter_id = request.GET.get("id", None)
    if source_chapter_id is not None:
        chapter=Chapter.objects.get(chapter_id=source_chapter_id)
        questions=FourAnswerExercise.objects.filter(chapter__chapter_id=chapter.chapter_id)
        
        breadcrumbs = [
            {"name":"Pagina principală", "link":"/"},
            {"name":"Întrebări", "link":"/view/questions/general"},
            {"name":chapter.name, "link":"#", "current_page":True},
        ]

        processed_questions=[]

        for question in questions:
            processed_questions.append({
                "question":question.question,
                "author":question.author.get_full_name(),
                "answer_count":question.answer_count,
                "order_number":question.order_number,
                "id":question.question_id,
                })

        context={
            "page_title":chapter.name,
            "breadcrumbs":breadcrumbs,
            "questions":processed_questions,
            "source_chapter_id":source_chapter_id,
        }
        return render(request, "view_questions_detail.html", context)
    else:
        return redirect('dashboard')



@require_http_methods(["GET"])
@login_required(login_url='login')
def manage_chapters_view(request):
    breadcrumbs = [
        {"name":"Pagina principală", "link":"/"},
        {"name":"Capitole", "link":"#", "current_page":True}
    ]
    context = {
        "page_title": "Capitole",
        "breadcrumbs":breadcrumbs,
        "chapters":Chapter.objects.all(),
    }
    return render(request, "view_chapters.html", context)

@require_http_methods(["GET"])
@login_required(login_url='login')
def manage_courses_general_view(request):
    chapters={}
    for chapter in Chapter.objects.all():
        count=Course.objects.filter(chapter__chapter_id=chapter.chapter_id).count()
        chapters[chapter]=count
        
    breadcrumbs = [
        {"name":"Pagina principală", "link":"/"},
        {"name":"Lecții", "link":"#", "current_page":True}
    ]
    context = {
        "page_title": "Lecții",
        "breadcrumbs":breadcrumbs,
        "chapters":chapters,
    }
    return render(request, "view_courses_general.html", context)

@require_http_methods(["GET"])
@login_required(login_url='login')
def manage_courses_detailed_view(request):
    source_chapter_id = request.GET.get("id", None)
    if source_chapter_id is not None:
        chapter=Chapter.objects.get(chapter_id=source_chapter_id)
        courses=Course.objects.filter(chapter__chapter_id=chapter.chapter_id)
        
        breadcrumbs = [
            {"name":"Pagina principală", "link":"/"},
            {"name":"Lecții", "link":"/view/courses/general"},
            {"name":chapter.name, "link":"#", "current_page":True},
        ]

        processed_courses=[]

        for course in courses:
            processed_courses.append({
                "name":course.name,
                "author":course.author.get_full_name(),
                "order_number":course.order_number,
                "id":course.course_id,
                })

        context={
            "page_title":chapter.name,
            "breadcrumbs":breadcrumbs,
            "courses":processed_courses,
            "source_chapter_id":source_chapter_id,
        }
        return render(request, "view_courses_detail.html", context)
    else:
        return redirect('dashboard')


#Add pages

@require_http_methods(["GET"])
@login_required(login_url='login')
def manage_questions_add_view(request):
    target_chapter_id=request.GET.get("source_chapter_id", None)
    context = {
        "page_title": "Adaugă o întrebare",
        "form":ExerciseCreationForm(initial={
            'question':request.GET.get("question",None),
            'author':request.GET.get("author_id",request.user),
            'answer1':request.GET.get("answer1",None),
            'answer2':request.GET.get("answer2",None),
            'answer3':request.GET.get("answer3",None),
            'answer4':request.GET.get("answer4",None),
            'correct_answer_index':request.GET.get("correct_answer_index",None),
            'chapter':request.GET.get("chapter_id",target_chapter_id),
            'order_number':request.GET.get("order_number",None),
        }),
        "status":request.GET.get("status", None),
    }
    return render(request, "add_question.html", context)

@require_http_methods(["GET"])
@login_required(login_url='login')
def manage_courses_add_view(request):
    target_chapter_id=request.GET.get("source_chapter_id", None)
    context = {
        "page_title": "Adaugă o lecție",
        "form":CourseCreationForm(initial={
            'name':request.GET.get("name",None),
            'author':request.GET.get("author_id",request.user),
            'content':request.GET.get("content",None),
            'chapter':request.GET.get("chapter_id",target_chapter_id),
            'order_number':request.GET.get("order_number",None),
        }),
        "status":request.GET.get("status", None),
    }
    return render(request, "add_course.html", context)

@require_http_methods(["GET"])
@login_required(login_url='login')
def manage_chapters_add_view(request):
    context = {
        "page_title": "Adaugă un capitol",
        "form":ChapterCreationForm(initial={
            "name":request.GET.get("name",None),
            "order_number":request.GET.get("on",None),
            "description":request.GET.get("desc",None),
        }),
        "status":request.GET.get("status", None),
    }
    return render(request, "add_chapter.html", context)


#Edit pages
@require_http_methods(["GET"])
@login_required(login_url='login')
def manage_questions_edit_view(request):
    question_id=request.GET.get("id", None)
    question_obj=FourAnswerExercise.objects.get(pk=question_id)
    question=question_obj.question
    chapter=question_obj.chapter
    author=question_obj.author
    order_number=question_obj.order_number
    answer1=question_obj.answer1
    answer2=question_obj.answer2
    answer3=question_obj.answer3
    answer4=question_obj.answer4
    correct_answer_index=question_obj.correct_answer_index
    custom_chapter=request.GET.get("chapter_id",None)
    if custom_chapter is not None:
        chapter=custom_chapter

    context = {
        "page_title": "Modifică o întrebare",
        "form":ExerciseCreationForm(initial={
            'question':request.GET.get("question",question),
            'author':request.GET.get("author_id",author),
            'correct_answer_index':request.GET.get("correct_answer_index",correct_answer_index),
            'chapter':chapter,
            'answer1':request.GET.get("answer1",answer1),
            'answer2':request.GET.get("answer2",answer2),
            'answer3':request.GET.get("answer3",answer3),
            'answer4':request.GET.get("answer4",answer4),
            'order_number':request.GET.get("order_number",order_number),
            }),
        "status":request.GET.get("status", None),
        'question_id':question_id
    }
    return render(request, "edit_question.html", context)

@require_http_methods(["GET"])
@login_required(login_url='login')
def manage_courses_edit_view(request):
    course_id=request.GET.get("id", None)
    course=Course.objects.get(course_id=course_id)
    name=course.name
    author=course.author
    content=course.content
    chapter=course.chapter #Placeholder
    custom_chapter=request.GET.get("chapter_id",None)
    if custom_chapter is not None:
        chapter=custom_chapter
    order_number=course.order_number

    context = {
        "page_title": "Modifică o lecție",
        "form":CourseCreationForm(initial={
            'name':request.GET.get("name",name),
            'author':request.GET.get("author_id",author),
            'content':request.GET.get("content",content),
            'chapter':chapter,
            'order_number':request.GET.get("order_number",order_number),
            }),
        "status":request.GET.get("status", None),
        'course_id':course_id
    }
    return render(request, "edit_course.html", context)

@require_http_methods(["GET"])
@login_required(login_url='login')
def manage_chapters_edit_view(request):
    chapter_id=request.GET.get("id",None)
    chapter=Chapter.objects.get(pk=chapter_id)
    name=chapter.name
    order_number=chapter.order_number
    description=chapter.description
    context = {
        "page_title": "Modifică un capitol",
        "form":ChapterCreationForm(initial={
            "name":request.GET.get("name",name),
            "order_number":request.GET.get("on",order_number),
            "description":request.GET.get("desc",description),
        }),
        "status":request.GET.get("status", None),
        "id":chapter_id,
    }
    return render(request, "edit_chapter.html", context)






################################## API #########################################

#Max order number: 



# Add API

@require_http_methods(["POST"])
@login_required(login_url='login')
def manage_questions_add(request):
    question=request.POST.get("question", None)
    chapter_id=request.POST.get("chapter", None)
    chapter=Chapter.objects.get(chapter_id=chapter_id)
    author_id=request.POST.get("author", None)
    author=User.objects.get(id=author_id)
    order_number=request.POST.get("order_number", None)
    answer1=request.POST.get("answer1", None)
    answer2=request.POST.get("answer2", None)
    answer3=request.POST.get("answer3", None)
    answer4=request.POST.get("answer4", None)
    correct_answer_index=request.POST.get("correct_answer_index", None)

    
    if FourAnswerExercise.objects.filter(chapter=chapter).filter(order_number=order_number).count() > 0:
        context={
            "question":question,
            "chapter_id":chapter_id,
            "author_id":author_id,
            "order_number":order_number,
            "answer1":answer1,
            "answer2":answer2,
            "answer3":answer3,
            "answer4":answer4,
            "correct_answer_index":correct_answer_index,
        }
        return redirect('/view/questions/add?status=1&{}'.format(urllib.parse.urlencode(context)))

    answer1=answer1.strip()
    answer2=answer2.strip()
    answer3=answer3.strip()
    answer4=answer4.strip()
    
    if str(correct_answer_index) == "1" and not answer1 \
        or str(correct_answer_index) == "2" and not answer2 \
        or str(correct_answer_index) == "3" and not answer3 \
        or str(correct_answer_index) == "4" and not answer4:

        context={
            "question":question,
            "chapter_id":chapter_id,
            "author_id":author_id,
            "order_number":order_number,
            "answer1":answer1,
            "answer2":answer2,
            "answer3":answer3,
            "answer4":answer4,
            "correct_answer_index":correct_answer_index,
        }
        return redirect('/view/questions/add?status=2&{}'.format(urllib.parse.urlencode(context)))

    if int(order_number) > MAX_ORDER_NUMBER:
        context={
            "question":question,
            "chapter_id":chapter_id,
            "author_id":author_id,
            "order_number":order_number,
            "answer1":answer1,
            "answer2":answer2,
            "answer3":answer3,
            "answer4":answer4,
            "correct_answer_index":correct_answer_index,
        }
        return redirect('/view/questions/add?status=3&{}'.format(urllib.parse.urlencode(context)))


    answer_count=0
    if answer1:
        answer_count += 1
    if answer2:
        answer_count += 1
    if answer3:
        answer_count += 1
    if answer4:
        answer_count += 1
    
    question_obj=FourAnswerExercise(
        question=question,
        chapter=chapter,
        author=author,
        order_number=order_number,
        answer1=answer1,
        answer2=answer2,
        answer3=answer3,
        answer4=answer4,
        correct_answer_index=correct_answer_index,
        answer_count=answer_count
    )
    question_obj.save()

    return redirect('/view/questions/detailed?id={}'.format(chapter_id))

@require_http_methods(["POST"])
@login_required(login_url='login')
def manage_courses_add(request):
    name=request.POST.get("name", None)
    author_id=request.POST.get("author", None)
    author=User.objects.get(id=author_id)
    content=request.POST.get("content", None)
    chapter_id=request.POST.get("chapter", None)
    chapter=Chapter.objects.get(chapter_id=chapter_id)
    order_number=request.POST.get("order_number", None)

    if Course.objects.filter(chapter=chapter).filter(order_number=order_number).count() > 0:
        context={
            "name":name,
            "author_id":author_id,
            "content":content,
            "chapter_id":chapter_id,
            "order_number":order_number,
        }
        return redirect('/view/courses/add?status=1&{}'.format(urllib.parse.urlencode(context)))
    
    if int(order_number) > MAX_ORDER_NUMBER:
        context={
            "name":name,
            "author_id":author_id,
            "content":content,
            "chapter_id":chapter_id,
            "order_number":order_number,
        }
        return redirect('/view/courses/add?status=3&{}'.format(urllib.parse.urlencode(context)))

    course=Course(
        name=name,
        author=author,
        content=content,
        chapter=chapter,
        order_number=order_number,
    )
    course.save()
    return redirect('/view/courses/detailed?id={}'.format(chapter_id))

@require_http_methods(["POST"])
@login_required(login_url='login')
def manage_chapters_add(request):
    name = request.POST.get("name", None)
    order_number = request.POST.get("order_number",None)
    description = request.POST.get("description",None)
    if Chapter.objects.filter(order_number=order_number).count() > 0:
        context={
            "name":name,
            "on":order_number,
            "desc":description,
        }
        return redirect('/view/chapters/add?status=1&{}'.format(urllib.parse.urlencode(context)))

    
    if int(order_number) > MAX_ORDER_NUMBER:
        context={
            "name":name,
            "on":order_number,
            "desc":description,
        }
        return redirect('/view/chapters/add?status=3&{}'.format(urllib.parse.urlencode(context)))
    
    Chapter.create(
        name=name,
        order_number=order_number,
        description=description,
    )
    return redirect('view_chapters')


# Edit API

@require_http_methods(["POST"])
@login_required(login_url='login')
def manage_questions_edit(request):
    question_id=request.POST.get("question_id", None)
    question_obj=FourAnswerExercise.objects.get(pk=question_id)
    question=request.POST.get("question", None)
    chapter_id=request.POST.get("chapter", None)
    chapter=Chapter.objects.get(chapter_id=chapter_id)
    author_id=request.POST.get("author", None)
    author=User.objects.get(id=author_id)
    order_number=request.POST.get("order_number", None)
    answer1=request.POST.get("answer1", None)
    answer2=request.POST.get("answer2", None)
    answer3=request.POST.get("answer3", None)
    answer4=request.POST.get("answer4", None)
    correct_answer_index=request.POST.get("correct_answer_index", None)

    if (int(order_number) != int(question_obj.order_number) or int(question_obj.chapter.chapter_id) != int(chapter_id)) \
        and FourAnswerExercise.objects.filter(chapter=chapter).filter(order_number=order_number).count() > 0:
        context={
            "question":question,
            "chapter_id":chapter_id,
            "author_id":author_id,
            "order_number":order_number,
            "answer1":answer1,
            "answer2":answer2,
            "answer3":answer3,
            "answer4":answer4,
            "correct_answer_index":correct_answer_index,
            "id":question_id,
        }
        return redirect('/view/questions/edit?status=1&{}'.format(urllib.parse.urlencode(context)))

    question_obj.question=question
    question_obj.chapter=chapter
    question_obj.author=author
    question_obj.order_number=order_number
    question_obj.answer1=answer1
    question_obj.answer2=answer2
    question_obj.answer3=answer3
    question_obj.answer4=answer4
    question_obj.correct_answer_index=correct_answer_index

    answer1=answer1.strip()
    answer2=answer2.strip()
    answer3=answer3.strip()
    answer4=answer4.strip()
    
    if str(correct_answer_index) == "1" and not answer1 \
        or str(correct_answer_index) == "2" and not answer2 \
        or str(correct_answer_index) == "3" and not answer3 \
        or str(correct_answer_index) == "4" and not answer4:

        context={
            "question":question,
            "chapter_id":chapter_id,
            "author_id":author_id,
            "order_number":order_number,
            "answer1":answer1,
            "answer2":answer2,
            "answer3":answer3,
            "answer4":answer4,
            "correct_answer_index":correct_answer_index,
        }
        return redirect('/view/questions/edit?status=2&{}'.format(urllib.parse.urlencode(context)))
    
    if int(order_number) > MAX_ORDER_NUMBER:
        context={
            "question":question,
            "chapter_id":chapter_id,
            "author_id":author_id,
            "order_number":order_number,
            "answer1":answer1,
            "answer2":answer2,
            "answer3":answer3,
            "answer4":answer4,
            "correct_answer_index":correct_answer_index,
        }
        return redirect('/view/questions/edit?status=3&{}'.format(urllib.parse.urlencode(context)))

    answer_count=0
    if answer1:
        answer_count += 1
    if answer2:
        answer_count += 1
    if answer3:
        answer_count += 1
    if answer4:
        answer_count += 1
    
    question_obj.answer_count=answer_count
    question_obj.save()

    return redirect('/view/questions/detailed?id={}'.format(chapter_id))


@require_http_methods(["POST"])
@login_required(login_url='login')
def manage_courses_edit(request):
    course_id=request.POST.get("course_id", None)
    course=Course.objects.get(pk=course_id)
    name=request.POST.get("name", None)
    author_id=request.POST.get("author", None)
    author=User.objects.get(id=author_id)
    content=request.POST.get("content", None)
    chapter_id=request.POST.get("chapter", None)
    chapter=Chapter.objects.get(pk=chapter_id)
    order_number=request.POST.get("order_number", None)

    if (int(order_number) != int(course.order_number) or int(course.chapter.chapter_id) != int(chapter_id)) \
        and Course.objects.filter(chapter=chapter).filter(order_number=order_number).count() > 0:
        context={
            "name":name,
            "author_id":author_id,
            "content":content,
            "chapter_id":chapter_id,
            "order_number":order_number,
            "id":course_id,
        }
        return redirect('/view/courses/edit?status=1&{}'.format(urllib.parse.urlencode(context)))

        
    if int(order_number) > MAX_ORDER_NUMBER:
        context={
            "name":name,
            "author_id":author_id,
            "content":content,
            "chapter_id":chapter_id,
            "order_number":order_number,
            "id":course_id,
        }
        return redirect('/view/courses/edit?status=3&{}'.format(urllib.parse.urlencode(context)))

    course.name=name
    course.author=author
    course.content=content
    course.chapter=chapter
    course.order_number=order_number
    course.save()
    return redirect('/view/courses/detailed?id={}'.format(chapter_id))


@require_http_methods(["POST"])
@login_required(login_url='login')
def manage_chapters_edit(request):
    name = request.POST.get("name", None)
    order_number = request.POST.get("order_number",None)
    description = request.POST.get("description",None)
    chapter_id = request.POST.get("id",None)
    chapter=Chapter.objects.get(pk=chapter_id)
    if int(order_number) != int(chapter.order_number) and Chapter.objects.filter(order_number=order_number).count() > 0:
        context={
            "name":name,
            "on":order_number,
            "desc":description,
            "id":chapter_id,
        }
        return redirect('/view/chapters/edit?status=1&{}'.format(urllib.parse.urlencode(context)))
        
    if int(order_number) > MAX_ORDER_NUMBER:
        context={
            "name":name,
            "on":order_number,
            "desc":description,
            "id":chapter_id,
        }
        return redirect('/view/chapters/edit?status=3&{}'.format(urllib.parse.urlencode(context)))
    
    chapter.name=name
    chapter.order_number=order_number
    chapter.description=description
    chapter.save()
    return redirect('view_chapters')


# Remove API
    
@require_http_methods(["GET"])
@login_required(login_url='login')
def manage_questions_remove(request):
    target_id = request.GET.get("id", None)
    source_chapter_id = request.GET.get("source_chapter_id", None)
    FourAnswerExercise.objects.filter(pk=target_id).delete()
    return redirect('/view/questions/detailed?id={}'.format(source_chapter_id))

@require_http_methods(["GET"])
@login_required(login_url='login')
def manage_courses_remove(request):
    target_id = request.GET.get("id", None)
    source_chapter_id = request.GET.get("source_chapter_id", None)
    Course.objects.filter(pk=target_id).delete()
    return redirect('/view/courses/detailed?id={}'.format(source_chapter_id))

@require_http_methods(["GET"])
@login_required(login_url='login')
def manage_chapters_remove(request):
    target_id = request.GET["id"]
    Chapter.objects.filter(chapter_id=target_id).delete()
    return redirect('view_chapters')

#TODO EDIT PAGES

#TODO ADD FISIERE (poate imagini?)
