from django.shortcuts import render, redirect
from .models import *
import bcrypt


# ********** functions that render page **********


def index(request):
    if request.session.get('email_session_id') != None:
        print('email_session_id already logged in')
        return redirect('/wishes')

    return render(request, 'index.html')


def wish_dashboard(request):
    # only allow user into dashboard if they have session id
    if request.session.get('email_session_id') == None:
        print('no session in email_session_id')
        return redirect('/')

    user_in_session = User.objects.get(
        email=request.session['email_session_id'])
    context = {
        'user_wishes': Wish.objects.filter(user=user_in_session, wish_granted=False),
        'user': user_in_session,
        'granted_wishes': Wish.objects.filter(wish_granted=True)

    }
    return render(request, 'wish_dashboard.html', context)


def create(request):
    user_in_session = User.objects.get(
        email=request.session['email_session_id'])
    context = {
        'user': user_in_session
    }
    return render(request, 'create.html', context)


def edit_wish(request, wish_id):
    # only allow user into dashboard if they have session id
    if request.session.get('email_session_id') == None:
        print('no session in email_session_id')
        return redirect('/')

    user_in_session = User.objects.get(
        email=request.session['email_session_id'])
    context = {
        'wish': Wish.objects.get(id=wish_id),
        'user': user_in_session
    }
    return render(request, 'edit_wish.html', context)


def stats(request):
    # only allow user into dashboard if they have session id
    if request.session.get('email_session_id') == None:
        print('no session in email_session_id')
        return redirect('/')

    user = User.objects.get(email=request.session['email_session_id'])
    context = {
        'user': user,
        'total_wishes_granted': Wish.objects.filter(wish_granted=True),
        'pending_wishes': Wish.objects.filter(wish_granted=False, user=user),
        'granted_wishes': Wish.objects.filter(wish_granted=True, user=user),
    }
    return render(request, 'stats.html', context)


# ******** functions that redirect to render page *********


def register(request):
    user_errors = User.objects.user_validator(request.POST)
    if len(user_errors) > 0:
        for key, value in user_errors.items():
            messages.error(request, value)
        return redirect("/")
    else:
        hashed_pw = bcrypt.hashpw(
            request.POST['password'].encode(), bcrypt.gensalt()).decode()
    print('hashed_pw:', hashed_pw)
    new_user = User.objects.create(
        first_name=request.POST['first_name'],
        last_name=request.POST['last_name'],
        email=request.POST['email'],
        password=hashed_pw
    )
    request.session['email_session_id'] = new_user.email
    return redirect('/wishes')


def login(request):
    user_list = User.objects.filter(email=request.POST['email'])
    if len(user_list) < 1:
        print('no user found')
        messages.error(request, 'User email was not found.')
        return redirect('/')
    else:
        print('user found -> logging in user')
        if bcrypt.checkpw(request.POST['password'].encode(), user_list[0].password.encode()):
            print('password match')
            request.session['email_session_id'] = user_list[0].email
            return redirect('/wishes')

        else:
            print('failed password')
            messages.error(request, 'Incorrect Password')
        return redirect('/')


def logout(request):
    print('loggin out user')
    print('clearing session email_session_id')
    request.session.clear()
    return redirect('/')


def create_wish(request):
    wish_errors = Wish.objects.wish_validator(request.POST)
    wish_in_db = Wish.objects.filter(wish_name=request.POST['wish_name'])
    if len(wish_errors) > 0:
        for key, value in wish_errors.items():
            messages.error(request, value)
        return redirect('/wishes/new')
    if len(wish_in_db) > 0:
        print('Wish already exists')
        messages.error(
            request, "Oops! You can's wish for the same item twice. Don't be greedy!")
        return redirect('/wishes/new')
    else:
        Wish.objects.create(
            wish_name=request.POST['wish_name'],
            wish_description=request.POST['wish_description'],
            user=User.objects.get(email=request.session['email_session_id'])

        )

    return redirect('/wishes')


def edit(request, wish_id):
    wish_errors = Wish.objects.wish_validator(request.POST)
    if len(wish_errors) > 0:
        for key, value in wish_errors.items():
            messages.error(request, value)
        return redirect(f'/wishes/edit/{wish_id}')
    else:
        wish_to_edit = Wish.objects.get(id=wish_id)
        wish_to_edit.wish_name = request.POST['wish_name']
        wish_to_edit.wish_description = request.POST['wish_description']
        wish_to_edit.save()

    return redirect('/wishes')


def delete(request, wish_id):
    wish_to_delete = Wish.objects.get(id=wish_id)
    wish_to_delete.delete()
    return redirect('/wishes')


def granted_wish(request, wish_id):
    wish_to_grant = Wish.objects.get(id=wish_id)
    wish_to_grant.wish_granted = True
    wish_to_grant.save()
    return redirect('/wishes')


def like_wish(request, wish_id):
    user_to_like = User.objects.get(
        email=request.session['email_session_id'])
    wish_to_like = Wish.objects.get(id=wish_id)
    wish_to_like.users_who_liked.add(user_to_like)
    return redirect('/wishes')
