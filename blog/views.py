from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.utils.text import slugify
from django.db.models import Count
import os
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from .models import Article, Comment, CommentReply, Download
from .forms import ArticleForm, CommentForm, CommentReplyForm
from .models import ContactMessage
from .forms import ContactForm

def home(request):
    """Page d'accueil avec présentation et derniers articles"""
    articles = Article.objects.filter(is_published=True)[:3]
    context = {
        'articles': articles,
    }
    return render(request, 'blog/home.html', context)

class ArticleListView(ListView):
    model = Article
    template_name = 'blog/article_list.html'
    context_object_name = 'articles'
    paginate_by = 6
    
    def get_queryset(self):
        return Article.objects.filter(is_published=True).annotate(
            comment_count=Count('comments')
        )

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'blog/article_detail.html'
    context_object_name = 'article'
    
    def get_queryset(self):
        return Article.objects.filter(is_published=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['reply_form'] = CommentReplyForm()
        
        # Récupérer les commentaires approuvés avec leurs réponses
        comments = self.object.comments.filter(is_approved=True).prefetch_related('replies')
        context['comments'] = comments
        
        return context

def download_file(request, article_id):
    """Gestion du téléchargement de fichier avec suivi"""
    article = get_object_or_404(Article, id=article_id, is_published=True)
    
    if article.file:
        # Enregistrer le téléchargement
        ip_address = get_client_ip(request)
        Download.objects.create(article=article, ip_address=ip_address)
        
        # Servir le fichier
        file_path = article.file.path
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
    else:
        messages.error(request, "Aucun fichier disponible pour le téléchargement.")
        return redirect('article_detail', slug=article.slug)

def get_client_ip(request):
    """Récupérer l'adresse IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def add_comment(request, article_id):
    """Ajouter un commentaire"""
    article = get_object_or_404(Article, id=article_id, is_published=True)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.save()
            
            messages.success(request, "Votre commentaire a été ajouté et sera visible après approbation.")
        else:
            messages.error(request, "Erreur lors de l'ajout du commentaire.")
    
    return redirect('article_detail', slug=article.slug)

@login_required
def add_reply(request, comment_id):
    """Ajouter une réponse à un commentaire (admin seulement)"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.method == 'POST':
        form = CommentReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.comment = comment
            reply.author_name = request.user.username
            reply.save()
            
            messages.success(request, "Votre réponse a été ajoutée.")
        else:
            messages.error(request, "Erreur lors de l'ajout de la réponse.")
    
    return redirect('article_detail', slug=comment.article.slug)

@login_required
def approve_comment(request, comment_id):
    """Approuver un commentaire (admin seulement)"""
    comment = get_object_or_404(Comment, id=comment_id)
    comment.is_approved = True
    comment.save()
    
    messages.success(request, "Commentaire approuvé avec succès.")
    return redirect('admin_dashboard')

# Vues d'administration
@login_required
def admin_dashboard(request):
    """Tableau de bord d'administration"""
    articles = Article.objects.all().order_by('-created_at')
    pending_comments = Comment.objects.filter(is_approved=False)
    recent_downloads = Download.objects.all().order_by('-downloaded_at')[:10]
    
    context = {
        'articles': articles,
        'pending_comments': pending_comments,
        'recent_downloads': recent_downloads,
    }
    return render(request, 'blog/admin/dashboard.html', context)

@login_required
def admin_article_create(request):
    """Créer un nouvel article"""
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save()
            messages.success(request, "Article créé avec succès!")
            return redirect('admin_dashboard')
    else:
        form = ArticleForm()
    
    context = {'form': form}
    return render(request, 'blog/admin/article_form.html', context)

@login_required
def admin_article_edit(request, article_id):
    """Modifier un article existant"""
    article = get_object_or_404(Article, id=article_id)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, "Article modifié avec succès!")
            return redirect('admin_dashboard')
    else:
        form = ArticleForm(instance=article)
    
    context = {'form': form, 'article': article}
    return render(request, 'blog/admin/article_form.html', context)

@login_required
def admin_article_delete(request, article_id):
    """Supprimer un article"""
    article = get_object_or_404(Article, id=article_id)
    
    if request.method == 'POST':
        article.delete()
        messages.success(request, "Article supprimé avec succès!")
        return redirect('admin_dashboard')
    
    context = {'article': article}
    return render(request, 'blog/admin/article_confirm_delete.html', context)




# Ajoutez ces fonctions à la fin de votre fichier views.py

def custom_login(request):
    """Vue de connexion personnalisée"""
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'admin_dashboard')
                return redirect(next_url)
    else:
        form = AuthenticationForm()
    
    return render(request, 'blog/admin/login.html', {'form': form})



def custom_logout(request):
    """Vue de déconnexion"""
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('home')

 

def contact(request):
    """Page de contact"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            
            # Envoyer un email (optionnel)
            send_contact_email(contact_message)
            
            messages.success(request, "Votre message a été envoyé avec succès ! Je vous répondrai dans les plus brefs délais.")
            return redirect('contact')
    else:
        form = ContactForm()
    
    context = {'form': form}
    return render(request, 'blog/contact.html', context)

def send_contact_email(contact_message):
    """Envoyer un email de notification pour un nouveau message de contact"""
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = f"Nouveau message de contact: {contact_message.subject}"
        message = f"""
        Nouveau message de contact reçu:
        
        Nom: {contact_message.name}
        Email: {contact_message.email}
        Sujet: {contact_message.subject}
        Message:
        {contact_message.message}
        
        Date: {contact_message.created_at}
        """
        
        # Envoyer à l'admin
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],  # Remplacez par votre email
            fail_silently=True,
        )
    except Exception as e:
        # Log l'erreur mais ne bloque pas l'envoi du message
        print(f"Erreur envoi email: {e}")

@staff_member_required
def contact_messages(request):
    """Liste des messages de contact (admin seulement)"""
    messages_list = ContactMessage.objects.all().order_by('-created_at')
    unread_count = ContactMessage.objects.filter(is_read=False).count()
    
    context = {
        'messages_list': messages_list,
        'unread_count': unread_count,
    }
    return render(request, 'blog/admin/contact_messages.html', context)

@staff_member_required
def contact_message_detail(request, message_id):
    """Détail d'un message de contact"""
    contact_message = get_object_or_404(ContactMessage, id=message_id)
    
    # Marquer comme lu
    if not contact_message.is_read:
        contact_message.is_read = True
        contact_message.save()
    
    context = {'message': contact_message}
    return render(request, 'blog/admin/contact_message_detail.html', context)

@staff_member_required
def delete_contact_message(request, message_id):
    """Supprimer un message de contact"""
    contact_message = get_object_or_404(ContactMessage, id=message_id)
    
    if request.method == 'POST':
        contact_message.delete()
        messages.success(request, "Message supprimé avec succès.")
        return redirect('contact_messages')
    
    context = {'message': contact_message}
    return render(request, 'blog/admin/contact_message_confirm_delete.html', context)