# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse

from .forms import LoginForm, SignUpForm
from django.contrib import messages

from .models import CustomUser


def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                messages.error(request,'Invalid credentials')
        else:
            messages.error(request,'Error validating the form')

    return render(request, "accounts/login.html", {"form": form})

def register_user(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            email = form.cleaned_data.get('email')
            if CustomUser.objects.filter(email__iexact=email).exists():
                messages.error(request,'Email exists')
                return redirect('register')
            user = authenticate(username=username, password=raw_password)
            form.save()
            messages.success(request, f'User created - please Sign IN.')

        else:
            messages.error(request,'Form is not valid')
            return redirect('register')
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form})

@login_required(login_url='login')
def Logout(request):
    logout(request)
    messages.success(request, '✅ Successfully Logged Out!')
    return redirect(reverse('login'))